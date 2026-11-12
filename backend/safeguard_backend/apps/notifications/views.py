"""
apps/notifications/views.py
SafeGuard AI — Push Notifications & Device Token Endpoints
FCM token registration aur delivery status monitoring.
"""

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

from .models import DeviceToken, NotificationDelivery
from .serializers import (
    DeviceTokenRegisterSerializer,
    DeviceTokenSerializer,
    NotificationDeliverySerializer,
)
from .services import (
    register_or_update_device_token,
    get_user_device_tokens,
    get_deliveries_for_user,
)


@extend_schema(
    tags=['Notifications'],
    summary='FCM Device Token Register / Refresh karo',
    description='Mobile device ka Firebase Cloud Messaging push token register ya refresh karta hai.',
    request=DeviceTokenRegisterSerializer,
    responses={
        200: DeviceTokenSerializer,
        201: DeviceTokenSerializer,
    },
)
class DeviceTokenRegisterView(APIView):
    """
    POST /api/v1/notifications/devices/register/
    # FCM device token register karne ka endpoint
    GET /api/v1/notifications/devices/register/ -> User ke active devices ki list
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """User ke registered devices dekhne ke liye"""
        tokens = get_user_device_tokens(request.user)
        serializer = DeviceTokenSerializer(tokens, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """Device token register ya update karo"""
        serializer = DeviceTokenRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data['token']
        platform = serializer.validated_data.get('platform', 'android')
        device_name = serializer.validated_data.get('device_name', '')

        device_token = register_or_update_device_token(
            user=request.user,
            token=token,
            platform=platform,
            device_name=device_name,
            request=request,
        )

        response_serializer = DeviceTokenSerializer(device_token)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    tags=['Notifications'],
    summary='Notification deliveries list karo',
    description='User ki emergency events ke notification deliveries ka status aur retries dekho.',
    parameters=[
        OpenApiParameter(
            'event_id',
            OpenApiTypes.UUID,
            description='Filter deliveries by specific Emergency Event ID',
            required=False,
        ),
    ],
    responses={200: NotificationDeliverySerializer(many=True)},
)
class NotificationDeliveryListView(generics.ListAPIView):
    """
    GET /api/v1/notifications/deliveries/
    Emergency notifications ki delivery status history list karta hai.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationDeliverySerializer

    def get_queryset(self):
        event_id = self.request.query_params.get('event_id')
        return get_deliveries_for_user(self.request.user, emergency_event_id=event_id)
