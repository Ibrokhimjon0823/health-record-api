import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def patient_user(db):
    user = User.objects.create_user(
        email="patient@test.com",
        password="testpass123",
        first_name="John",
        last_name="Doe",
        role="patient",
    )
    return user


@pytest.fixture
def doctor_user(db):
    user = User.objects.create_user(
        email="doctor@test.com",
        password="testpass123",
        first_name="Jane",
        last_name="Smith",
        role="doctor",
    )
    return user


@pytest.fixture
def authenticated_patient_client(api_client, patient_user):
    refresh = RefreshToken.for_user(patient_user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    api_client.user = patient_user
    return api_client


@pytest.fixture
def authenticated_doctor_client(api_client, doctor_user):
    refresh = RefreshToken.for_user(doctor_user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    api_client.user = doctor_user
    return api_client


@pytest.fixture
def patient_profile(patient_user):
    from apps.accounts.models import PatientProfile
    from datetime import date

    return PatientProfile.objects.create(
        user=patient_user,
        date_of_birth=date(1990, 1, 1),
        gender="male",
        address="123 Test Street",
    )


@pytest.fixture
def doctor_profile(doctor_user):
    from apps.accounts.models import DoctorProfile

    return DoctorProfile.objects.create(
        user=doctor_user,
        specialization="General Medicine",
        license_number="DOC12345",
        years_of_experience=10,
    )


@pytest.fixture
def health_record(patient_user, doctor_user):
    from apps.records.models import HealthRecord

    return HealthRecord.objects.create(
        patient=patient_user,
        doctor=doctor_user,
        record_type="consultation",
        description="Test health record",
    )