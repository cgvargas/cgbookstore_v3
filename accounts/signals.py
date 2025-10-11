"""
Signals para criação automática de UserProfile.

Este módulo garante que todo User criado automaticamente tenha um UserProfile associado.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Cria UserProfile automaticamente quando um novo User é criado.

    Args:
        sender: Model que enviou o signal (User)
        instance: Instância do User que foi salvo
        created: Boolean indicando se é uma nova instância
        **kwargs: Argumentos adicionais do signal
    """
    if created:
        UserProfile.objects.create(
            user=instance,
            theme_preference='fantasy',  # Tema padrão
            level=1,
            total_xp=0
        )


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