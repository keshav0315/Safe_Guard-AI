"""
apps/emergencies/views.py
SafeGuard AI — Emergency API views.
Thin views pattern: Serializer validation -> Service execution -> HTTP Response.
Business logic aur transactions services.py me hain.
"""

from rest_framework import generics, status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    SOSCreateSerializer,
    EmergencyEventSerializer,
    EmergencyDetailSerializer,
    EmergencyEventActionSerializer,
)
from .services import (
    trigger_sos,
    cancel_emergency,
    resolve_emergency,
    get_user_emergencies,
    get_emergency_by_id_and_owner,
)


def _get_client_ip(request):
    """Client request se remote IP extract karne ka utility helper"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


class SOSCreateView(APIView):
    """
    POST /api/v1/emergencies/sos/
    User emergency button dabate hi yahan SOS alert trigger hota hai.
    Idempotent endpoint hai: agar same request repeat hoti hai to duplicate alert nahi banta.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Request data serializer validate karega
        serializer = SOSCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ip_address = _get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')

        # Thin view: service call me saara business logic execute hoga
        event, is_created = trigger_sos(
            user=request.user,
            validated_data=serializer.validated_data,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        output_serializer = EmergencyEventSerializer(event)
        # Naya event bana to 201 Created, duplicate idempotent trigger par 200 OK
        status_code = status.HTTP_201_CREATED if is_created else status.HTTP_200_OK
        return Response(output_serializer.data, status=status_code)


class EmergencyHistoryView(generics.ListAPIView):
    """
    GET /api/v1/emergencies/
    User ke saare past emergency events ki paginated list return karta hai.
    Optional query params: ?status=active/resolved/cancelled & ?event_type=sos/panic/test
    """
    permission_classes = [IsAuthenticated]
    serializer_class = EmergencyEventSerializer

    def get_queryset(self):
        status_param = self.request.query_params.get('status')
        event_type_param = self.request.query_params.get('event_type')
        return get_user_emergencies(
            user=self.request.user,
            status_filter=status_param,
            event_type_filter=event_type_param,
        )


class EmergencyDetailView(generics.RetrieveAPIView):
    """
    GET /api/v1/emergencies/<event_id>/
    Ek specific emergency event ki poori details (location history + notification deliveries) fetch karna.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = EmergencyDetailSerializer

    def get_object(self):
        event_id = self.kwargs.get('event_id')
        event = get_emergency_by_id_and_owner(event_id, self.request.user)
        if not event:
            raise NotFound("Emergency event nahi mila ya access permitted nahi hai.")
        return event


class EmergencyCancelView(APIView):
    """
    POST /api/v1/emergencies/<event_id>/cancel/
    Active emergency ko user dwara cancel karne ke liye.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, event_id, *args, **kwargs):
        event = get_emergency_by_id_and_owner(event_id, request.user)
        if not event:
            raise NotFound("Emergency event nahi mila ya access permitted nahi hai.")

        action_serializer = EmergencyEventActionSerializer(data=request.data)
        action_serializer.is_valid(raise_exception=True)
        notes = action_serializer.validated_data.get('notes', '')

        ip_address = _get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')

        # Service me status transition aur location sharing stop ki jaati hai
        updated_event = cancel_emergency(
            event=event,
            user=request.user,
            notes=notes,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        output_serializer = EmergencyEventSerializer(updated_event)
        return Response(output_serializer.data, status=status.HTTP_200_OK)


class EmergencyResolveView(APIView):
    """
    POST /api/v1/emergencies/<event_id>/resolve/
    Emergency ko safaltapoorvak resolve mark karne ke liye.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, event_id, *args, **kwargs):
        event = get_emergency_by_id_and_owner(event_id, request.user)
        if not event:
            raise NotFound("Emergency event nahi mila ya access permitted nahi hai.")

        action_serializer = EmergencyEventActionSerializer(data=request.data)
        action_serializer.is_valid(raise_exception=True)
        notes = action_serializer.validated_data.get('notes', '')

        ip_address = _get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')

        # Service me status resolved set karke audit log record hota hai
        updated_event = resolve_emergency(
            event=event,
            user=request.user,
            notes=notes,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        output_serializer = EmergencyEventSerializer(updated_event)
        return Response(output_serializer.data, status=status.HTTP_200_OK)
