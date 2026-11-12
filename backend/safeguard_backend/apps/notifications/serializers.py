"""
apps/notifications/serializers.py
SafeGuard AI — Push Notification & Device Token Serializers
FCM device registration aur delivery tracking serializers.
"""

from rest_framework import serializers
from .models import DeviceToken, NotificationDelivery


class DeviceTokenRegisterSerializer(serializers.Serializer):
    """
    # FCM device token register karne ka endpoint serializer
    Mobile app se push token receive karke validate karta hai.
    """
    token = serializers.CharField(
        max_length=512,
        required=True,
        trim_whitespace=True,
        help_text='Firebase Cloud Messaging (FCM) registration token.',
    )
    platform = serializers.ChoiceField(
        choices=DeviceToken.PLATFORM_CHOICES,
        default='android',
        help_text='Target device operating system (android, ios, web).',
    )
    device_name = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
        default='',
        help_text='User readable device name (e.g. Samsung Galaxy S23, iPhone 15).',
    )

    def validate_token(self, value):
        # Token empty ya sirf whitespace nahi hona chahiye
        if not value or not value.strip():
            raise serializers.ValidationError('Valid FCM token zaroori hai.')
        return value.strip()


class DeviceTokenSerializer(serializers.ModelSerializer):
    """
    Device Token representation serializer.
    Security: Full token sensitive hota hai, isliye safe representation provide ki gayi hai.
    """
    token_preview = serializers.SerializerMethodField()

    class Meta:
        model = DeviceToken
        fields = [
            'id',
            'platform',
            'device_name',
            'token_preview',
            'is_active',
            'last_seen_at',
            'created_at',
        ]
        read_only_fields = fields

    def get_token_preview(self, obj) -> str:
        # Full token ko expose mat karo — sirf preview safe hai
        if obj.token:
            return f"{obj.token[:8]}...{obj.token[-6:]}" if len(obj.token) > 14 else "***"
        return ""


class NotificationDeliverySerializer(serializers.ModelSerializer):
    """
    Notification delivery log serializer.
    Emergency alerts ki delivery status, timestamp aur retries dikhane ke liye.
    """
    emergency_event_id = serializers.UUIDField(source='emergency_event.id', read_only=True)
    recipient_name = serializers.CharField(
        source='recipient_contact.contact_name',
        read_only=True,
        default=None,
    )
    recipient_phone = serializers.CharField(
        source='recipient_contact.phone_number',
        read_only=True,
        default=None,
    )
    platform = serializers.CharField(
        source='device_token.platform',
        read_only=True,
        default=None,
    )

    class Meta:
        model = NotificationDelivery
        fields = [
            'id',
            'emergency_event',
            'emergency_event_id',
            'recipient_contact',
            'recipient_name',
            'recipient_phone',
            'device_token',
            'platform',
            'provider_message_id',
            'status',
            'attempted_at',
            'delivered_at',
            'failure_code',
            'failure_message',
            'retry_count',
            'next_retry_at',
        ]
        read_only_fields = fields
