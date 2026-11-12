from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import UserProfile

User = get_user_model()


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'display_name', 'role', 'is_active', 'is_guardian_managed', 'created_at']
    list_filter = ['role', 'is_active', 'is_guardian_managed', 'preferred_language']
    search_fields = ['email', 'display_name', 'phone_number']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-created_at']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'bio']
    search_fields = ['user__email', 'user__display_name']
    readonly_fields = ['user']
