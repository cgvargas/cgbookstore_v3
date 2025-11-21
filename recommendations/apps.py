from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)


class RecommendationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'recommendations'

    def ready(self):
        """
        Pré-carrega sklearn no startup para evitar delay na primeira requisição.
        O carregamento do sklearn demora ~6 segundos, então fazemos isso no boot.
        """
        import threading

        def preload_sklearn():
            try:
                from .algorithms import _load_sklearn
                _load_sklearn()
                logger.info("sklearn pré-carregado com sucesso no startup")
            except Exception as e:
                logger.warning(f"Falha ao pré-carregar sklearn: {e}")

        # Carregar em thread separada para não bloquear o startup
        thread = threading.Thread(target=preload_sklearn, daemon=True)
        thread.start()
