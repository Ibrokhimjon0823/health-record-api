import pytest
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status

from apps.records.models import HealthRecord, HealthRecordFile, DoctorAnnotation, RecordType


@pytest.mark.django_db
class TestPatientHealthRecordListCreateView:
    def test_list_patient_records(self, authenticated_patient_client, health_record):
        url = reverse("records:patient-record-list")
        response = authenticated_patient_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["id"] == str(health_record.id)

    def test_list_only_own_records(self, authenticated_patient_client, patient_user, doctor_user):
        other_patient = patient_user.__class__.objects.create_user(
            email="other@patient.com",
            password="pass123",
            first_name="Other",
            last_name="Patient",
            role="patient",
        )
        HealthRecord.objects.create(
            patient=other_patient,
            doctor=doctor_user,
            record_type=RecordType.CONSULTATION,
        )
        own_record = HealthRecord.objects.create(
            patient=patient_user,
            doctor=doctor_user,
            record_type=RecordType.LAB_RESULT,
        )
        
        url = reverse("records:patient-record-list")
        response = authenticated_patient_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["id"] == str(own_record.id)

    def test_create_health_record(self, authenticated_patient_client, doctor_user):
        url = reverse("records:patient-record-list")
        data = {
            "doctor": str(doctor_user.id),
            "record_type": RecordType.PRESCRIPTION,
            "description": "New prescription record",
        }
        response = authenticated_patient_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        
        record = HealthRecord.objects.get(id=response.data["id"])
        assert record.patient == authenticated_patient_client.user
        assert record.doctor == doctor_user
        assert record.record_type == RecordType.PRESCRIPTION

    def test_create_record_with_files(self, authenticated_patient_client, doctor_user):
        url = reverse("records:patient-record-list")
        test_file = SimpleUploadedFile(
            "test_report.pdf",
            b"Test file content",
            content_type="application/pdf"
        )
        data = {
            "doctor": str(doctor_user.id),
            "record_type": RecordType.LAB_RESULT,
            "description": "Lab results",
            "files": [test_file],
        }
        response = authenticated_patient_client.post(url, data, format="multipart")
        assert response.status_code == status.HTTP_201_CREATED
        
        record = HealthRecord.objects.get(id=response.data["id"])
        assert record.files.count() == 1

    def test_create_record_doctor_required(self, authenticated_patient_client):
        url = reverse("records:patient-record-list")
        data = {
            "record_type": RecordType.CONSULTATION,
            "description": "Missing doctor",
        }
        response = authenticated_patient_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_unauthenticated_access(self, api_client):
        url = reverse("records:patient-record-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestPatientHealthRecordRetrieveUpdateView:
    def test_retrieve_health_record(self, authenticated_patient_client, health_record):
        url = reverse("records:patient-record-detail", kwargs={"pk": health_record.id})
        response = authenticated_patient_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == str(health_record.id)
        assert response.data["description"] == health_record.description

    def test_update_health_record(self, authenticated_patient_client, health_record):
        url = reverse("records:patient-record-detail", kwargs={"pk": health_record.id})
        data = {
            "description": "Updated description",
        }
        response = authenticated_patient_client.patch(url, data, format="json")
        assert response.status_code == status.HTTP_200_OK
        
        health_record.refresh_from_db()
        assert health_record.description == "Updated description"

    def test_cannot_update_other_patient_record(self, authenticated_patient_client, doctor_user):
        other_patient = authenticated_patient_client.user.__class__.objects.create_user(
            email="other2@patient.com",
            password="pass123",
            first_name="Other2",
            last_name="Patient2",
            role="patient",
        )
        other_record = HealthRecord.objects.create(
            patient=other_patient,
            doctor=doctor_user,
            record_type=RecordType.CONSULTATION,
        )
        
        url = reverse("records:patient-record-detail", kwargs={"pk": other_record.id})
        response = authenticated_patient_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestHealthRecordFileDeleteView:
    def test_delete_file(self, authenticated_patient_client, health_record):
        test_file = SimpleUploadedFile(
            "test_delete.pdf",
            b"Delete me",
            content_type="application/pdf"
        )
        file_record = HealthRecordFile.objects.create(
            record=health_record,
            file=test_file,
        )
        
        url = reverse("records:health-record-file-delete", kwargs={"pk": file_record.id})
        response = authenticated_patient_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not HealthRecordFile.objects.filter(id=file_record.id).exists()

    def test_cannot_delete_other_patient_file(self, authenticated_patient_client, doctor_user):
        other_patient = authenticated_patient_client.user.__class__.objects.create_user(
            email="other3@patient.com",
            password="pass123",
            first_name="Other3",
            last_name="Patient3",
            role="patient",
        )
        other_record = HealthRecord.objects.create(
            patient=other_patient,
            doctor=doctor_user,
        )
        file_record = HealthRecordFile.objects.create(
            record=other_record,
            file=SimpleUploadedFile("other.pdf", b"content"),
        )
        
        url = reverse("records:health-record-file-delete", kwargs={"pk": file_record.id})
        response = authenticated_patient_client.delete(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestDoctorHealthRecordListView:
    def test_list_assigned_records(self, authenticated_doctor_client, patient_user):
        record = HealthRecord.objects.create(
            patient=patient_user,
            doctor=authenticated_doctor_client.user,
            record_type=RecordType.CONSULTATION,
        )
        
        url = reverse("records:doctor-record-list")
        response = authenticated_doctor_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["id"] == str(record.id)

    def test_list_only_assigned_records(self, authenticated_doctor_client, patient_user):
        other_doctor = authenticated_doctor_client.user.__class__.objects.create_user(
            email="other@doctor.com",
            password="pass123",
            first_name="Other",
            last_name="Doctor",
            role="doctor",
        )
        HealthRecord.objects.create(
            patient=patient_user,
            doctor=other_doctor,
            record_type=RecordType.LAB_RESULT,
        )
        own_record = HealthRecord.objects.create(
            patient=patient_user,
            doctor=authenticated_doctor_client.user,
            record_type=RecordType.PRESCRIPTION,
        )
        
        url = reverse("records:doctor-record-list")
        response = authenticated_doctor_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["id"] == str(own_record.id)

    def test_patient_cannot_access(self, authenticated_patient_client):
        url = reverse("records:doctor-record-list")
        response = authenticated_patient_client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestDoctorHealthRecordDetailView:
    def test_view_assigned_record(self, authenticated_doctor_client, patient_user):
        record = HealthRecord.objects.create(
            patient=patient_user,
            doctor=authenticated_doctor_client.user,
            record_type=RecordType.IMAGING,
        )
        
        url = reverse("records:doctor-record-detail", kwargs={"pk": record.id})
        response = authenticated_doctor_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == str(record.id)

    def test_cannot_view_unassigned_record(self, authenticated_doctor_client, patient_user):
        other_doctor = authenticated_doctor_client.user.__class__.objects.create_user(
            email="other2@doctor.com",
            password="pass123",
            first_name="Other2",
            last_name="Doctor2",
            role="doctor",
        )
        record = HealthRecord.objects.create(
            patient=patient_user,
            doctor=other_doctor,
        )
        
        url = reverse("records:doctor-record-detail", kwargs={"pk": record.id})
        response = authenticated_doctor_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestDoctorAnnotationCreateView:
    def test_create_annotation(self, authenticated_doctor_client, patient_user):
        record = HealthRecord.objects.create(
            patient=patient_user,
            doctor=authenticated_doctor_client.user,
            record_type=RecordType.CONSULTATION,
        )
        
        url = reverse("records:doctor-annotation-create")
        data = {
            "record": str(record.id),
            "note": "Patient responding well to treatment",
        }
        response = authenticated_doctor_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        
        annotation = DoctorAnnotation.objects.get(id=response.data["id"])
        assert annotation.record == record
        assert annotation.note == "Patient responding well to treatment"

    def test_cannot_annotate_unassigned_record(self, authenticated_doctor_client, patient_user):
        other_doctor = authenticated_doctor_client.user.__class__.objects.create_user(
            email="other3@doctor.com",
            password="pass123",
            first_name="Other3",
            last_name="Doctor3",
            role="doctor",
        )
        record = HealthRecord.objects.create(
            patient=patient_user,
            doctor=other_doctor,
        )
        
        url = reverse("records:doctor-annotation-create")
        data = {
            "record": str(record.id),
            "note": "Should not work",
        }
        response = authenticated_doctor_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestDoctorAnnotationUpdateView:
    def test_update_annotation(self, authenticated_doctor_client, patient_user):
        record = HealthRecord.objects.create(
            patient=patient_user,
            doctor=authenticated_doctor_client.user,
        )
        annotation = DoctorAnnotation.objects.create(
            record=record,
            note="Original note",
        )
        
        url = reverse("records:doctor-annotation-update", kwargs={"pk": annotation.id})
        data = {
            "note": "Updated note",
        }
        response = authenticated_doctor_client.patch(url, data, format="json")
        assert response.status_code == status.HTTP_200_OK
        
        annotation.refresh_from_db()
        assert annotation.note == "Updated note"

    def test_cannot_update_other_doctor_annotation(self, authenticated_doctor_client, patient_user):
        other_doctor = authenticated_doctor_client.user.__class__.objects.create_user(
            email="other4@doctor.com",
            password="pass123",
            first_name="Other4",
            last_name="Doctor4",
            role="doctor",
        )
        record = HealthRecord.objects.create(
            patient=patient_user,
            doctor=other_doctor,
        )
        annotation = DoctorAnnotation.objects.create(
            record=record,
            note="Other doctor's note",
        )
        
        url = reverse("records:doctor-annotation-update", kwargs={"pk": annotation.id})
        data = {"note": "Should not work"}
        response = authenticated_doctor_client.patch(url, data, format="json")
        assert response.status_code == status.HTTP_404_NOT_FOUND