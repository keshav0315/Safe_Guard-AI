"""
apps/audit/urls.py
SafeGuard AI — Audit App URLs
Path: /api/v1/audit/history/
"""

from django.urls import path
from .views import AuditHistoryListView

app_name = 'audit'

urlpatterns = [
    # Audit log history retrieval endpoint
    path('history/', AuditHistoryListView.as_view(), name='audit-history'),
]
