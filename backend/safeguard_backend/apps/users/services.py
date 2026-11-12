# User-related business logic yaha hai

from django.contrib.auth import get_user_model
from .models import UserProfile

User = get_user_model()


def get_user_by_id(user_id):
    """User ko ID se fetch karna"""
    try:
        return User.objects.select_related('profile').get(id=user_id, is_active=True)
    except User.DoesNotExist:
        return None


def ensure_user_profile_exists(user):
    """User ka profile ensure karna - agar nahi hai to create karo"""
    profile, created = UserProfile.objects.get_or_create(user=user)
    return profile


def deactivate_user_account(user):
    """User account band karna - soft delete"""
    user.is_active = False
    user.save(update_fields=['is_active', 'updated_at'])
    return user
