from django.apps import AppConfig


class MonitoringConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'monitoring'
    verbose_name = 'Monitoramento e Alertas'

    def ready(self):
        """Importar signals ao iniciar o app."""
        pass
