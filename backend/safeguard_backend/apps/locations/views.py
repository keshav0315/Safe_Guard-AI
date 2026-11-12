"""
apps/locations/views.py
SafeGuard AI — Location API views.
Thin views pattern: Serializer validation -> Service execution -> HTTP response.
Expiring tokens aur privacy-aware shared location access yahan handle hota hai.
"""

from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    LocationSubmitSerializer,
    LocationSnapshotSerializer,
    SharedLocationPublicSerializer,
)
from .services import (
    record_location,
    get_shared_location_by_token,
    get_user_location_history,
)


def _get_client_ip(request):
    """Client request se remote IP extract karne ka utility helper"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


class LocationSubmitView(APIView):
    """
    POST /api/v1/locations/
    User apni current GPS location submit karta hai.
    Private, trusted contacts, ya public link sharing ke saath snapshot banata hai.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = LocationSubmitSerializer(
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)

        ip_address = _get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')

        # Thin view: service call me saara business logic execute hoga
        snapshot = record_location(
            user=request.user,
            validated_data=serializer.validated_data,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        output_serializer = LocationSnapshotSerializer(
            snapshot,
            context={'request': request},
        )
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class SharedLocationView(APIView):
    """
    GET /api/v1/locations/shared/<share_token>/
    Public link ya contact access token ke zariye shared location dekhne ke liye endpoint.
    Expiring tokens aur privacy controls enforce karta hai.
    Login mandatory nahi hai taaki emergency contacts browser link se turant location dekh sakein.
    """
    permission_classes = [AllowAny]

    def get(self, request, share_token, *args, **kwargs):
        ip_address = _get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')

        # Service privacy check, active state, aur expiry verify karti hai
        snapshot = get_shared_location_by_token(
            share_token=share_token,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        # Sirf privacy-safe public fields return kiye jaate hain
        output_serializer = SharedLocationPublicSerializer(snapshot)
        return Response(output_serializer.data, status=status.HTTP_200_OK)


class LocationHistoryView(generics.ListAPIView):
    """
    GET /api/v1/locations/history/
    Authenticated user ki past location snapshots ki paginated list.
    Query filters: ?emergency_event_id=<uuid>&sharing_scope=private/contacts/public_link
    """
    permission_classes = [IsAuthenticated]
    serializer_class = LocationSnapshotSerializer

    def get_queryset(self):
        emergency_id = self.request.query_params.get('emergency_event_id')
        scope = self.request.query_params.get('sharing_scope')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        return get_user_location_history(
            user=self.request.user,
            emergency_event_id=emergency_id,
            start_date=start_date,
            end_date=end_date,
            sharing_scope=scope,
        )
