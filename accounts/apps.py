"""
Configuração do app Accounts.
"""

from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """
    Configuração do aplicativo Accounts.
    
    Responsável por:
    - Definir nome do app
    - Configurar auto field padrão
    - Registrar signals
    """
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
    verbose_name = 'Contas e Perfis'
    
    def ready(self):
        """
        Importa signals quando o app estiver pronto.
        
        Este método é chamado automaticamente pelo Django
        durante a inicialização. Garante que os signals
        sejam registrados corretamente.
        """
        import accounts.signals  # noqa: F401