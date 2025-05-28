import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from datetime import date

from apps.accounts.models import PatientProfile, DoctorProfile, Role

User = get_user_model()


@pytest.mark.django_db
class TestLoginView:
    def test_login_success(self, api_client, patient_user):
        url = reverse("accounts:login")
        data = {
            "email": "patient@test.com",
            "password": "testpass123",
        }
        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert "tokens" in response.data
        assert "access" in response.data["tokens"]
        assert "refresh" in response.data["tokens"]
        assert response.data["email"] == patient_user.email

    def test_login_invalid_credentials(self, api_client):
        url = reverse("accounts:login")
        data = {
            "email": "wrong@test.com",
            "password": "wrongpass",
        }
        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_missing_fields(self, api_client):
        url = reverse("accounts:login")
        data = {"email": "test@test.com"}
        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestRegisterView:
    def test_register_patient_success(self, api_client):
        url = reverse("accounts:register")
        data = {
            "email": "newpatient@test.com",
            "password": "newpass123",
            "first_name": "New",
            "last_name": "Patient",
            "role": "patient",
        }
        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert "tokens" in response.data
        assert "access" in response.data["tokens"]
        assert "refresh" in response.data["tokens"]
        
        user = User.objects.get(email="newpatient@test.com")
        assert user.role == Role.PATIENT
        assert user.first_name == "New"
        assert user.last_name == "Patient"

    def test_register_doctor_success(self, api_client):
        url = reverse("accounts:register")
        data = {
            "email": "newdoctor@test.com",
            "password": "newpass123",
            "first_name": "New",
            "last_name": "Doctor",
            "role": "doctor",
        }
        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["role"] == "doctor"

    def test_register_duplicate_email(self, api_client, patient_user):
        url = reverse("accounts:register")
        data = {
            "email": patient_user.email,
            "password": "newpass123",
            "first_name": "Duplicate",
            "last_name": "User",
            "role": "patient",
        }
        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_invalid_role(self, api_client):
        url = reverse("accounts:register")
        data = {
            "email": "invalid@test.com",
            "password": "pass123",
            "first_name": "Invalid",
            "last_name": "Role",
            "role": "admin",
        }
        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestProfileCreateView:
    def test_create_patient_profile_success(self, authenticated_patient_client):
        url = reverse("accounts:profile-create")
        data = {
            "date_of_birth": "1990-01-01",
            "gender": "male",
            "address": "123 Test Street",
        }
        response = authenticated_patient_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        
        profile = PatientProfile.objects.get(user=authenticated_patient_client.user)
        assert profile.gender == "male"
        assert profile.address == "123 Test Street"

    def test_create_doctor_profile_success(self, authenticated_doctor_client):
        url = reverse("accounts:profile-create")
        data = {
            "specialization": "Cardiology",
            "license_number": "CARD12345",
            "years_of_experience": 10,
        }
        response = authenticated_doctor_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        
        profile = DoctorProfile.objects.get(user=authenticated_doctor_client.user)
        assert profile.specialization == "Cardiology"
        assert profile.license_number == "CARD12345"

    def test_create_profile_already_exists(self, authenticated_patient_client, patient_profile):
        url = reverse("accounts:profile-create")
        data = {
            "date_of_birth": "1995-01-01",
            "gender": "female",
            "address": "456 New Street",
        }
        response = authenticated_patient_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_profile_unauthenticated(self, api_client):
        url = reverse("accounts:profile-create")
        data = {
            "date_of_birth": "1990-01-01",
            "gender": "male",
            "address": "123 Test Street",
        }
        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestProfileUpdateView:
    def test_update_patient_profile_success(self, authenticated_patient_client, patient_profile):
        url = reverse("accounts:profile-update")
        data = {
            "date_of_birth": "1990-01-01",
            "gender": "female",
            "address": "789 Updated Street",
        }
        response = authenticated_patient_client.patch(url, data, format="json")
        assert response.status_code == status.HTTP_200_OK
        
        patient_profile.refresh_from_db()
        assert patient_profile.gender == "female"
        assert patient_profile.address == "789 Updated Street"

    def test_update_doctor_profile_success(self, authenticated_doctor_client, doctor_profile):
        url = reverse("accounts:profile-update")
        data = {
            "specialization": "Neurology",
            "years_of_experience": 15,
        }
        response = authenticated_doctor_client.patch(url, data, format="json")
        assert response.status_code == status.HTTP_200_OK
        
        doctor_profile.refresh_from_db()
        assert doctor_profile.specialization == "Neurology"
        assert doctor_profile.years_of_experience == 15

    def test_update_profile_no_profile(self, authenticated_patient_client):
        url = reverse("accounts:profile-update")
        data = {
            "gender": "male",
            "address": "123 Street",
        }
        response = authenticated_patient_client.patch(url, data, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestDoctorListView:
    def test_list_doctors_as_patient(self, authenticated_patient_client, patient_profile, doctor_user, doctor_profile):
        url = reverse("accounts:doctor-list")
        response = authenticated_patient_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["email"] == doctor_user.email

    def test_list_doctors_excludes_without_profile(self, authenticated_patient_client, patient_profile):
        User.objects.create_user(
            email="noprofile@doctor.com",
            password="pass123",
            first_name="No",
            last_name="Profile",
            role=Role.DOCTOR,
        )
        url = reverse("accounts:doctor-list")
        response = authenticated_patient_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0

    def test_list_doctors_as_doctor_forbidden(self, authenticated_doctor_client):
        url = reverse("accounts:doctor-list")
        response = authenticated_doctor_client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_list_doctors_unauthenticated(self, api_client):
        url = reverse("accounts:doctor-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED