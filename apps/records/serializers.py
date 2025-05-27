from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers
from rest_framework.serializers import CurrentUserDefault

from apps.accounts import serializers as account_serializers

from . import models

User = get_user_model()


class HealthRecordFileSerializer(serializers.ModelSerializer):
    """
    Serializer for health record file uploads.

    Handles file information for health records. Used for both
    displaying existing files and handling new uploads.
    """

    class Meta:
        model = models.HealthRecordFile
        fields = [
            "id",
            "file",
        ]


class HealthRecordAnnotationSerializer(serializers.ModelSerializer):
    """
    Read-only serializer for doctor annotations.

    Displays annotation details including timestamps. All fields
    are read-only as annotations cannot be modified after creation.
    """

    class Meta:
        model = models.DoctorAnnotation
        fields = [
            "id",
            "note",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class HealthRecordSerializer(serializers.ModelSerializer):
    """
    Comprehensive read serializer for health records.

    Includes full details of the health record with nested patient
    and doctor information, associated files, and all annotations.
    Used for displaying health record information.
    """

    files = HealthRecordFileSerializer(many=True)
    annotations = HealthRecordAnnotationSerializer(many=True)
    patient = account_serializers.UserSerializer()
    doctor = account_serializers.UserSerializer()

    class Meta:
        model = models.HealthRecord
        fields = [
            "id",
            "patient",
            "doctor",
            "record_type",
            "description",
            "files",
            "annotations",
        ]
        read_only_fields = fields


class HealthRecordWriteSerializer(serializers.ModelSerializer):
    """
    Write serializer for creating and updating health records.

    Handles health record creation with file uploads. Patient is
    automatically set to the current user. Files are handled in
    bulk during creation.
    """

    files = serializers.ListField(
        child=serializers.FileField(), write_only=True, required=False
    )
    patient = serializers.HiddenField(default=CurrentUserDefault())

    class Meta:
        model = models.HealthRecord
        fields = [
            "id",
            "patient",
            "doctor",
            "record_type",
            "description",
            "files",
        ]

    def create(self, validated_data):
        """
        Create health record and associated files in a transaction.
        """
        files = validated_data.pop("files", [])
        with transaction.atomic():
            record = super().create(validated_data)
            models.HealthRecordFile.objects.bulk_create(
                models.HealthRecordFile(record=record, file=file) for file in files
            )
            return record


class AnnotationWriteSerializer(serializers.ModelSerializer):
    """
    Serializer for doctors to create annotations.

    Ensures doctors can only annotate health records assigned to them
    through custom queryset filtering in the record field.
    """

    class RecordPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
        """
        Custom field that limits record choices to those assigned to the doctor.
        """

        def get_queryset(self):
            """
            Filter health records to only those assigned to the requesting doctor.
            """
            return super().get_queryset().filter(doctor=self.context["request"].user)

    record = RecordPrimaryKeyRelatedField(queryset=models.HealthRecord.objects)

    class Meta:
        model = models.DoctorAnnotation
        fields = [
            "id",
            "record",
            "note",
        ]


class AnnotationListSerializer(serializers.ModelSerializer):
    """
    Read-only serializer for listing annotations.

    Provides a simple view of annotations with basic information
    and timestamps. All fields are read-only.
    """

    class Meta:
        model = models.DoctorAnnotation
        fields = [
            "id",
            "record",
            "note",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields
