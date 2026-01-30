"""
Signals para invalidar cache da home page quando dados relevantes mudam.

IMPORTANTE: Não invalidar em updates de contadores (views, clicks) pois
são operações frequentes que não afetam o conteúdo exibido.
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

# Campos que, quando alterados sozinhos, NÃO devem invalidar o cache
BANNER_COUNTER_FIELDS = {'views_count', 'clicks_count', 'updated_at'}


def invalidate_home_cache():
    """Invalida o cache da home page."""
    cache.delete('home_full_context')
    logger.info("[CACHE] Home cache invalidado")


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


@receiver(post_save, sender='core.Book')
@receiver(post_delete, sender='core.Book')
def book_changed(sender, **kwargs):
    """Invalida cache quando Book muda."""
    invalidate_home_cache()


@receiver(post_save, sender='core.Author')
@receiver(post_delete, sender='core.Author')
def author_changed(sender, **kwargs):
    """Invalida cache quando Author muda."""
    invalidate_home_cache()
