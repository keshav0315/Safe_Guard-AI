# User API views - sirf HTTP handling, logic service mein hai

from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .serializers import UserRegistrationSerializer, UserDetailSerializer, UserUpdateSerializer
from .services import ensure_user_profile_exists


class UserRegistrationView(generics.CreateAPIView):
    """Naya user register karne ka endpoint"""
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        # Profile automatically create karo
        ensure_user_profile_exists(user)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    GET: Apni profile dekho
    PATCH: Apni profile update karo
    Sirf authenticated user apni profile access kar sakta hai.
    """
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserUpdateSerializer
        return UserDetailSerializer

    def get_object(self):
        # Yaha authenticated user ki object return ho rahi hai
        ensure_user_profile_exists(self.request.user)
        return self.request.user
