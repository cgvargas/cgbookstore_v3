"""
AppConfig para o módulo de Product Analytics.
"""
from django.apps import AppConfig


class ProductAnalyticsConfig(AppConfig):
    name = "product_analytics"
    verbose_name = "Product Analytics"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        """
        Importa signals quando o app está pronto.
        Não conecta signals de outros apps aqui para manter baixo acoplamento.
        """
        pass  # Signals serão conectados manualmente se necessário
