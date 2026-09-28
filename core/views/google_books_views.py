"""
Views para integração com Google Books no Admin.
"""

from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from core.utils.google_books_api import search_books, download_cover, get_book_by_id, parse_google_books_date
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
        # Verificar se já existe pelo ISBN (higienizado)
        raw_isbn = book_data.get('isbn_13') or book_data.get('isbn_10')
        clean_isbn = str(raw_isbn).replace('-', '').strip()[:14] if raw_isbn else ''
        if clean_isbn and Book.objects.filter(isbn=clean_isbn).exists():
            messages.warning(request, f'Livro já existe no catálogo (ISBN: {clean_isbn})')
            return redirect('admin:core_book_changelist')

        # Criar/buscar autor (case-insensitive e normalizado)
        author = None
        authors_list = book_data.get('authors', [])
        if authors_list:
            author_name = authors_list[0]  # Pegar primeiro autor
            # Normalizar: remover espaços extras e formatar corretamente
            author_name = ' '.join(str(author_name).split()).strip()[:200]
            
            if author_name:
                # Buscar autor existente (case-insensitive)
                existing_author = Author.objects.filter(name__iexact=author_name).first()
                
                if existing_author:
                    author = existing_author
                else:
                    # Obter tamanho máximo seguro do slug (compatível com varchar(50) ou varchar(220))
                    author_slug_field = Author._meta.get_field('slug')
                    author_max_len = getattr(author_slug_field, 'max_length', 50) or 50
                    safe_slug_len = min(author_max_len, 220)
                    
                    base_slug = slugify(author_name)[:safe_slug_len - 15].rstrip('-') or 'autor'
                    slug = base_slug
                    counter = 1
                    while Author.objects.filter(slug=slug).exists():
                        slug = f"{base_slug}-{counter}"
                        counter += 1

                    raw_title = book_data.get('title') or ''
                    author = Author.objects.create(
                        name=author_name,
                        slug=slug,
                        bio=f'Autor(a) de {raw_title}'[:500] if raw_title else ''
                    )

        # Criar/buscar categoria
        category = None
        categories_list = book_data.get('categories', [])
        if categories_list:
            raw_category_name = categories_list[0]  # Pegar primeira categoria
            category_name = ' '.join(str(raw_category_name).split()).strip()[:200]
            
            if category_name:
                category = Category.objects.filter(name__iexact=category_name).first()
                if not category:
                    cat_slug_field = Category._meta.get_field('slug')
                    cat_max_len = getattr(cat_slug_field, 'max_length', 50) or 50
                    safe_slug_len = min(cat_max_len, 220)

                    base_slug = slugify(category_name)[:safe_slug_len - 15].rstrip('-') or 'categoria'
                    slug = base_slug
                    counter = 1
                    while Category.objects.filter(slug=slug).exists():
                        slug = f"{base_slug}-{counter}"
                        counter += 1

                    category = Category.objects.create(
                        name=category_name,
                        slug=slug
                    )

        # Criar livro com campos sanitizados e protegidos contra overflow
        raw_title = book_data.get('title') or 'Sem título'
        title = ' '.join(str(raw_title).split()).strip()[:300]
        
        raw_subtitle = book_data.get('subtitle') or ''
        subtitle = ' '.join(str(raw_subtitle).split()).strip()[:500] if raw_subtitle else ''
        
        book_slug_field = Book._meta.get_field('slug')
        book_max_len = getattr(book_slug_field, 'max_length', 350) or 350
        base_slug = slugify(title)[:book_max_len - 15].rstrip('-') or 'livro'
        book_slug = base_slug
        counter = 1
        while Book.objects.filter(slug=book_slug).exists():
            book_slug = f"{base_slug}-{counter}"
            counter += 1

        google_books_id_val = str(book_data.get('google_book_id') or '').strip()[:100]

        book = Book.objects.create(
            title=title,
            subtitle=subtitle,
            slug=book_slug,
            author=author,
            category=category,
            publisher=str(book_data.get('publisher') or '').strip()[:200],
            publication_date=parse_google_books_date(book_data.get('published_date')),
            isbn=clean_isbn or None,
            page_count=book_data.get('page_count'),
            language=str(book_data.get('language') or 'pt-BR').strip()[:10],
            description=book_data.get('description', '') or '',
            price=book_data.get('price') or None,
            average_rating=book_data.get('average_rating', 0.0) or 0.0,
            ratings_count=book_data.get('ratings_count', 0) or 0,
            preview_link=book_data.get('preview_link', '') or '',
            info_link=book_data.get('info_link', '') or '',
            google_books_id=google_books_id_val or None
        )

        # Baixar capa
        thumbnail = book_data.get('thumbnail')
        if thumbnail:
            cover_path = download_cover(thumbnail, book.slug)
            if cover_path:
                book.cover_image = cover_path
                book.save()

                # Registro automático de Procedência Técnica (SEM presunção de licença)
                from core.services.image_rights_provenance_service import ImageRightsProvenanceService
                ImageRightsProvenanceService.register_external_provenance(
                    target_obj=book,
                    image_field_name='cover_image',
                    provider=ImageRightsProvenanceService.PROVIDER_GOOGLE_BOOKS,
                    source_url=thumbnail,
                    provider_asset_id=google_books_id_val,
                    license_type='google_books',
                    provenance_method='api_download',
                    safe_metadata={
                        'google_book_id': google_books_id_val,
                        'publisher_declared': book_data.get('publisher'),
                        'published_date': book_data.get('published_date'),
                    },
                    performed_by=request.user,
                    source='admin'
                )

        messages.success(
            request,
            f'Livro "{book.title}" importado com sucesso! '
            f'<a href="{reverse("admin:core_book_change", args=[book.id])}">Editar</a>'
        )

        return redirect('admin:core_book_changelist')

    except Exception as e:
        messages.error(request, f'Erro ao importar livro: {str(e)}')
        return redirect('admin:google_books_search')