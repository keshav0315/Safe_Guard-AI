# Firebase Cloud Messaging integration
# Push notifications yahan se jaate hain

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def _get_firebase_app():
    """
    Firebase app initialize karna.
    Credentials environment se load hoti hain - hardcode nahi karna.
    """
    import firebase_admin
    from firebase_admin import credentials
    from django.conf import settings
    import os

    if not firebase_admin._apps:
        cred_path = getattr(settings, 'FIREBASE_CREDENTIALS_PATH', '')
        if cred_path and os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        else:
            # Development mein default app use karo
            logger.warning('Firebase credentials not found. FCM notifications will be simulated.')
            return None
    return firebase_admin.get_app()

def send_fcm_notification(
    device_token: str,
    title: str,
    body: str,
    data: Dict[str, Any] = None,
) -> Dict[str, Any]:
    """
    FCM push notification bhejne ka main function.
    Sensitive location data payload mein mat daalo.
    Return: {'success': bool, 'message_id': str, 'error_code': str}
    """
    try:
        from firebase_admin import messaging

        app = _get_firebase_app()
        if app is None:
            # Firebase available nahi hai - simulate success for development
            logger.info(f'[DEV] FCM notification simulated for token ending in ...{device_token[-8:]}')
            return {'success': True, 'message_id': 'simulated_id', 'error_code': ''}

        # FCM message banao
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            data={k: str(v) for k, v in (data or {}).items()},  # All values must be strings
            token=device_token,
            android=messaging.AndroidConfig(
                priority='high',  # Emergency alerts ke liye high priority
                notification=messaging.AndroidNotification(
                    sound='emergency_alert',
                    priority='max',
                )
            ),
        )

        message_id = messaging.send(message)
        logger.info(f'FCM notification sent successfully.')
        return {'success': True, 'message_id': message_id, 'error_code': ''}

    except Exception as e:
        error_str = str(e)
        logger.error(f'FCM notification failed: {error_str}')
        # Token invalid hai to specific error return karo
        if 'registration-token-not-registered' in error_str:
            return {'success': False, 'message_id': '', 'error_code': 'registration-token-not-registered'}
        return {'success': False, 'message_id': '', 'error_code': 'fcm_error'}
