"""
apps/locations/serializers.py
SafeGuard AI — Location tracking, snapshot, aur secure sharing serializers.
Privacy controls aur expiring share token validation yahan hoti hai.
"""

from django.utils import timezone
from rest_framework import serializers

from .models import LocationSnapshot, LocationSharingSession
from apps.emergencies.models import EmergencyEvent
from apps.contacts.models import TrustedContact
from common.validators.location_validators import (
    validate_latitude,
    validate_longitude,
    validate_accuracy,
)


class LocationSubmitSerializer(serializers.Serializer):
    """
    User device se current GPS coordinates submit karne ke liye serializer.
    """
    latitude = serializers.DecimalField(
        max_digits=9,
        decimal_places=6,
        required=True,
        validators=[validate_latitude],
        help_text="Latitude (-90 to 90).",
    )

    longitude = serializers.DecimalField(
        max_digits=9,
        decimal_places=6,
        required=True,
        validators=[validate_longitude],
        help_text="Longitude (-180 to 180).",
    )

    accuracy_meters = serializers.FloatField(
        required=False,
        allow_null=True,
        validators=[validate_accuracy],
        help_text="GPS accuracy in meters.",
    )

    altitude_meters = serializers.FloatField(
        required=False,
        allow_null=True,
        help_text="Altitude in meters.",
    )

    captured_at = serializers.DateTimeField(
        required=False,
        allow_null=True,
        help_text="Device par capture hone ka samay (defaults to now).",
    )

    sharing_scope = serializers.ChoiceField(
        choices=LocationSnapshot.SHARING_SCOPE_CHOICES,
        default='private',
        help_text="Sharing scope: private, contacts, ya public_link.",
    )

    emergency_event_id = serializers.UUIDField(
        required=False,
        allow_null=True,
        help_text="Agar emergency event se link karna ho to event ka UUID.",
    )

    expires_in_minutes = serializers.IntegerField(
        required=False,
        default=60,
        min_value=1,
        max_value=10080,  # 7 days max
        help_text="Location sharing kitne minutes tak valid rahegi (default 60 mins).",
    )

    shared_with_contact_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        default=list,
        help_text="Contacts ke UUIDs jinhe yeh location specific access token ke saath share karni hai.",
    )

    def validate_emergency_event_id(self, value):
        if value is None:
            return value
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if user and user.is_authenticated:
            # Check karte hain ki emergency event user ka hi hai
            exists = EmergencyEvent.objects.filter(id=value, owner=user).exists()
            if not exists:
                raise serializers.ValidationError(
                    "Emergency event nahi mila ya access permitted nahi hai."
                )
        return value

    def validate_shared_with_contact_ids(self, value):
        if not value:
            return value
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if user and user.is_authenticated:
            # Check karte hain ki saare contacts current user ke active contacts hain
            valid_count = TrustedContact.objects.filter(
                id__in=value,
                owner=user,
                is_active=True,
            ).count()
            if valid_count != len(set(value)):
                raise serializers.ValidationError(
                    "Ek ya zyada trusted contacts invalid hain ya aapke account se linked nahi hain."
                )
        return value


class LocationSharingSessionSerializer(serializers.ModelSerializer):
    """
    Specific contact ke saath bani sharing session details.
    """
    shared_with_contact_id = serializers.UUIDField(
        source='shared_with_contact.id',
        read_only=True,
    )
    shared_with_contact_name = serializers.CharField(
        source='shared_with_contact.contact_name',
        read_only=True,
    )

    class Meta:
        model = LocationSharingSession
        fields = [
            'id',
            'shared_with_contact_id',
            'shared_with_contact_name',
            'access_token',
            'expires_at',
            'is_active',
            'last_accessed_at',
            'created_at',
        ]
        read_only_fields = fields


class LocationSnapshotSerializer(serializers.ModelSerializer):
    """
    Full details serializer for LocationSnapshot — owner view ke liye.
    """
    owner_id = serializers.UUIDField(source='owner.id', read_only=True)
    emergency_event_id = serializers.UUIDField(
        source='emergency_event.id',
        read_only=True,
        allow_null=True,
    )
    share_url = serializers.SerializerMethodField()
    is_expired = serializers.SerializerMethodField()
    sharing_sessions = LocationSharingSessionSerializer(many=True, read_only=True)

    class Meta:
        model = LocationSnapshot
        fields = [
            'id',
            'owner_id',
            'emergency_event_id',
            'latitude',
            'longitude',
            'accuracy_meters',
            'altitude_meters',
            'captured_at',
            'sharing_scope',
            'share_token',
            'share_url',
            'expires_at',
            'is_sharing_active',
            'is_expired',
            'sharing_sessions',
            'created_at',
        ]
        read_only_fields = [
            'id',
            'owner_id',
            'emergency_event_id',
            'share_token',
            'share_url',
            'is_expired',
            'created_at',
        ]

    def get_share_url(self, obj):
        # Public / shared link generate karte hain
        if not obj.share_token or not obj.is_sharing_active:
            return None
        request = self.context.get('request')
        path = f"/api/v1/locations/shared/{obj.share_token}/"
        if request:
            return request.build_absolute_uri(path)
        return path

    def get_is_expired(self, obj):
        if obj.expires_at:
            return obj.expires_at < timezone.now()
        return False


class SharedLocationPublicSerializer(serializers.Serializer):
    """
    Privacy-friendly serializer for public link / contact access via share token.
    IMPORTANT: Koi passwords, email, phone numbers ya sensitive PII expose nahi hota.
    """
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    accuracy_meters = serializers.FloatField(allow_null=True)
    altitude_meters = serializers.FloatField(allow_null=True)
    captured_at = serializers.DateTimeField()
    expires_at = serializers.DateTimeField(allow_null=True)
    is_sharing_active = serializers.BooleanField()
    owner_display_name = serializers.SerializerMethodField()
    emergency_active = serializers.SerializerMethodField()

    def get_owner_display_name(self, obj):
        # Sirf user ka display name reveal hota hai
        return obj.owner.display_name if hasattr(obj, 'owner') and obj.owner else "SafeGuard User"

    def get_emergency_active(self, obj):
        # Agar emergency event linked hai to kya abhi bhi active hai
        if obj.emergency_event:
            return obj.emergency_event.status == 'active'
        return False
