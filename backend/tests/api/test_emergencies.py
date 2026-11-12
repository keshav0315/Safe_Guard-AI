# =============================================================================
# API Tests — Emergency SOS Workflow & Idempotency Reliability
# =============================================================================

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.emergencies.models import EmergencyEvent
from apps.locations.models import LocationSnapshot

User = get_user_model()


class TestEmergencySOSWorkflow(TestCase):
    """
    Emergency SOS lifecycle tests:
    1. One-touch SOS creation
    2. Idempotency protection against accidental double-clicks
    3. Location snapshot capture
    4. Cancellation with reason
    5. Independent of AI service availability
    """

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='woman_safety@safeguard.ai',
            display_name='Neha Verma',
            password='Password123!'
        )
        self.other_user = User.objects.create_user(
            email='random_user@safeguard.ai',
            display_name='Random User',
            password='Password123!'
        )
        self.client.force_authenticate(user=self.user)
        self.sos_url = '/api/v1/emergencies/sos/'

    def test_sos_one_touch_creation(self):
        payload = {
            'idempotency_key': 'evt-client-101',
            'event_type': 'sos',
            'notes': 'Suspect following me',
            'latitude': '28.613900',
            'longitude': '77.209000',
            'accuracy_meters': 5.2,
        }
        response = self.client.post(self.sos_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data.get('status'), 'active')

        # Check DB
        self.assertEqual(EmergencyEvent.objects.filter(owner=self.user).count(), 1)
        # Check Location Snapshot created
        self.assertEqual(LocationSnapshot.objects.filter(owner=self.user).count(), 1)

    def test_sos_duplicate_idempotency_protection(self):
        """
        Jab mobile user ghabrahat mein 2 baar SOS dabaye to duplicate alert nahi banega,
        vahi same event return hoga with HTTP 200 OK
        """
        payload = {
            'idempotency_key': 'double-tap-12345',
            'event_type': 'sos',
        }
        # Pehla tap
        res1 = self.client.post(self.sos_url, payload, format='json')
        self.assertEqual(res1.status_code, status.HTTP_201_CREATED)

        # Dusra tap (same idempotency_key)
        res2 = self.client.post(self.sos_url, payload, format='json')
        self.assertEqual(res2.status_code, status.HTTP_200_OK)
        self.assertEqual(res1.data.get('id'), res2.data.get('id'))

        # DB mein sirf ek hi event hona chahiye
        self.assertEqual(EmergencyEvent.objects.filter(owner=self.user).count(), 1)

    def test_cancel_active_sos_event(self):
        # Pehle SOS banao
        event = EmergencyEvent.objects.create(
            owner=self.user,
            event_type='sos',
            status='active',
            idempotency_key='test-cancel-key-99'
        )
        cancel_url = f'/api/v1/emergencies/{event.id}/cancel/'
        response = self.client.post(cancel_url, {'reason': 'False alarm, reached safe place'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        event.refresh_from_db()
        self.assertEqual(event.status, 'cancelled')
        self.assertIsNotNone(event.cancelled_at)

    def test_cannot_cancel_other_users_emergency(self):
        other_event = EmergencyEvent.objects.create(
            owner=self.other_user,
            event_type='sos',
            status='active',
            idempotency_key='attacker-target-key'
        )
        cancel_url = f'/api/v1/emergencies/{other_event.id}/cancel/'
        response = self.client.post(cancel_url, {'reason': 'Malicious cancel'}, format='json')
        # 404 Not Found aana chahiye taaki resource ki existence bhi pata na chale
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
