"""
apps/emergencies/admin.py
SafeGuard AI — Django admin interface for EmergencyEvent model.
"""

from django.contrib import admin
from .models import EmergencyEvent


@admin.register(EmergencyEvent)
class EmergencyEventAdmin(admin.ModelAdmin):
    """
    Emergency alerts ka central monitoring panel admin ke liye.
    """
    list_display = [
        'id',
        'owner',
        'event_type',
        'status',
        'created_at',
        'acknowledged_at',
        'cancelled_at',
        'resolved_at',
    ]
    list_filter = [
        'status',
        'event_type',
        'created_at',
    ]
    search_fields = [
        'id',
        'owner__email',
        'owner__display_name',
        'idempotency_key',
        'notes',
    ]
    readonly_fields = [
        'id',
        'idempotency_key',
        'created_at',
        'updated_at',
    ]
    ordering = ['-created_at']
    date_hierarchy = 'created_at'

    # Admin actions: Mass status update capability agar zaroorat pade
    actions = ['mark_as_resolved']

    @admin.action(description="Mark selected emergencies as Resolved")
    def mark_as_resolved(self, request, queryset):
        from django.utils import timezone
        updated = queryset.filter(status='active').update(
            status='resolved',
            resolved_at=timezone.now(),
        )
        self.message_user(request, f"{updated} emergency events successfully resolved.")
