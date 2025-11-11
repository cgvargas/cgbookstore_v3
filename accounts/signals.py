"""
Signals para criação automática de UserProfile e notificações de boas-vindas.

Este módulo garante que todo User criado automaticamente tenha um UserProfile associado
e receba uma notificação de boas-vindas.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Cria UserProfile automaticamente quando um novo User é criado.

    Também cria notificação de boas-vindas no sininho.

    Args:
        sender: Model que enviou o signal (User)
        instance: Instância do User que foi salvo
        created: Boolean indicando se é uma nova instância
        **kwargs: Argumentos adicionais do signal
    """
    if created:
        # Criar UserProfile
        UserProfile.objects.create(
            user=instance,
            theme_preference='fantasy',  # Tema padrão
            level=1,
            total_xp=0
        )

        # Criar notificação de boas-vindas
        try:
            from accounts.models.reading_notification import SystemNotification
            from allauth.account.models import EmailAddress

            # Verificar se email está verificado
            email_verified = EmailAddress.objects.filter(
                user=instance,
                verified=True
            ).exists()

            if email_verified:
                # Email já verificado (login social ou admin)
                message = (
                    f"Bem-vindo(a) à CGBookStore, {instance.username}! "
                    "Explore nossa biblioteca, descubra novos livros e "
                    "conecte-se com outros leitores apaixonados por literatura!"
                )
                notification_type = 'system_upgrade'  # Tipo genérico de sistema
            else:
                # Email não verificado - incentivar verificação
                message = (
                    f"Bem-vindo(a) à CGBookStore, {instance.username}! "
                    "Para uma experiência completa, verifique seu email. "
                    "Enviamos um link de confirmação para você. "
                    "Explore nossa biblioteca e descubra novos livros enquanto isso!"
                )
                notification_type = 'system_upgrade'

            SystemNotification.objects.create(
                user=instance,
                notification_type=notification_type,
                message=message,
                priority=1,  # Baixa prioridade (informativa)
                action_url='/',
                action_text='Explorar Biblioteca',
                is_read=False
            )

            logger.info(f"Notificação de boas-vindas criada para {instance.username}")

        except Exception as e:
            logger.error(f"Erro ao criar notificação de boas-vindas: {e}")
            # Não falhar o cadastro por causa de notificação


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Salva o UserProfile sempre que o User é salvo.

    Garante sincronização entre User e UserProfile.
    Se o profile não existir (caso raro), cria um novo.

    Args:
        sender: Model que enviou o signal (User)
        instance: Instância do User que foi salvo
        **kwargs: Argumentos adicionais do signal
    """
    try:
        instance.profile.save()
    except UserProfile.DoesNotExist:
        # Fallback: criar profile se não existir
        UserProfile.objects.create(
            user=instance,
            theme_preference='fantasy',
            level=1,
            total_xp=0
        )