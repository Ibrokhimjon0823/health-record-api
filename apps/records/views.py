from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions

from apps.accounts import permissions as account_permissions

from . import models, serializers


@extend_schema(tags=["Health Records"])
class PatientHealthRecordListCreateView(generics.ListCreateAPIView):
    """
    List and create health records for authenticated patients.

    GET: Returns all health records belonging to the authenticated patient,
    including associated files and doctor annotations.

    POST: Creates a new health record for the patient. Requires selecting
    a doctor and can optionally include file uploads.
    """

    permission_classes = [account_permissions.IsPatient]

    def get_serializer_class(self):
        """
        Use different serializers for read and write operations.
        """
        if self.request.method in permissions.SAFE_METHODS:
            return serializers.HealthRecordSerializer
        return serializers.HealthRecordWriteSerializer

    def get_queryset(self):
        """
        Return health records for the authenticated patient with optimized queries.
        """
        return (
            models.HealthRecord.objects.filter(patient=self.request.user)
            .select_related("patient", "doctor")
            .prefetch_related("files")
        )


@extend_schema(tags=["Health Records"])
class PatientHealthRecordRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    """
    Retrieve or update a specific health record for authenticated patients.

    GET: Returns detailed information about a specific health record.

    PUT/PATCH: Updates health record information. Files can be added
    but not removed through this endpoint.
    """

    permission_classes = [account_permissions.IsPatient]

    def get_serializer_class(self):
        """
        Use different serializers for read and write operations.
        """
        if self.request.method in permissions.SAFE_METHODS:
            return serializers.HealthRecordSerializer
        return serializers.HealthRecordWriteSerializer

    def get_queryset(self):
        """
        Return health records for the authenticated patient with optimized queries.
        """
        return (
            models.HealthRecord.objects.filter(patient=self.request.user)
            .select_related("patient", "doctor")
            .prefetch_related("files")
        )


@extend_schema(tags=["Health Records"])
class HealthRecordFileDeleteView(generics.DestroyAPIView):
    """
    Delete a file from a health record.

    Only the patient who owns the health record can delete files.
    This permanently removes the file from storage.
    """

    permission_classes = [account_permissions.IsPatient]

    def get_queryset(self):
        """
        Return files belonging to the authenticated patient's health records.
        """
        return models.HealthRecordFile.objects.filter(record__patient=self.request.user)


@extend_schema(tags=["Health Records"])
class DoctorHealthRecordListView(generics.ListAPIView):
    """
    List health records assigned to the authenticated doctor.

    Returns all health records where the authenticated doctor is assigned.
    Includes patient information, files, and any annotations made.
    """

    permission_classes = [account_permissions.IsDoctor]
    serializer_class = serializers.HealthRecordSerializer

    def get_queryset(self):
        """
        Return health records assigned to the authenticated doctor.
        """
        return (
            models.HealthRecord.objects.filter(doctor=self.request.user)
            .select_related("patient", "doctor")
            .prefetch_related("files")
        )


@extend_schema(tags=["Health Records"])
class DoctorHealthRecordDetailView(generics.RetrieveAPIView):
    """
    View details of a specific health record assigned to the doctor.

    Provides read-only access to health record details including
    patient information, uploaded files, and all annotations.
    """

    permission_classes = [account_permissions.IsDoctor]
    serializer_class = serializers.HealthRecordSerializer

    def get_queryset(self):
        """
        Return health records assigned to the authenticated doctor.
        """
        return (
            models.HealthRecord.objects.filter(doctor=self.request.user)
            .select_related("patient", "doctor")
            .prefetch_related("files")
        )


@extend_schema(tags=["Health Records"])
class DoctorAnnotationCreateView(generics.CreateAPIView):
    """
    Add annotations to health records.

    Allows doctors to add professional notes and observations to health
    records they are assigned to. Annotations are permanent and cannot
    be edited or deleted once created.
    """

    permission_classes = [account_permissions.IsDoctor]
    serializer_class = serializers.AnnotationWriteSerializer


class DoctorAnnotationUpdateView(generics.UpdateAPIView):
    """
    Update an existing annotation made by the doctor.

    Allows doctors to update their own annotations on health records.
    Annotations can be modified but not deleted.
    """

    permission_classes = [account_permissions.IsDoctor]
    serializer_class = serializers.AnnotationWriteSerializer

    def get_queryset(self):
        """
        Return annotations made by the authenticated doctor.
        """
        return models.DoctorAnnotation.objects.filter(record__doctor=self.request.user)
