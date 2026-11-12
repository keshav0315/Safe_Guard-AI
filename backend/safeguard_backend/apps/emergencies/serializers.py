"""
apps/emergencies/serializers.py
SafeGuard AI — Emergency events aur SOS alerts ke serializers yahan hain.
Data validation, coordinate checks, aur response structuring ke liye.
"""

from rest_framework import serializers
from .models import EmergencyEvent
from apps.locations.models import LocationSnapshot
from apps.notifications.models import NotificationDelivery
from common.validators.location_validators import (
    validate_latitude,
    validate_longitude,
    validate_accuracy,
)


class SOSCreateSerializer(serializers.Serializer):
    """
    User jab emergency me SOS trigger karta hai, tab yeh serializer data validate karta hai.
    SOS request fast aur robust honi chahiye.
    """

    # Idempotency key se duplicate SOS alerts prevent hote hain
    idempotency_key = serializers.CharField(
        max_length=255,
        required=True,
        help_text="Unique client request ID taaki accidental double-tap par duplicate alert na bane.",
    )

    event_type = serializers.ChoiceField(
        choices=EmergencyEvent.EVENT_TYPE_CHOICES,
        default='sos',
        help_text="Alert type: sos, panic, ya test.",
    )

    notes = serializers.CharField(
        required=False,
        allow_blank=True,
        default='',
        help_text="Optional description ya situation details.",
    )

    # Optional initial GPS coordinates
    latitude = serializers.DecimalField(
        max_digits=9,
        decimal_places=6,
        required=False,
        allow_null=True,
        validators=[validate_latitude],
        help_text="Current latitude (-90 to 90).",
    )

    longitude = serializers.DecimalField(
        max_digits=9,
        decimal_places=6,
        required=False,
        allow_null=True,
        validators=[validate_longitude],
        help_text="Current longitude (-180 to 180).",
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
        help_text="Device par location capture hone ka timestamp.",
    )

    def validate(self, attrs):
        # Coordinates validation: agar ek coordinate diya hai to dusra bhi mandatory hai
        lat = attrs.get('latitude')
        lng = attrs.get('longitude')
        if (lat is not None and lng is None) or (lat is None and lng is not None):
            raise serializers.ValidationError(
                "Latitude aur Longitude dono ek saath provide karna zaroori hai."
            )
        return attrs


class EmergencyEventActionSerializer(serializers.Serializer):
    """
    Emergency cancel ya resolve karte waqt optional notes provide karne ke liye.
    """
    notes = serializers.CharField(
        required=False,
        allow_blank=True,
        default='',
        help_text="Cancellation ya resolution reason/note.",
    )


class LocationSummarySerializer(serializers.ModelSerializer):
    """
    Emergency ke saath latest location snapshot ka brief summary.
    """
    class Meta:
        model = LocationSnapshot
        fields = [
            'id',
            'latitude',
            'longitude',
            'accuracy_meters',
            'captured_at',
            'share_token',
        ]


class NotificationDeliverySummarySerializer(serializers.ModelSerializer):
    """
    Contacts ko bheje gaye notification alerts ka summary.
    """
    recipient_name = serializers.CharField(
        source='recipient_contact.contact_name',
        read_only=True,
    )
    recipient_phone = serializers.CharField(
        source='recipient_contact.phone_number',
        read_only=True,
    )

    class Meta:
        model = NotificationDelivery
        fields = [
            'id',
            'recipient_name',
            'recipient_phone',
            'status',
            'attempted_at',
            'delivered_at',
            'retry_count',
        ]


class EmergencyEventSerializer(serializers.ModelSerializer):
    """
    Standard Emergency Event response serializer.
    """
    owner_id = serializers.UUIDField(source='owner.id', read_only=True)
    owner_name = serializers.CharField(source='owner.display_name', read_only=True)
    latest_location = serializers.SerializerMethodField()
    notifications_count = serializers.SerializerMethodField()

    class Meta:
        model = EmergencyEvent
        fields = [
            'id',
            'owner_id',
            'owner_name',
            'event_type',
            'status',
            'idempotency_key',
            'notes',
            'created_at',
            'acknowledged_at',
            'cancelled_at',
            'resolved_at',
            'updated_at',
            'latest_location',
            'notifications_count',
        ]
        read_only_fields = [
            'id',
            'owner_id',
            'owner_name',
            'status',
            'created_at',
            'acknowledged_at',
            'cancelled_at',
            'resolved_at',
            'updated_at',
        ]

    def get_latest_location(self, obj):
        # Emergency ke latest location snapshot ki details fetch karte hain
        latest_loc = obj.location_snapshots.order_by('-captured_at', '-created_at').first()
        if latest_loc:
            return LocationSummarySerializer(latest_loc).data
        return None

    def get_notifications_count(self, obj):
        # Kitne trusted contacts ko alerts deliver hue ya pending hain
        return obj.notification_deliveries.count()


class EmergencyDetailSerializer(EmergencyEventSerializer):
    """
    Detailed Emergency Event response serializer — with full location history
    and notification delivery status list.
    """
    location_history = serializers.SerializerMethodField()
    notifications = NotificationDeliverySummarySerializer(
        source='notification_deliveries',
        many=True,
        read_only=True,
    )

    class Meta(EmergencyEventSerializer.Meta):
        fields = EmergencyEventSerializer.Meta.fields + [
            'location_history',
            'notifications',
        ]

    def get_location_history(self, obj):
        snapshots = obj.location_snapshots.order_by('-captured_at', '-created_at')[:20]
        return LocationSummarySerializer(snapshots, many=True).data
