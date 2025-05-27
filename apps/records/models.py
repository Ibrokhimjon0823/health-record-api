from django.conf import settings
from django.db import models

from apps.core.models import BaseModel


class RecordType(models.TextChoices):
    CONSULTATION = "consultation", "Consultation"
    LAB_RESULT = "lab_result", "Lab Result"
    PRESCRIPTION = "prescription", "Prescription"
    IMAGING = "imaging", "Imaging"
    PROCEDURE = "procedure", "Procedure"
    GENERAL = "general", "General"


class HealthRecord(BaseModel):
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="health_records",
        limit_choices_to={"role": "patient"},
    )
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="health_records_as_doctor",
        limit_choices_to={"role": "doctor"},
    )
    record_type = models.CharField(
        max_length=20,
        choices=RecordType.choices,
        default=RecordType.GENERAL,
        db_index=True,
    )
    description = models.TextField(blank=True)

    def __str__(self):
        return f"Health Record of {self.patient.email} ({self.record_type})"


class HealthRecordFile(BaseModel):
    record = models.ForeignKey(
        HealthRecord, on_delete=models.CASCADE, related_name="files"
    )
    file = models.FileField(upload_to="health_records/files/")

    def __str__(self):
        return f"File for {self.record} ({self.file.name})"


class DoctorAnnotation(BaseModel):
    record = models.ForeignKey(
        HealthRecord, on_delete=models.CASCADE, related_name="annotations"
    )
    note = models.TextField()

    def __str__(self):
        return f"Annotated by {self.record.doctor.get_full_name()} on {self.record_id} at ({self.created_at})"
