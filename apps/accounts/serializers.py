from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from . import models


class PatientSerializer(serializers.ModelSerializer):
    """
    Serializer for patient profile creation and updates.
    
    Automatically associates the profile with the current authenticated user.
    """
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = models.PatientProfile
        fields = [
            "user",
            "date_of_birth",
            "gender",
            "address",
        ]


class DoctorSerializer(serializers.ModelSerializer):
    """
    Serializer for doctor profile creation and updates.
    
    Automatically associates the profile with the current authenticated user.
    """
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = models.DoctorProfile
        fields = [
            "user",
            "specialization",
            "license_number",
            "years_of_experience",
        ]


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user information with their profile data.
    
    Dynamically includes the appropriate profile (patient or doctor) based on
    the user's role.
    """
    profile = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = [
            "pk",
            "first_name",
            "last_name",
            "email",
            "role",
            "profile",
        ]

    def get_profile(self, obj):
        """
        Return the user's profile data based on their role.
        """
        if profile := obj.profile:
            if obj.role == "patient":
                return PatientSerializer(profile, context=self.context).data
            return DoctorSerializer(profile, context=self.context).data


class LoginSerializer(TokenObtainPairSerializer):
    """
    Custom login serializer that returns user data along with JWT tokens.
    
    Extends the default TokenObtainPairSerializer to include full user
    information in the response.
    """
    
    def validate(self, data):
        """
        Validate credentials and return user data with tokens.
        """
        tokens = super().validate(data)
        user_data = UserSerializer(self.user, context=self.context).data
        user_data["tokens"] = tokens
        return user_data


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    
    Handles user creation with password hashing and returns the created
    user data. Password field is write-only for security.
    """
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = get_user_model()
        fields = [
            "pk",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "role",
            "password",
            "tokens",
        ]
        read_only_fields = ["tokens"]

    def create(self, validated_data):
        """
        Create a new user with the validated data.
        """
        return get_user_model().objects.create_user(**validated_data)