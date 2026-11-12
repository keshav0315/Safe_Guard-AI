"""
apps/contacts/admin.py
SafeGuard AI — Trusted Contacts Admin Interface
Django Admin se trusted contacts dekhne aur manage karne ke liye.
"""

from django.contrib import admin
from .models import TrustedContact


@admin.register(TrustedContact)
class TrustedContactAdmin(admin.ModelAdmin):
    """
    Admin panel par trusted contacts ka overview.
    Owner, phone number, verification status aur active state display karta hai.
    """
    list_display = [
        'contact_name',
        'owner',
        'relationship_label',
        'phone_number',
        'email',
        'verification_status',
        'consent_status',
        'is_active',
        'created_at',
    ]
    list_filter = [
        'verification_status',
        'consent_status',
        'is_active',
        'relationship_label',
        'created_at',
    ]
    search_fields = [
        'contact_name',
        'phone_number',
        'email',
        'owner__email',
        'owner__display_name',
    ]
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-created_at']

    # Admin actions: activate/deactivate bulk contacts
    actions = ['mark_as_verified', 'deactivate_contacts']

    @admin.action(description='Selected contacts ko verified mark karo')
    def mark_as_verified(self, request, queryset):
        # Admin manually verify kar sakta hai agar test ya operational requirement ho
        updated = queryset.update(verification_status='verified')
        self.message_user(request, f'{updated} contacts ko verified mark kar diya gaya hai.')

    @admin.action(description='Selected contacts ko deactivate (soft delete) karo')
    def deactivate_contacts(self, request, queryset):
        # Soft delete helper
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} contacts ko deactivate kar diya gaya hai.')
