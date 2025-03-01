from django.apps import AppConfig


class TourConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tour'
    def ready(self):
        import tour.signals  # Import signals to ensure they are registered