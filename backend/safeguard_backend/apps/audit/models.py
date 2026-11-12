"""
apps/audit/models.py
SafeGuard AI — Audit log model — kaun ne kya kiya, kab kiya.
CRITICAL: Kabhi passwords, tokens, raw location, ya sensitive PII log mat karo.
"""
import uuid
from django.conf import settings
from django.db import models


class AuditLog(models.Model):
    """
    System ke har important action ka tamper-evident log.
    Compliance, security monitoring aur debugging ke liye use hota hai.

    KABHI LOG MAT KARO: passwords, tokens, raw location coordinates, sensitive PII.
    """

    ACTION_CATEGORY_CHOICES = [
        ('auth', 'Authentication'),
        ('profile', 'Profile'),
        ('contact', 'Contact Management'),
        ('emergency', 'Emergency Event'),
        ('location', 'Location'),
        ('notification', 'Notification'),
        ('ai', 'AI Inference'),
        ('admin', 'Admin Action'),
        ('security', 'Security Event'),
    ]

    SEVERITY_CHOICES = [
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('critical', 'Critical'),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name='Log ID',
    )

    # Actor — kaun sa user tha — null agar anonymous request thi
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='audit_logs',
        db_index=True,
        verbose_name='Actor',
    )

    action_category = models.CharField(
        max_length=20,
        choices=ACTION_CATEGORY_CHOICES,
        db_index=True,
        verbose_name='Action Category',
    )

    # Specific action — e.g. 'sos_created', 'login_success', 'contact_added'
    action = models.CharField(
        max_length=100,
        verbose_name='Action',
    )

    severity = models.CharField(
        max_length=10,
        choices=SEVERITY_CHOICES,
        default='info',
        db_index=True,
        verbose_name='Severity',
    )

    # Target object type — e.g. 'EmergencyEvent', 'TrustedContact'
    target_object_type = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Target Object Type',
    )

    # Target object UUID — kis object pe action hua
    target_object_id = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Target Object ID',
    )

    # IP address — security monitoring ke liye
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='IP Address',
    )

    user_agent = models.TextField(blank=True, verbose_name='User Agent')

    # Non-sensitive context — KABHI passwords, tokens, raw location mat daalo
    extra_data = models.JSONField(
        default=dict,
        verbose_name='Extra Data',
        help_text='NEVER include: passwords, tokens, raw coordinates, or sensitive PII.',
    )

    # Audit logs immutable hone chahiye — auto_now_add, no auto_now
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Created At',
    )

    class Meta:
        # Newest logs pehle dikhenge
        ordering = ['-created_at']
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
        indexes = [
            models.Index(fields=['actor', 'created_at'], name='audit_actor_created_idx'),
            models.Index(fields=['action_category'], name='audit_category_idx'),
            models.Index(fields=['severity'], name='audit_severity_idx'),
            models.Index(fields=['action_category', 'created_at'], name='audit_category_created_idx'),
        ]

    def __str__(self):
        actor_str = str(self.actor) if self.actor else 'Anonymous'
        return f'[{self.severity.upper()}] {self.action_category}:{self.action} by {actor_str} @ {self.created_at}'
