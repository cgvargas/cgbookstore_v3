from django.apps import AppConfig


class EreaderConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ereader'
    verbose_name = 'RetroReader - Leitor de E-Books'

    def ready(self):
        import ereader.signals
