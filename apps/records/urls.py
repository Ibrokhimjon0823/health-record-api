from django.urls import path

from . import views

app_name = "records"

urlpatterns = [
    path(
        "patient/",
        views.PatientHealthRecordListCreateView.as_view(),
        name="patient-record-list",
    ),
    path(
        "patient/<uuid:pk>/",
        views.PatientHealthRecordRetrieveUpdateView.as_view(),
        name="patient-record-detail",
    ),
    path(
        "files/<uuid:pk>/",
        views.HealthRecordFileDeleteView.as_view(),
        name="health-record-file-delete",
    ),
    path(
        "doctor/",
        views.DoctorHealthRecordListView.as_view(),
        name="doctor-record-list",
    ),
    path(
        "doctor/<uuid:pk>/",
        views.DoctorHealthRecordDetailView.as_view(),
        name="doctor-record-detail",
    ),
    path(
        "doctor/annotations/",
        views.DoctorAnnotationCreateView.as_view(),
        name="doctor-annotation-create",
    ),
    path(
        "doctor/annotations/<uuid:pk>/",
        views.DoctorAnnotationUpdateView.as_view(),
        name="doctor-annotation-update",
    ),
]
