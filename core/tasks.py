"""
Tarefas assíncronas do Core.
"""

from celery import shared_task
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


@shared_task
def clear_expired_cache():
    """
    Limpa entradas expiradas do cache.
    Executada periodicamente via Celery Beat.
    """
    try:
        # Redis limpa automaticamente, mas forçamos para garantir
        cache.clear()
        logger.info("✅ Cache limpo com sucesso")
        return "Cache cleared"
    except Exception as e:
        logger.error(f"❌ Erro ao limpar cache: {e}")
        return f"Error: {e}"


@shared_task
def test_async_task(message):
    """Task de teste para validar Celery."""
    logger.info(f"📨 Task executada: {message}")
    return f"Processed: {message}"


@shared_task
def send_notification_email(user_id, notification_type, context):
    """
    Envia email de notificação de forma assíncrona.

    Args:
        user_id: ID do usuário
        notification_type: Tipo de notificação (new_post, reply, etc)
        context: Contexto adicional para o email
    """
    try:
        from django.contrib.auth.models import User
        from django.core.mail import send_mail
        from django.template.loader import render_to_string

        user = User.objects.get(id=user_id)

        # TODO: Implementar templates de email
        subject = f"CGBookStore - {notification_type}"
        message = render_to_string('emails/notification.html', context)

        send_mail(
            subject,
            message,
            'noreply@cgbookstore.com',
            [user.email],
            fail_silently=False,
        )

        logger.info(f"✅ Email enviado para {user.email}")
        return f"Email sent to {user.email}"
    except Exception as e:
        logger.error(f"❌ Erro ao enviar email: {e}")
        return f"Error: {e}"
