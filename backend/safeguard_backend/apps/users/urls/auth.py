"""
Authentication URLs — SafeGuard AI
Registration, Login, Token Refresh and Blacklist
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenBlacklistView
from apps.users.views import UserRegistrationView

app_name = 'auth'

urlpatterns = [
    # Naya user account banane ke liye endpoint
    path('register/', UserRegistrationView.as_view(), name='register'),
    # Login karke JWT access aur refresh token praapt karne ke liye
    path('token/', TokenObtainPairView.as_view(), name='token-obtain'),
    # Expired access token ko naya banane ke liye
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    # Logout ke samay refresh token ko blacklist karne ke liye
    path('token/blacklist/', TokenBlacklistView.as_view(), name='token-blacklist'),
]
