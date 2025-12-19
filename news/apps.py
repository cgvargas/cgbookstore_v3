from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)


class NewsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'news'
    verbose_name = '📰 Notícias'
    
    def ready(self):
        """Inicia o scheduler quando o Django carrega."""
        import os
        
        # Evitar executar duas vezes (runserver recarrega)
        if os.environ.get('RUN_MAIN') != 'true':
            return
        
        # Importar aqui para evitar circular imports
        try:
            from news.scheduler import start_scheduler
            start_scheduler()
        except Exception as e:
            logger.warning(f"Não foi possível iniciar scheduler: {e}")
