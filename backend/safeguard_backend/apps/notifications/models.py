"""
apps/notifications/models.py
SafeGuard AI — Device tokens aur notification delivery tracking yahan hai.
FCM push notifications ke liye use hota hai.
"""
import uuid
from django.conf import settings
from django.db import models


class DeviceToken(models.Model):
    """
    User ke device ka FCM push notification token.
    IMPORTANT: Token ko logs mein kabhi mat print karo — sensitive data hai.
    """

    PLATFORM_CHOICES = [
        ('android', 'Android'),
        ('ios', 'iOS'),
        ('web', 'Web'),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name='Token ID',
    )

    # Owner — kis user ka device token hai
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='device_tokens',
        db_index=True,
        verbose_name='Owner',
    )

    # FCM token — KABHI LOGS MEIN MAT DAALO — sensitive hai
    token = models.CharField(
        max_length=512,
        verbose_name='FCM Token',
    )

    platform = models.CharField(
        max_length=10,
        choices=PLATFORM_CHOICES,
        default='android',
        verbose_name='Platform',
    )

    device_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Device Name',
    )

    # Jab bhi device app use kare, yeh auto-update hoga
    last_seen_at = models.DateTimeField(auto_now=True, verbose_name='Last Seen At')

    is_active = models.BooleanField(default=True, verbose_name='Is Active')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')

    class Meta:
        ordering = ['-last_seen_at']
        verbose_name = 'Device Token'
        verbose_name_plural = 'Device Tokens'
        # Ek user ke paas ek token ek hi baar hoga
        unique_together = [['owner', 'token']]
        indexes = [
            models.Index(fields=['owner'], name='device_token_owner_idx'),
            models.Index(fields=['is_active'], name='device_token_active_idx'),
        ]

    def __str__(self):
        # Token ko truncate karo — poora token mat dikhao
        token_preview = self.token[:8] + '...' if self.token else '(empty)'
        return f'DeviceToken({self.platform}) — {self.owner} [{token_preview}]'


class NotificationDelivery(models.Model):
    """
    Har notification delivery ka record — retry logic ke liye bhi use hota hai.
    Emergency event se linked hai.
    """

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
        ('retrying', 'Retrying'),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name='Delivery ID',
    )

    # Kaun si emergency ke liye notification bheja gaya
    emergency_event = models.ForeignKey(
        'emergencies.EmergencyEvent',
        on_delete=models.CASCADE,
        related_name='notification_deliveries',
        verbose_name='Emergency Event',
    )

    # Recipient contact — null agar contact delete ho jaye
    recipient_contact = models.ForeignKey(
        'contacts.TrustedContact',
        null=True,
        on_delete=models.SET_NULL,
        related_name='received_notifications',
        verbose_name='Recipient Contact',
    )

    # Kaun se device token pe bheja gaya — null agar token delete ho jaye
    device_token = models.ForeignKey(
        DeviceToken,
        null=True,
        on_delete=models.SET_NULL,
        related_name='notification_deliveries',
        verbose_name='Device Token',
    )

    # FCM ya push provider ka message ID — tracking ke liye
    provider_message_id = models.CharField(
        max_length=512,
        blank=True,
        verbose_name='Provider Message ID',
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True,
        verbose_name='Status',
    )

    attempted_at = models.DateTimeField(auto_now_add=True, verbose_name='Attempted At')

    # Jab delivery confirm hui
    delivered_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Delivered At',
    )

    # Failure code — provider ka error code
    failure_code = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Failure Code',
    )

    failure_message = models.TextField(blank=True, verbose_name='Failure Message')

    # Kitni baar retry hua
    retry_count = models.PositiveSmallIntegerField(
        default=0,
        verbose_name='Retry Count',
    )

    # Agla retry kab hoga — null means no retry scheduled
    next_retry_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Next Retry At',
    )

    class Meta:
        ordering = ['-attempted_at']
        verbose_name = 'Notification Delivery'
        verbose_name_plural = 'Notification Deliveries'
        indexes = [
            models.Index(fields=['emergency_event'], name='notif_delivery_event_idx'),
            models.Index(fields=['status'], name='notif_delivery_status_idx'),
            models.Index(fields=['next_retry_at'], name='notif_delivery_retry_idx'),
        ]

    def __str__(self):
        return f'Delivery[{self.status}] to {self.recipient_contact} for {self.emergency_event}'
