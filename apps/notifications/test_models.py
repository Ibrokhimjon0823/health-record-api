import pytest
from datetime import datetime, timezone
from apps.notifications.models import Notification, NotificationType
from apps.records.models import HealthRecord


@pytest.mark.django_db
class TestNotification:
    def test_create_notification(self, patient_user, health_record):
        notification = Notification.objects.create(
            recipient=patient_user,
            record=health_record,
            notification_type=NotificationType.PATIENT_ASSIGNED,
            message="You have been assigned to Dr. Smith",
        )
        assert notification.recipient == patient_user
        assert notification.record == health_record
        assert notification.notification_type == NotificationType.PATIENT_ASSIGNED
        assert notification.message == "You have been assigned to Dr. Smith"
        assert not notification.is_read
        assert notification.read_at is None

    def test_notification_str(self, patient_user, health_record):
        notification = Notification.objects.create(
            recipient=patient_user,
            record=health_record,
            notification_type=NotificationType.RECORD_ANNOTATED,
            message="Your record has been annotated",
        )
        assert str(notification) == f"Your record has been annotated - {patient_user.email}"

    def test_mark_as_read(self, patient_user, health_record):
        notification = Notification.objects.create(
            recipient=patient_user,
            record=health_record,
            notification_type=NotificationType.PATIENT_ASSIGNED,
            message="Test notification",
        )
        
        assert not notification.is_read
        assert notification.read_at is None
        
        notification.mark_as_read()
        
        assert notification.is_read
        assert notification.read_at is not None
        assert notification.read_at == notification.created_at

    def test_mark_as_read_idempotent(self, patient_user, health_record):
        notification = Notification.objects.create(
            recipient=patient_user,
            record=health_record,
            notification_type=NotificationType.RECORD_ANNOTATED,
            message="Test notification",
        )
        
        notification.mark_as_read()
        first_read_at = notification.read_at
        
        notification.mark_as_read()
        notification.refresh_from_db()
        
        assert notification.read_at == first_read_at

    def test_notification_ordering(self, patient_user, doctor_user):
        record1 = HealthRecord.objects.create(
            patient=patient_user,
            doctor=doctor_user,
        )
        record2 = HealthRecord.objects.create(
            patient=patient_user,
            doctor=doctor_user,
        )
        
        notification1 = Notification.objects.create(
            recipient=patient_user,
            record=record1,
            notification_type=NotificationType.PATIENT_ASSIGNED,
            message="First notification",
        )
        notification2 = Notification.objects.create(
            recipient=patient_user,
            record=record2,
            notification_type=NotificationType.RECORD_ANNOTATED,
            message="Second notification",
        )
        
        notifications = list(Notification.objects.all())
        assert notifications[0] == notification2
        assert notifications[1] == notification1

    def test_notification_cascade_delete(self, patient_user, health_record):
        notification = Notification.objects.create(
            recipient=patient_user,
            record=health_record,
            notification_type=NotificationType.PATIENT_ASSIGNED,
            message="Test notification",
        )
        notification_id = notification.id
        
        health_record.delete()
        
        assert not Notification.objects.filter(id=notification_id).exists()

    def test_multiple_notifications_per_record(self, patient_user, doctor_user, health_record):
        # Clear any notifications created by signals
        Notification.objects.filter(record=health_record).delete()
        
        notification1 = Notification.objects.create(
            recipient=patient_user,
            record=health_record,
            notification_type=NotificationType.PATIENT_ASSIGNED,
            message="Record created",
        )
        notification2 = Notification.objects.create(
            recipient=doctor_user,
            record=health_record,
            notification_type=NotificationType.PATIENT_ASSIGNED,
            message="Patient assigned to you",
        )
        notification3 = Notification.objects.create(
            recipient=patient_user,
            record=health_record,
            notification_type=NotificationType.RECORD_ANNOTATED,
            message="Doctor added notes",
        )
        
        assert Notification.objects.filter(record=health_record).count() == 3
        assert patient_user.notifications.count() == 2
        assert doctor_user.notifications.count() == 1