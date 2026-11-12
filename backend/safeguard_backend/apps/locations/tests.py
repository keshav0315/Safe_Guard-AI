"""
apps/locations/tests.py
SafeGuard AI — Tests for Location snapshot, history, and sharing token endpoints.
"""

import uuid
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from apps.locations.models import LocationSnapshot
from apps.contacts.models import TrustedContact

User = get_user_model()


class LocationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='loctest@safeguard.ai',
            display_name='Location User',
            password='TestPassword123!',
        )
        self.contact = TrustedContact.objects.create(
            owner=self.user,
            contact_name='Sister',
            phone_number='+919123456789',
            is_active=True,
        )
        self.client.force_authenticate(user=self.user)

    def test_location_submit_private(self):
        url = reverse('locations:location-submit')
        payload = {
            'latitude': 12.971599,
            'longitude': 77.594566,
            'accuracy_meters': 8.0,
            'sharing_scope': 'private',
        }
        response = self.client.post(url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.data
        self.assertIn('id', data)
        self.assertEqual(data['sharing_scope'], 'private')

        # Snapshot in database
        snapshot = LocationSnapshot.objects.get(id=data['id'])
        self.assertEqual(snapshot.owner, self.user)
        self.assertEqual(float(snapshot.latitude), 12.971599)

    def test_location_submit_with_contacts_sharing(self):
        url = reverse('locations:location-submit')
        payload = {
            'latitude': 22.572645,
            'longitude': 88.363892,
            'sharing_scope': 'contacts',
            'expires_in_minutes': 120,
            'shared_with_contact_ids': [str(self.contact.id)],
        }
        response = self.client.post(url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data['sharing_sessions']), 1)

    def test_shared_location_via_public_link(self):
        snapshot = LocationSnapshot.objects.create(
            owner=self.user,
            latitude=28.704060,
            longitude=77.102493,
            captured_at=timezone.now(),
            sharing_scope='public_link',
            share_token='test-secure-token-12345',
            expires_at=timezone.now() + timezone.timedelta(hours=1),
            is_sharing_active=True,
        )

        # Unauthenticated client access test
        unauth_client = APIClient()
        url = reverse('locations:location-shared', kwargs={'share_token': snapshot.share_token})
        response = unauth_client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(float(response.data['latitude']), 28.704060)
        self.assertEqual(response.data['owner_display_name'], 'Location User')

    def test_shared_location_expired(self):
        snapshot = LocationSnapshot.objects.create(
            owner=self.user,
            latitude=28.704060,
            longitude=77.102493,
            captured_at=timezone.now() - timezone.timedelta(hours=2),
            sharing_scope='public_link',
            share_token='expired-token-999',
            expires_at=timezone.now() - timezone.timedelta(minutes=10),
            is_sharing_active=True,
        )
        unauth_client = APIClient()
        url = reverse('locations:location-shared', kwargs={'share_token': snapshot.share_token})
        response = unauth_client.get(url)
        # Should be an error indicating expiration
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_403_FORBIDDEN])

    def test_location_history(self):
        LocationSnapshot.objects.create(
            owner=self.user,
            latitude=13.082680,
            longitude=80.270721,
            captured_at=timezone.now(),
            sharing_scope='private',
            share_token=str(uuid.uuid4()),
        )
        url = reverse('locations:location-history')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)
