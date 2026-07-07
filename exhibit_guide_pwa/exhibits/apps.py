from django.apps import AppConfig


class ExhibitsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'exhibits'

    def ready(self):
        import exhibits.signals  # noqa: F401
