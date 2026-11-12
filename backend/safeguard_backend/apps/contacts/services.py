# Contact management business logic

from django.db import transaction
from .models import TrustedContact


def get_active_contacts_for_user(user):
    """User ke active trusted contacts fetch karna"""
    return TrustedContact.objects.filter(owner=user, is_active=True).order_by('contact_name')


def create_trusted_contact(user, validated_data):
    """Naya trusted contact create karna"""
    with transaction.atomic():
        contact = TrustedContact.objects.create(owner=user, **validated_data)
    return contact


def deactivate_contact(contact):
    """Contact ko soft delete karna - hard delete se better for audit"""
    contact.is_active = False
    contact.save(update_fields=['is_active', 'updated_at'])
    return contact


def get_contact_by_id_and_owner(contact_id, user):
    """Contact fetch karna with ownership check"""
    try:
        return TrustedContact.objects.get(id=contact_id, owner=user, is_active=True)
    except TrustedContact.DoesNotExist:
        return None
