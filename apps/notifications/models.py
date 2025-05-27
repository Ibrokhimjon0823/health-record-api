from django.conf import settings
from django.db import models

from apps.core.models import BaseModel


class NotificationType(models.TextChoices):
    PATIENT_ASSIGNED = "patient_assigned", "Patient Assigned"
    RECORD_ANNOTATED = "record_annotated", "Record Annotated"


class Notification(BaseModel):
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications"
    )
    record = models.ForeignKey(
        "records.HealthRecord",
        on_delete=models.CASCADE,
    )
    notification_type = models.CharField(
        max_length=30, choices=NotificationType.choices
    )
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.message} - {self.recipient.email}"

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = self.created_at
            self.save(update_fields=["is_read", "read_at"])
