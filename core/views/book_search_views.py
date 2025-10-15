"""
Views para busca e importação de livros do Google Books (user-facing).
Permite que usuários comuns busquem e adicionem livros à sua biblioteca.
"""

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404
from django.utils.text import slugify
from core.utils.google_books_api import (
    search_books,
    get_book_by_id,
    download_cover,
    parse_google_books_date
)
from core.models import Book, Author, Category
import json


@login_required
@require_http_methods(["GET"])
def google_books_search_user(request):
    """
    Busca livros no Google Books API para usuários.

    Parâmetros GET:
    - q (str): Termo de busca geral
    - max_results (int, opcional): Número máximo de resultados (padrão: 10)
    - start_index (int, opcional): Índice inicial para paginação (padrão: 0)

    Retorna JSON:
    - success (bool): Se a operação foi bem-sucedida
    - total_items (int): Total de resultados encontrados
    - books (list): Lista de livros [{google_book_id, title, authors, ...}]
    - message (str, opcional): Mensagem de erro
    """
    try:
        query = request.GET.get('q', '').strip()

        if not query:
            return JsonResponse({
                'success': False,
                'message': 'Termo de busca não fornecido.'
            }, status=400)

        # Parâmetros de paginação
        max_results = int(request.GET.get('max_results', 10))
        start_index = int(request.GET.get('start_index', 0))

        # Limitar max_results para evitar sobrecarga
        max_results = min(max_results, 20)

        # Buscar no Google Books
        results = search_books(
            query=query,
            max_results=max_results,
            start_index=start_index
        )

        # Verificar erros
        if 'error' in results:
            return JsonResponse({
                'success': False,
                'message': results['error']
            }, status=500)

        # Verificar se há resultados
        if not results.get('books'):
            return JsonResponse({
                'success': True,
                'total_items': 0,
                'books': [],
                'message': 'Nenhum livro encontrado. Tente outros termos.'
            })

        # Processar resultados para incluir informações úteis
        processed_books = []
        for book in results['books']:
            # Verificar se livro já existe no catálogo local
            isbn = book.get('isbn_13') or book.get('isbn_10')
            exists_in_catalog = False
            local_book_id = None

            if isbn:
                local_book = Book.objects.filter(isbn=isbn).first()
                if local_book:
                    exists_in_catalog = True
                    local_book_id = local_book.id

            # Adicionar flags úteis
            book['exists_in_catalog'] = exists_in_catalog
            book['local_book_id'] = local_book_id

            processed_books.append(book)

        return JsonResponse({
            'success': True,
            'total_items': results.get('total_items', 0),
            'books': processed_books
        })

    except ValueError as e:
        return JsonResponse({
            'success': False,
            'message': 'Parâmetros inválidos.'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao buscar livros: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["POST"])
def import_google_book_user(request, google_book_id):
    """
    Importa um livro do Google Books para o catálogo local.
    Qualquer usuário autenticado pode importar livros.

    Parâmetros:
    - google_book_id (str): ID do livro no Google Books (via URL)

    Retorna JSON:
    - success (bool): Se a operação foi bem-sucedida
    - message (str): Mensagem de feedback
    - book_id (int): ID do livro no catálogo local
    - book_title (str): Título do livro
    - already_existed (bool): Se o livro já existia no catálogo
    """
    try:
        # Buscar dados do livro no Google Books
        book_data = get_book_by_id(google_book_id)

        if not book_data:
            return JsonResponse({
                'success': False,
                'message': 'Não foi possível obter dados do livro no Google Books.'
            }, status=404)

        # Verificar se já existe pelo ISBN
        isbn = book_data.get('isbn_13') or book_data.get('isbn_10')

        if isbn:
            existing_book = Book.objects.filter(isbn=isbn).first()
            if existing_book:
                return JsonResponse({
                    'success': True,
                    'message': f'Livro já existe no catálogo!',
                    'book_id': existing_book.id,
                    'book_title': existing_book.title,
                    'already_existed': True
                })

        # Verificar se já existe pelo título (fallback se não tiver ISBN)
        title = book_data.get('title')
        if not isbn and title:
            existing_book = Book.objects.filter(title__iexact=title).first()
            if existing_book:
                return JsonResponse({
                    'success': True,
                    'message': f'Livro já existe no catálogo!',
                    'book_id': existing_book.id,
                    'book_title': existing_book.title,
                    'already_existed': True
                })

        # Criar/buscar autor
        author = None
        authors_list = book_data.get('authors', [])
        if authors_list:
            author_name = authors_list[0]  # Pegar primeiro autor
            author, created = Author.objects.get_or_create(
                name=author_name,
                defaults={
                    'slug': slugify(author_name),
                    'bio': f'Autor(a) de {title}'
                }
            )

        # Criar/buscar categoria
        category = None
        categories_list = book_data.get('categories', [])
        if categories_list:
            category_name = categories_list[0]  # Pegar primeira categoria
            category, created = Category.objects.get_or_create(
                name=category_name,
                defaults={'slug': slugify(category_name)}
            )

        # Criar livro no catálogo local
        book = Book.objects.create(
            title=title,
            subtitle=book_data.get('subtitle', ''),
            slug=slugify(title),
            author=author,
            category=category,
            publisher=book_data.get('publisher', ''),
            publication_date=parse_google_books_date(book_data.get('published_date')),
            isbn=isbn or '',
            page_count=book_data.get('page_count'),
            language=book_data.get('language', 'pt-BR'),
            description=book_data.get('description', ''),
            price=book_data.get('price') or None,
            average_rating=book_data.get('average_rating', 0.0),
            ratings_count=book_data.get('ratings_count', 0),
            preview_link=book_data.get('preview_link', ''),
            info_link=book_data.get('info_link', ''),
            google_books_id=google_book_id
        )

        # Baixar capa (assíncrono, não bloqueia a resposta)
        thumbnail = book_data.get('thumbnail')
        if thumbnail:
            cover_path = download_cover(thumbnail, book.slug)
            if cover_path:
                book.cover_image = cover_path
                book.save()

        return JsonResponse({
            'success': True,
            'message': f'"{book.title}" importado com sucesso!',
            'book_id': book.id,
            'book_title': book.title,
            'already_existed': False
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao importar livro: {str(e)}'
        }, status=500)