# Reusable permission classes - security ke liye

from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsOwner(BasePermission):
    """Object sirf uska owner hi access kar sake"""
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        if hasattr(obj, 'user'):
            return obj.user == request.user
        return False

class IsOwnerOrReadOnly(BasePermission):
    """Owner edit kar sake, authenticated users read kar sakein"""
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return request.user.is_authenticated
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        return False

class IsAdminOrOwner(BasePermission):
    """Admin ya object owner access kar sake"""
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        return False

class IsGuardianOrAdmin(BasePermission):
    """Guardian ya admin access kar sake - child accounts ke liye"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.role in ['guardian', 'admin'] or request.user.is_staff
        )
