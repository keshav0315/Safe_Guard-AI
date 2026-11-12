"""
apps/ai_detection/admin.py
SafeGuard AI — AI Detection Admin Configuration
AI Model Registry aur Advisory Inference Records admin interface.
"""

from django.contrib import admin
from .models import AIModelRegistry, AIInferenceRecord


@admin.register(AIModelRegistry)
class AIModelRegistryAdmin(admin.ModelAdmin):
    """
    AI Model Registry admin view.
    Model versioning, signal types, aur model safety limitations track karta hai.
    """
    list_display = [
        'model_name',
        'model_version',
        'signal_type',
        'status',
        'requires_consent',
        'created_at',
    ]
    list_filter = ['signal_type', 'status', 'requires_consent', 'created_at']
    search_fields = ['model_name', 'description', 'limitations']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-created_at']


@admin.register(AIInferenceRecord)
class AIInferenceRecordAdmin(admin.ModelAdmin):
    """
    Historical AI Inference logs admin view.
    CRITICAL: AI results sirf advisory hain, automatic SOS trigger nahi hona chahiye.
    Data compliance aur forensic integrity ke liye records read-only hain.
    """
    list_display = [
        'id',
        'owner',
        'signal_type',
        'result_label',
        'confidence_score',
        'is_advisory_only',
        'consent_recorded',
        'created_at',
    ]
    list_filter = [
        'signal_type',
        'is_advisory_only',
        'consent_recorded',
        'created_at',
    ]
    search_fields = [
        'owner__email',
        'owner__display_name',
        'result_label',
    ]
    ordering = ['-created_at']

    readonly_fields = [
        'id',
        'owner',
        'model_registry',
        'signal_type',
        'result_label',
        'confidence_score',
        'is_advisory_only',
        'inference_metadata',
        'retention_expires_at',
        'consent_recorded',
        'created_at',
    ]

    def has_add_permission(self, request):
        # Admin se manual fake inferences inject nahi hone chahiye
        return False

    def has_change_permission(self, request, obj=None):
        # Inference records immutable hain
        return False
