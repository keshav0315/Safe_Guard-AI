"""
apps/audit/serializers.py
SafeGuard AI — Audit Log Serializers
Security aur compliance ke liye audit records render karne ke serializers.
"""

from rest_framework import serializers
from .models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    """
    Audit log record ka read-only serializer.
    Kissi bhi user ko tamper karne ki permission nahi hai — audit trail immutable hota hai.
    """
    actor_email = serializers.CharField(source='actor.email', read_only=True, default=None)
    actor_name = serializers.CharField(source='actor.display_name', read_only=True, default=None)

    class Meta:
        model = AuditLog
        fields = [
            'id',
            'actor',
            'actor_email',
            'actor_name',
            'action_category',
            'action',
            'severity',
            'target_object_type',
            'target_object_id',
            'ip_address',
            'user_agent',
            'extra_data',
            'created_at',
        ]
        # Security ke liye har field read-only hai — audit log ko API se modify nahi kiya ja sakta
        read_only_fields = fields


class AuditLogFilterQuerySerializer(serializers.Serializer):
    """
    Query parameters validate karne ke liye serializer (category, severity, date range filters).
    """
    category = serializers.ChoiceField(
        choices=[c[0] for c in AuditLog.ACTION_CATEGORY_CHOICES],
        required=False,
    )
    severity = serializers.ChoiceField(
        choices=[s[0] for s in AuditLog.SEVERITY_CHOICES],
        required=False,
    )
    start_date = serializers.DateTimeField(required=False)
    end_date = serializers.DateTimeField(required=False)
