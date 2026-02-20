# C:\Users\claud\OneDrive\ProjectsDjango\CGBookStore_v3\core\views\home_view.py

from django.views.generic import TemplateView
from django.utils import timezone
from django.db.models import Q, Prefetch
from django.core.cache import cache
from django.contrib.contenttypes.models import ContentType
from core.models import Section, SectionItem, Event, Book, Banner, Author, Video, FeaturedAuthorSettings
from news.models import Article
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

        # === BANNERS (Serializados como Dicts) ===
        start = time.time()
        banners_qs = list(Banner.objects.filter(active=True).filter(
            Q(start_date__isnull=True) | Q(start_date__lte=now)
        ).filter(
            Q(end_date__isnull=True) | Q(end_date__gte=now)
        ).order_by('order'))
        
        # OTIMIZAÇÃO: Serializar para dicts para pré-calcular .url e evitar chamadas de storage no template
        banners = []
        for b in banners_qs:
            banners.append({
                'id': b.id,
                'title': b.title,
                'subtitle': b.subtitle,
                'description': b.description,
                'height': b.height,
                'image': {'url': b.image.url} if b.image else None,  # Estrutura compatível com template {{ b.image.url }}
                'image_position_horizontal': b.image_position_horizontal,
                'image_position_vertical': b.image_position_vertical,
                'overlay_opacity': b.overlay_opacity,
                'blur_edges': b.blur_edges,
                'blur_intensity': b.blur_intensity,
                'link_url': b.link_url,
                'link_text': b.link_text,
                'open_in_new_tab': b.open_in_new_tab,
            })

        logger.info(f"[HOME] Banners: {len(banners)} (serialized) - {(time.time() - start)*1000:.0f}ms")

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

        # === SEÇÃO ESPECIAL: AUTOR EM DESTAQUE ===
        # Buscar configurações ativas de autor em destaque
        start = time.time()
        import random
        
        featured_author_settings = FeaturedAuthorSettings.get_active()
        featured_author_books = []
        
        if featured_author_settings and featured_author_settings.author:
            author = featured_author_settings.author
            # Buscar todos os IDs de livros do autor (query leve, sem join)
            author_book_ids = list(Book.objects.filter(
                author=author
            ).values_list('id', flat=True))
            
            # Aleatorizar em Python (instantâneo)
            if len(author_book_ids) > 12:
                author_book_ids = random.sample(author_book_ids, 12)
            
            # Buscar apenas os livros selecionados com dados completos
            featured_author_books = list(Book.objects.filter(
                id__in=author_book_ids
            ).select_related('author', 'category'))
            
            # Embaralhar resultado final
            random.shuffle(featured_author_books)
        
        logger.info(f"[HOME] Featured Author Books: {len(featured_author_books)} - {(time.time() - start)*1000:.0f}ms")

        # Montar contexto
        home_context = {
            'banners': banners,
            'sections': sections_data,
            'featured_event': featured_event,
            'featured_author': featured_author_settings,
            'featured_author_books': featured_author_books,
            # Manter tolkien_books para retrocompatibilidade
            'tolkien_books': featured_author_books,
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
        article_ids = set()

        # Obter content types (cached pelo Django)
        book_ct = ContentType.objects.get_for_model(Book)
        author_ct = ContentType.objects.get_for_model(Author)
        video_ct = ContentType.objects.get_for_model(Video)
        article_ct = ContentType.objects.get_for_model(Article)

        for section in sections:
            for item in section.items.all():
                if item.content_type_id == book_ct.id:
                    book_ids.add(item.object_id)
                elif item.content_type_id == author_ct.id:
                    author_ids.add(item.object_id)
                elif item.content_type_id == video_ct.id:
                    video_ids.add(item.object_id)
                elif item.content_type_id == article_ct.id:
                    article_ids.add(item.object_id)

        # Buscar TODOS os objetos de uma vez
        books_map = {}
        authors_map = {}
        videos_map = {}
        articles_map = {}

        if book_ids:
            # Otimização: usar only() para carregar apenas campos necessários
            # REMOVIDO 'cover' e 'discount_price' da lista
            books = Book.objects.filter(id__in=book_ids).select_related('category', 'author').only(
                'id', 'title', 'slug', 'price', 
                'category__name', 'author__name', 'author__slug'
            )
            books_map = {book.id: book for book in books}

        if author_ids:
            authors = Author.objects.filter(id__in=author_ids)
            authors_map = {author.id: author for author in authors}

        if video_ids:
            videos = Video.objects.filter(id__in=video_ids, active=True)
            videos_map = {video.id: video for video in videos}

        if article_ids:
            articles = Article.objects.filter(id__in=article_ids, is_published=True).select_related('category', 'author').only(
                'id', 'title', 'slug', 'excerpt', 'published_at',
                'category__name', 'category__slug', 'category__color',
                'author__username', 'featured_image'
            )
            articles_map = {article.id: article for article in articles}

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
                elif item.content_type_id == article_ct.id:
                    obj = articles_map.get(item.object_id)
                    obj_type = 'article'

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
            # Extrair URL do background se existir
            background_url = section.background_image.url if section.background_image else None

            section_dict = {
                'id': section.id,
                'title': section.title,
                'subtitle': section.subtitle,
                'content_type': section.content_type,
                'layout': section.layout,
                'css_class': section.css_class,
                'background_color': section.background_color,
                'background_image_url': background_url,
                'container_opacity': section.container_opacity,
                # Container background image settings
                'container_background_image_url': section.container_background_image.url if section.container_background_image else None,
                'container_background_image_opacity': section.container_background_image_opacity,
                'container_background_size': section.container_background_size,
                'container_background_position': section.container_background_position,
                # Banner settings
                'banner_image_url': banner_url,
                'banner_position_vertical': section.banner_position_vertical,
                'banner_position_horizontal': section.banner_position_horizontal,
                'banner_height': section.banner_height,
                'banner_overlay_opacity': section.banner_overlay_opacity,
                'banner_blur_edges': section.banner_blur_edges,
                'banner_blur_intensity': section.banner_blur_intensity,
                # Card style settings
                'card_style': section.card_style,
                'card_hover_effect': section.card_hover_effect,
                'custom_css': section.custom_css,
                # Display settings
                'show_price': section.show_price,
                'show_rating': section.show_rating,
                'show_author': section.show_author,
                'items_per_row': section.items_per_row,
                # Links
                'show_see_more': section.show_see_more,
                'see_more_url': section.see_more_url,
                # Items
                'items': items_data,
            }
            sections_data.append(section_dict)

        return sections_data