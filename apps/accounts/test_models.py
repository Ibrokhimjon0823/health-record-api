from datetime import date

import pytest
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError

from apps.accounts.models import DoctorProfile, Gender, PatientProfile, Role

User = get_user_model()


@pytest.mark.django_db
class TestUserModel:
    def test_create_user_with_email(self):
        user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
            role=Role.PATIENT,
        )
        assert user.email == "test@example.com"
        assert user.check_password("testpass123")
        assert user.role == Role.PATIENT
        assert user.is_active
        assert not user.is_staff
        assert not user.is_superuser

    def test_create_superuser(self):
        admin = User.objects.create_superuser(
            email="admin@example.com",
            password="adminpass123",
            first_name="Admin",
            last_name="User",
            role=Role.DOCTOR,
        )
        assert admin.is_staff
        assert admin.is_superuser

    def test_email_unique_constraint(self):
        User.objects.create_user(
            email="unique@example.com",
            password="pass123",
            first_name="First",
            last_name="User",
            role=Role.PATIENT,
        )
        with pytest.raises(IntegrityError):
            User.objects.create_user(
                email="unique@example.com",
                password="pass456",
                first_name="Second",
                last_name="User",
                role=Role.DOCTOR,
            )

    def test_user_str_representation(self):
        user = User.objects.create_user(
            email="str@example.com",
            password="pass123",
            first_name="String",
            last_name="Test",
            role=Role.DOCTOR,
        )
        assert str(user) == "str@example.com (doctor)"

    def test_get_full_name(self):
        user = User.objects.create_user(
            email="fullname@example.com",
            password="pass123",
            first_name="John",
            last_name="Doe",
            role=Role.PATIENT,
        )
        assert user.get_full_name() == "John Doe"

    def test_user_tokens_property(self):
        user = User.objects.create_user(
            email="tokens@example.com",
            password="pass123",
            first_name="Token",
            last_name="Test",
            role=Role.PATIENT,
        )
        tokens = user.tokens
        assert "access" in tokens
        assert "refresh" in tokens
        assert isinstance(tokens["access"], str)
        assert isinstance(tokens["refresh"], str)

    def test_profile_property_patient(self, patient_user, patient_profile):
        assert patient_user.profile == patient_profile

    def test_profile_property_doctor(self, doctor_user, doctor_profile):
        assert doctor_user.profile == doctor_profile

    def test_profile_property_none(self):
        user = User.objects.create_user(
            email="noprofile@example.com",
            password="pass123",
            first_name="No",
            last_name="Profile",
            role=Role.PATIENT,
        )
        assert user.profile is None


@pytest.mark.django_db
class TestPatientProfile:
    def test_create_patient_profile(self, patient_user):
        profile = PatientProfile.objects.create(
            user=patient_user,
            date_of_birth=date(1985, 5, 15),
            gender=Gender.FEMALE,
            address="456 Medical Ave",
        )
        assert profile.user == patient_user
        assert profile.date_of_birth == date(1985, 5, 15)
        assert profile.gender == Gender.FEMALE
        assert profile.address == "456 Medical Ave"

    def test_patient_profile_str(self, patient_user):
        profile = PatientProfile.objects.create(
            user=patient_user,
            date_of_birth=date(1990, 1, 1),
            gender=Gender.MALE,
        )
        assert str(profile) == f"Profile of {patient_user.email}"

    def test_patient_profile_one_to_one(self, patient_user):
        PatientProfile.objects.create(
            user=patient_user,
            date_of_birth=date(1990, 1, 1),
            gender=Gender.OTHER,
        )
        with pytest.raises(IntegrityError):
            PatientProfile.objects.create(
                user=patient_user,
                date_of_birth=date(1995, 1, 1),
                gender=Gender.MALE,
            )

    def test_patient_profile_requires_patient_role(self, doctor_user):
        profile = PatientProfile.objects.create(
            user=doctor_user,
            date_of_birth=date(1990, 1, 1),
            gender=Gender.MALE,
        )
        assert profile.user.role == Role.DOCTOR


@pytest.mark.django_db
class TestDoctorProfile:
    def test_create_doctor_profile(self, doctor_user):
        profile = DoctorProfile.objects.create(
            user=doctor_user,
            specialization="Cardiology",
            license_number="DOC98765",
            years_of_experience=15,
        )
        assert profile.user == doctor_user
        assert profile.specialization == "Cardiology"
        assert profile.license_number == "DOC98765"
        assert profile.years_of_experience == 15

    def test_doctor_profile_str(self, doctor_user):
        profile = DoctorProfile.objects.create(
            user=doctor_user,
            specialization="Pediatrics",
            license_number="DOC11111",
            years_of_experience=5,
        )
        assert str(profile) == f"Profile of Dr. {doctor_user.last_name}"

    def test_doctor_profile_one_to_one(self, doctor_user):
        DoctorProfile.objects.create(
            user=doctor_user,
            specialization="Surgery",
            license_number="DOC22222",
            years_of_experience=20,
        )
        with pytest.raises(IntegrityError):
            DoctorProfile.objects.create(
                user=doctor_user,
                specialization="Neurology",
                license_number="DOC33333",
                years_of_experience=10,
            )

    def test_doctor_profile_requires_doctor_role(self, patient_user):
        profile = DoctorProfile.objects.create(
            user=patient_user,
            specialization="General Medicine",
            license_number="DOC44444",
            years_of_experience=8,
        )
        assert profile.user.role == Role.PATIENT
