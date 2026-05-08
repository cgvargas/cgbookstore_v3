from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)


class NewsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'news'
    verbose_name = '📰 Notícias'
    
    def ready(self):
        """Inicia o scheduler e registra signals quando o Django carrega."""
        import os
        
        # Registrar signals (sempre, independente do ambiente)
        try:
            import news.signals  # noqa: F401
            logger.debug("[NEWS] Signals registrados com sucesso.")
        except Exception as e:
            logger.warning(f"Não foi possível registrar signals do news: {e}")

        # Evitar executar o scheduler duas vezes (runserver recarrega)
        if os.environ.get('RUN_MAIN') != 'true':
            return
        
        # Importar aqui para evitar circular imports
        try:
            from news.scheduler import start_scheduler
            start_scheduler()
        except Exception as e:
            logger.warning(f"Não foi possível iniciar scheduler: {e}")
