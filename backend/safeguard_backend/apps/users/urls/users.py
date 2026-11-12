"""
User Profile URLs — SafeGuard AI
Current user profile fetch and update
"""

from django.urls import path
from apps.users.views import UserProfileView

app_name = 'users'

urlpatterns = [
    # Authenticated user ki apni profile retrieve aur update karne ke liye
    path('me/', UserProfileView.as_view(), name='me'),
]
