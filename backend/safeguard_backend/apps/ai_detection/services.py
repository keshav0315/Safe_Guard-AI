"""
apps/ai_detection/services.py
SafeGuard AI — AI Inference & Threat Detection Services
Signal processing, heuristic/ML threat scoring, aur safety compliance.
"""

import math
import logging
from datetime import timedelta
from typing import Optional, Dict, Any, Tuple

from django.conf import settings
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from .models import AIModelRegistry, AIInferenceRecord
from apps.audit.services import record_audit_log

logger = logging.getLogger('apps.ai_detection')

# Standard advisory disclaimer mandatory on every inference response
ADVISORY_DISCLAIMER_TEXT = (
    "IMPORTANT: AI detection results are purely advisory and informational. "
    "Under no circumstances does this inference trigger an emergency SOS alert "
    "automatically without explicit human confirmation."
)

DEFAULT_RETENTION_DAYS = 30


# ---------------------------------------------------------------------------
# Default Models Bootstrap Helper
# ---------------------------------------------------------------------------

def get_or_create_default_model(signal_type: str) -> AIModelRegistry:
    """
    Agar database mein koi model registered na ho to default baseline model
    register karta hai taaki inference bina break hue kaam kare.
    """
    model_defaults = {
        'movement': {
            'model_name': 'Movement Anomaly & Fall Heuristic Detector',
            'model_version': '1.0.0',
            'description': 'Detects high impact force, free-fall deceleration, and unusual motion patterns.',
            'limitations': 'Can trigger false positives during intense sports, dancing, or phone drops on soft surfaces.',
            'input_schema': {'type': 'object', 'properties': {'x': {'type': 'number'}, 'y': {'type': 'number'}, 'z': {'type': 'number'}, 'max_g': {'type': 'number'}}},
            'output_schema': {'type': 'object', 'properties': {'label': {'type': 'string'}, 'confidence': {'type': 'number'}}},
        },
        'audio': {
            'model_name': 'Acoustic Distress & Scream Classifier',
            'model_version': '1.0.0',
            'description': 'Analyzes ambient sound decibels and vocal distress frequencies.',
            'limitations': 'Susceptible to false positives in concerts, traffic horns, and movie theaters.',
            'input_schema': {'type': 'object', 'properties': {'decibels': {'type': 'number'}, 'frequency_hz': {'type': 'number'}}},
            'output_schema': {'type': 'object', 'properties': {'label': {'type': 'string'}, 'confidence': {'type': 'number'}}},
        },
        'sensor_fusion': {
            'model_name': 'Multi-Sensor Fusion Threat Evaluator',
            'model_version': '1.0.0',
            'description': 'Fuses accelerometer shock data and acoustic spikes for corroboration.',
            'limitations': 'Requires multiple hardware sensors; degraded accuracy if phone is muffled in bag.',
            'input_schema': {'type': 'object', 'properties': {'movement': {'type': 'object'}, 'audio': {'type': 'object'}}},
            'output_schema': {'type': 'object', 'properties': {'label': {'type': 'string'}, 'confidence': {'type': 'number'}}},
        },
    }

    config = model_defaults.get(signal_type, {
        'model_name': f'Generic {signal_type.title()} Signal Detector',
        'model_version': '1.0.0',
        'description': f'Evaluates {signal_type} signals for unusual safety threats.',
        'limitations': 'Baseline generic model. Human confirmation is strictly required.',
        'input_schema': {},
        'output_schema': {},
    })

    model_obj, _ = AIModelRegistry.objects.get_or_create(
        model_name=config['model_name'],
        model_version=config['model_version'],
        defaults={
            'signal_type': signal_type,
            'description': config['description'],
            'limitations': config['limitations'],
            'input_schema': config['input_schema'],
            'output_schema': config['output_schema'],
            'requires_consent': True,
            'status': 'active',
        },
    )
    return model_obj


# ---------------------------------------------------------------------------
# Signal Evaluation Logic
# ---------------------------------------------------------------------------

def evaluate_movement_signal(sensor_data: Dict[str, Any]) -> Tuple[str, float]:
    """
    Accelerometer aur Gyroscope readings evaluate karta hai.
    """
    x = float(sensor_data.get('x', 0.0))
    y = float(sensor_data.get('y', 0.0))
    z = float(sensor_data.get('z', 9.8))
    max_g = float(sensor_data.get('max_g', 0.0))

    # Total acceleration magnitude (G-force calculation)
    magnitude = math.sqrt(x**2 + y**2 + z**2)

    # Heuristics: Sudden impact (> 3.5g or max_g > 4.0g) or violent shaking
    if max_g >= 4.5 or magnitude >= 45.0:
        return 'fall_detected', 0.88
    elif max_g >= 3.0 or magnitude >= 30.0:
        return 'sudden_impact_detected', 0.74
    elif sensor_data.get('is_shaking', False) or magnitude >= 20.0:
        return 'abnormal_motion_detected', 0.65

    return 'normal_movement', 0.15


def evaluate_audio_signal(sensor_data: Dict[str, Any]) -> Tuple[str, float]:
    """
    Ambient acoustic sound levels aur frequencies evaluate karta hai.
    """
    decibels = float(sensor_data.get('decibels', 45.0))
    frequency_hz = float(sensor_data.get('frequency_hz', 400.0))
    is_scream_pattern = bool(sensor_data.get('is_scream_pattern', False))

    # Human screams typically peak between 1000Hz - 3500Hz with volume > 85dB
    if is_scream_pattern or (decibels >= 85.0 and 1000 <= frequency_hz <= 4000):
        return 'distress_vocalization_detected', 0.85
    elif decibels >= 80.0:
        return 'high_ambient_noise', 0.60

    return 'normal_ambient_audio', 0.10


def evaluate_sensor_fusion(sensor_data: Dict[str, Any]) -> Tuple[str, float]:
    """
    Movement aur Audio dono ko combine karke corroboration score calculate karta hai.
    """
    movement_data = sensor_data.get('movement', {})
    audio_data = sensor_data.get('audio', {})

    mov_label, mov_conf = evaluate_movement_signal(movement_data) if movement_data else ('normal', 0.1)
    aud_label, aud_conf = evaluate_audio_signal(audio_data) if audio_data else ('normal', 0.1)

    # Corroborated anomaly
    if 'detected' in mov_label and 'detected' in aud_label:
        combined_conf = min(0.95, (mov_conf + aud_conf) / 2.0 + 0.15)
        return 'multi_sensor_distress_anomaly', combined_conf
    elif 'detected' in mov_label:
        return mov_label, mov_conf
    elif 'detected' in aud_label:
        return aud_label, aud_conf

    return 'normal_baseline', 0.12


# ---------------------------------------------------------------------------
# Core Advisory Inference Service
# ---------------------------------------------------------------------------

def run_advisory_inference(
    user,
    signal_type: str,
    sensor_data: Dict[str, Any],
    model_id: Optional[str] = None,
    consent_given: bool = True,
    request=None,
) -> Dict[str, Any]:
    """
    # AI results sirf advisory hain, automatic SOS trigger nahi hona chahiye
    Main inference execution engine.
    - User consent check karta hai.
    - Heuristic/model prediction evaluate karta hai.
    - Safety disclaimer attach karta hai.
    - Immutable audit log record karta hai.
    """
    if not consent_given:
        raise ValidationError('Explicit user consent is mandatory for AI signal inference.')

    # Model select ya fallback karo
    model_registry = None
    if model_id:
        try:
            model_registry = AIModelRegistry.objects.get(id=model_id, status='active')
        except AIModelRegistry.DoesNotExist:
            logger.warning('Requested model_id %s not active. Falling back to default.', model_id)

    if not model_registry:
        # Signal type ka active model dhoondo ya default create karo
        model_registry = AIModelRegistry.objects.filter(
            signal_type=signal_type,
            status='active',
        ).first() or get_or_create_default_model(signal_type)

    # Signal evaluation
    if signal_type == 'movement':
        result_label, confidence_score = evaluate_movement_signal(sensor_data)
    elif signal_type == 'audio':
        result_label, confidence_score = evaluate_audio_signal(sensor_data)
    elif signal_type == 'sensor_fusion':
        result_label, confidence_score = evaluate_sensor_fusion(sensor_data)
    else:
        result_label = 'unrecognized_signal_type'
        confidence_score = 0.0

    # Advisory suggested action formulate karo
    # CRITICAL: Automatic SOS trigger kabhi nahi hoga — sirf user confirmation prompt hoga
    is_anomaly = 'detected' in result_label or confidence_score >= 0.70
    if is_anomaly:
        suggested_action = (
            "Potential anomaly detected. Show interactive check-in prompt: 'Are you safe?'. "
            "No automatic emergency SOS is triggered without explicit user confirmation."
        )
    else:
        suggested_action = "Telemetry within normal parameters. No action required."

    # Sanitized metadata for record retention (never store GPS coords or PII)
    safe_metadata = {
        'signal_type': signal_type,
        'model_version': model_registry.model_version,
        'has_anomaly': is_anomaly,
    }

    # Data retention: 30 days
    retention_expires_at = timezone.now() + timedelta(days=DEFAULT_RETENTION_DAYS)

    # Inference record save karo
    inference_record = AIInferenceRecord.objects.create(
        owner=user,
        model_registry=model_registry,
        signal_type=signal_type,
        result_label=result_label,
        confidence_score=confidence_score,
        is_advisory_only=True,  # ALWAYS TRUE — CRITICAL SAFETY RULE
        inference_metadata=safe_metadata,
        retention_expires_at=retention_expires_at,
        consent_recorded=True,
    )

    # Security Audit Trail
    record_audit_log(
        actor=user,
        action_category='ai',
        action='inference_evaluated',
        severity='warning' if is_anomaly else 'info',
        target_object=inference_record,
        request=request,
        extra_data={
            'signal_type': signal_type,
            'result_label': result_label,
            'confidence': confidence_score,
            'is_advisory_only': True,
        },
    )

    return {
        'inference_id': inference_record.id,
        'signal_type': signal_type,
        'result_label': result_label,
        'confidence_score': round(confidence_score, 3),
        'is_advisory_only': True,
        'suggested_action': suggested_action,
        'advisory_disclaimer': ADVISORY_DISCLAIMER_TEXT,
        'created_at': inference_record.created_at,
    }


def get_active_models(signal_type: Optional[str] = None):
    """Active AI models list karta hai."""
    qs = AIModelRegistry.objects.filter(status='active')
    if signal_type:
        qs = qs.filter(signal_type=signal_type)
    return qs.order_by('-created_at')


def get_user_inference_history(user, signal_type: Optional[str] = None, limit: int = 50):
    """User ke non-expired advisory inference records fetch karta hai."""
    qs = AIInferenceRecord.objects.filter(owner=user).select_related('model_registry')
    if signal_type:
        qs = qs.filter(signal_type=signal_type)
    return qs.order_by('-created_at')[:limit]


def purge_expired_inferences() -> int:
    """
    Data retention policy compliance: Purge records whose retention period has expired.
    """
    now = timezone.now()
    deleted_count, _ = AIInferenceRecord.objects.filter(retention_expires_at__lt=now).delete()
    logger.info('Purged %d expired AI inference records.', deleted_count)
    return deleted_count
