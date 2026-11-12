"""
apps/emergencies/services.py
SafeGuard AI — Emergency business logic service layer.
SOS alert creation, idempotency verification, trusted contacts notification queuing,
aur cancellation/resolution workflow yahan handle hota hai.
"""

import logging
import secrets
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from .models import EmergencyEvent
from apps.contacts.models import TrustedContact
from apps.locations.models import LocationSnapshot, LocationSharingSession
from apps.notifications.models import NotificationDelivery
from apps.audit.models import AuditLog

logger = logging.getLogger(__name__)


def trigger_sos(user, validated_data, ip_address=None, user_agent=''):
    """
    Is service ka kaam emergency event create karna aur alerts dispatch karna hai.
    Returns tuple: (emergency_event, is_created)
    """
    idempotency_key = validated_data.get('idempotency_key')

    # Duplicate SOS request ko rokne ke liye idempotency check kar rahe hain
    # Agar client ne accidental double tap kiya ho to duplicate event nahi banega
    existing_event = EmergencyEvent.objects.filter(idempotency_key=idempotency_key).first()
    if existing_event:
        if existing_event.owner_id != user.id:
            logger.warning(
                f"Idempotency collision detected: key={idempotency_key} by user={user.id}"
            )
            raise ValidationError({'idempotency_key': 'Idempotency key already used by another account.'})
        # Existing event ko bina duplicate alert banaye return kar rahe hain
        logger.info(
            f"Duplicate SOS trigger suppressed for event={existing_event.id} user={user.id}"
        )
        return existing_event, False

    # Atomic transaction me event, initial location, aur notification delivery records create honge
    with transaction.atomic():
        event = EmergencyEvent.objects.create(
            owner=user,
            event_type=validated_data.get('event_type', 'sos'),
            status='active',
            idempotency_key=idempotency_key,
            notes=validated_data.get('notes', ''),
        )

        # Initial location snapshot agar request payload me di gayi ho
        lat = validated_data.get('latitude')
        lng = validated_data.get('longitude')
        snapshot = None

        if lat is not None and lng is not None:
            # Emergency ke waqt location trusted contacts ke liye turant shareable banayi jaati hai
            captured_at = validated_data.get('captured_at') or timezone.now()
            share_token = secrets.token_urlsafe(32)

            snapshot = LocationSnapshot.objects.create(
                owner=user,
                emergency_event=event,
                latitude=lat,
                longitude=lng,
                accuracy_meters=validated_data.get('accuracy_meters'),
                altitude_meters=validated_data.get('altitude_meters'),
                captured_at=captured_at,
                sharing_scope='contacts',
                share_token=share_token,
                expires_at=timezone.now() + timezone.timedelta(hours=24),
                is_sharing_active=True,
            )

        # User ke active trusted contacts fetch kar rahe hain
        active_contacts = list(TrustedContact.objects.filter(owner=user, is_active=True))

        # Agar snapshot bana hai to har contact ke liye secure sharing session create karo
        if snapshot:
            for contact in active_contacts:
                LocationSharingSession.objects.create(
                    location_snapshot=snapshot,
                    shared_with_contact=contact,
                    access_token=secrets.token_urlsafe(32),
                    expires_at=snapshot.expires_at,
                    is_active=True,
                )

        # CRITICAL: SOS alert must NEVER depend on AI availability.
        # Direct notifications queue ho rahe hain har verified/active contact ke liye
        notification_records = [
            NotificationDelivery(
                emergency_event=event,
                recipient_contact=contact,
                status='pending',
            )
            for contact in active_contacts
        ]
        if notification_records:
            NotificationDelivery.objects.bulk_create(notification_records)

        # Audit trail: Tamper-evident log create karte hain
        # SECURITY NOTICE: Kabhi passwords, tokens, ya raw coordinates audit log me nahi daalte
        try:
            AuditLog.objects.create(
                actor=user,
                action_category='emergency',
                action='sos_triggered',
                severity='critical',
                target_object_type='EmergencyEvent',
                target_object_id=str(event.id),
                ip_address=ip_address,
                user_agent=user_agent[:500] if user_agent else '',
                extra_data={
                    'event_type': event.event_type,
                    'contacts_count': len(active_contacts),
                    'has_initial_location': bool(snapshot),
                },
            )
        except Exception as audit_err:
            logger.error(f"Failed to write audit log for emergency {event.id}: {audit_err}")

        logger.info(
            f"Emergency SOS triggered: id={event.id} user={user.id} contacts_alerted={len(active_contacts)}"
        )
        return event, True


def cancel_emergency(event, user, notes='', ip_address=None, user_agent=''):
    """
    User ne emergency cancel ki hai (misclick ya situation safe ho gayi).
    """
    if event.owner_id != user.id:
        raise ValidationError("Sirf emergency creator hi is alert ko cancel kar sakta hai.")

    if event.status == 'cancelled':
        return event

    if event.status == 'resolved':
        raise ValidationError("Yeh emergency pehle se resolved hai aur cancel nahi ki ja sakti.")

    with transaction.atomic():
        event.status = 'cancelled'
        event.cancelled_at = timezone.now()
        if notes:
            event.notes = f"{event.notes}\n[Cancelled]: {notes}".strip()
        event.save(update_fields=['status', 'cancelled_at', 'notes', 'updated_at'])

        # Emergency cancel hone par live location sharing turant deactivate karte hain privacy ke liye
        LocationSnapshot.objects.filter(emergency_event=event).update(is_sharing_active=False)
        LocationSharingSession.objects.filter(location_snapshot__emergency_event=event).update(is_active=False)

        try:
            AuditLog.objects.create(
                actor=user,
                action_category='emergency',
                action='emergency_cancelled',
                severity='info',
                target_object_type='EmergencyEvent',
                target_object_id=str(event.id),
                ip_address=ip_address,
                user_agent=user_agent[:500] if user_agent else '',
                extra_data={'status_transition': 'cancelled'},
            )
        except Exception as audit_err:
            logger.error(f"Audit log failed on emergency cancel {event.id}: {audit_err}")

    logger.info(f"Emergency cancelled: id={event.id} user={user.id}")
    return event


def resolve_emergency(event, user, notes='', ip_address=None, user_agent=''):
    """
    Emergency safaltapoorvak resolve ho chuki hai (help arrived ya user secure hai).
    """
    if event.owner_id != user.id:
        raise ValidationError("Sirf emergency creator hi is alert ko resolve kar sakta hai.")

    if event.status == 'resolved':
        return event

    if event.status == 'cancelled':
        raise ValidationError("Yeh emergency pehle se cancelled hai aur resolve nahi ki ja sakti.")

    with transaction.atomic():
        event.status = 'resolved'
        event.resolved_at = timezone.now()
        if notes:
            event.notes = f"{event.notes}\n[Resolved]: {notes}".strip()
        event.save(update_fields=['status', 'resolved_at', 'notes', 'updated_at'])

        # Emergency resolve hone par location sharing sessions expire/inactive karte hain
        LocationSnapshot.objects.filter(emergency_event=event).update(is_sharing_active=False)
        LocationSharingSession.objects.filter(location_snapshot__emergency_event=event).update(is_active=False)

        try:
            AuditLog.objects.create(
                actor=user,
                action_category='emergency',
                action='emergency_resolved',
                severity='info',
                target_object_type='EmergencyEvent',
                target_object_id=str(event.id),
                ip_address=ip_address,
                user_agent=user_agent[:500] if user_agent else '',
                extra_data={'status_transition': 'resolved'},
            )
        except Exception as audit_err:
            logger.error(f"Audit log failed on emergency resolve {event.id}: {audit_err}")

    logger.info(f"Emergency resolved: id={event.id} user={user.id}")
    return event


def get_user_emergencies(user, status_filter=None, event_type_filter=None):
    """
    User ki saari past emergency events fetch karna with prefetching for performance.
    """
    qs = (
        EmergencyEvent.objects.filter(owner=user)
        .prefetch_related('location_snapshots', 'notification_deliveries')
        .order_by('-created_at')
    )

    if status_filter:
        qs = qs.filter(status=status_filter)

    if event_type_filter:
        qs = qs.filter(event_type=event_type_filter)

    return qs


def get_emergency_by_id_and_owner(event_id, user):
    """
    Specific emergency event fetch karna with ownership check taaki koi dusra user access na kar sake.
    """
    return (
        EmergencyEvent.objects.filter(id=event_id, owner=user)
        .prefetch_related('location_snapshots', 'notification_deliveries__recipient_contact')
        .first()
    )
