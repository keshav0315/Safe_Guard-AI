# =============================================================================
# Security & Permissions Tests — Access Controls & Cross-User Isolation
# =============================================================================

from decimal import Decimal
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.contacts.models import TrustedContact
from apps.emergencies.models import EmergencyEvent
from apps.locations.models import LocationSnapshot

User = get_user_model()


class TestSecurityAndDataIsolation(TestCase):
    """
    Penetration & Authorization Tests:
    1. Unauthenticated request blocks
    2. Horizontal privilege escalation prevention (User A access User B)
    3. Location share token expiry enforcement
    """

    def setUp(self):
        self.client = APIClient()
        self.alice = User.objects.create_user(
            email='alice@safeguard.ai',
            display_name='Alice Safe',
            password='PasswordAlice123'
        )
        self.bob = User.objects.create_user(
            email='bob@safeguard.ai',
            display_name='Bob Malicious',
            password='PasswordBob123'
        )

    def test_unauthenticated_endpoints_return_401(self):
        # Protected routes list
        protected_routes = [
            ('/api/v1/users/me/', 'GET'),
            ('/api/v1/contacts/', 'GET'),
            ('/api/v1/emergencies/', 'GET'),
            ('/api/v1/emergencies/sos/', 'POST'),
            ('/api/v1/locations/', 'POST'),
            ('/api/v1/notifications/devices/register/', 'POST'),
            ('/api/v1/ai/inference/', 'POST'),
            ('/api/v1/audit/history/', 'GET'),
        ]
        unauth_client = APIClient()
        for path, method in protected_routes:
            if method == 'GET':
                res = unauth_client.get(path)
            else:
                res = unauth_client.post(path, {}, format='json')
            self.assertEqual(
                res.status_code,
                status.HTTP_401_UNAUTHORIZED,
                f"Endpoint {path} ({method}) should be protected by authentication"
            )

    def test_cross_user_contact_isolation(self):
        # Alice creates a contact
        contact_alice = TrustedContact.objects.create(
            owner=self.alice,
            contact_name='Alice Sister',
            phone_number='+919876500000'
        )

        # Bob logs in and tries to access Alice's contact
        self.client.force_authenticate(user=self.bob)
        res = self.client.get(f'/api/v1/contacts/{contact_alice.id}/')
        # Bob should get 404 Not Found
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_shared_location_token_expiry_enforcement(self):
        # Alice creates an expired location snapshot
        expired_snapshot = LocationSnapshot.objects.create(
            owner=self.alice,
            latitude=Decimal('28.535500'),
            longitude=Decimal('77.391000'),
            captured_at=timezone.now() - timedelta(hours=3),
            sharing_scope='public_link',
            share_token='expired-secret-token-12345',
            expires_at=timezone.now() - timedelta(hours=1),
            is_sharing_active=True,
        )

        # Anyone accessing expired share link should be rejected (400 Bad Request or 404 Not Found)
        unauth_client = APIClient()
        res = unauth_client.get('/api/v1/locations/shared/expired-secret-token-12345/')
        self.assertIn(res.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND])
