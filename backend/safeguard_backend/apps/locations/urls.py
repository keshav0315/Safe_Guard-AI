"""
apps/locations/urls.py
SafeGuard AI — Location URL routing.
Endpoints:
- POST /api/v1/locations/                     -> Submit location snapshot
- GET  /api/v1/locations/shared/<share_token>/ -> View shared location via token
- GET  /api/v1/locations/history/             -> Location history
"""

from django.urls import path
from .views import (
    LocationSubmitView,
    SharedLocationView,
    LocationHistoryView,
)

app_name = 'locations'

urlpatterns = [
    # Nayi location capture submit karne ke liye
    path('', LocationSubmitView.as_view(), name='location-submit'),

    # Shared location link ko access karne ke liye (public/contact access token)
    path('shared/<str:share_token>/', SharedLocationView.as_view(), name='location-shared'),

    # User ki past locations ki history dekhne ke liye
    path('history/', LocationHistoryView.as_view(), name='location-history'),
]
