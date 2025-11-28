from django.apps import AppConfig


class NewAuthorsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'new_authors'
    verbose_name = 'Autores Emergentes'

    def ready(self):
        """Importa os signals quando o app estiver pronto"""
        try:
            import new_authors.signals
        except ImportError:
            pass
