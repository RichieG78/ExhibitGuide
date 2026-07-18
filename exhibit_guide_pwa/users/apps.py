from django.apps import AppConfig


class UsersConfig(AppConfig):
    """Application configuration for user profiles and activity workflows."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
