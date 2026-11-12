# Health check - deployment monitoring ke liye

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db import connection
from django.utils import timezone
import django


class HealthCheckView(APIView):
    """
    GET /api/v1/health/
    Server ki health check karna.
    Secrets ya internal details expose mat karo.
    """
    permission_classes = [AllowAny]
    authentication_classes = []  # Auth skip karo health check ke liye

    def get(self, request):
        health_data = {
            'status': 'healthy',
            'timestamp': timezone.now().isoformat(),
            'version': 'v1',
            'django_version': django.__version__,
            'checks': {}
        }

        # Database check karo
        try:
            connection.ensure_connection()
            health_data['checks']['database'] = 'ok'
        except Exception as e:
            health_data['checks']['database'] = 'error'
            health_data['status'] = 'degraded'

        # Redis check karo (optional)
        try:
            from django.core.cache import cache
            cache.set('health_check', 'ok', 10)
            if cache.get('health_check') == 'ok':
                health_data['checks']['cache'] = 'ok'
        except Exception:
            health_data['checks']['cache'] = 'unavailable'

        status_code = 200 if health_data['status'] == 'healthy' else 503
        return Response(health_data, status=status_code)
