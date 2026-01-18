# core/views/universe_view.py
"""
View dinâmica para Universos Literários.
Exibe página temática de um autor e seu universo de obras.
"""

from django.views.generic import DetailView
from django.core.cache import cache
from django.db.models import Q
from django.http import Http404

from core.models import LiteraryUniverse, Book
import logging

logger = logging.getLogger(__name__)


class LiteraryUniverseView(DetailView):
    """
    View genérica para qualquer universo literário.
    Exibe livros, artigos, vídeos e conteúdo do universo.
    """
    
    model = LiteraryUniverse
    template_name = 'core/literary_universe.html'
    context_object_name = 'universe'
    
    # Cache de 30 minutos
    CACHE_TIMEOUT = 1800
    
    def get_queryset(self):
        """Retorna apenas universos ativos."""
        return LiteraryUniverse.objects.filter(
            is_active=True
        ).select_related('author')
    
    def get_object(self, queryset=None):
        """Busca o universo pelo slug."""
        if queryset is None:
            queryset = self.get_queryset()
        
        slug = self.kwargs.get('slug')
        
        try:
            obj = queryset.get(slug=slug)
        except LiteraryUniverse.DoesNotExist:
            raise Http404("Universo não encontrado")
        
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        universe = self.object
        
        # Cache key baseada no universo
        cache_key = f'literary_universe_{universe.slug}'
        cached_context = cache.get(cache_key)
        
        if cached_context:
            logger.info(f"[UNIVERSE:{universe.slug}] Cache HIT")
            context.update(cached_context)
            return context
        
        logger.info(f"[UNIVERSE:{universe.slug}] Cache MISS - construindo contexto...")
        
        # === LIVROS DO AUTOR ===
        author_books = list(Book.objects.filter(
            author=universe.author
        ).select_related('author', 'category').order_by('title'))
        
        # === ARTIGOS RELACIONADOS ===
        # Combina artigos selecionados manualmente + artigos por tag do autor
        author_articles = []
        manual_article_ids = set()
        
        try:
            from news.models import Article, Tag
            
            # 1. Artigos selecionados manualmente no admin
            manual_articles = list(universe.articles.filter(is_published=True))
            author_articles.extend(manual_articles)
            manual_article_ids = set(a.id for a in manual_articles)
            
            # 2. Artigos por tag com sobrenome do autor (excluindo os já adicionados)
            author_surname = universe.author.name.split()[-1]
            author_tag = Tag.objects.filter(
                Q(name__icontains=author_surname) |
                Q(slug__icontains=author_surname.lower())
            ).first()
            
            if author_tag:
                auto_articles = Article.objects.filter(
                    tags=author_tag,
                    is_published=True
                ).exclude(
                    id__in=manual_article_ids
                ).select_related('category').order_by('-published_at')[:10]
                author_articles.extend(list(auto_articles))
                
        except Exception as e:
            logger.warning(f"[UNIVERSE:{universe.slug}] Erro ao buscar artigos: {e}")
        
        # === VÍDEOS ===
        all_videos = list(universe.get_all_videos())
        
        # === CONTEÚDO ADICIONAL ===
        games = list(universe.content_items.filter(
            content_type='game', is_active=True
        ).order_by('display_order'))
        
        adaptations = list(universe.content_items.filter(
            content_type='adaptation', is_active=True
        ).order_by('display_order'))
        
        podcasts = list(universe.content_items.filter(
            content_type='podcast', is_active=True
        ).order_by('display_order'))
        
        other_content = list(universe.content_items.filter(
            is_active=True
        ).exclude(
            content_type__in=['game', 'adaptation', 'podcast']
        ).order_by('display_order'))
        
        # === BANNERS POR POSIÇÃO ===
        banners_after_hero = list(universe.get_active_banners('after_hero'))
        banners_before_books = list(universe.get_active_banners('before_books'))
        banners_after_books = list(universe.get_active_banners('after_books'))
        banners_before_articles = list(universe.get_active_banners('before_articles'))
        banners_after_articles = list(universe.get_active_banners('after_articles'))
        banners_before_videos = list(universe.get_active_banners('before_videos'))
        banners_after_videos = list(universe.get_active_banners('after_videos'))
        banners_footer = list(universe.get_active_banners('footer'))
        
        # === ESTATÍSTICAS ===
        total_pages = sum(book.page_count or 0 for book in author_books)
        
        # Contexto para cache
        page_context = {
            'author': universe.author,
            'author_books': author_books,
            'books_count': len(author_books),
            'author_articles': author_articles,
            'articles_count': len(author_articles),
            'videos': all_videos,
            'videos_count': len(all_videos),
            'games': games,
            'adaptations': adaptations,
            'podcasts': podcasts,
            'other_content': other_content,
            'total_pages': total_pages,
            # Banners
            'banners_after_hero': banners_after_hero,
            'banners_before_books': banners_before_books,
            'banners_after_books': banners_after_books,
            'banners_before_articles': banners_before_articles,
            'banners_after_articles': banners_after_articles,
            'banners_before_videos': banners_before_videos,
            'banners_after_videos': banners_after_videos,
            'banners_footer': banners_footer,
        }
        
        # Cachear
        cache.set(cache_key, page_context, self.CACHE_TIMEOUT)
        
        context.update(page_context)
        return context
