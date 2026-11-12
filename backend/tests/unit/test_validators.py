"""
Unit tests for SafeGuard AI location validators.
Testing latitude, longitude, and accuracy validation functions.
"""

import pytest
from rest_framework import serializers
from common.validators.location_validators import (
    validate_latitude,
    validate_longitude,
    validate_accuracy,
)


class TestLocationValidators:
    """Test suite for GPS coordinate and accuracy validation logic."""

    def test_valid_latitude(self):
        """Valid latitudes between -90 and 90 should pass unchanged."""
        assert validate_latitude(0.0) == 0.0
        assert validate_latitude(28.6139) == 28.6139
        assert validate_latitude(-33.8688) == -33.8688
        assert validate_latitude(90.0) == 90.0
        assert validate_latitude(-90.0) == -90.0
        assert validate_latitude(None) is None

    @pytest.mark.parametrize("invalid_lat", [90.0001, -90.0001, 91, -91, 180, -180])
    def test_invalid_latitude_raises_validation_error(self, invalid_lat):
        """Latitudes outside [-90, 90] must raise serializers.ValidationError."""
        with pytest.raises(serializers.ValidationError) as excinfo:
            validate_latitude(invalid_lat)
        assert "Latitude must be between -90 and 90 degrees." in str(excinfo.value)

    def test_valid_longitude(self):
        """Valid longitudes between -180 and 180 should pass unchanged."""
        assert validate_longitude(0.0) == 0.0
        assert validate_longitude(77.2090) == 77.2090
        assert validate_longitude(-122.4194) == -122.4194
        assert validate_longitude(180.0) == 180.0
        assert validate_longitude(-180.0) == -180.0
        assert validate_longitude(None) is None

    @pytest.mark.parametrize("invalid_lng", [180.0001, -180.0001, 181, -181, 360, -360])
    def test_invalid_longitude_raises_validation_error(self, invalid_lng):
        """Longitudes outside [-180, 180] must raise serializers.ValidationError."""
        with pytest.raises(serializers.ValidationError) as excinfo:
            validate_longitude(invalid_lng)
        assert "Longitude must be between -180 and 180 degrees." in str(excinfo.value)

    def test_valid_accuracy(self):
        """Non-negative GPS accuracy values in meters should pass."""
        assert validate_accuracy(0.0) == 0.0
        assert validate_accuracy(5.25) == 5.25
        assert validate_accuracy(100.0) == 100.0
        assert validate_accuracy(None) is None

    @pytest.mark.parametrize("invalid_acc", [-0.01, -1.0, -50.0])
    def test_invalid_accuracy_raises_validation_error(self, invalid_acc):
        """Negative GPS accuracy must raise serializers.ValidationError."""
        with pytest.raises(serializers.ValidationError) as excinfo:
            validate_accuracy(invalid_acc)
        assert "Accuracy cannot be negative." in str(excinfo.value)
