"""
apps/ai_detection/models.py
SafeGuard AI — AI models registry aur inference records yahan hain.
IMPORTANT: AI ka result kabhi akele SOS trigger nahi karega — advisory only.
"""
import uuid
from django.conf import settings
from django.db import models


class AIModelRegistry(models.Model):
    """
    Available AI models ka registry — kaunsa model available hai, kya karta hai.
    Model limitations document karna ZAROORI hai safety ke liye.
    """

    SIGNAL_TYPE_CHOICES = [
        ('movement', 'Movement'),
        ('audio', 'Audio'),
        ('facial', 'Facial Expression'),
        ('physiological', 'Physiological'),
        ('sensor_fusion', 'Sensor Fusion'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('deprecated', 'Deprecated'),
        ('unavailable', 'Unavailable'),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name='Registry ID',
    )

    model_name = models.CharField(
        max_length=100,
        verbose_name='Model Name',
    )

    model_version = models.CharField(
        max_length=50,
        verbose_name='Model Version',
    )

    signal_type = models.CharField(
        max_length=30,
        choices=SIGNAL_TYPE_CHOICES,
        verbose_name='Signal Type',
    )

    description = models.TextField(blank=True, verbose_name='Description')

    # Input format kya hoga — JSON schema
    input_schema = models.JSONField(
        default=dict,
        verbose_name='Input Schema',
    )

    # Output format kya hoga — JSON schema
    output_schema = models.JSONField(
        default=dict,
        verbose_name='Output Schema',
    )

    # ZAROORI: Model ki limitations document karna safety ke liye — false positives, etc.
    limitations = models.TextField(
        blank=True,
        verbose_name='Limitations',
        help_text='IMPORTANT: Document all known limitations, false positive rates, biases, edge cases.',
    )

    # Consent required hai — user ne permission di ho tabhi use hoga
    requires_consent = models.BooleanField(
        default=True,
        verbose_name='Requires Consent',
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        db_index=True,
        verbose_name='Status',
    )

    # Agar external service hai to endpoint URL — blank means local model
    endpoint_url = models.CharField(
        max_length=512,
        blank=True,
        verbose_name='Endpoint URL',
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'AI Model Registry'
        verbose_name_plural = 'AI Model Registries'
        # Same model ka same version ek hi baar register hoga
        unique_together = [['model_name', 'model_version']]

    def __str__(self):
        return f'{self.model_name} v{self.model_version} ({self.get_signal_type_display()})'


class AIInferenceRecord(models.Model):
    """
    Har AI inference ka record — kya detect hua, kab, kiske liye.
    CRITICAL RULE: is_advisory_only=True — AI akele SOS trigger NAHI karega.
    Data retention ka dhyan rakhna — expires_at field hai.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name='Inference ID',
    )

    # Kis user ke liye inference hui
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='inference_records',
        db_index=True,
        verbose_name='Owner',
    )

    # Kaun sa model use hua — SET_NULL agar model registry se hata diya jaye
    model_registry = models.ForeignKey(
        AIModelRegistry,
        on_delete=models.SET_NULL,
        null=True,
        related_name='inference_records',
        verbose_name='AI Model Registry',
    )

    signal_type = models.CharField(
        max_length=50,
        verbose_name='Signal Type',
    )

    result_label = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Result Label',
    )

    # Confidence 0.0 to 1.0 — higher means more confident
    confidence_score = models.FloatField(
        null=True,
        blank=True,
        verbose_name='Confidence Score',
    )

    # IMPORTANT: Yeh field True rahega — AI result sirf advisory hai, action nahi
    is_advisory_only = models.BooleanField(
        default=True,
        verbose_name='Is Advisory Only',
        help_text='CRITICAL: AI inference alone must NEVER trigger SOS. Always requires human confirmation.',
    )

    # Non-sensitive metadata only — raw sensor data, tokens, PII kabhi mat daalo
    inference_metadata = models.JSONField(
        default=dict,
        verbose_name='Inference Metadata',
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Created At',
    )

    # Data retention — is date ke baad record delete ho sakta hai
    retention_expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Retention Expires At',
    )

    # Consent record hua hai ya nahi — GDPR compliance ke liye
    consent_recorded = models.BooleanField(
        default=False,
        verbose_name='Consent Recorded',
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'AI Inference Record'
        verbose_name_plural = 'AI Inference Records'
        indexes = [
            models.Index(fields=['owner'], name='ai_inference_owner_idx'),
            models.Index(fields=['created_at'], name='ai_inference_created_idx'),
            models.Index(fields=['owner', 'created_at'], name='ai_inference_owner_created_idx'),
        ]

    def __str__(self):
        return f'Inference[{self.signal_type}] for {self.owner} — {self.result_label} ({self.confidence_score})'
