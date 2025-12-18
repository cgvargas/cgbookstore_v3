# core/views/tolkien_view.py
"""
View dedicada ao mundo de J.R.R. Tolkien (Autor em Destaque).
Exibe livros do autor e artigos relacionados.
Usa configurações do FeaturedAuthorSettings para personalização.
"""

from django.views.generic import TemplateView
from django.core.cache import cache
from django.db.models import Q
from django.shortcuts import redirect
from core.models import Book, Author, FeaturedAuthorSettings
from news.models import Article, Tag
import logging

logger = logging.getLogger(__name__)


class TolkienWorldView(TemplateView):
    """
    Página especial dedicada ao autor em destaque.
    Exibe todos os livros do autor e artigos relacionados.
    Usa configurações do FeaturedAuthorSettings para textos e SEO.
    """
    template_name = 'core/tolkien_world.html'
    
    # Cache timeout de 30 minutos
    CACHE_TIMEOUT = 1800

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Buscar configurações ativas
        settings = FeaturedAuthorSettings.get_active()
        
        if not settings:
            # Fallback: buscar autor Tolkien diretamente
            author = Author.objects.filter(
                Q(name__icontains='tolkien') | Q(name__icontains='j.r.r')
            ).first()
            settings = None
        else:
            author = settings.author
        
        cache_key = f'featured_author_page_{author.id if author else "none"}'
        cached_context = cache.get(cache_key)
        
        if cached_context:
            logger.info("[FEATURED_AUTHOR] Cache HIT")
            context.update(cached_context)
            context['settings'] = settings  # Settings sempre fresco
            return context
        
        logger.info("[FEATURED_AUTHOR] Cache MISS - construindo contexto...")
        
        # Buscar todos os livros do autor
        author_books = []
        if author:
            author_books = list(Book.objects.filter(
                author=author
            ).select_related('author', 'category').order_by('title'))
        
        # Buscar artigos com tag do autor
        author_articles = []
        if author:
            try:
                # Buscar tag pelo nome do autor
                author_tag = Tag.objects.filter(
                    Q(name__icontains=author.name.split()[-1]) |  # Sobrenome
                    Q(slug__icontains=author.name.split()[-1].lower())
                ).first()
                
                if author_tag:
                    author_articles = list(Article.objects.filter(
                        tags=author_tag,
                        is_published=True
                    ).select_related('category', 'author').order_by('-published_at')[:10])
            except Exception as e:
                logger.warning(f"[FEATURED_AUTHOR] Erro ao buscar artigos: {e}")
        
        # Estatísticas
        total_pages = sum(book.page_count or 0 for book in author_books)
        
        page_context = {
            'author': author,
            'tolkien_books': author_books,  # Retrocompatibilidade
            'author_books': author_books,
            'tolkien_articles': author_articles,  # Retrocompatibilidade
            'author_articles': author_articles,
            'books_count': len(author_books),
            'articles_count': len(author_articles),
            'total_pages': total_pages,
        }
        
        # Cachear contexto
        cache.set(cache_key, page_context, self.CACHE_TIMEOUT)
        
        context.update(page_context)
        context['settings'] = settings  # Settings sempre fresco para permitir edições
        return context

