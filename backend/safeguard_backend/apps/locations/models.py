"""
apps/locations/models.py
SafeGuard AI — Location snapshots aur sharing sessions yahan manage hote hain.
"""
import uuid
from decimal import Decimal
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class LocationSnapshot(models.Model):
    """
    User ki location ka ek snapshot — emergency ke waqt ya manual sharing ke liye.
    Latitude/longitude validated hain — invalid coordinates nahi jaayenge.
    """

    SHARING_SCOPE_CHOICES = [
        ('private', 'Private'),
        ('contacts', 'Trusted Contacts'),
        ('public_link', 'Public Link'),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name='Snapshot ID',
    )

    # Owner — kis user ki location hai yeh
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='location_snapshots',
        db_index=True,
        verbose_name='Owner',
    )

    # Emergency event se link — optional, sirf SOS ke case mein set hoga
    emergency_event = models.ForeignKey(
        'emergencies.EmergencyEvent',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='location_snapshots',
        db_index=True,
        verbose_name='Emergency Event',
    )

    # Latitude — sirf valid values (-90 to 90) allow hain
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        validators=[
            MinValueValidator(Decimal('-90.0'), message='Latitude -90 se kam nahi ho sakti.'),
            MaxValueValidator(Decimal('90.0'), message='Latitude 90 se zyada nahi ho sakti.'),
        ],
        verbose_name='Latitude',
    )

    # Longitude — sirf valid values (-180 to 180) allow hain
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        validators=[
            MinValueValidator(Decimal('-180.0'), message='Longitude -180 se kam nahi ho sakti.'),
            MaxValueValidator(Decimal('180.0'), message='Longitude 180 se zyada nahi ho sakti.'),
        ],
        verbose_name='Longitude',
    )

    # GPS accuracy — optional, meters mein
    accuracy_meters = models.FloatField(
        null=True,
        blank=True,
        verbose_name='Accuracy (meters)',
    )

    altitude_meters = models.FloatField(
        null=True,
        blank=True,
        verbose_name='Altitude (meters)',
    )

    # Jab device ne location capture ki — server time se alag ho sakta hai
    captured_at = models.DateTimeField(verbose_name='Captured At')

    sharing_scope = models.CharField(
        max_length=20,
        choices=SHARING_SCOPE_CHOICES,
        default='private',
        db_index=True,
        verbose_name='Sharing Scope',
    )

    # Public link sharing ke liye unique token — blank by default
    share_token = models.CharField(
        max_length=255,
        unique=True,
        blank=True,
        verbose_name='Share Token',
    )

    # Sharing kab expire hogi — null means never expires
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name='Expires At',
    )

    # Is sharing active hai ya band kar di gayi
    is_sharing_active = models.BooleanField(
        default=True,
        verbose_name='Is Sharing Active',
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Location Snapshot'
        verbose_name_plural = 'Location Snapshots'
        indexes = [
            models.Index(fields=['owner'], name='loc_snapshot_owner_idx'),
            models.Index(fields=['emergency_event'], name='loc_snapshot_emergency_idx'),
            models.Index(fields=['sharing_scope'], name='loc_snapshot_scope_idx'),
            models.Index(fields=['expires_at'], name='loc_snapshot_expires_idx'),
            models.Index(fields=['owner', 'sharing_scope'], name='loc_snapshot_owner_scope_idx'),
        ]

    def __str__(self):
        return f'Location({self.latitude}, {self.longitude}) of {self.owner} @ {self.captured_at}'


class LocationSharingSession(models.Model):
    """
    Ek specific trusted contact ke saath location sharing session.
    Access token se secure access hota hai.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name='Session ID',
    )

    # Kaun sa snapshot share ho raha hai
    location_snapshot = models.ForeignKey(
        LocationSnapshot,
        on_delete=models.CASCADE,
        related_name='sharing_sessions',
        verbose_name='Location Snapshot',
    )

    # Kis contact ke saath share ho raha hai
    shared_with_contact = models.ForeignKey(
        'contacts.TrustedContact',
        on_delete=models.CASCADE,
        related_name='location_sharing_sessions',
        verbose_name='Shared With Contact',
    )

    # Unique access token — sirf isi token se access hoga
    access_token = models.CharField(
        max_length=255,
        unique=True,
        verbose_name='Access Token',
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')

    # Session kab expire hoga
    expires_at = models.DateTimeField(verbose_name='Expires At')

    is_active = models.BooleanField(default=True, verbose_name='Is Active')

    # Jab last time contact ne location access ki
    last_accessed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Last Accessed At',
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Location Sharing Session'
        verbose_name_plural = 'Location Sharing Sessions'
        indexes = [
            models.Index(fields=['location_snapshot'], name='loc_session_snapshot_idx'),
            models.Index(fields=['shared_with_contact'], name='loc_session_contact_idx'),
            models.Index(fields=['expires_at'], name='loc_session_expires_idx'),
        ]

    def __str__(self):
        return f'SharingSession for {self.shared_with_contact} — expires {self.expires_at}'
