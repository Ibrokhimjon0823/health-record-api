from django.apps import AppConfig


class RecordsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.records"

    def ready(self):
        from . import signals  # noqa: F401
