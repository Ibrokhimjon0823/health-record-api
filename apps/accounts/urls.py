from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path(
        "login/",
        views.LoginView.as_view(),
        name="login",
    ),
    path(
        "register/",
        views.RegisterView.as_view(),
        name="register",
    ),
    path(
        "profile-create/",
        views.ProfileCreateView.as_view(),
        name="profile-create",
    ),
    path(
        "profile-update/",
        views.ProfileUpdateView.as_view(),
        name="profile-update",
    ),
    path(
        "doctors/",
        views.DoctorListView.as_view(),
        name="doctor-list",
    ),
]
