# Location data validation helpers

from rest_framework import serializers

def validate_latitude(value):
    """Latitude valid range check: -90 to 90"""
    if value is not None and not (-90 <= float(value) <= 90):
        raise serializers.ValidationError('Latitude must be between -90 and 90 degrees.')
    return value

def validate_longitude(value):
    """Longitude valid range check: -180 to 180"""
    if value is not None and not (-180 <= float(value) <= 180):
        raise serializers.ValidationError('Longitude must be between -180 and 180 degrees.')
    return value

def validate_accuracy(value):
    """GPS accuracy negative nahi ho sakti"""
    if value is not None and float(value) < 0:
        raise serializers.ValidationError('Accuracy cannot be negative.')
    return value
