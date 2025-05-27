from django.urls import path

from . import views

urlpatterns = [
    path(
        "",
        views.NotificationListView.as_view(),
        name="notification-list",
    ),
    path(
        "<uuid:pk>/",
        views.NotificationDetailView.as_view(),
        name="notification-detail",
    ),
    path(
        "mark-all-read/",
        views.MarkAllNotificationsReadView.as_view(),
        name="mark-all-notifications-read",
    ),
    path(
        "delete-all/",
        views.DeleteAllNotificationsView.as_view(),
        name="delete-all-notifications",
    ),
]
