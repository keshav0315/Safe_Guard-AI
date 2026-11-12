"""
API Integration tests for SafeGuard AI Trusted Contacts endpoints.
Covers contact creation, ownership filtering (own contacts only),
cross-user isolation, and soft deletion.
"""

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from apps.contacts.models import TrustedContact

User = get_user_model()


@pytest.mark.django_db
class TestTrustedContactsAPI:
    """Test suite for /api/v1/contacts/ endpoints."""

    @pytest.fixture
    def client(self):
        return APIClient()

    @pytest.fixture
    def user_a(self):
        return User.objects.create_user(
            email="user_a@example.com",
            display_name="User Alpha",
            password="Password123!",
        )

    @pytest.fixture
    def user_b(self):
        return User.objects.create_user(
            email="user_b@example.com",
            display_name="User Beta",
            password="Password123!",
        )

    def test_create_trusted_contact_success(self, client, user_a):
        """Authenticated user can add a trusted contact with valid phone or email."""
        client.force_authenticate(user=user_a)

        payload = {
            "contact_name": "Ramesh Kumar",
            "phone_number": "+919811122233",
            "email": "ramesh@example.com",
            "relationship_label": "Brother",
            "notes": "Call immediately during emergency",
        }
        response = client.post("/api/v1/contacts/", payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["contact_name"] == "Ramesh Kumar"
        assert data["relationship_label"] == "Brother"
        assert data["is_active"] is True

        # Database verification
        contact = TrustedContact.objects.get(id=data["id"])
        assert contact.owner == user_a
        assert contact.contact_name == "Ramesh Kumar"

    def test_list_contacts_returns_own_contacts_only(self, client, user_a, user_b):
        """User A should only see contacts belonging to User A, never User B's contacts."""
        contact_a = TrustedContact.objects.create(
            owner=user_a,
            contact_name="Alpha Contact",
            phone_number="+919111111111",
            is_active=True,
        )
        contact_b = TrustedContact.objects.create(
            owner=user_b,
            contact_name="Beta Secret Contact",
            phone_number="+919222222222",
            is_active=True,
        )

        client.force_authenticate(user=user_a)
        response = client.get("/api/v1/contacts/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        contacts = data.get("results", data) if isinstance(data, dict) else data

        contact_ids = [c["id"] for c in contacts]
        assert str(contact_a.id) in contact_ids
        assert str(contact_b.id) not in contact_ids

    def test_cross_user_contact_access_forbidden_or_not_found(self, client, user_a, user_b):
        """User A cannot access User B's contact directly via /api/v1/contacts/<pk>/."""
        contact_b = TrustedContact.objects.create(
            owner=user_b,
            contact_name="Beta Private Contact",
            phone_number="+919333333333",
            is_active=True,
        )

        client.force_authenticate(user=user_a)
        response = client.get(f"/api/v1/contacts/{contact_b.id}/")

        assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_403_FORBIDDEN]

    def test_soft_delete_trusted_contact(self, client, user_a):
        """Deleting a contact marks is_active=False without hard deleting row."""
        contact = TrustedContact.objects.create(
            owner=user_a,
            contact_name="Deactivate Me",
            phone_number="+919444444444",
            is_active=True,
        )

        client.force_authenticate(user=user_a)
        response = client.delete(f"/api/v1/contacts/{contact.id}/")

        assert response.status_code == status.HTTP_200_OK

        # Verify soft delete in DB
        contact.refresh_from_db()
        assert contact.is_active is False

        # Contact should no longer appear in active list
        list_response = client.get("/api/v1/contacts/")
        assert list_response.status_code == status.HTTP_200_OK
        list_data = list_response.json()
        active_contacts = list_data.get("results", list_data) if isinstance(list_data, dict) else list_data
        active_ids = [c["id"] for c in active_contacts]
        assert str(contact.id) not in active_ids
