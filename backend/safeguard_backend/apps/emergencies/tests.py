"""
apps/emergencies/tests.py
SafeGuard AI — Tests for Emergency and SOS endpoints and services.
"""

import uuid
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.emergencies.models import EmergencyEvent
from apps.contacts.models import TrustedContact
from apps.locations.models import LocationSnapshot
from apps.notifications.models import NotificationDelivery

User = get_user_model()


class EmergencyTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='testuser@safeguard.ai',
            display_name='Test Victim',
            password='TestPassword123!',
        )
        self.other_user = User.objects.create_user(
            email='other@safeguard.ai',
            display_name='Other User',
            password='TestPassword123!',
        )
        self.contact = TrustedContact.objects.create(
            owner=self.user,
            contact_name='Mom',
            phone_number='+919876543210',
            relationship_label='Mother',
            is_active=True,
        )
        self.client.force_authenticate(user=self.user)

    def test_sos_create_success(self):
        # Initial SOS alert trigger test
        payload = {
            'idempotency_key': f'sos-{uuid.uuid4()}',
            'event_type': 'sos',
            'notes': 'Help needed right now!',
            'latitude': 28.613939,
            'longitude': 77.209021,
            'accuracy_meters': 12.5,
        }
        url = reverse('emergencies:sos-create')
        response = self.client.post(url, data=payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.data
        self.assertIn('id', data)
        self.assertEqual(data['status'], 'active')
        self.assertEqual(data['event_type'], 'sos')

        # Verify database objects
        event = EmergencyEvent.objects.get(id=data['id'])
        self.assertEqual(event.owner, self.user)

        # Location snapshot created
        snapshot = LocationSnapshot.objects.filter(emergency_event=event).first()
        self.assertIsNotNone(snapshot)
        self.assertEqual(float(snapshot.latitude), 28.613939)

        # Notification deliveries queued for active contacts
        deliveries = NotificationDelivery.objects.filter(emergency_event=event)
        self.assertEqual(deliveries.count(), 1)
        self.assertEqual(deliveries.first().recipient_contact, self.contact)

    def test_sos_idempotency_duplicate_request(self):
        # Accidental double tap test: same idempotency key must not create duplicate
        key = f'sos-{uuid.uuid4()}'
        payload = {
            'idempotency_key': key,
            'event_type': 'sos',
            'latitude': 19.076090,
            'longitude': 72.877426,
        }
        url = reverse('emergencies:sos-create')

        # First trigger: 201 Created
        resp1 = self.client.post(url, data=payload, format='json')
        self.assertEqual(resp1.status_code, status.HTTP_201_CREATED)
        event_id1 = resp1.data['id']

        # Second trigger (double-tap): 200 OK, returns same event ID
        resp2 = self.client.post(url, data=payload, format='json')
        self.assertEqual(resp2.status_code, status.HTTP_200_OK)
        self.assertEqual(resp2.data['id'], event_id1)

        # Database count must be 1
        self.assertEqual(EmergencyEvent.objects.filter(idempotency_key=key).count(), 1)

    def test_emergency_history(self):
        EmergencyEvent.objects.create(
            owner=self.user,
            idempotency_key=str(uuid.uuid4()),
            event_type='sos',
            status='active',
        )
        url = reverse('emergencies:emergency-history')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)

    def test_emergency_cancel(self):
        event = EmergencyEvent.objects.create(
            owner=self.user,
            idempotency_key=str(uuid.uuid4()),
            event_type='sos',
            status='active',
        )
        url = reverse('emergencies:emergency-cancel', kwargs={'event_id': event.id})
        response = self.client.post(url, data={'notes': 'False alarm'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        event.refresh_from_db()
        self.assertEqual(event.status, 'cancelled')
        self.assertIsNotNone(event.cancelled_at)

    def test_emergency_resolve(self):
        event = EmergencyEvent.objects.create(
            owner=self.user,
            idempotency_key=str(uuid.uuid4()),
            event_type='sos',
            status='active',
        )
        url = reverse('emergencies:emergency-resolve', kwargs={'event_id': event.id})
        response = self.client.post(url, data={'notes': 'Help reached'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        event.refresh_from_db()
        self.assertEqual(event.status, 'resolved')
        self.assertIsNotNone(event.resolved_at)
