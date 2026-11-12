"""
apps/emergencies/models.py
SafeGuard AI — Emergency events ka core model yahan hai.
SOS, Panic, Test events track kiye jaate hain.
"""
import uuid
from django.conf import settings
from django.db import models


class EmergencyEvent(models.Model):
    """
    Har baar jab user SOS/Panic trigger kare tab ek EmergencyEvent create hota hai.
    Idempotency key se duplicate events prevent hote hain.
    """

    EVENT_TYPE_CHOICES = [
        ('sos', 'SOS Alert'),
        ('panic', 'Panic Button'),
        ('test', 'Test Alert'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('cancelled', 'Cancelled'),
        ('resolved', 'Resolved'),
        ('acknowledged', 'Acknowledged'),
    ]

    # UUID primary key — globally unique emergency event identifier
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name='Event ID',
    )

    # Owner wo user hai jisne emergency trigger ki
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='emergency_events',
        db_index=True,
        verbose_name='Owner',
    )

    event_type = models.CharField(
        max_length=20,
        choices=EVENT_TYPE_CHOICES,
        default='sos',
        db_index=True,
        verbose_name='Event Type',
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        db_index=True,
        verbose_name='Status',
    )

    # Idempotency key — same event baar baar create hone se rokta hai
    idempotency_key = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        verbose_name='Idempotency Key',
    )

    # Optional user notes — kya hua tha describe karna ho to
    notes = models.TextField(blank=True, verbose_name='Notes')

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Created At',
    )

    # Jab kisi contact ne acknowledge kiya — tab yeh timestamp set hoga
    acknowledged_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Acknowledged At',
    )

    # User ne cancel kiya — tab cancel timestamp
    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Cancelled At',
    )

    # Emergency resolve hui — tab yeh timestamp
    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Resolved At',
    )

    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Emergency Event'
        verbose_name_plural = 'Emergency Events'
        indexes = [
            models.Index(fields=['owner'], name='emergency_owner_idx'),
            models.Index(fields=['status'], name='emergency_status_idx'),
            models.Index(fields=['created_at'], name='emergency_created_at_idx'),
            models.Index(fields=['idempotency_key'], name='emergency_idempotency_idx'),
            models.Index(fields=['owner', 'status'], name='emergency_owner_status_idx'),
        ]

    def __str__(self):
        return f'[{self.get_event_type_display()}] {self.owner} — {self.status} @ {self.created_at}'
