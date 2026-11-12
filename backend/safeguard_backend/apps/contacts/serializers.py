from rest_framework import serializers
from .models import TrustedContact


class TrustedContactSerializer(serializers.ModelSerializer):
    # Trusted contact ki details
    class Meta:
        model = TrustedContact
        fields = [
            'id', 'contact_name', 'phone_number', 'email', 'relationship_label',
            'verification_status', 'consent_status', 'is_active', 'notes', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'verification_status', 'consent_status', 'created_at', 'updated_at']

    def validate(self, attrs):
        # Phone ya email mein se koi ek zaroori hai
        if not attrs.get('phone_number') and not attrs.get('email'):
            raise serializers.ValidationError('Either phone_number or email is required.')
        return attrs


class TrustedContactCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrustedContact
        fields = ['contact_name', 'phone_number', 'email', 'relationship_label', 'notes']

    def validate(self, attrs):
        if not attrs.get('phone_number') and not attrs.get('email'):
            raise serializers.ValidationError('Either phone_number or email is required.')
        return attrs
