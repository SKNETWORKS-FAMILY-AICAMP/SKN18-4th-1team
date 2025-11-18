from django.apps import AppConfig


class UserConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "user_app"
    verbose_name = "사용자"

    def ready(self):
        # Import signals so that login hooks are registered once the app loads.
        from . import signals  # noqa: F401
