# C:\Users\claud\OneDrive\ProjectsDjango\CGBookStore_v3\core\views\home_view.py

from django.views.generic import TemplateView
from django.utils import timezone
from django.db.models import Q, Prefetch
from django.core.cache import cache
from django.contrib.contenttypes.models import ContentType
from core.models import Section, SectionItem, Event, Book, Banner, Author, Video
import logging
import time

logger = logging.getLogger(__name__)


class HomeView(TemplateView):
    """
    View para a página inicial.
    Exibe seções dinâmicas gerenciadas pelo admin e widget de evento.

    Otimizações aplicadas:
    - Cache de 30 minutos para contexto completo da home
    - Dados serializados como dicts para evitar N+1 queries após restaurar do cache
    - Pré-carregamento de TODOS os objetos em queries únicas
    """
    template_name = 'core/home.html'

    # Cache timeout em segundos (30 minutos)
    CACHE_TIMEOUT = 1800

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        start_total = time.time()

        # Tentar cache completo do contexto da home
        cache_key = 'home_full_context'
        cached_context = cache.get(cache_key)

        if cached_context is not None:
            logger.info(f"[HOME] Cache HIT - tempo: {(time.time() - start_total)*1000:.0f}ms")
            context.update(cached_context)
            return context

        logger.info("[HOME] Cache MISS - construindo contexto...")

        # === BANNERS ===
        start = time.time()
        banners = list(Banner.objects.filter(active=True).filter(
            Q(start_date__isnull=True) | Q(start_date__lte=now)
        ).filter(
            Q(end_date__isnull=True) | Q(end_date__gte=now)
        ).order_by('order'))
        logger.info(f"[HOME] Banners: {len(banners)} - {(time.time() - start)*1000:.0f}ms")

        # === SEÇÕES COM OBJETOS PRÉ-CARREGADOS (como dicts) ===
        start = time.time()
        sections_data = self._build_sections_as_dicts()
        logger.info(f"[HOME] Sections: {len(sections_data)} - {(time.time() - start)*1000:.0f}ms")

        # === EVENTO EM DESTAQUE ===
        start = time.time()
        featured_event = Event.objects.filter(
            active=True,
            featured=True,
            start_date__gt=now
        ).exclude(
            status='cancelled'
        ).order_by('start_date').first()
        logger.info(f"[HOME] Event: {'found' if featured_event else 'none'} - {(time.time() - start)*1000:.0f}ms")

        # Montar contexto
        home_context = {
            'banners': banners,
            'sections': sections_data,
            'featured_event': featured_event,
        }

        # Cachear contexto completo
        cache.set(cache_key, home_context, self.CACHE_TIMEOUT)
        logger.info(f"[HOME] Total build time: {(time.time() - start_total)*1000:.0f}ms")

        context.update(home_context)
        return context

    def _build_sections_as_dicts(self):
        """
        Constrói lista de seções como dicts serializáveis.
        Inclui todos os dados necessários para o template, evitando queries N+1 após cache.
        """
        start = time.time()

        # Buscar seções e items ativos apenas
        active_items = Prefetch(
            'items',
            queryset=SectionItem.objects.filter(active=True).select_related('content_type').order_by('order')
        )
        sections = list(Section.objects.filter(active=True).prefetch_related(
            active_items,
        ).order_by('order'))
        logger.debug(f"[HOME] Sections query: {(time.time() - start)*1000:.0f}ms")

        if not sections:
            return []

        # Coletar IDs por tipo de conteúdo
        book_ids = set()
        author_ids = set()
        video_ids = set()

        # Obter content types (cached pelo Django)
        book_ct = ContentType.objects.get_for_model(Book)
        author_ct = ContentType.objects.get_for_model(Author)
        video_ct = ContentType.objects.get_for_model(Video)

        for section in sections:
            for item in section.items.all():
                if item.content_type_id == book_ct.id:
                    book_ids.add(item.object_id)
                elif item.content_type_id == author_ct.id:
                    author_ids.add(item.object_id)
                elif item.content_type_id == video_ct.id:
                    video_ids.add(item.object_id)

        # Buscar TODOS os objetos de uma vez
        books_map = {}
        authors_map = {}
        videos_map = {}

        if book_ids:
            books = Book.objects.filter(id__in=book_ids).select_related('category', 'author')
            books_map = {book.id: book for book in books}

        if author_ids:
            authors = Author.objects.filter(id__in=author_ids)
            authors_map = {author.id: author for author in authors}

        if video_ids:
            videos = Video.objects.filter(id__in=video_ids)
            videos_map = {video.id: video for video in videos}

        # Construir estrutura de dados serializável
        sections_data = []
        for section in sections:
            items_data = []
            for item in section.items.all():
                # Obter objeto de conteúdo
                obj = None
                obj_type = None
                if item.content_type_id == book_ct.id:
                    obj = books_map.get(item.object_id)
                    obj_type = 'book'
                elif item.content_type_id == author_ct.id:
                    obj = authors_map.get(item.object_id)
                    obj_type = 'author'
                elif item.content_type_id == video_ct.id:
                    obj = videos_map.get(item.object_id)
                    obj_type = 'video'

                if obj is None:
                    continue

                # Calcular título de exibição
                if item.custom_title:
                    display_title = item.custom_title
                elif hasattr(obj, 'title') and obj.title:
                    display_title = obj.title
                elif hasattr(obj, 'name') and obj.name:
                    display_title = obj.name
                else:
                    display_title = str(obj)

                # Criar dict do item com dados já resolvidos
                item_dict = {
                    'id': item.id,
                    'display_title': display_title,
                    'custom_description': item.custom_description,
                    'obj_type': obj_type,
                    'obj': obj,
                }
                items_data.append(item_dict)

            # Extrair URL do banner se existir
            banner_url = section.banner_image.url if section.banner_image else None

            section_dict = {
                'id': section.id,
                'title': section.title,
                'subtitle': section.subtitle,
                'content_type': section.content_type,
                'layout': section.layout,
                'css_class': section.css_class,
                'background_color': section.background_color,
                'banner_image_url': banner_url,
                'container_opacity': section.container_opacity,
                'show_see_more': section.show_see_more,
                'see_more_url': section.see_more_url,
                'items': items_data,
            }
            sections_data.append(section_dict)

        return sections_data