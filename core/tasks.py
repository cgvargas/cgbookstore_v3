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



@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def delete_storage_file(self, file_name: str, storage_backend: str = 'default'):
    """
    Deleta um arquivo do storage (Cloudflare R2 ou outro backend) de forma assíncrona.

    Desacopla a deleção de arquivos do ciclo de vida da requisição Django,
    evitando que chamadas HTTP ao R2 adicionem latência ao response do admin.

    Args:
        file_name: Path do arquivo no storage (ex: 'books/covers/livro.jpg')
        storage_backend: Nome do backend de storage (padrão: 'default')

    Retry: até 3 vezes com intervalo de 30s em caso de falha de rede.
    """
    if not file_name:
        logger.debug("[STORAGE] delete_storage_file chamada com file_name vazio, ignorando.")
        return "skipped: empty file_name"

    try:
        from django.core.files.storage import storages
        storage = storages[storage_backend]
        if storage.exists(file_name):
            storage.delete(file_name)
            logger.info(f"[STORAGE] ✅ Arquivo deletado do R2: {file_name}")
            return f"deleted: {file_name}"
        else:
            logger.info(f"[STORAGE] Arquivo não encontrado no R2 (já deletado?): {file_name}")
            return f"not_found: {file_name}"
    except Exception as exc:
        logger.error(f"[STORAGE] ❌ Erro ao deletar '{file_name}': {exc}")
        raise self.retry(exc=exc)




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
