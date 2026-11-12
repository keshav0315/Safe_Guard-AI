"""
apps/emergencies/urls.py
SafeGuard AI — Emergency URL routing.
Endpoints:
- POST /api/v1/emergencies/sos/             -> Trigger SOS alert (idempotent)
- GET  /api/v1/emergencies/                 -> Emergency events history
- GET  /api/v1/emergencies/<event_id>/      -> Emergency event details
- POST /api/v1/emergencies/<event_id>/cancel/  -> Cancel emergency
- POST /api/v1/emergencies/<event_id>/resolve/ -> Resolve emergency
"""

from django.urls import path
from .views import (
    SOSCreateView,
    EmergencyHistoryView,
    EmergencyDetailView,
    EmergencyCancelView,
    EmergencyResolveView,
)

app_name = 'emergencies'

urlpatterns = [
    # SOS alert trigger endpoint
    path('sos/', SOSCreateView.as_view(), name='sos-create'),

    # User ki emergency history dekhne ke liye
    path('', EmergencyHistoryView.as_view(), name='emergency-history'),

    # Kisi specific emergency ki full details fetch karne ke liye
    path('<uuid:event_id>/', EmergencyDetailView.as_view(), name='emergency-detail'),

    # Emergency alert ko user dwara cancel karne ke liye
    path('<uuid:event_id>/cancel/', EmergencyCancelView.as_view(), name='emergency-cancel'),

    # Emergency ko resolved mark karne ke liye
    path('<uuid:event_id>/resolve/', EmergencyResolveView.as_view(), name='emergency-resolve'),
]
