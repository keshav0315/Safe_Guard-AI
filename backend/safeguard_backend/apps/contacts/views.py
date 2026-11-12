from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import TrustedContact
from .serializers import TrustedContactSerializer, TrustedContactCreateSerializer
from .services import (
    get_active_contacts_for_user,
    create_trusted_contact,
    deactivate_contact,
    get_contact_by_id_and_owner,
)
from .permissions import IsContactOwner


class TrustedContactListCreateView(generics.ListCreateAPIView):
    """
    GET: Apne sare active contacts dekho
    POST: Naya contact add karo
    """
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TrustedContactCreateSerializer
        return TrustedContactSerializer

    def get_queryset(self):
        # Sirf current user ke contacts - no cross-user access
        return get_active_contacts_for_user(self.request.user)

    def perform_create(self, serializer):
        create_trusted_contact(self.request.user, serializer.validated_data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        contact = create_trusted_contact(request.user, serializer.validated_data)
        output = TrustedContactSerializer(contact)
        return Response(output.data, status=status.HTTP_201_CREATED)


class TrustedContactDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Ek specific contact ki details
    PATCH: Contact update karo
    DELETE: Contact deactivate karo (soft delete)
    """
    permission_classes = [IsAuthenticated, IsContactOwner]
    serializer_class = TrustedContactSerializer

    def get_object(self):
        contact = get_contact_by_id_and_owner(self.kwargs['pk'], self.request.user)
        if not contact:
            from rest_framework.exceptions import NotFound
            raise NotFound('Contact not found.')
        self.check_object_permissions(self.request, contact)
        return contact

    def destroy(self, request, *args, **kwargs):
        # Hard delete ki jagah soft delete karo
        contact = self.get_object()
        deactivate_contact(contact)
        return Response({'message': 'Contact deactivated successfully.'}, status=status.HTTP_200_OK)
