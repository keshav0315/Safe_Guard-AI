"""
apps/contacts/models.py
SafeGuard AI — Trusted contacts ka model yahan define ho raha hai.
"""
import uuid
from django.conf import settings
from django.db import models


class TrustedContact(models.Model):
    """
    User ke trusted contacts — jinhe emergency mein alert bheja jayega.
    """

    VERIFICATION_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('failed', 'Failed'),
    ]

    CONSENT_STATUS_CHOICES = [
        ('not_requested', 'Not Requested'),
        ('requested', 'Requested'),
        ('given', 'Given'),
        ('withdrawn', 'Withdrawn'),
    ]

    # UUID primary key — har contact ka unique identifier
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name='Contact ID',
    )

    # Owner wo user hai jisne yeh contact add kiya — CASCADE delete hoga
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='trusted_contacts',
        db_index=True,
        verbose_name='Owner',
    )

    contact_name = models.CharField(
        max_length=150,
        verbose_name='Contact Name',
    )

    phone_number = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Phone Number',
    )

    email = models.EmailField(
        blank=True,
        verbose_name='Email',
    )

    # Relationship label — e.g. 'Mother', 'Friend', 'Colleague'
    relationship_label = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Relationship Label',
    )

    # Verification status — kya contact ka number verify hua hai
    verification_status = models.CharField(
        max_length=20,
        choices=VERIFICATION_STATUS_CHOICES,
        default='pending',
        verbose_name='Verification Status',
    )

    # Consent status — kya contact ne alerts receive karne ki permission di hai
    consent_status = models.CharField(
        max_length=20,
        choices=CONSENT_STATUS_CHOICES,
        default='not_requested',
        verbose_name='Consent Status',
    )

    # Soft delete ke liye — is_active False karo, actually delete mat karo
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name='Is Active',
    )

    notes = models.TextField(blank=True, verbose_name='Notes')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Trusted Contact'
        verbose_name_plural = 'Trusted Contacts'
        # Ek user ke paas ek hi phone number se ek contact ho sakta hai
        constraints = [
            models.UniqueConstraint(
                fields=['owner', 'phone_number'],
                condition=models.Q(phone_number__gt=''),
                name='unique_owner_phone_number',
            )
        ]
        indexes = [
            models.Index(fields=['owner'], name='contact_owner_idx'),
            models.Index(fields=['is_active'], name='contact_active_idx'),
            models.Index(fields=['owner', 'is_active'], name='contact_owner_active_idx'),
        ]

    def __str__(self):
        return f'{self.contact_name} ({self.relationship_label or "Contact"}) — {self.owner}'
