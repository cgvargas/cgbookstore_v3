from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, StreamingHttpResponse
from django.db.models import Q
from django.core.paginator import Paginator
import requests

from .models import EBook, UserLibrary, UserBookProgress, ReaderSettings


def library_view(request):
    """Página principal da biblioteca de e-books."""
    ebooks = EBook.objects.filter(is_active=True)
    
    # Filtros
    source = request.GET.get('source')
    language = request.GET.get('language')
    search = request.GET.get('q')
    
    if source:
        ebooks = ebooks.filter(source=source)
    if language:
        ebooks = ebooks.filter(language=language)
    if search:
        ebooks = ebooks.filter(
            Q(title__icontains=search) | 
            Q(author__icontains=search)
        )
    
    # Ordenação
    order = request.GET.get('order', '-created_at')
    ebooks = ebooks.order_by(order)
    
    # Paginação
    paginator = Paginator(ebooks, 24)
    page = request.GET.get('page', 1)
    ebooks = paginator.get_page(page)
    
    # Livros na biblioteca do usuário (para marcar favoritos)
    user_library_ids = []
    if request.user.is_authenticated:
        user_library_ids = list(
            UserLibrary.objects.filter(user=request.user)
            .values_list('ebook_id', flat=True)
        )
    
    context = {
        'ebooks': ebooks,
        'user_library_ids': user_library_ids,
        'sources': EBook.SOURCE_CHOICES,
        'languages': EBook.LANGUAGE_CHOICES,
        'current_source': source,
        'current_language': language,
        'search_query': search,
    }
    return render(request, 'ereader/library.html', context)


def search_books_view(request):
    """Busca de livros nas APIs externas."""
    query = request.GET.get('q', '')
    source = request.GET.get('source', 'gutenberg')
    
    context = {
        'query': query,
        'source': source,
    }
    return render(request, 'ereader/search.html', context)


@login_required
def my_library_view(request):
    """Biblioteca pessoal do usuário."""
    library_items = UserLibrary.objects.filter(user=request.user).select_related('ebook')
    
    # Progresso de leitura
    progress_dict = {}
    progress_items = UserBookProgress.objects.filter(
        user=request.user,
        ebook__in=[item.ebook for item in library_items]
    )
    for p in progress_items:
        progress_dict[p.ebook_id] = p
    
    context = {
        'library_items': library_items,
        'progress_dict': progress_dict,
    }
    return render(request, 'ereader/my_library.html', context)


def book_detail_view(request, book_id):
    """Detalhes de um livro."""
    ebook = get_object_or_404(EBook, id=book_id, is_active=True)
    
    # Incrementar contador de visualizações
    ebook.view_count += 1
    ebook.save(update_fields=['view_count'])
    
    # Verificar se está na biblioteca do usuário
    in_library = False
    progress = None
    if request.user.is_authenticated:
        in_library = UserLibrary.objects.filter(
            user=request.user, ebook=ebook
        ).exists()
        progress = UserBookProgress.objects.filter(
            user=request.user, ebook=ebook
        ).first()
    
    # Livros relacionados (mesmo autor ou assuntos)
    related_books = EBook.objects.filter(
        is_active=True
    ).filter(
        Q(author=ebook.author) | Q(subjects__overlap=ebook.subjects)
    ).exclude(id=ebook.id)[:6]
    
    context = {
        'ebook': ebook,
        'in_library': in_library,
        'progress': progress,
        'related_books': related_books,
    }
    return render(request, 'ereader/book_detail.html', context)


@login_required
def reader_view(request, book_id):
    """Página do leitor RetroReader."""
    from django.urls import reverse
    import json
    
    ebook = get_object_or_404(EBook, id=book_id, is_active=True)
    
    # Obter ou criar progresso
    progress, created = UserBookProgress.objects.get_or_create(
        user=request.user,
        ebook=ebook
    )
    
    # Obter configurações do leitor
    settings, _ = ReaderSettings.objects.get_or_create(user=request.user)
    
    # Adicionar à biblioteca automaticamente se ainda não estiver
    UserLibrary.objects.get_or_create(user=request.user, ebook=ebook)
    
    # Build EBOOK_DATA as a Python dict for safe JSON rendering
    ebook_data_json = json.dumps({
        'id': ebook.id,
        'title': ebook.title,
        'author': ebook.author,
        'epubUrl': reverse('ereader:epub_proxy', args=[ebook.id]),
        'savedProgress': {
            'cfi': progress.current_cfi or '',
            'percentage': float(progress.percentage),
        },
        'apiUrls': {
            'saveProgress': reverse('ereader_api:save_progress', args=[ebook.id]),
            'getProgress': reverse('ereader_api:progress', args=[ebook.id]),
            'bookmarks': reverse('ereader_api:book_bookmarks', args=[ebook.id]),
            'createBookmark': reverse('ereader_api:create_bookmark'),
            'deleteBookmarkBase': '/api/ereader/bookmarks/',
            'highlights': reverse('ereader_api:book_highlights', args=[ebook.id]),
            'createHighlight': reverse('ereader_api:create_highlight'),
            'notes': reverse('ereader_api:book_notes', args=[ebook.id]),
            'createNote': reverse('ereader_api:create_note'),
            'settings': reverse('ereader_api:settings'),
        },
    })
    
    context = {
        'ebook': ebook,
        'progress': progress,
        'settings': settings,
        'ebook_data_json': ebook_data_json,
    }
    return render(request, 'ereader/reader.html', context)


@login_required
def add_to_library(request, book_id):
    """Adiciona livro à biblioteca do usuário."""
    if request.method == 'POST':
        ebook = get_object_or_404(EBook, id=book_id, is_active=True)
        UserLibrary.objects.get_or_create(user=request.user, ebook=ebook)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'Livro adicionado à biblioteca!'})
        
        messages.success(request, f'"{ebook.title}" adicionado à sua biblioteca!')
        return redirect('ereader:book_detail', book_id=book_id)
    
    return redirect('ereader:library')


@login_required
def remove_from_library(request, book_id):
    """Remove livro da biblioteca do usuário."""
    if request.method == 'POST':
        UserLibrary.objects.filter(user=request.user, ebook_id=book_id).delete()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'Livro removido da biblioteca!'})
        
        messages.success(request, 'Livro removido da sua biblioteca!')
        return redirect('ereader:my_library')
    
    return redirect('ereader:library')


def epub_proxy(request, book_id):
    """
    Proxy para servir EPUBs de fontes externas.
    Resolve problemas de CORS ao baixar o EPUB e servir localmente.
    """
    ebook = get_object_or_404(EBook, id=book_id, is_active=True)
    
    epub_url = ebook.get_epub_url()
    if not epub_url:
        return HttpResponse('EPUB não disponível', status=404)
    
    # Se for arquivo local, redirecionar
    # Se for arquivo local, servir diretamente via Django
    if epub_url.startswith('/'):
        try:
            from django.conf import settings
            import os
            
            # Remover MEDIA_URL do início para obter caminho relativo
            if epub_url.startswith(settings.MEDIA_URL):
                rel_path = epub_url[len(settings.MEDIA_URL):]
            else:
                rel_path = epub_url.lstrip('/')
                
            file_path = os.path.join(settings.MEDIA_ROOT, rel_path)
            
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    file_content = f.read()
                
                # Validar que é um ZIP/EPUB (magic bytes: PK)
                if not file_content[:2] == b'PK':
                    return HttpResponse(
                        'Arquivo não é um EPUB válido. O arquivo pode ser um .mobi que não foi convertido. '
                        'Delete o livro e faça upload de um arquivo .epub.',
                        status=400
                    )
                    
                response = HttpResponse(file_content, content_type='application/epub+zip')
                response['Content-Disposition'] = f'inline; filename="{os.path.basename(file_path)}"'
                response['Access-Control-Allow-Origin'] = '*'
                return response
            else:
                 return HttpResponse(f'Arquivo local não encontrado: {file_path}', status=404)
        except Exception as e:
            return HttpResponse(f'Erro ao ler arquivo local: {str(e)}', status=500)
    
    try:
        # Baixar o EPUB do servidor remoto
        response = requests.get(epub_url, timeout=30, stream=True)
        response.raise_for_status()
        
        content = response.content
        
        # Validar que é um ZIP/EPUB (magic bytes: PK)
        if not content[:2] == b'PK':
            return HttpResponse(
                'Arquivo baixado não é um EPUB válido (formato ZIP). '
                'O arquivo pode ser um .mobi que não foi convertido corretamente. '
                'Delete o livro e faça upload de um arquivo .epub.',
                status=400
            )
        
        # Criar resposta
        django_response = HttpResponse(
            content,
            content_type='application/epub+zip'
        )
        django_response['Content-Disposition'] = f'inline; filename="{ebook.external_id or ebook.id}.epub"'
        django_response['Access-Control-Allow-Origin'] = '*'
        
        return django_response
        
    except requests.RequestException as e:
        return HttpResponse(f'Erro ao baixar EPUB: {str(e)}', status=502)

def debug_env_view(request):
    """View para diagnosticar ambiente de produção"""
    import sys
    import pkg_resources
    
    info = []
    info.append(f"<h1>Diagnóstico de Ambiente</h1>")
    info.append(f"<strong>Python Version:</strong> {sys.version}")
    info.append(f"<strong>Platform:</strong> {sys.platform}")
    
    try:
        import mobi
        info.append(f"<div style='color:green'><strong>Mobi Library:</strong> IMPORT SUCCESS - {mobi}</div>")
    except Exception as e:
        info.append(f"<div style='color:red'><strong>Mobi Library:</strong> IMPORT FAILED - {e}</div>")
        
    try:
        dist = pkg_resources.get_distribution("mobi")
        info.append(f"<strong>Mobi Package Info:</strong> {dist} - Location: {dist.location}")
    except Exception as e:
        info.append(f"<strong>Mobi Package Info:</strong> Failed to get info - {e}")

    try:
        dist = pkg_resources.get_distribution("ebooklib")
        info.append(f"<strong>EbookLib Info:</strong> {dist}")
    except Exception as e:
        info.append(f"<strong>EbookLib Info:</strong> Failed to get info - {e}")
        
    return HttpResponse("<br><br>".join(info))
