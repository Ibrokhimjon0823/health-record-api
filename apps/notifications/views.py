from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from . import models, serializers


@extend_schema(tags=["Notifications"])
class NotificationListView(generics.ListAPIView):
    """
    List all notifications for the authenticated user.
    
    Returns a paginated list of notifications ordered by creation date.
    Includes related health record information. Does not automatically
    mark notifications as read.
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.NotificationSerializer

    def get_queryset(self):
        """
        Filter notifications to only show those for the current user.
        """
        return models.Notification.objects.filter(
            recipient=self.request.user
        ).select_related("record")


@extend_schema(tags=["Notifications"])
class NotificationDetailView(generics.RetrieveAPIView):
    """
    Retrieve a single notification and mark it as read.
    
    When a notification is retrieved through this endpoint, it is
    automatically marked as read with the current timestamp.
    """
    
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.NotificationSerializer

    def get_queryset(self):
        """
        Filter notifications to only show those for the current user.
        """
        return models.Notification.objects.filter(
            recipient=self.request.user
        ).select_related("record")

    def get_object(self):
        """
        Get the notification and mark it as read.
        """
        notification = super().get_object()
        notification.mark_as_read()
        return notification


@extend_schema(tags=["Notifications"])
class MarkAllNotificationsReadView(generics.GenericAPIView):
    """
    Mark all unread notifications as read for the authenticated user.
    
    Bulk updates all unread notifications to set is_read=True and
    read_at to the current timestamp.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Get all unread notifications for the current user.
        """
        return models.Notification.objects.filter(
            recipient=self.request.user, is_read=False
        )

    def post(self, request, *args, **kwargs):
        """
        Mark all unread notifications as read.
        """
        self.get_queryset().update(is_read=True, read_at=timezone.now())
        return Response(status=status.HTTP_200_OK)


@extend_schema(tags=["Notifications"])
class DeleteAllNotificationsView(generics.GenericAPIView):
    """
    Delete all notifications for the authenticated user.
    
    Permanently removes all notifications (both read and unread) for
    the current user. This action cannot be undone.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Get all notifications for the current user.
        """
        return models.Notification.objects.filter(recipient=self.request.user)

    def delete(self, request, *args, **kwargs):
        """
        Delete all notifications for the user.
        """
        self.get_queryset().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)