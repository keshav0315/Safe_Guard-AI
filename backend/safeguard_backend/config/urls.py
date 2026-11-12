"""
SafeGuard AI — Root URL Configuration
Saare app URLs yahan register honge.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)


def health_check(request):
    """
    Simple health check endpoint — load balancer aur monitoring ke liye.
    Yeh check karta hai ki server up hai.
    """
    return JsonResponse({
        'status': 'healthy',
        'service': 'SafeGuard AI Backend',
        'version': '1.0.0',
    }, status=200)


# Admin URL — production mein custom path use karo
admin_url = getattr(settings, 'ADMIN_URL', 'admin/')

urlpatterns = [
    # -----------------------------------------------------------------------
    # Django Admin
    # -----------------------------------------------------------------------
    path(admin_url, admin.site.urls),

    # -----------------------------------------------------------------------
    # Health Check — monitoring ke liye
    # -----------------------------------------------------------------------
    path('api/v1/health/', health_check, name='health-check'),

    # -----------------------------------------------------------------------
    # API v1 Routes — saare app endpoints
    # -----------------------------------------------------------------------
    path('api/v1/auth/', include('apps.users.urls.auth', namespace='auth')),
    path('api/v1/users/', include('apps.users.urls.users', namespace='users')),
    path('api/v1/contacts/', include('apps.contacts.urls', namespace='contacts')),
    path('api/v1/emergencies/', include('apps.emergencies.urls', namespace='emergencies')),
    path('api/v1/locations/', include('apps.locations.urls', namespace='locations')),
    path('api/v1/notifications/', include('apps.notifications.urls', namespace='notifications')),
    path('api/v1/ai/', include('apps.ai_detection.urls', namespace='ai_detection')),
    path('api/v1/audit/', include('apps.audit.urls', namespace='audit')),

    # -----------------------------------------------------------------------
    # API Schema & Documentation — drf-spectacular
    # -----------------------------------------------------------------------
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path(
        'api/docs/',
        SpectacularSwaggerView.as_view(url_name='schema'),
        name='swagger-ui',
    ),
    path(
        'api/redoc/',
        SpectacularRedocView.as_view(url_name='schema'),
        name='redoc',
    ),
]

# ---------------------------------------------------------------------------
# Development mein media files serve karo
# ---------------------------------------------------------------------------
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
