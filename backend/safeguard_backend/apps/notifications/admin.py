"""
apps/notifications/admin.py
SafeGuard AI — Notification Admin Configuration
FCM device tokens aur delivery records Django Admin interface.
"""

from django.contrib import admin
from .models import DeviceToken, NotificationDelivery


@admin.register(DeviceToken)
class DeviceTokenAdmin(admin.ModelAdmin):
    """
    Device Token admin panel view.
    IMPORTANT: Token ko logs ya clear view mein expose nahi karte — security measure.
    """
    list_display = [
        'owner',
        'platform',
        'device_name',
        'token_preview',
        'is_active',
        'last_seen_at',
        'created_at',
    ]
    list_filter = ['platform', 'is_active', 'created_at']
    search_fields = ['owner__email', 'owner__display_name', 'device_name']
    readonly_fields = ['id', 'last_seen_at', 'created_at']
    ordering = ['-last_seen_at']

    @admin.display(description='Token Preview')
    def token_preview(self, obj):
        # Truncate token for safety in admin view
        if obj.token:
            return f"{obj.token[:8]}...{obj.token[-6:]}" if len(obj.token) > 14 else "***"
        return "-"


@admin.register(NotificationDelivery)
class NotificationDeliveryAdmin(admin.ModelAdmin):
    """
    Emergency notification deliveries admin interface.
    Delivery status, provider IDs, aur retry metrics track karta hai.
    """
    list_display = [
        'id',
        'emergency_event',
        'recipient_contact',
        'status',
        'retry_count',
        'provider_message_id',
        'attempted_at',
        'delivered_at',
    ]
    list_filter = ['status', 'attempted_at', 'retry_count']
    search_fields = [
        'emergency_event__id',
        'provider_message_id',
        'recipient_contact__contact_name',
        'recipient_contact__phone_number',
    ]
    readonly_fields = ['id', 'attempted_at', 'delivered_at']
    ordering = ['-attempted_at']
