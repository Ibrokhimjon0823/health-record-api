from rest_framework import serializers

from apps.records import serializers as record_serializers

from . import models


class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for notification data.
    
    Read-only serializer that includes the related health record details.
    All fields are read-only as notifications are created by the system
    and should not be modified through the API.
    """
    record = record_serializers.HealthRecordSerializer()

    class Meta:
        model = models.Notification
        fields = [
            "id",
            "record",
            "notification_type",
            "message",
            "is_read",
            "read_at",
            "created_at",
        ]
        read_only_fields = fields