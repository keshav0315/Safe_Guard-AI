"""
apps/locations/admin.py
SafeGuard AI — Django admin interface for Location models.
"""

from django.contrib import admin
from .models import LocationSnapshot, LocationSharingSession


@admin.register(LocationSnapshot)
class LocationSnapshotAdmin(admin.ModelAdmin):
    """
    Location snapshots ka admin management panel.
    """
    list_display = [
        'id',
        'owner',
        'emergency_event',
        'latitude',
        'longitude',
        'accuracy_meters',
        'sharing_scope',
        'is_sharing_active',
        'expires_at',
        'created_at',
    ]
    list_filter = [
        'sharing_scope',
        'is_sharing_active',
        'created_at',
    ]
    search_fields = [
        'id',
        'owner__email',
        'owner__display_name',
        'share_token',
    ]
    readonly_fields = [
        'id',
        'share_token',
        'created_at',
    ]
    ordering = ['-created_at']
    date_hierarchy = 'created_at'


@admin.register(LocationSharingSession)
class LocationSharingSessionAdmin(admin.ModelAdmin):
    """
    Trusted contacts ke saath live sharing sessions ka admin view.
    """
    list_display = [
        'id',
        'location_snapshot',
        'shared_with_contact',
        'is_active',
        'expires_at',
        'last_accessed_at',
        'created_at',
    ]
    list_filter = [
        'is_active',
        'created_at',
    ]
    search_fields = [
        'id',
        'access_token',
        'shared_with_contact__contact_name',
        'shared_with_contact__phone_number',
    ]
    readonly_fields = [
        'id',
        'access_token',
        'created_at',
    ]
    ordering = ['-created_at']
