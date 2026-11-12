"""
apps/audit/admin.py
SafeGuard AI — Audit Log Admin Configuration
Audit trail ko read-only aur immutable banata hai taaki compliance aur forensic audit safe rahe.
"""

from django.contrib import admin
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """
    Security audit log records ka Django admin view.
    Tamper-evidence ke liye manual editing aur direct creation block ki gayi hai.
    """
    list_display = [
        'created_at',
        'actor',
        'action_category',
        'action',
        'severity',
        'target_object_type',
        'target_object_id',
        'ip_address',
    ]
    list_filter = [
        'action_category',
        'severity',
        'created_at',
    ]
    search_fields = [
        'actor__email',
        'actor__display_name',
        'action',
        'target_object_type',
        'target_object_id',
        'ip_address',
    ]
    ordering = ['-created_at']

    # Audit log immutable hona chahiye — saare fields read-only hain
    readonly_fields = [
        'id',
        'actor',
        'action_category',
        'action',
        'severity',
        'target_object_type',
        'target_object_id',
        'ip_address',
        'user_agent',
        'extra_data',
        'created_at',
    ]

    def has_add_permission(self, request):
        # Admin se directly fake audit log inject nahi kiya ja sakta
        return False

    def has_change_permission(self, request, obj=None):
        # Existing audit log tamper/edit nahi kiya ja sakta
        return False

    def has_delete_permission(self, request, obj=None):
        # Normal admin audit log delete nahi kar sakta — forensic integrity ke liye
        return request.user.is_superuser
