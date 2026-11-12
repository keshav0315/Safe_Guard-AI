"""
apps/audit/views.py
SafeGuard AI — Audit Log API Views
User aur system activities ka tamper-evident log dekhne ke endpoints.
"""

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

from .models import AuditLog
from .serializers import AuditLogSerializer
from .services import get_audit_logs_for_user


@extend_schema(
    tags=['Audit'],
    summary='Audit history fetch karo',
    description='Current user ki security aur activity history retrieve karta hai. Staff/Admin pore system ke logs dekh sakte hain.',
    parameters=[
        OpenApiParameter('category', OpenApiTypes.STR, description='Action category filter (auth, emergency, security, etc.)', required=False),
        OpenApiParameter('severity', OpenApiTypes.STR, description='Severity filter (info, warning, critical)', required=False),
        OpenApiParameter('start_date', OpenApiTypes.DATETIME, description='ISO 8601 start date filter', required=False),
        OpenApiParameter('end_date', OpenApiTypes.DATETIME, description='ISO 8601 end date filter', required=False),
    ],
)
class AuditHistoryListView(generics.ListAPIView):
    """
    GET /api/v1/audit/history/
    # Security audit log history dekhne ka endpoint.
    Regular user sirf apne records dekh sakta hai; Admins saare system logs access kar sakte hain.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = AuditLogSerializer

    def get_queryset(self):
        category = self.request.query_params.get('category')
        severity = self.request.query_params.get('severity')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        return get_audit_logs_for_user(
            user=self.request.user,
            category=category,
            severity=severity,
            start_date=start_date,
            end_date=end_date,
        )
