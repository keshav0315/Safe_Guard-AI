"""
apps/audit/services.py
SafeGuard AI — Tamper-evident Audit Logging Services
Security events, emergency triggers, aur critical updates yahan log hote hain.
"""

import copy
import logging
from typing import Optional, Dict, Any
from django.db.models import QuerySet
from django.utils import timezone
from .models import AuditLog

logger = logging.getLogger('apps.audit')

# Sensitive keys list jo audit log ke extra_data mein KABHI nahi aane chahiye
SENSITIVE_KEYS = {
    'password',
    'password_hash',
    'token',
    'access_token',
    'refresh_token',
    'secret',
    'authorization',
    'jwt',
    'otp',
    'pin',
    'credit_card',
    'cvv',
    'ssn',
    'raw_coordinates',
    'latitude',
    'longitude',
}


def sanitize_audit_data(data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """
    # Security audit log mein kabhi password ya sensitive data save mat karo
    Extra data ko recursively sanitize karta hai taaki PII ya credentials leak na hon.
    """
    if not data or not isinstance(data, dict):
        return {}

    cleaned = {}
    for key, value in data.items():
        lower_key = str(key).lower()

        # Agar key sensitive list mein hai to redact karo
        if any(sensitive in lower_key for sensitive in SENSITIVE_KEYS):
            cleaned[key] = '[REDACTED]'
        elif isinstance(value, dict):
            cleaned[key] = sanitize_audit_data(value)
        elif isinstance(value, list):
            cleaned[key] = [
                sanitize_audit_data(item) if isinstance(item, dict) else item
                for item in value
            ]
        elif isinstance(value, (str, int, float, bool)) or value is None:
            cleaned[key] = value
        else:
            cleaned[key] = str(value)

    return cleaned


def extract_client_ip(request) -> Optional[str]:
    """
    Request se accurate client IP nikalne ka helper.
    Reverse proxy (e.g., Nginx, AWS ALB) ke piche X-Forwarded-For check karta hai.
    """
    if not request:
        return None

    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        # X-Forwarded-For mein multiple IPs ho sakti hain: client, proxy1, proxy2...
        ip = x_forwarded_for.split(',')[0].strip()
        return ip
    return request.META.get('REMOTE_ADDR')


def extract_user_agent(request) -> str:
    """Request se client browser / mobile OS user agent fetch karta hai."""
    if not request:
        return ''
    return request.META.get('HTTP_USER_AGENT', '')[:500]


def record_audit_log(
    actor=None,
    action_category: str = 'security',
    action: str = '',
    severity: str = 'info',
    target_object=None,
    target_object_type: str = '',
    target_object_id: str = '',
    request=None,
    extra_data: Optional[Dict[str, Any]] = None,
) -> Optional[AuditLog]:
    """
    System ke har critical event ko record karne ka main service function.
    
    CRITICAL RULE:
    - Agar audit log write fail ho jaye, to main application flow crash nahi hona chahiye.
    - Exceptions ko safely catch aur log kiya jata hai.
    """
    try:
        # Agar actor explicit nahi diya hai aur request authenticated hai to actor request.user hoga
        if actor is None and request and hasattr(request, 'user') and request.user.is_authenticated:
            actor = request.user

        # Target object pass kiya gaya ho to uska type aur primary key auto-extract karo
        if target_object is not None:
            if not target_object_type:
                target_object_type = target_object.__class__.__name__
            if not target_object_id and hasattr(target_object, 'pk'):
                target_object_id = str(target_object.pk)

        ip_address = extract_client_ip(request) if request else None
        user_agent = extract_user_agent(request) if request else ''

        # Data sanitization taaki sensitive tokens ya passwords database mein na jayein
        safe_extra_data = sanitize_audit_data(extra_data)

        # Audit record create karo
        audit_entry = AuditLog.objects.create(
            actor=actor,
            action_category=action_category,
            action=action,
            severity=severity,
            target_object_type=target_object_type,
            target_object_id=target_object_id,
            ip_address=ip_address,
            user_agent=user_agent,
            extra_data=safe_extra_data,
        )
        return audit_entry

    except Exception as exc:
        # Audit logging failure par silent warning taaki primary emergency request block na ho
        logger.warning(
            'Failed to record audit log: %s | action=%s, category=%s',
            str(exc),
            action,
            action_category,
            exc_info=True,
        )
        return None


def get_audit_logs_for_user(
    user,
    category: Optional[str] = None,
    severity: Optional[str] = None,
    start_date=None,
    end_date=None,
) -> QuerySet[AuditLog]:
    """
    User ke liye audit history filter karta hai.
    - Staff/Admin user saare logs dekh sakte hain.
    - Regular user sirf apne actor wale records hi dekh sakta hai (data privacy compliance).
    """
    if getattr(user, 'is_staff', False) or getattr(user, 'role', '') == 'admin':
        queryset = AuditLog.objects.all()
    else:
        # Sirf current user ke audit logs return karo
        queryset = AuditLog.objects.filter(actor=user)

    if category:
        queryset = queryset.filter(action_category=category)
    if severity:
        queryset = queryset.filter(severity=severity)
    if start_date:
        queryset = queryset.filter(created_at__gte=start_date)
    if end_date:
        queryset = queryset.filter(created_at__lte=end_date)

    return queryset.select_related('actor').order_by('-created_at')
