from rest_framework.permissions import BasePermission


class IsContactOwner(BasePermission):
    """
    Contact sirf uski owner user hi access kar sake.
    Cross-user contact access strictly banned hai.
    """

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user
