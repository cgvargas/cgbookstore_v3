"""
Signals para invalidar cache da home page quando dados relevantes mudam.

IMPORTANTE: Não invalidar em updates de contadores (views, clicks) pois
são operações frequentes que não afetam o conteúdo exibido.
"""
from django.db.models.signals import post_save, post_delete, pre_delete
from django.db.backends.signals import connection_created
from django.dispatch import receiver
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

# Campos que, quando alterados sozinhos, NÃO devem invalidar o cache
BANNER_COUNTER_FIELDS = {'views_count', 'clicks_count', 'updated_at'}


def invalidate_home_cache():
    """Invalida o cache da home page (público e chaves de usuários)."""
    cache.delete('home_full_context')
    if hasattr(cache, 'delete_pattern'):
        try:
            cache.delete_pattern('home_context_user_*')
            logger.info("[CACHE] Pattern home_context_user_* deletado")
        except Exception as e:
            logger.warning(f"[CACHE] Falha ao rodar delete_pattern: {e}")
            cache.clear()
    else:
        cache.clear()
        logger.info("[CACHE] Todo o cache foi limpo (fallback)")
    logger.info("[CACHE] Home cache invalidado")


# ==============================================================================
# SIGNALS DE CACHE — Invalidação da home page
# ==============================================================================

@receiver(post_save, sender='core.Section')
@receiver(post_delete, sender='core.Section')
def section_changed(sender, **kwargs):
    """Invalida cache quando Section muda."""
    invalidate_home_cache()


@receiver(post_save, sender='core.SectionItem')
@receiver(post_delete, sender='core.SectionItem')
def section_item_changed(sender, **kwargs):
    """Invalida cache quando SectionItem muda."""
    invalidate_home_cache()


@receiver(post_save, sender='core.Banner')
def banner_saved(sender, instance, **kwargs):
    """
    Invalida cache quando Banner muda, mas ignora updates de contadores.
    """
    # Se update_fields foi especificado, verificar se são apenas contadores
    update_fields = kwargs.get('update_fields')
    if update_fields is not None:
        # Se TODOS os campos atualizados são contadores, não invalidar
        if set(update_fields).issubset(BANNER_COUNTER_FIELDS):
            return

    invalidate_home_cache()


@receiver(post_delete, sender='core.Banner')
def banner_deleted(sender, **kwargs):
    """Invalida cache quando Banner é deletado."""
    invalidate_home_cache()


@receiver(post_save, sender='core.Event')
@receiver(post_delete, sender='core.Event')
def event_changed(sender, **kwargs):
    """Invalida cache quando Event muda."""
    invalidate_home_cache()


@receiver(post_save, sender='core.Video')
@receiver(post_delete, sender='core.Video')
def video_changed(sender, **kwargs):
    """Invalida cache quando Video muda (ex: nova thumbnail)."""
    invalidate_home_cache()


# ==============================================================================
# SIGNALS DE BOOK — R2 Assíncrono + Cache
# ==============================================================================

@receiver(pre_delete, sender='core.Book', dispatch_uid='book_pre_delete_r2_async')
def book_pre_delete_capture_files(sender, instance, **kwargs):
    """
    Captura o nome do arquivo ANTES da deleção e zera o campo.

    Isso impede que o django_cleanup faça a chamada HTTP síncrona ao R2
    durante o request do admin (que causava ~1.5s de latência).

    O arquivo capturado será deletado de forma assíncrona via Celery
    no signal post_delete abaixo.
    """
    # Capturar o nome do arquivo antes de ser zerado
    cover_name = None
    if instance.cover_image and instance.cover_image.name:
        cover_name = instance.cover_image.name

    # Guardar no objeto para usar no post_delete
    # (o objeto instance é passado para os receivers na mesma thread)
    instance._pending_file_delete = cover_name

    # Zerar o campo para que o django_cleanup não encontre arquivo para deletar
    # (evita a chamada HTTP síncrona ao R2 durante o request)
    if cover_name:
        instance.cover_image = None
        logger.debug(f"[STORAGE] Arquivo capturado para deleção async: {cover_name}")


@receiver(post_delete, sender='core.Book', dispatch_uid='book_post_delete_cache_and_r2')
def book_post_delete(sender, instance, **kwargs):
    """
    Após deleção do Book:
    1. Agenda deleção do arquivo R2 via Celery (assíncrono, não bloqueia o request)
    2. Invalida o cache da home page
    """
    # Deletar arquivo do R2 de forma assíncrona
    file_name = getattr(instance, '_pending_file_delete', None)
    if file_name:
        try:
            from core.tasks import delete_storage_file
            delete_storage_file.delay(file_name)
            logger.info(f"[STORAGE] Task agendada para deletar: {file_name}")
        except Exception as e:
            # Fallback: logar mas não bloquear o response
            logger.error(f"[STORAGE] ❌ Falha ao agendar task de deleção: {e}")

    # Invalidar cache da home
    invalidate_home_cache()


@receiver(post_save, sender='core.Book')
def book_changed(sender, **kwargs):
    """Invalida cache quando Book muda."""
    invalidate_home_cache()


@receiver(post_save, sender='core.Author')
@receiver(post_delete, sender='core.Author')
def author_changed(sender, **kwargs):
    """Invalida cache quando Author muda."""
    invalidate_home_cache()


@receiver(post_save, sender='news.Article')
@receiver(post_delete, sender='news.Article')
def news_article_changed(sender, **kwargs):
    """Invalida cache quando um artigo de notícias muda ou é deletado."""
    invalidate_home_cache()


@receiver(post_save, sender='news.Category')
@receiver(post_delete, sender='news.Category')
def news_category_changed(sender, **kwargs):
    """Invalida cache quando uma categoria de notícias muda ou é deletada."""
    invalidate_home_cache()


# ==============================================================================
# SIGNAL DE DB — Statement Timeout por Conexão
# ==============================================================================

@receiver(connection_created)
def set_db_statement_timeout(sender, connection, **kwargs):
    """
    Define statement_timeout para cada nova conexão PostgreSQL.

    POR QUÊ AQUI e não em settings.py OPTIONS:
    O Supabase usa PgBouncer em transaction mode, onde comandos SET
    não persistem entre transações. Este signal roda a cada nova conexão
    obtida do pool, garantindo que o timeout seja aplicado via SQL real.

    Timeout: 25s (antes do timeout do Gunicorn de 30s)
    """
    if connection.vendor == 'postgresql':
        try:
            with connection.cursor() as cursor:
                cursor.execute("SET statement_timeout = '25000'")  # 25 segundos em ms
            logger.debug("[DB] statement_timeout=25s aplicado via connection_created")
        except Exception as e:
            logger.warning(f"[DB] Falha ao aplicar statement_timeout: {e}")

