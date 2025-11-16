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
        notification_type: Tipo de notificação (new_post, reply, comment, mention, etc)
        context: Contexto adicional para o email (deve incluir campos como
                 notification_title, notification_message, action_url, etc)
    """
    try:
        from django.contrib.auth.models import User
        from django.core.mail import EmailMultiAlternatives
        from django.template.loader import render_to_string
        from django.conf import settings

        user = User.objects.get(id=user_id)

        # Adicionar usuário ao contexto
        context['user'] = user

        # Mapear tipos de notificação para emojis e títulos padrão
        notification_defaults = {
            'new_post': {
                'emoji': '📝',
                'title': 'Nova Publicação'
            },
            'reply': {
                'emoji': '💬',
                'title': 'Nova Resposta'
            },
            'comment': {
                'emoji': '💬',
                'title': 'Novo Comentário'
            },
            'mention': {
                'emoji': '👤',
                'title': 'Você foi mencionado'
            },
            'like': {
                'emoji': '❤️',
                'title': 'Nova Curtida'
            },
            'follow': {
                'emoji': '👥',
                'title': 'Novo Seguidor'
            },
            'book_recommendation': {
                'emoji': '📚',
                'title': 'Nova Recomendação de Livro'
            },
        }

        # Aplicar valores padrão se não fornecidos no contexto
        if notification_type in notification_defaults:
            context.setdefault('notification_emoji',
                             notification_defaults[notification_type]['emoji'])
            context.setdefault('notification_title',
                             notification_defaults[notification_type]['title'])

        # Renderizar subject
        subject = render_to_string('emails/notification_subject.txt', context)
        subject = ' '.join(subject.splitlines()).strip()

        # Renderizar corpo do email (HTML e texto)
        html_body = render_to_string('emails/notification.html', context)
        text_body = render_to_string('emails/notification.txt', context)

        # Criar email com HTML e alternativa texto
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_body,  # Corpo em texto simples (fallback)
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@cgbookstore.com'),
            to=[user.email]
        )
        msg.attach_alternative(html_body, "text/html")  # Versão HTML
        msg.send()

        logger.info(f"✅ Email de notificação '{notification_type}' enviado para {user.email}")
        return f"Email sent to {user.email}"
    except Exception as e:
        logger.error(f"❌ Erro ao enviar email de notificação: {e}")
        return f"Error: {e}"
