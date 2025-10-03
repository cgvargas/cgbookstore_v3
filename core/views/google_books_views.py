"""
Views para integração com Google Books no Admin.
"""

from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from core.utils.google_books_api import search_books, download_cover
from core.models import Book, Author, Category
from django.utils.text import slugify


@staff_member_required
def google_books_search(request):
    """
    View para buscar livros no Google Books.
    """
    results = None
    query_params = {}

    if request.method == 'GET' and any(request.GET.get(k) for k in ['title', 'author', 'isbn', 'publisher', 'query']):
        # Coletar parâmetros
        title = request.GET.get('title', '').strip()
        author = request.GET.get('author', '').strip()
        isbn = request.GET.get('isbn', '').strip()
        publisher = request.GET.get('publisher', '').strip()
        query = request.GET.get('query', '').strip()
        max_results = 10  # Fixo em 10 por página
        page = int(request.GET.get('page', 1))
        start_index = (page - 1) * max_results

        # Guardar params para o form
        query_params = {
            'title': title,
            'author': author,
            'isbn': isbn,
            'publisher': publisher,
            'query': query,
            'page': page
        }

        # Buscar no Google Books
        results = search_books(
            title=title if title else None,
            author=author if author else None,
            isbn=isbn if isbn else None,
            publisher=publisher if publisher else None,
            query=query if query else None,
            max_results=max_results,
            start_index=start_index
        )

        if 'error' in results:
            messages.error(request, f'Erro na busca: {results["error"]}')
            results = None
        elif 'books' not in results or not results['books']:
            messages.warning(request, 'Nenhum livro encontrado. Tente outros termos.')
            results = None
        else:
            # Adicionar info de paginação
            total_items = results.get('total_items', 0)

            # Proteção: garantir pelo menos 1 página se houver resultados
            if total_items > 0:
                max_pages = min(20, (total_items + max_results - 1) // max_results)
            else:
                max_pages = 1

            # Validar página atual
            if page > max_pages:
                page = max_pages
            elif page < 1:
                page = 1

            # Calcular range de páginas visíveis (máximo 5 páginas)
            range_start = max(1, page - 2)
            range_end = min(max_pages + 1, range_start + 5)

            # Ajustar range_start se estiver no final
            if range_end - range_start < 5:
                range_start = max(1, range_end - 5)

            results['pagination'] = {
                'current_page': page,
                'max_results': max_results,
                'total_pages': max_pages,
                'has_previous': page > 1,
                'has_next': page < max_pages,
                'previous_page': page - 1,
                'next_page': page + 1,
                'page_range': range(range_start, range_end)
            }

    context = {
        'title': 'Buscar Livros no Google Books',
        'results': results,
        'query_params': query_params,
    }

    return render(request, 'admin/core/book/google_books_search.html', context)


@staff_member_required
def google_books_import(request, google_book_id):
    """
    View para importar um livro do Google Books.
    """
    from core.utils.google_books_api import get_book_by_id

    if request.method != 'POST':
        return redirect('admin:google_books_search')

    # Buscar dados do livro
    book_data = get_book_by_id(google_book_id)

    if not book_data:
        messages.error(request, 'Não foi possível obter dados do livro.')
        return redirect('admin:google_books_search')

    try:
        # Verificar se já existe pelo ISBN
        isbn = book_data.get('isbn_13') or book_data.get('isbn_10')
        if isbn and Book.objects.filter(isbn=isbn).exists():
            messages.warning(request, f'Livro já existe no catálogo (ISBN: {isbn})')
            return redirect('admin:core_book_changelist')

        # Criar/buscar autor
        author = None
        authors_list = book_data.get('authors', [])
        if authors_list:
            author_name = authors_list[0]  # Pegar primeiro autor
            author, created = Author.objects.get_or_create(
                name=author_name,
                defaults={
                    'slug': slugify(author_name),
                    'bio': f'Autor(a) de {book_data.get("title")}'
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

        # Criar livro
        book = Book.objects.create(
            title=book_data.get('title'),
            subtitle=book_data.get('subtitle', ''),
            slug=slugify(book_data.get('title')),
            author=author,
            category=category,
            publisher=book_data.get('publisher', ''),
            publication_date=book_data.get('published_date'),
            isbn=isbn or '',
            page_count=book_data.get('page_count'),
            language=book_data.get('language', 'pt-BR'),
            description=book_data.get('description', ''),
            price=book_data.get('price', 49.90),  # Preço padrão se não houver
            average_rating=book_data.get('average_rating', 0.0),
            ratings_count=book_data.get('ratings_count', 0),
            preview_link=book_data.get('preview_link', ''),
            info_link=book_data.get('info_link', ''),
            google_books_id=book_data.get('google_book_id', '')
        )

        # Baixar capa
        thumbnail = book_data.get('thumbnail')
        if thumbnail:
            cover_path = download_cover(thumbnail, book.slug)
            if cover_path:
                book.cover_image = cover_path
                book.save()

        messages.success(
            request,
            f'Livro "{book.title}" importado com sucesso! '
            f'<a href="{reverse("admin:core_book_change", args=[book.id])}">Editar</a>'
        )

        return redirect('admin:core_book_changelist')

    except Exception as e:
        messages.error(request, f'Erro ao importar livro: {str(e)}')
        return redirect('admin:google_books_search')