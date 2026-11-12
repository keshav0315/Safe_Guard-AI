# Background tasks - notification delivery yaha hota hai

from celery import shared_task
import logging

logger = logging.getLogger(__name__)

@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,  # 60 seconds baad retry
    name='send_emergency_notifications'
)
def send_emergency_notifications_task(self, event_id):
    """
    Emergency notifications background mein bhejne ka task.
    Celery se async run hota hai - API response wait nahi karta.
    3 baar retry karega agar fail ho.
    """
    try:
        from apps.emergencies.models import EmergencyEvent
        from apps.contacts.models import TrustedContact
        from apps.notifications.models import DeviceToken, NotificationDelivery
        from infrastructure.firebase.fcm import send_fcm_notification

        # Event fetch karo
        try:
            event = EmergencyEvent.objects.select_related('owner').get(id=event_id)
        except EmergencyEvent.DoesNotExist:
            logger.error(f'Emergency event {event_id} not found for notification.')
            return

        # Sirf active events ke notifications bhejo
        if event.status not in ['active', 'acknowledged']:
            logger.info(f'Event {event_id} is not active, skipping notifications.')
            return

        # Owner ke trusted contacts fetch karo
        contacts = TrustedContact.objects.filter(
            owner=event.owner,
            is_active=True,
            consent_status='given'
        )

        for contact in contacts:
            # Har contact ke liye notification bhejo
            _send_notification_to_contact(event, contact)

    except Exception as exc:
        logger.error(f'Notification task failed for event {event_id}: {exc}')
        # Retry karo
        raise self.retry(exc=exc)

def _send_notification_to_contact(event, contact):
    """Single contact ko notification bhejne ki helper function"""
    from apps.notifications.models import DeviceToken, NotificationDelivery
    from infrastructure.firebase.fcm import send_fcm_notification
    from apps.notifications.services import create_delivery_record, update_delivery_status

    # Contact ke user ke device tokens dhundho
    # Note: Contact ke paas app hona zaroori nahi - FCM sirf app users ko milta hai
    # Future mein SMS/email fallback add kar sakte hain
    logger.info(f'Sending notification for event {event.id} to contact {contact.contact_name}')

    # Delivery record create karo
    delivery = create_delivery_record(event, recipient_contact=contact)

    # FCM notification bhejo (agar contact ka app account hai)
    try:
        # Contact ke email/phone se user dhundho
        from django.contrib.auth import get_user_model
        User = get_user_model()
        contact_user = User.objects.filter(
            email=contact.email, is_active=True
        ).first() if contact.email else None

        if contact_user:
            tokens = DeviceToken.objects.filter(owner=contact_user, is_active=True)
            for token_obj in tokens:
                result = send_fcm_notification(
                    device_token=token_obj.token,
                    title='🆘 Emergency Alert',
                    body=f'{event.owner.display_name} needs help! They have triggered an SOS alert.',
                    data={
                        'event_id': str(event.id),
                        'event_type': event.event_type,
                        'type': 'emergency_sos',
                    }
                )
                if result.get('success'):
                    update_delivery_status(delivery.id, 'sent',
                                          provider_message_id=result.get('message_id', ''))
                else:
                    update_delivery_status(delivery.id, 'failed',
                                          failure_code=result.get('error_code', 'unknown'))
                    # Token invalid hai to deactivate karo
                    if result.get('error_code') in ['registration-token-not-registered', 'invalid-registration-token']:
                        from apps.notifications.services import deactivate_device_token
                        deactivate_device_token(token_obj.token)
        else:
            # Contact ka account nahi hai - future mein SMS add karo
            update_delivery_status(delivery.id, 'failed',
                                  failure_code='no_app_account',
                                  failure_message='Contact does not have app account for push notification')
    except Exception as e:
        update_delivery_status(delivery.id, 'failed',
                              failure_message=str(e)[:500])
        logger.error(f'Failed to send notification: {e}')
