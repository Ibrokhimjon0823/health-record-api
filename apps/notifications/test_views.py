import pytest
from django.urls import reverse
from rest_framework import status
from datetime import datetime, timezone

from apps.notifications.models import Notification, NotificationType
from apps.records.models import HealthRecord


@pytest.mark.django_db
class TestNotificationListView:
    def test_list_user_notifications(self, authenticated_patient_client, health_record):
        notification1 = Notification.objects.create(
            recipient=authenticated_patient_client.user,
            record=health_record,
            notification_type=NotificationType.PATIENT_ASSIGNED,
            message="You have been assigned to a doctor",
        )
        notification2 = Notification.objects.create(
            recipient=authenticated_patient_client.user,
            record=health_record,
            notification_type=NotificationType.RECORD_ANNOTATED,
            message="Your record has been updated",
        )
        
        url = reverse("notifications:notification-list")
        response = authenticated_patient_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2
        
        notification_ids = [n["id"] for n in response.data]
        assert str(notification1.id) in notification_ids
        assert str(notification2.id) in notification_ids

    def test_list_only_own_notifications(self, authenticated_patient_client, doctor_user, health_record):
        own_notification = Notification.objects.create(
            recipient=authenticated_patient_client.user,
            record=health_record,
            notification_type=NotificationType.PATIENT_ASSIGNED,
            message="Your notification",
        )
        other_notification = Notification.objects.create(
            recipient=doctor_user,
            record=health_record,
            notification_type=NotificationType.PATIENT_ASSIGNED,
            message="Other user notification",
        )
        
        url = reverse("notifications:notification-list")
        response = authenticated_patient_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["id"] == str(own_notification.id)

    def test_notifications_ordered_by_created_at(self, authenticated_patient_client, health_record):
        older_notification = Notification.objects.create(
            recipient=authenticated_patient_client.user,
            record=health_record,
            notification_type=NotificationType.PATIENT_ASSIGNED,
            message="Older notification",
        )
        newer_notification = Notification.objects.create(
            recipient=authenticated_patient_client.user,
            record=health_record,
            notification_type=NotificationType.RECORD_ANNOTATED,
            message="Newer notification",
        )
        
        url = reverse("notifications:notification-list")
        response = authenticated_patient_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data[0]["id"] == str(newer_notification.id)
        assert response.data[1]["id"] == str(older_notification.id)

    def test_unauthenticated_access(self, api_client):
        url = reverse("notifications:notification-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestNotificationDetailView:
    def test_retrieve_and_mark_as_read(self, authenticated_patient_client, health_record):
        notification = Notification.objects.create(
            recipient=authenticated_patient_client.user,
            record=health_record,
            notification_type=NotificationType.PATIENT_ASSIGNED,
            message="Test notification",
        )
        assert not notification.is_read
        
        url = reverse("notifications:notification-detail", kwargs={"pk": notification.id})
        response = authenticated_patient_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == str(notification.id)
        
        notification.refresh_from_db()
        assert notification.is_read
        assert notification.read_at is not None

    def test_retrieve_already_read_notification(self, authenticated_patient_client, health_record):
        notification = Notification.objects.create(
            recipient=authenticated_patient_client.user,
            record=health_record,
            notification_type=NotificationType.RECORD_ANNOTATED,
            message="Already read notification",
            is_read=True,
            read_at=datetime.now(timezone.utc),
        )
        
        url = reverse("notifications:notification-detail", kwargs={"pk": notification.id})
        response = authenticated_patient_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_cannot_retrieve_other_user_notification(self, authenticated_patient_client, doctor_user, health_record):
        notification = Notification.objects.create(
            recipient=doctor_user,
            record=health_record,
            notification_type=NotificationType.PATIENT_ASSIGNED,
            message="Other user notification",
        )
        
        url = reverse("notifications:notification-detail", kwargs={"pk": notification.id})
        response = authenticated_patient_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        notification.refresh_from_db()
        assert not notification.is_read

    def test_retrieve_nonexistent_notification(self, authenticated_patient_client):
        import uuid
        fake_id = uuid.uuid4()
        url = reverse("notifications:notification-detail", kwargs={"pk": fake_id})
        response = authenticated_patient_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestMarkAllNotificationsReadView:
    def test_mark_all_notifications_as_read(self, authenticated_patient_client, health_record):
        notifications = []
        for i in range(3):
            notification = Notification.objects.create(
                recipient=authenticated_patient_client.user,
                record=health_record,
                notification_type=NotificationType.PATIENT_ASSIGNED,
                message=f"Notification {i}",
            )
            notifications.append(notification)
        
        url = reverse("notifications:mark-all-notifications-read")
        response = authenticated_patient_client.post(url)
        assert response.status_code == status.HTTP_200_OK
        
        for notification in notifications:
            notification.refresh_from_db()
            assert notification.is_read
            assert notification.read_at is not None

    def test_mark_all_skips_already_read(self, authenticated_patient_client, health_record):
        read_notification = Notification.objects.create(
            recipient=authenticated_patient_client.user,
            record=health_record,
            notification_type=NotificationType.PATIENT_ASSIGNED,
            message="Already read",
            is_read=True,
            read_at=datetime.now(timezone.utc),
        )
        unread_notification = Notification.objects.create(
            recipient=authenticated_patient_client.user,
            record=health_record,
            notification_type=NotificationType.RECORD_ANNOTATED,
            message="Unread",
        )
        
        url = reverse("notifications:mark-all-notifications-read")
        response = authenticated_patient_client.post(url)
        assert response.status_code == status.HTTP_200_OK
        
        unread_notification.refresh_from_db()
        assert unread_notification.is_read

    def test_mark_all_only_affects_own_notifications(self, authenticated_patient_client, doctor_user, health_record):
        own_notification = Notification.objects.create(
            recipient=authenticated_patient_client.user,
            record=health_record,
            notification_type=NotificationType.PATIENT_ASSIGNED,
            message="Own notification",
        )
        other_notification = Notification.objects.create(
            recipient=doctor_user,
            record=health_record,
            notification_type=NotificationType.PATIENT_ASSIGNED,
            message="Other notification",
        )
        
        url = reverse("notifications:mark-all-notifications-read")
        response = authenticated_patient_client.post(url)
        assert response.status_code == status.HTTP_200_OK
        
        own_notification.refresh_from_db()
        other_notification.refresh_from_db()
        assert own_notification.is_read
        assert not other_notification.is_read

    def test_mark_all_when_no_unread(self, authenticated_patient_client):
        url = reverse("notifications:mark-all-notifications-read")
        response = authenticated_patient_client.post(url)
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestDeleteAllNotificationsView:
    def test_delete_all_notifications(self, authenticated_patient_client, health_record):
        notifications = []
        for i in range(3):
            notification = Notification.objects.create(
                recipient=authenticated_patient_client.user,
                record=health_record,
                notification_type=NotificationType.PATIENT_ASSIGNED,
                message=f"Notification {i}",
            )
            notifications.append(notification)
        
        url = reverse("notifications:delete-all-notifications")
        response = authenticated_patient_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        assert authenticated_patient_client.user.notifications.count() == 0

    def test_delete_all_includes_read_notifications(self, authenticated_patient_client, health_record):
        read_notification = Notification.objects.create(
            recipient=authenticated_patient_client.user,
            record=health_record,
            notification_type=NotificationType.PATIENT_ASSIGNED,
            message="Read notification",
            is_read=True,
            read_at=datetime.now(timezone.utc),
        )
        unread_notification = Notification.objects.create(
            recipient=authenticated_patient_client.user,
            record=health_record,
            notification_type=NotificationType.RECORD_ANNOTATED,
            message="Unread notification",
        )
        
        url = reverse("notifications:delete-all-notifications")
        response = authenticated_patient_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        assert authenticated_patient_client.user.notifications.count() == 0

    def test_delete_all_only_affects_own_notifications(self, authenticated_patient_client, doctor_user, health_record):
        own_notification = Notification.objects.create(
            recipient=authenticated_patient_client.user,
            record=health_record,
            notification_type=NotificationType.PATIENT_ASSIGNED,
            message="Own notification",
        )
        other_notification = Notification.objects.create(
            recipient=doctor_user,
            record=health_record,
            notification_type=NotificationType.PATIENT_ASSIGNED,
            message="Other notification",
        )
        
        url = reverse("notifications:delete-all-notifications")
        response = authenticated_patient_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        assert not Notification.objects.filter(id=own_notification.id).exists()
        assert Notification.objects.filter(id=other_notification.id).exists()

    def test_delete_all_when_no_notifications(self, authenticated_patient_client):
        url = reverse("notifications:delete-all-notifications")
        response = authenticated_patient_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT