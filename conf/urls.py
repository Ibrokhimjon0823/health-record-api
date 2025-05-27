from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "api/schema/",
        SpectacularAPIView.as_view(),
        name="schema",
    ),
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/accounts/",
        include("apps.accounts.urls"),
    ),
    path(
        "api/records/",
        include("apps.records.urls"),
    ),
    path(
        "api/notifications/",
        include("apps.notifications.urls"),
    ),
]
