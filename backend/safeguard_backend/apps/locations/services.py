"""
apps/locations/services.py
SafeGuard AI — Location tracking aur privacy-focused sharing services.
Location snapshot creation, expiring token management, aur contact sharing sessions yahan handle hote hain.
"""

import logging
import secrets
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError

from .models import LocationSnapshot, LocationSharingSession
from apps.emergencies.models import EmergencyEvent
from apps.contacts.models import TrustedContact
from apps.audit.models import AuditLog

logger = logging.getLogger(__name__)


def record_location(user, validated_data, ip_address=None, user_agent=''):
    """
    Is service ka kaam user ki location save karna aur sharing sessions initialize karna hai.
    Supports expiring tokens aur contacts/public privacy levels.
    """
    lat = validated_data['latitude']
    lng = validated_data['longitude']
    accuracy = validated_data.get('accuracy_meters')
    altitude = validated_data.get('altitude_meters')
    captured_at = validated_data.get('captured_at') or timezone.now()
    sharing_scope = validated_data.get('sharing_scope', 'private')
    emergency_event_id = validated_data.get('emergency_event_id')
    expires_in_minutes = validated_data.get('expires_in_minutes', 60)
    contact_ids = validated_data.get('shared_with_contact_ids', [])

    # Emergency event agar provide kiya gaya ho to fetch karte hain
    emergency_event = None
    if emergency_event_id:
        emergency_event = EmergencyEvent.objects.filter(id=emergency_event_id, owner=user).first()
        if not emergency_event:
            raise ValidationError({'emergency_event_id': 'Emergency event nahi mila ya access permitted nahi hai.'})

    # Location sharing ke liye secure cryptographically random token generate karte hain
    # Har snapshot ke paas unique share_token hota hai jo database unique constraint ensure karta hai
    share_token = secrets.token_urlsafe(32)

    # Privacy control: Sharing kab expire hogi calculate kar rahe hain
    expires_at = timezone.now() + timezone.timedelta(minutes=expires_in_minutes)

    with transaction.atomic():
        snapshot = LocationSnapshot.objects.create(
            owner=user,
            emergency_event=emergency_event,
            latitude=lat,
            longitude=lng,
            accuracy_meters=accuracy,
            altitude_meters=altitude,
            captured_at=captured_at,
            sharing_scope=sharing_scope,
            share_token=share_token,
            expires_at=expires_at,
            is_sharing_active=True,
        )

        # Specific trusted contacts ke saath individual session tokens create karte hain
        if contact_ids:
            valid_contacts = TrustedContact.objects.filter(
                id__in=contact_ids,
                owner=user,
                is_active=True,
            )
            sessions = [
                LocationSharingSession(
                    location_snapshot=snapshot,
                    shared_with_contact=contact,
                    access_token=secrets.token_urlsafe(32),
                    expires_at=expires_at,
                    is_active=True,
                )
                for contact in valid_contacts
            ]
            LocationSharingSession.objects.bulk_create(sessions)

        # Audit trail: Tamper-evident logging
        # CRITICAL: Raw location coordinates audit log me KABHI nahi daalte
        try:
            AuditLog.objects.create(
                actor=user,
                action_category='location',
                action='location_snapshot_created',
                severity='info',
                target_object_type='LocationSnapshot',
                target_object_id=str(snapshot.id),
                ip_address=ip_address,
                user_agent=user_agent[:500] if user_agent else '',
                extra_data={
                    'sharing_scope': sharing_scope,
                    'has_emergency': bool(emergency_event),
                    'sessions_count': len(contact_ids),
                },
            )
        except Exception as audit_err:
            logger.error(f"Audit log failed for location snapshot {snapshot.id}: {audit_err}")

    logger.info(
        f"Location snapshot created: id={snapshot.id} user={user.id} scope={sharing_scope}"
    )
    return snapshot


def get_shared_location_by_token(share_token, ip_address=None, user_agent=''):
    """
    Share token ke zariye location verify aur retrieve karna with privacy checks.
    Supports both public snapshot share token aur specific contact access token.
    """
    if not share_token:
        raise NotFound("Share token provide karna anivarya hai.")

    # 1. Pehle check karte hain kya yeh LocationSnapshot ka direct share_token hai
    snapshot = (
        LocationSnapshot.objects.filter(share_token=share_token)
        .select_related('owner', 'emergency_event')
        .first()
    )

    if snapshot:
        # Privacy check 1: Scope private nahi hona chahiye
        if snapshot.sharing_scope == 'private':
            raise PermissionDenied("Yeh location private hai aur share nahi ki ja sakti.")

        # Privacy check 2: Owner ne sharing band to nahi kar di
        if not snapshot.is_sharing_active:
            raise PermissionDenied("Yeh location sharing link owner dwara deactivate kar diya gaya hai.")

        # Privacy check 3: Expiry time check
        if snapshot.expires_at and snapshot.expires_at < timezone.now():
            raise ValidationError("Yeh location sharing link expire ho chuka hai.")

        return snapshot

    # 2. Agar direct share_token nahi mila, to check karte hain kya yeh LocationSharingSession access_token hai
    session = (
        LocationSharingSession.objects.filter(access_token=share_token)
        .select_related(
            'location_snapshot__owner',
            'location_snapshot__emergency_event',
            'shared_with_contact',
        )
        .first()
    )

    if session:
        # Session aur snapshot active hona zaroori hai
        if not session.is_active or not session.location_snapshot.is_sharing_active:
            raise PermissionDenied("Yeh location sharing session ab active nahi hai.")

        if session.expires_at < timezone.now():
            raise ValidationError("Yeh location sharing session expire ho chuki hai.")

        # Last accessed timestamp update karte hain
        session.last_accessed_at = timezone.now()
        session.save(update_fields=['last_accessed_at'])

        return session.location_snapshot

    # Agar na snapshot mila na session mila
    raise NotFound("Shared location link invalid hai ya exist nahi karta.")


def get_user_location_history(
    user,
    emergency_event_id=None,
    start_date=None,
    end_date=None,
    sharing_scope=None,
):
    """
    Authenticated user ki past location history fetch karne ka function.
    """
    qs = (
        LocationSnapshot.objects.filter(owner=user)
        .select_related('emergency_event')
        .prefetch_related('sharing_sessions__shared_with_contact')
        .order_by('-captured_at', '-created_at')
    )

    if emergency_event_id:
        qs = qs.filter(emergency_event_id=emergency_event_id)

    if start_date:
        qs = qs.filter(captured_at__gte=start_date)

    if end_date:
        qs = qs.filter(captured_at__lte=end_date)

    if sharing_scope:
        qs = qs.filter(sharing_scope=sharing_scope)

    return qs


def revoke_location_sharing(snapshot, user):
    """
    Owner kisi bhi waqt apni location sharing band kar sakta hai.
    """
    if snapshot.owner_id != user.id:
        raise PermissionDenied("Aap sirf apni location sharing ko revoke kar sakte hain.")

    with transaction.atomic():
        snapshot.is_sharing_active = False
        snapshot.save(update_fields=['is_sharing_active'])
        # Linked sessions bhi band ho jaate hain
        snapshot.sharing_sessions.update(is_active=False)

    logger.info(f"Location sharing revoked for snapshot {snapshot.id} by user {user.id}")
    return snapshot
