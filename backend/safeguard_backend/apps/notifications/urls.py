"""
apps/notifications/urls.py
SafeGuard AI — Notification URL Routing
Endpoints:
- POST/GET /api/v1/notifications/devices/register/
- GET      /api/v1/notifications/deliveries/
"""

from django.urls import path
from .views import DeviceTokenRegisterView, NotificationDeliveryListView

app_name = 'notifications'

urlpatterns = [
    # FCM push notification token registration endpoint
    path('devices/register/', DeviceTokenRegisterView.as_view(), name='device-register'),

    # Emergency notification delivery tracking endpoint
    path('deliveries/', NotificationDeliveryListView.as_view(), name='notification-deliveries'),
]
