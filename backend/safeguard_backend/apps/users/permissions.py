from rest_framework.permissions import BasePermission


class IsOwnerOrAdmin(BasePermission):
    """
    Sirf object ka owner ya admin access kar sake.
    Object-level permission - bahut zaroori security check.
    """

    def has_object_permission(self, request, view, obj):
        # Admin ko sab kuch access
        if request.user.is_staff:
            return True
        # Object ka owner check karo
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        if hasattr(obj, 'user'):
            return obj.user == request.user
        return obj == request.user
