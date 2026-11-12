"""
apps/contacts/urls.py
SafeGuard AI — Trusted Contacts URL Routing
Endpoints:
- GET/POST  /api/v1/contacts/        -> List user contacts or create new contact
- GET/PATCH/DELETE /api/v1/contacts/<pk>/ -> Retrieve, update or deactivate contact
"""

from django.urls import path
from .views import TrustedContactListCreateView, TrustedContactDetailView

app_name = 'contacts'

urlpatterns = [
    # Saare contacts dekhne aur naya contact register karne ke liye
    path('', TrustedContactListCreateView.as_view(), name='contact-list-create'),

    # Kisi specific contact ki details dekhne, update karne ya soft-delete karne ke liye
    path('<uuid:pk>/', TrustedContactDetailView.as_view(), name='contact-detail'),
]
