# User registration, profile serializers

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import UserProfile

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    # Naya user register karne ke liye serializer
    password = serializers.CharField(write_only=True, min_length=8, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['email', 'display_name', 'phone_number', 'password', 'password_confirm', 'preferred_language']

    def validate(self, attrs):
        # Password match check
        if attrs['password'] != attrs.pop('password_confirm'):
            raise serializers.ValidationError({'password_confirm': 'Passwords do not match.'})
        return attrs

    def create(self, validated_data):
        # User create karna with hashed password
        return User.objects.create_user(**validated_data)


class UserProfileSerializer(serializers.ModelSerializer):
    # Profile details dikhane ke liye
    class Meta:
        model = UserProfile
        fields = ['bio', 'profile_picture_url', 'emergency_message']


class UserDetailSerializer(serializers.ModelSerializer):
    # Authenticated user ki full details
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'display_name', 'phone_number', 'role', 'preferred_language',
            'is_guardian_managed', 'profile', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'email', 'role', 'created_at', 'updated_at']


class UserUpdateSerializer(serializers.ModelSerializer):
    # User apni profile update kar sake
    profile = UserProfileSerializer(required=False)

    class Meta:
        model = User
        fields = ['display_name', 'phone_number', 'preferred_language', 'profile']

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})
        # User fields update karo
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        # Profile bhi update karo agar data aaya
        if profile_data:
            profile, _ = UserProfile.objects.get_or_create(user=instance)
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()
        return instance
