"""
apps/ai_detection/urls.py
SafeGuard AI — AI Detection URL Routing
Mounted at /api/v1/ai/
Endpoints:
- POST/GET /api/v1/ai/inference/
- GET      /api/v1/ai/models/
"""

from django.urls import path
from .views import AIInferenceView, AIModelRegistryListView

app_name = 'ai_detection'

urlpatterns = [
    # AI Threat detection advisory inference endpoint
    path('inference/', AIInferenceView.as_view(), name='ai-inference'),

    # Registered AI models listing endpoint
    path('models/', AIModelRegistryListView.as_view(), name='ai-models'),
]
