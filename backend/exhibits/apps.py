from django.apps import AppConfig


class ExhibitsConfig(AppConfig):
    """Application configuration for the exhibits domain app."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'exhibits'

    def ready(self):
        """Import signal handlers when Django finishes loading app registry."""
        import exhibits.signals  # noqa: F401
