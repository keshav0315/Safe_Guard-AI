"""
apps/ai_detection/views.py
SafeGuard AI — AI Detection & Threat Inference API Views
Sensor threat detection inference endpoints aur AI model registry listing.
"""

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

from .models import AIModelRegistry, AIInferenceRecord
from .serializers import (
    AIModelRegistrySerializer,
    AIInferenceRequestSerializer,
    AIInferenceResponseSerializer,
    AIInferenceRecordSerializer,
)
from .services import (
    run_advisory_inference,
    get_active_models,
    get_user_inference_history,
)


@extend_schema(
    tags=['AI Detection'],
    summary='AI Threat Detection Inference Run Karo',
    description=(
        'Sensor telemetry evaluate karke potential threats ya anomalies check karta hai. '
        'IMPORTANT: AI results sirf advisory hain, automatic SOS trigger nahi hona chahiye.'
    ),
    request=AIInferenceRequestSerializer,
    responses={
        200: AIInferenceResponseSerializer,
    },
)
class AIInferenceView(APIView):
    """
    POST /api/v1/ai/inference/
    # AI results sirf advisory hain, automatic SOS trigger nahi hona chahiye
    Sensor data evaluate karta hai aur advisory result return karta hai.

    GET /api/v1/ai/inference/
    User ki past inference records history return karta hai.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """User ki historical inference history fetch karo"""
        signal_type = request.query_params.get('signal_type')
        records = get_user_inference_history(request.user, signal_type=signal_type)
        serializer = AIInferenceRecordSerializer(records, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """Advisory sensor inference execute karo"""
        serializer = AIInferenceRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        signal_type = serializer.validated_data['signal_type']
        sensor_data = serializer.validated_data['sensor_data']
        user_consent = serializer.validated_data['user_consent']
        model_id = serializer.validated_data.get('model_id')

        # Advisory inference evaluate karo
        result = run_advisory_inference(
            user=request.user,
            signal_type=signal_type,
            sensor_data=sensor_data,
            model_id=str(model_id) if model_id else None,
            consent_given=user_consent,
            request=request,
        )

        response_serializer = AIInferenceResponseSerializer(result)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    tags=['AI Detection'],
    summary='Available AI Models List Karo',
    description='Registry se active threat detection AI models, schemas aur known limitations fetch karta hai.',
    parameters=[
        OpenApiParameter(
            'signal_type',
            OpenApiTypes.STR,
            description='Filter models by signal type (movement, audio, sensor_fusion, etc.)',
            required=False,
        ),
    ],
    responses={200: AIModelRegistrySerializer(many=True)},
)
class AIModelRegistryListView(generics.ListAPIView):
    """
    GET /api/v1/ai/models/
    Registered AI models aur unki limitations dekhne ke liye endpoint.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = AIModelRegistrySerializer

    def get_queryset(self):
        signal_type = self.request.query_params.get('signal_type')
        return get_active_models(signal_type=signal_type)
