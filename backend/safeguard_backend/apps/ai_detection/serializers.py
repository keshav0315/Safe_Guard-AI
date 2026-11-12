"""
apps/ai_detection/serializers.py
SafeGuard AI — AI Model Registry & Inference Serializers
Advisory signal processing, threat detection schemas, aur consent tracking.
"""

from rest_framework import serializers
from .models import AIModelRegistry, AIInferenceRecord

ADVISORY_DISCLAIMER_TEXT = (
    "IMPORTANT: AI detection results are purely advisory and informational. "
    "Under no circumstances does this inference trigger an emergency SOS alert "
    "automatically without explicit human confirmation."
)


class AIModelRegistrySerializer(serializers.ModelSerializer):
    """
    Registered AI models ka serializer — versions, input schemas aur known limitations.
    """
    class Meta:
        model = AIModelRegistry
        fields = [
            'id',
            'model_name',
            'model_version',
            'signal_type',
            'description',
            'input_schema',
            'output_schema',
            'limitations',
            'requires_consent',
            'status',
            'endpoint_url',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AIInferenceRequestSerializer(serializers.Serializer):
    """
    Sensor data submission for AI inference.
    # AI results sirf advisory hain, automatic SOS trigger nahi hona chahiye
    User consent mandatory hai GDPR aur safety compliance ke liye.
    """
    model_id = serializers.UUIDField(
        required=False,
        help_text='Specific AI Model Registry ID (optional). Agar provide nahi kiya to default active model use hoga.',
    )
    signal_type = serializers.ChoiceField(
        choices=AIModelRegistry.SIGNAL_TYPE_CHOICES,
        default='movement',
        help_text='Signal type (movement, audio, facial, physiological, sensor_fusion).',
    )
    sensor_data = serializers.DictField(
        required=True,
        help_text='Raw sensor telemetry (e.g. accelerometer readings, decibel levels, gyroscope).',
    )
    user_consent = serializers.BooleanField(
        required=True,
        help_text='User consent confirmation. Mandatory for privacy compliance.',
    )

    def validate_user_consent(self, value):
        if not value:
            raise serializers.ValidationError(
                'AI inference ke liye user explicit consent zaroori hai. Please provide consent.'
            )
        return value

    def validate_sensor_data(self, value):
        if not value or not isinstance(value, dict):
            raise serializers.ValidationError('Valid sensor_data dictionary provide karna zaroori hai.')
        return value


class AIInferenceResponseSerializer(serializers.Serializer):
    """
    Advisory inference evaluation response with explicit disclaimer.
    """
    inference_id = serializers.UUIDField()
    signal_type = serializers.CharField()
    result_label = serializers.CharField()
    confidence_score = serializers.FloatField()
    is_advisory_only = serializers.BooleanField(default=True)
    suggested_action = serializers.CharField()
    advisory_disclaimer = serializers.CharField(default=ADVISORY_DISCLAIMER_TEXT)
    created_at = serializers.DateTimeField()


class AIInferenceRecordSerializer(serializers.ModelSerializer):
    """
    Historical inference record representation.
    """
    owner_email = serializers.CharField(source='owner.email', read_only=True)
    model_name = serializers.CharField(
        source='model_registry.model_name',
        read_only=True,
        default=None,
    )
    model_version = serializers.CharField(
        source='model_registry.model_version',
        read_only=True,
        default=None,
    )

    class Meta:
        model = AIInferenceRecord
        fields = [
            'id',
            'owner',
            'owner_email',
            'model_registry',
            'model_name',
            'model_version',
            'signal_type',
            'result_label',
            'confidence_score',
            'is_advisory_only',
            'inference_metadata',
            'created_at',
            'retention_expires_at',
            'consent_recorded',
        ]
        read_only_fields = fields
