"""
View de autocomplete para admin de Section Items.
Busca livros, autores e vídeos por nome via AJAX.
"""
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q
from core.models import Book, Author, Video
from news.models import Article


@staff_member_required
def section_item_autocomplete(request):
    """
    Endpoint de autocomplete para buscar items por nome.
    
    Parâmetros GET:
    - q: termo de busca
    - content_type: 'book', 'author' ou 'video'
    
    Retorna JSON com lista de {id, text} para Select2.
    """
    query = request.GET.get('q', '').strip()
    content_type = request.GET.get('content_type', '').lower()
    
    if not query or len(query) < 2:
        return JsonResponse({'results': []})
    
    results = []
    
    if content_type == 'book':
        books = Book.objects.filter(
            Q(title__icontains=query) | 
            Q(author__name__icontains=query)
        ).select_related('author').order_by('title')[:20]
        
        results = [
            {
                'id': book.id,
                'text': f"{book.title} - {book.author.name if book.author else 'Sem autor'}"
            }
            for book in books
        ]
    
    elif content_type == 'author':
        authors = Author.objects.filter(
            name__icontains=query
        ).order_by('name')[:20]
        
        results = [
            {'id': author.id, 'text': author.name}
            for author in authors
        ]
    
    elif content_type == 'video':
        videos = Video.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query)
        ).order_by('title')[:20]
        
        results = [
            {'id': video.id, 'text': video.title}
            for video in videos
        ]
    
    elif content_type == 'article':
        articles = Article.objects.filter(
            title__icontains=query
        ).order_by('-published_at', '-created_at')[:20]
        
        results = [
            {'id': article.id, 'text': article.title}
            for article in articles
        ]
    
    return JsonResponse({'results': results})
