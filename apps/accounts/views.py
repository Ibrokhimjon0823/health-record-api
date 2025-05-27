from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions
from rest_framework_simplejwt.views import TokenObtainPairView

from . import permissions as account_permissions
from . import serializers


@extend_schema(tags=["Accounts"])
class LoginView(TokenObtainPairView):
    """
    Authenticate a user and return JWT tokens.
    
    Accepts email and password credentials and returns access/refresh tokens
    along with user information.
    """

    authentication_classes = []
    serializer_class = serializers.LoginSerializer


@extend_schema(tags=["Accounts"])
class RegisterView(generics.CreateAPIView):
    """
    Register a new user in the system.
    
    Creates a new user account with the provided information and returns
    the user data along with authentication tokens. The user can register
    as either a 'patient' or 'doctor' role.
    """

    authentication_classes = []
    serializer_class = serializers.RegisterSerializer


@extend_schema(tags=["Accounts"])
class ProfileCreateView(generics.CreateAPIView):
    """
    Create a profile for the authenticated user.
    
    This endpoint creates either a PatientProfile or DoctorProfile based on
    the user's role. Users must be authenticated and not have an existing
    profile to access this endpoint.
    """

    permission_classes = [
        permissions.IsAuthenticated & account_permissions.NoProfileSet
    ]

    def get_serializer_class(self):
        """
        Return the appropriate serializer based on user role.
        """
        if self.request.user.role == "patient":
            return serializers.PatientSerializer
        return serializers.DoctorSerializer


@extend_schema(tags=["Accounts"])
class ProfileUpdateView(generics.UpdateAPIView):
    """
    Update the authenticated user's profile.
    
    Allows users to update their existing profile information. The profile
    type (Patient or Doctor) is automatically determined based on the user's
    role. Users must have an existing profile to access this endpoint.
    """

    permission_classes = [
        permissions.IsAuthenticated & account_permissions.IsProfileSet
    ]

    def get_serializer_class(self):
        """
        Return the appropriate serializer based on user role.
        """
        if self.request.user.role == "patient":
            return serializers.PatientSerializer
        return serializers.DoctorSerializer

    def get_object(self):
        """
        Return the current user's profile instance.
        """
        return self.request.user.profile


@extend_schema(tags=["Accounts"])
class DoctorListView(generics.ListAPIView):
    """
    List all doctors with completed profiles.
    
    Returns a paginated list of doctors who have completed their profile
    setup. Only accessible by users with the 'patient' role. Includes
    doctor information and their profile details.
    """

    permission_classes = [account_permissions.IsPatient]
    serializer_class = serializers.UserSerializer

    def get_queryset(self):
        """
        Return all doctors with completed profiles.
        """
        return (
            get_user_model()
            .objects.filter(role="doctor", doctor_profile__isnull=False)
            .select_related("doctor_profile")
        )