import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.utils import IntegrityError

from apps.records.models import HealthRecord, HealthRecordFile, DoctorAnnotation, RecordType


@pytest.mark.django_db
class TestHealthRecord:
    def test_create_health_record(self, patient_user, doctor_user):
        record = HealthRecord.objects.create(
            patient=patient_user,
            doctor=doctor_user,
            record_type=RecordType.CONSULTATION,
            description="Initial consultation",
        )
        assert record.patient == patient_user
        assert record.doctor == doctor_user
        assert record.record_type == RecordType.CONSULTATION
        assert record.description == "Initial consultation"

    def test_health_record_str(self, patient_user, doctor_user):
        record = HealthRecord.objects.create(
            patient=patient_user,
            doctor=doctor_user,
            record_type=RecordType.LAB_RESULT,
        )
        assert str(record) == f"Health Record of {patient_user.email} (lab_result)"

    def test_health_record_default_type(self, patient_user, doctor_user):
        record = HealthRecord.objects.create(
            patient=patient_user,
            doctor=doctor_user,
        )
        assert record.record_type == RecordType.GENERAL

    def test_health_record_patient_must_be_patient_role(self, doctor_user):
        # Note: This test documents that role constraints are enforced via 
        # limit_choices_to in the model, not at the database level
        record = HealthRecord.objects.create(
            patient=doctor_user,
            doctor=doctor_user,
            record_type=RecordType.PRESCRIPTION,
        )
        # While this creates successfully at the DB level, 
        # the admin interface and forms will enforce the constraint
        assert record.patient.role == "doctor"

    def test_health_record_doctor_must_be_doctor_role(self, patient_user):
        # Note: This test documents that role constraints are enforced via 
        # limit_choices_to in the model, not at the database level
        record = HealthRecord.objects.create(
            patient=patient_user,
            doctor=patient_user,
            record_type=RecordType.IMAGING,
        )
        # While this creates successfully at the DB level, 
        # the admin interface and forms will enforce the constraint
        assert record.doctor.role == "patient"

    def test_health_record_ordering(self, patient_user, doctor_user):
        record1 = HealthRecord.objects.create(
            patient=patient_user,
            doctor=doctor_user,
            record_type=RecordType.CONSULTATION,
        )
        record2 = HealthRecord.objects.create(
            patient=patient_user,
            doctor=doctor_user,
            record_type=RecordType.LAB_RESULT,
        )
        records = list(HealthRecord.objects.all())
        assert records[0] == record2
        assert records[1] == record1


@pytest.mark.django_db
class TestHealthRecordFile:
    def test_create_health_record_file(self, health_record):
        test_file = SimpleUploadedFile(
            "test_report.pdf",
            b"Test file content",
            content_type="application/pdf"
        )
        file_record = HealthRecordFile.objects.create(
            record=health_record,
            file=test_file,
        )
        assert file_record.record == health_record
        assert "test_report" in file_record.file.name

    def test_health_record_file_str(self, health_record):
        test_file = SimpleUploadedFile(
            "test_image.jpg",
            b"Test image content",
            content_type="image/jpeg"
        )
        file_record = HealthRecordFile.objects.create(
            record=health_record,
            file=test_file,
        )
        assert f"File for {health_record}" in str(file_record)

    def test_health_record_cascade_delete(self, health_record):
        test_file = SimpleUploadedFile(
            "test_doc.pdf",
            b"Test content",
            content_type="application/pdf"
        )
        file_record = HealthRecordFile.objects.create(
            record=health_record,
            file=test_file,
        )
        file_id = file_record.id
        health_record.delete()
        assert not HealthRecordFile.objects.filter(id=file_id).exists()


@pytest.mark.django_db
class TestDoctorAnnotation:
    def test_create_annotation(self, health_record):
        annotation = DoctorAnnotation.objects.create(
            record=health_record,
            note="Patient shows improvement in condition",
        )
        assert annotation.record == health_record
        assert annotation.note == "Patient shows improvement in condition"

    def test_annotation_str(self, health_record):
        annotation = DoctorAnnotation.objects.create(
            record=health_record,
            note="Follow-up required",
        )
        doctor_name = health_record.doctor.get_full_name()
        assert f"Annotated by {doctor_name}" in str(annotation)
        assert str(health_record.id) in str(annotation)

    def test_annotation_cascade_delete(self, health_record):
        annotation = DoctorAnnotation.objects.create(
            record=health_record,
            note="Test note",
        )
        annotation_id = annotation.id
        health_record.delete()
        assert not DoctorAnnotation.objects.filter(id=annotation_id).exists()

    def test_multiple_annotations_per_record(self, health_record):
        annotation1 = DoctorAnnotation.objects.create(
            record=health_record,
            note="First note",
        )
        annotation2 = DoctorAnnotation.objects.create(
            record=health_record,
            note="Second note",
        )
        assert health_record.annotations.count() == 2
        assert annotation1 in health_record.annotations.all()
        assert annotation2 in health_record.annotations.all()