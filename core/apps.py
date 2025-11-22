from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        """Registra signals para invalidação de cache."""
        # Importar signals aqui para evitar importações circulares
        from core.signals import cache_signals  # noqa: F401
