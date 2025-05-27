from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.notifications import models as notification_models
from apps.notifications.tasks import send_notification_email

from .models import DoctorAnnotation, HealthRecord


@receiver(post_save, sender=HealthRecord)
def notify_doctor_on_health_record_creation(sender, instance, created, **kwargs):
    """
    Send notification to doctor when a new health record is created
    """
    if created:
        notification = notification_models.Notification.objects.create(
            recipient=instance.doctor,
            record=instance,
            notification_type=notification_models.NotificationType.PATIENT_ASSIGNED,
            message=f"New health record created by patient {instance.patient.get_full_name()}",
        )
        send_notification_email.delay(notification.id)


@receiver(post_save, sender=DoctorAnnotation)
def notify_patient_on_annotation(sender, instance, created, **kwargs):
    """
    Send notification to patient when doctor adds an annotation
    Only notify if the annotation is not internal
    """
    if created:
        notification = notification_models.Notification.objects.create(
            recipient=instance.record.patient,
            record=instance.record,
            notification_type=notification_models.NotificationType.RECORD_ANNOTATED,
            message=f"Dr. {instance.record.doctor.get_full_name()} has annotated health record: {instance.record_id}",
        )
        send_notification_email.delay(notification.id)
