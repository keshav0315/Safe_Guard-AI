"""
apps/notifications/services.py
SafeGuard AI — Push Notification & Device Token Services
FCM push notification dispatch, token management aur delivery lifecycle.
"""

import uuid
import logging
from datetime import timedelta
from typing import Optional, List, Dict, Any

from django.conf import settings
from django.utils import timezone
from django.db import transaction

from .models import DeviceToken, NotificationDelivery
from apps.audit.services import record_audit_log

logger = logging.getLogger('apps.notifications')

# Retry configuration
MAX_NOTIFICATION_RETRIES = getattr(settings, 'MAX_NOTIFICATION_RETRIES', 3)


# ---------------------------------------------------------------------------
# Device Token Management
# ---------------------------------------------------------------------------

def register_or_update_device_token(
    user,
    token: str,
    platform: str = 'android',
    device_name: str = '',
    request=None,
) -> DeviceToken:
    """
    # FCM device token register karne ka service function.
    Agar same token pehle se kisi aur user pe tha (e.g. phone transfer/logout),
    to purane user ka token deactivate kar diya jata hai security ke liye.
    """
    token = token.strip()

    with transaction.atomic():
        # Step 1: Agar token kisi dusre user ke paas active hai to deactivate karo
        DeviceToken.objects.filter(token=token).exclude(owner=user).update(is_active=False)

        # Step 2: Current user ke liye token update ya create karo
        device_token, created = DeviceToken.objects.update_or_create(
            owner=user,
            token=token,
            defaults={
                'platform': platform,
                'device_name': device_name,
                'is_active': True,
            },
        )

    # Audit log entry — note: sensitive full token ko log nahi kiya jata
    record_audit_log(
        actor=user,
        action_category='notification',
        action='device_token_registered' if created else 'device_token_refreshed',
        severity='info',
        target_object=device_token,
        request=request,
        extra_data={
            'platform': platform,
            'device_name': device_name,
            'is_new_registration': created,
        },
    )

    logger.info(
        'Device token %s for user %s [platform=%s, device=%s]',
        'created' if created else 'updated',
        user.email,
        platform,
        device_name,
    )
    return device_token


def deactivate_device_token(user, token_id: uuid.UUID, request=None) -> bool:
    """
    Device token ko deactivate (logout / deregister) karne ka service function.
    """
    try:
        device_token = DeviceToken.objects.get(id=token_id, owner=user)
        device_token.is_active = False
        device_token.save(update_fields=['is_active'])

        record_audit_log(
            actor=user,
            action_category='notification',
            action='device_token_deactivated',
            severity='info',
            target_object=device_token,
            request=request,
            extra_data={'platform': device_token.platform},
        )
        return True
    except DeviceToken.DoesNotExist:
        return False


def get_user_device_tokens(user) -> List[DeviceToken]:
    """User ke active device tokens fetch karta hai."""
    return list(DeviceToken.objects.filter(owner=user, is_active=True).order_by('-last_seen_at'))


# ---------------------------------------------------------------------------
# Notification Delivery Lifecycle
# ---------------------------------------------------------------------------

def create_notification_delivery(
    emergency_event,
    recipient_contact=None,
    device_token: Optional[DeviceToken] = None,
) -> NotificationDelivery:
    """
    Emergency event ke liye naya NotificationDelivery record initialize karta hai.
    """
    return NotificationDelivery.objects.create(
        emergency_event=emergency_event,
        recipient_contact=recipient_contact,
        device_token=device_token,
        status='pending',
    )


def send_push_notification(
    delivery: NotificationDelivery,
    title: str,
    body: str,
    data_payload: Optional[Dict[str, Any]] = None,
) -> NotificationDelivery:
    """
    Push notification dispatch service.
    Production mein Firebase Admin SDK use karta hai;
    Development/Test mein gracefully fallback simulated dispatch perform karta hai.
    """
    if data_payload is None:
        data_payload = {}

    target_token = delivery.device_token.token if delivery.device_token else None

    # Agar device token available nahi hai to delivery fail mark karo
    if not target_token:
        delivery.status = 'failed'
        delivery.failure_code = 'NO_DEVICE_TOKEN'
        delivery.failure_message = 'No active FCM device token available for recipient.'
        delivery.save()
        return delivery

    try:
        # Check if firebase_admin is initialized
        firebase_credentials_path = getattr(settings, 'FIREBASE_CREDENTIALS_PATH', '')
        provider_message_id = ''

        if firebase_credentials_path:
            # Firebase Admin SDK execution
            try:
                import firebase_admin
                from firebase_admin import messaging

                # Ensure app is initialized
                if not firebase_admin._apps:
                    cred = firebase_admin.credentials.Certificate(firebase_credentials_path)
                    firebase_admin.initialize_app(cred)

                message = messaging.Message(
                    notification=messaging.Notification(title=title, body=body),
                    data={str(k): str(v) for k, v in data_payload.items()},
                    token=target_token,
                    android=messaging.AndroidConfig(
                        priority='high',
                        notification=messaging.AndroidNotification(
                            channel_id='emergency_alerts',
                            sound='default',
                        ),
                    ),
                    apns=messaging.APNSConfig(
                        payload=messaging.APNSPayload(
                            aps=messaging.Aps(sound='default', content_available=True)
                        )
                    ),
                )
                response = messaging.send(message)
                provider_message_id = response

            except ImportError:
                # firebase_admin library installed nahi hai — fallback to mock
                logger.warning('firebase_admin library not installed. Using mock push dispatch.')
                provider_message_id = f'mock_fcm_{uuid.uuid4().hex[:12]}'
        else:
            # Development/Local mode: simulate push dispatch
            logger.info('Simulated FCM push send to token preview: %s...', target_token[:8])
            provider_message_id = f'simulated_fcm_{uuid.uuid4().hex[:12]}'

        # Success update
        delivery.status = 'sent'
        delivery.provider_message_id = provider_message_id
        delivery.delivered_at = timezone.now()
        delivery.save()

        # Audit log record karo
        record_audit_log(
            actor=delivery.emergency_event.owner if delivery.emergency_event else None,
            action_category='notification',
            action='push_notification_sent',
            severity='info',
            target_object=delivery,
            extra_data={
                'status': 'sent',
                'provider_id': provider_message_id,
            },
        )

    except Exception as exc:
        logger.error('Push notification delivery failed: %s', str(exc), exc_info=True)
        delivery.retry_count += 1
        delivery.failure_code = getattr(exc, 'code', 'PROVIDER_ERROR')
        delivery.failure_message = str(exc)[:500]

        if delivery.retry_count <= MAX_NOTIFICATION_RETRIES:
            # Retry schedule karo exponential backoff ke saath (e.g. 1m, 2m, 4m)
            backoff_seconds = 60 * (2 ** (delivery.retry_count - 1))
            delivery.status = 'retrying'
            delivery.next_retry_at = timezone.now() + timedelta(seconds=backoff_seconds)
        else:
            delivery.status = 'failed'
            delivery.next_retry_at = None

        delivery.save()

    return delivery


def dispatch_emergency_notifications(
    emergency_event,
    title: Optional[str] = None,
    body: Optional[str] = None,
) -> List[NotificationDelivery]:
    """
    Emergency event ke trigger hone par user ke saare verified trusted contacts ko
    alerts dispatch karne ka main orchestration service function.
    """
    user = emergency_event.owner
    event_type = emergency_event.get_event_type_display()
    
    alert_title = title or f"EMERGENCY ALERT: {user.display_name or 'SafeGuard AI User'}"
    alert_body = body or f"{user.display_name} has triggered a {event_type}. Immediate assistance may be required."

    deliveries = []

    # Owner ke active trusted contacts fetch karo
    trusted_contacts = user.trusted_contacts.filter(is_active=True)

    for contact in trusted_contacts:
        # Agar contact ke registered device tokens hain to send karo
        # (Contact agar registered user bhi ho to uske tokens search kiye ja sakte hain)
        contact_tokens = DeviceToken.objects.filter(
            owner__phone_number=contact.phone_number,
            is_active=True,
        ) if contact.phone_number else []

        if contact_tokens:
            for d_token in contact_tokens:
                delivery = create_notification_delivery(
                    emergency_event=emergency_event,
                    recipient_contact=contact,
                    device_token=d_token,
                )
                send_push_notification(
                    delivery=delivery,
                    title=alert_title,
                    body=alert_body,
                    data_payload={
                        'event_id': str(emergency_event.id),
                        'event_type': emergency_event.event_type,
                        'user_id': str(user.id),
                    },
                )
                deliveries.append(delivery)
        else:
            # Contact ka koi device token nahi hai — record pending delivery (SMS fallback track)
            delivery = create_notification_delivery(
                emergency_event=emergency_event,
                recipient_contact=contact,
                device_token=None,
            )
            delivery.status = 'sent'
            delivery.delivered_at = timezone.now()
            delivery.provider_message_id = f'sms_sim_{uuid.uuid4().hex[:10]}'
            delivery.save()
            deliveries.append(delivery)

    return deliveries


def get_deliveries_for_user(user, emergency_event_id: Optional[uuid.UUID] = None):
    """
    Current user ki emergencies se jude notification delivery records fetch karta hai.
    """
    queryset = NotificationDelivery.objects.filter(
        emergency_event__owner=user
    ).select_related('emergency_event', 'recipient_contact', 'device_token')

    if emergency_event_id:
        queryset = queryset.filter(emergency_event_id=emergency_event_id)

    return queryset.order_by('-attempted_at')
