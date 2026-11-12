"""
API Integration tests for SafeGuard AI Authentication & Profile endpoints.
Covers registration, JWT token acquisition, and /api/v1/users/me/ profile operations.
"""

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


@pytest.mark.django_db
class TestAuthenticationAPI:
    """Test suite for user registration and JWT authentication endpoints."""

    @pytest.fixture
    def client(self):
        return APIClient()

    def test_user_registration_success(self, client):
        """Registering with valid fields creates a user and returns 201 Created."""
        payload = {
            "email": "priya.sharma@example.com",
            "display_name": "Priya Sharma",
            "phone_number": "+919876543210",
            "password": "SecurePassword123!",
            "password_confirm": "SecurePassword123!",
            "preferred_language": "hi",
        }
        response = client.post("/api/v1/auth/register/", payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(email="priya.sharma@example.com").exists()
        created_user = User.objects.get(email="priya.sharma@example.com")
        assert created_user.display_name == "Priya Sharma"
        assert created_user.check_password("SecurePassword123!")
        # Profile should be created automatically
        assert hasattr(created_user, "profile")

    def test_user_registration_password_mismatch(self, client):
        """Mismatched password and password_confirm must return 400 Bad Request."""
        payload = {
            "email": "mismatch@example.com",
            "display_name": "Mismatch User",
            "password": "PasswordOne123!",
            "password_confirm": "PasswordTwo456!",
        }
        response = client.post("/api/v1/auth/register/", payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "password_confirm" in response.data.get("error", {}).get("details", {}) or "password_confirm" in str(response.data)

    def test_login_jwt_obtain_pair_success(self, client):
        """Valid credentials return JWT access and refresh tokens."""
        User.objects.create_user(
            email="login.test@example.com",
            display_name="Login Test",
            password="ValidPassword123!",
        )

        payload = {
            "email": "login.test@example.com",
            "password": "ValidPassword123!",
        }
        response = client.post("/api/v1/auth/token/", payload, format="json")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access" in data
        assert "refresh" in data

    def test_login_jwt_invalid_credentials_rejected(self, client):
        """Invalid credentials must return 401 Unauthorized."""
        User.objects.create_user(
            email="user@example.com",
            display_name="Test User",
            password="CorrectPassword123!",
        )

        payload = {
            "email": "user@example.com",
            "password": "WrongPassword999!",
        }
        response = client.post("/api/v1/auth/token/", payload, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_user_profile_me_authenticated(self, client):
        """Authenticated user can fetch their own profile with /api/v1/users/me/."""
        user = User.objects.create_user(
            email="me.user@example.com",
            display_name="Me User",
            password="Password123!",
            preferred_language="en",
        )
        client.force_authenticate(user=user)

        response = client.get("/api/v1/users/me/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == "me.user@example.com"
        assert data["display_name"] == "Me User"
        assert data["preferred_language"] == "en"

    def test_get_user_profile_me_unauthenticated_blocked(self, client):
        """Unauthenticated request to /api/v1/users/me/ must be rejected with 401."""
        response = client.get("/api/v1/users/me/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_patch_user_profile_me(self, client):
        """User can update their display name and preferred language."""
        user = User.objects.create_user(
            email="update.me@example.com",
            display_name="Original Name",
            password="Password123!",
            preferred_language="en",
        )
        client.force_authenticate(user=user)

        update_payload = {
            "display_name": "Updated SafeGuard User",
            "preferred_language": "hi",
        }
        response = client.patch("/api/v1/users/me/", update_payload, format="json")

        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.display_name == "Updated SafeGuard User"
        assert user.preferred_language == "hi"
