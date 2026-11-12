"""
API Integration tests for SafeGuard AI Health Check endpoint.
Publicly accessible for uptime monitoring, Docker, and load balancers.
"""

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestHealthCheckAPI:
    """Test suite for /api/v1/health/ monitoring endpoint."""

    @pytest.fixture
    def client(self):
        return APIClient()

    def test_health_check_returns_200_ok(self, client):
        """Health check endpoint should return 200 OK with healthy status payload."""
        url = reverse('health-check')
        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data.get('status') == 'healthy'
        assert data.get('service') == 'SafeGuard AI Backend'
        assert data.get('version') == '1.0.0'

    def test_health_check_public_access_no_auth_required(self, client):
        """Endpoint must be publicly accessible without any Authorization header."""
        response = client.get('/api/v1/health/')
        assert response.status_code == status.HTTP_200_OK
