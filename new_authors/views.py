"""
Views para o app New Authors
Plataforma de autores emergentes
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg, Count
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.utils.text import slugify

from .models import (
    EmergingAuthor,
    AuthorBook,
    Chapter,
    AuthorBookReview,
    BookFollower,
    BookLike,
    PublisherProfile,
    PublisherInterest
)


# ========== VIEWS PÚBLICAS ==========

def books_list(request):
    """Lista todos os livros publicados de autores emergentes"""
    books = AuthorBook.objects.filter(
        status='published'
    ).select_related('author__user').order_by('-published_at')

    # Filtros
    genre_filter = request.GET.get('genre')
    search = request.GET.get('search')
    sort = request.GET.get('sort', '-published_at')

    if genre_filter:
        books = books.filter(genre=genre_filter)

    if search:
        books = books.filter(
            Q(title__icontains=search) |
            Q(synopsis__icontains=search) |
            Q(author__user__username__icontains=search)
        )

    # Ordenação
    valid_sorts = {
        'recent': '-published_at',
        'popular': '-views_count',
        'rating': '-rating_average',
        'title': 'title'
    }
    books = books.order_by(valid_sorts.get(sort, '-published_at'))

    # Paginação
    paginator = Paginator(books, 12)
    page = request.GET.get('page')
    books_page = paginator.get_page(page)

    # Gêneros para filtro
    genres = AuthorBook.GENRE_CHOICES

    context = {
        'books': books_page,
        'genres': genres,
        'current_genre': genre_filter,
        'current_sort': sort,
        'search_query': search or '',
    }
    return render(request, 'new_authors/books_list.html', context)


def book_detail(request, slug):
    """Detalhes de um livro específico"""
    # Buscar o livro
    book = get_object_or_404(
        AuthorBook.objects.select_related('author__user'),
        slug=slug
    )

    # Apenas o autor pode ver livros não publicados
    if book.status != 'published':
        if not request.user.is_authenticated:
            return HttpResponseForbidden("Este livro ainda não foi publicado.")
        try:
            author = request.user.emerging_author_profile
            if book.author != author:
                return HttpResponseForbidden("Este livro ainda não foi publicado.")
        except (EmergingAuthor.DoesNotExist, AttributeError):
            return HttpResponseForbidden("Este livro ainda não foi publicado.")

    # Verificar se o usuário é o autor
    is_author = False
    if request.user.is_authenticated:
        try:
            author = request.user.emerging_author_profile
            is_author = (book.author == author)
        except (EmergingAuthor.DoesNotExist, AttributeError):
            pass

    # Incrementa visualizações apenas para livros publicados
    if book.status == 'published':
        book.increment_views()

    # Capítulos (autor vê todos, outros só publicados)
    if is_author:
        chapters = book.chapters.all().order_by('number')
    else:
        chapters = book.chapters.filter(is_published=True).order_by('number')

    # Reviews aprovadas
    reviews = book.reviews.filter(is_approved=True).select_related('user').order_by('-created_at')[:10]

    # Verificar se usuário já segue o livro e curtiu
    is_following = False
    has_liked = False
    user_review = None
    if request.user.is_authenticated:
        is_following = BookFollower.objects.filter(book=book, user=request.user).exists()
        has_liked = BookLike.objects.filter(book=book, user=request.user).exists()
        try:
            user_review = AuthorBookReview.objects.get(book=book, user=request.user)
        except AuthorBookReview.DoesNotExist:
            pass

    # Livros relacionados (mesmo gênero)
    related_books = AuthorBook.objects.filter(
        genre=book.genre,
        status='published'
    ).exclude(id=book.id).order_by('-rating_average')[:4]

    context = {
        'book': book,
        'chapters': chapters,
        'reviews': reviews,
        'is_following': is_following,
        'has_liked': has_liked,
        'user_review': user_review,
        'related_books': related_books,
        'is_author': is_author,
    }
    return render(request, 'new_authors/book_detail.html', context)


def chapter_read(request, book_slug, chapter_number):
    """Visualizador de capítulo"""
    book = get_object_or_404(AuthorBook, slug=book_slug)

    # Verificar se o livro está publicado ou se o usuário é o autor
    is_author = False
    if request.user.is_authenticated:
        try:
            author = request.user.emerging_author_profile
            is_author = (book.author == author)
        except (EmergingAuthor.DoesNotExist, AttributeError):
            pass

    if book.status != 'published' and not is_author:
        return HttpResponseForbidden("Este livro ainda não foi publicado.")

    # Buscar capítulo (autor pode ver rascunhos)
    chapter_filter = {'book': book, 'number': chapter_number}
    if not is_author:
        chapter_filter['is_published'] = True

    chapter = get_object_or_404(Chapter, **chapter_filter)

    # Verificar se capítulo é gratuito ou requer login
    if not is_author and not chapter.is_free and not request.user.is_authenticated:
        messages.warning(request, 'Você precisa estar logado para ler este capítulo.')
        return redirect('accounts:login')

    # Incrementa visualizações apenas para livros publicados
    if book.status == 'published' and chapter.is_published:
        chapter.increment_views()

    # Capítulo anterior e próximo
    prev_filter = {'book': book, 'number__lt': chapter_number}
    next_filter = {'book': book, 'number__gt': chapter_number}

    if not is_author:
        prev_filter['is_published'] = True
        next_filter['is_published'] = True

    prev_chapter = Chapter.objects.filter(**prev_filter).order_by('-number').first()
    next_chapter = Chapter.objects.filter(**next_filter).order_by('number').first()

    context = {
        'book': book,
        'chapter': chapter,
        'prev_chapter': prev_chapter,
        'next_chapter': next_chapter,
    }
    return render(request, 'new_authors/chapter_read.html', context)


def author_profile(request, username):
    """Perfil público de um autor emergente"""
    author = get_object_or_404(
        EmergingAuthor.objects.select_related('user'),
        user__username=username,
        is_active=True
    )

    # Livros publicados do autor
    books = author.books.filter(status='published').order_by('-published_at')

    # Estatísticas
    stats = {
        'total_books': books.count(),
        'total_views': sum(b.views_count for b in books),
        'avg_rating': books.aggregate(Avg('rating_average'))['rating_average__avg'] or 0,
        'total_chapters': sum(b.chapters.filter(is_published=True).count() for b in books),
    }

    context = {
        'author': author,
        'books': books,
        'stats': stats,
    }
    return render(request, 'new_authors/author_profile.html', context)


# ========== VIEWS DE AUTORES (REQUER LOGIN) ==========

@login_required
def become_author(request):
    """Página para se tornar um autor emergente"""
    # Verificar se já é autor
    try:
        author = request.user.emerging_author_profile
        return redirect('new_authors:author_dashboard')
    except EmergingAuthor.DoesNotExist:
        pass

    if request.method == 'POST':
        bio = request.POST.get('bio')

        author = EmergingAuthor.objects.create(
            user=request.user,
            bio=bio
        )

        messages.success(request, 'Parabéns! Agora você é um autor emergente na plataforma!')
        return redirect('new_authors:author_dashboard')

    return render(request, 'new_authors/become_author.html')


@login_required
def author_dashboard(request):
    """Dashboard do autor emergente"""
    try:
        author = request.user.emerging_author_profile
    except EmergingAuthor.DoesNotExist:
        messages.warning(request, 'Você precisa se tornar um autor primeiro.')
        return redirect('new_authors:become_author')

    # Livros do autor
    books = author.books.all().order_by('-created_at')

    # Estatísticas
    stats = {
        'total_books': books.count(),
        'published_books': books.filter(status='published').count(),
        'draft_books': books.filter(status='draft').count(),
        'total_views': sum(b.views_count for b in books),
        'total_reviews': sum(b.reviews.filter(is_approved=True).count() for b in books),
    }

    # Últimas reviews recebidas
    recent_reviews = AuthorBookReview.objects.filter(
        book__author=author,
        is_approved=True
    ).select_related('book', 'user').order_by('-created_at')[:5]

    context = {
        'author': author,
        'books': books,
        'stats': stats,
        'recent_reviews': recent_reviews,
    }
    return render(request, 'new_authors/author_dashboard.html', context)


# ========== VIEWS DE INTERAÇÃO ==========

@login_required
@require_POST
def follow_book(request, book_id):
    """Seguir/deixar de seguir um livro"""
    book = get_object_or_404(AuthorBook, id=book_id, status='published')

    follower, created = BookFollower.objects.get_or_create(
        book=book,
        user=request.user
    )

    if not created:
        follower.delete()
        return JsonResponse({'status': 'unfollowed', 'message': 'Você deixou de seguir este livro.'})
    else:
        return JsonResponse({'status': 'followed', 'message': 'Você está seguindo este livro!'})


@login_required
@require_POST
def like_book(request, book_id):
    """Curtir/descurtir um livro"""
    book = get_object_or_404(AuthorBook, id=book_id)

    like, created = BookLike.objects.get_or_create(
        book=book,
        user=request.user
    )

    if not created:
        like.delete()
        return JsonResponse({
            'status': 'unliked',
            'message': 'Você removeu sua curtida deste livro.',
            'likes_count': book.likes_count
        })
    else:
        return JsonResponse({
            'status': 'liked',
            'message': 'Você curtiu este livro!',
            'likes_count': book.likes_count
        })


@login_required
@require_POST
def submit_review(request, book_id):
    """Submeter uma avaliação/review de um livro"""
    book = get_object_or_404(AuthorBook, id=book_id, status='published')

    # Verificar se já avaliou
    existing_review = AuthorBookReview.objects.filter(book=book, user=request.user).first()

    rating = int(request.POST.get('rating', 0))
    title = request.POST.get('title', '')
    comment = request.POST.get('comment', '')

    if rating < 1 or rating > 5:
        return JsonResponse({'status': 'error', 'message': 'Avaliação inválida.'}, status=400)

    if len(comment) < 10:
        return JsonResponse({'status': 'error', 'message': 'Comentário muito curto.'}, status=400)

    if existing_review:
        existing_review.rating = rating
        existing_review.title = title
        existing_review.comment = comment
        existing_review.save()
        return JsonResponse({'status': 'success', 'message': 'Sua avaliação foi atualizada!'})
    else:
        AuthorBookReview.objects.create(
            book=book,
            user=request.user,
            rating=rating,
            title=title,
            comment=comment
        )
        return JsonResponse({'status': 'success', 'message': 'Sua avaliação foi enviada!'})


@login_required
@require_POST
def mark_review_helpful(request, review_id):
    """Marcar uma review como útil"""
    review = get_object_or_404(AuthorBookReview, id=review_id)
    review.helpful_count += 1
    review.save()
    return JsonResponse({'status': 'success', 'count': review.helpful_count})


# ========== VIEWS DE EDITORAS ==========

@login_required
def become_publisher(request):
    """Página para se tornar uma editora"""
    # Verificar se já é editora
    try:
        publisher = request.user.publisher_profile
        return redirect('new_authors:publisher_dashboard')
    except PublisherProfile.DoesNotExist:
        pass

    if request.method == 'POST':
        company_name = request.POST.get('company_name')
        description = request.POST.get('description')
        email = request.POST.get('email')
        website = request.POST.get('website', '')
        phone = request.POST.get('phone', '')

        # Validações
        if not company_name or len(company_name) < 3:
            messages.error(request, 'Nome da editora deve ter pelo menos 3 caracteres.')
            return render(request, 'new_authors/become_publisher.html')

        if not description or len(description) < 50:
            messages.error(request, 'Descrição deve ter pelo menos 50 caracteres.')
            return render(request, 'new_authors/become_publisher.html')

        if not email:
            messages.error(request, 'Email de contato é obrigatório.')
            return render(request, 'new_authors/become_publisher.html')

        # Criar perfil de editora (não verificado)
        publisher = PublisherProfile.objects.create(
            user=request.user,
            company_name=company_name,
            description=description,
            email=email,
            website=website,
            phone=phone,
            is_verified=False,  # Requer aprovação do administrador
            is_active=True
        )

        messages.success(
            request,
            'Solicitação de cadastro enviada! Sua editora será analisada por nossa equipe. '
            'Você receberá um email quando for aprovada.'
        )
        return redirect('new_authors:publisher_pending')

    return render(request, 'new_authors/become_publisher.html')


@login_required
def publisher_pending(request):
    """Página de aguardando aprovação para editoras"""
    try:
        publisher = request.user.publisher_profile
    except PublisherProfile.DoesNotExist:
        messages.warning(request, 'Você não tem um perfil de editora.')
        return redirect('new_authors:become_publisher')

    if publisher.is_verified:
        return redirect('new_authors:publisher_dashboard')

    context = {
        'publisher': publisher,
    }
    return render(request, 'new_authors/publisher_pending.html', context)


@login_required
def publisher_dashboard(request):
    """Dashboard para editoras"""
    try:
        publisher = request.user.publisher_profile
    except PublisherProfile.DoesNotExist:
        messages.warning(request, 'Você não tem um perfil de editora.')
        return redirect('new_authors:become_publisher')

    # Verificar se está verificada
    if not publisher.is_verified:
        messages.warning(request, 'Sua editora ainda não foi verificada. Aguarde a aprovação.')
        return redirect('new_authors:publisher_pending')

    # Filtros
    genre_filter = request.GET.get('genre')
    min_rating = request.GET.get('min_rating', 4.0)
    min_views = request.GET.get('min_views', 100)
    sort_by = request.GET.get('sort', '-rating_average')

    # Query base de livros
    books_query = AuthorBook.objects.filter(
        status='published',
        rating_count__gte=3
    ).select_related('author__user')

    # Aplicar filtros
    if genre_filter:
        books_query = books_query.filter(genre=genre_filter)

    try:
        books_query = books_query.filter(
            rating_average__gte=float(min_rating),
            views_count__gte=int(min_views)
        )
    except (ValueError, TypeError):
        pass

    # Ordenação
    valid_sorts = {
        'rating': '-rating_average',
        'views': '-views_count',
        'likes': '-likes_count',
        'recent': '-published_at',
        'chapters': '-chapters__count'
    }
    sort_field = valid_sorts.get(sort_by, '-rating_average')

    if sort_by == 'chapters':
        books_query = books_query.annotate(
            chapter_count=Count('chapters', filter=Q(chapters__is_published=True))
        ).order_by('-chapter_count')
    else:
        books_query = books_query.order_by(sort_field)

    # Limitar resultados
    top_books = books_query[:30]

    # Estatísticas gerais da plataforma
    platform_stats = {
        'total_books': AuthorBook.objects.filter(status='published').count(),
        'total_authors': EmergingAuthor.objects.filter(is_active=True).count(),
        'avg_rating': AuthorBook.objects.filter(
            status='published',
            rating_count__gte=1
        ).aggregate(Avg('rating_average'))['rating_average__avg'] or 0,
        'total_chapters': Chapter.objects.filter(is_published=True).count(),
    }

    # Top autores por engajamento
    top_authors = EmergingAuthor.objects.filter(
        is_active=True,
        books__status='published'
    ).annotate(
        total_engagement=Count('books__reviews') + Count('books__followers')
    ).order_by('-total_engagement', '-total_views')[:10]

    # Interesses da editora
    interests = publisher.interests.all().select_related(
        'book__author__user'
    ).order_by('-created_at')

    # Estatísticas dos interesses
    interest_stats = {
        'total': interests.count(),
        'pending': interests.filter(status='pending').count(),
        'contacted': interests.filter(status='contacted').count(),
        'negotiating': interests.filter(status='negotiating').count(),
    }

    context = {
        'publisher': publisher,
        'top_books': top_books,
        'top_authors': top_authors,
        'interests': interests[:10],
        'platform_stats': platform_stats,
        'interest_stats': interest_stats,
        'genres': AuthorBook.GENRE_CHOICES,
        'current_genre': genre_filter,
        'current_sort': sort_by,
        'min_rating': min_rating,
        'min_views': min_views,
    }
    return render(request, 'new_authors/publisher_dashboard.html', context)


@login_required
def publisher_book_detail(request, book_id):
    """Detalhes completos de um livro para editoras (com informações de contato do autor)"""
    try:
        publisher = request.user.publisher_profile
    except PublisherProfile.DoesNotExist:
        messages.warning(request, 'Você não tem um perfil de editora.')
        return redirect('new_authors:books_list')

    book = get_object_or_404(
        AuthorBook.objects.select_related('author__user'),
        id=book_id,
        status='published'
    )

    # Verificar se já demonstrou interesse
    existing_interest = PublisherInterest.objects.filter(
        publisher=publisher,
        book=book
    ).first()

    # Estatísticas detalhadas do livro
    book_stats = {
        'total_chapters': book.chapters.filter(is_published=True).count(),
        'total_words': sum(ch.word_count for ch in book.chapters.filter(is_published=True)),
        'avg_chapter_views': book.chapters.filter(is_published=True).aggregate(
            Avg('views_count')
        )['views_count__avg'] or 0,
        'followers_count': book.followers.count(),
        'likes_count': book.likes_count,
        'reviews_count': book.reviews.filter(is_approved=True).count(),
    }

    # Outros livros do autor
    author_books = book.author.books.filter(
        status='published'
    ).exclude(id=book.id).order_by('-published_at')[:5]

    # Reviews em destaque
    featured_reviews = book.reviews.filter(
        is_approved=True
    ).order_by('-helpful_count', '-created_at')[:5]

    # Capítulos com mais views
    top_chapters = book.chapters.filter(
        is_published=True
    ).order_by('-views_count')[:5]

    context = {
        'publisher': publisher,
        'book': book,
        'book_stats': book_stats,
        'author_books': author_books,
        'featured_reviews': featured_reviews,
        'top_chapters': top_chapters,
        'existing_interest': existing_interest,
    }
    return render(request, 'new_authors/publisher_book_detail.html', context)


@login_required
@require_POST
def express_interest(request, book_id):
    """Editora expressa interesse em um livro"""
    try:
        publisher = request.user.publisher_profile
    except PublisherProfile.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Você não é uma editora.'}, status=403)

    if not publisher.is_verified:
        return JsonResponse({'status': 'error', 'message': 'Sua editora precisa ser verificada primeiro.'}, status=403)

    book = get_object_or_404(AuthorBook, id=book_id, status='published')
    message = request.POST.get('message', '')

    if len(message) < 20:
        return JsonResponse({'status': 'error', 'message': 'Mensagem muito curta (mínimo 20 caracteres).'}, status=400)

    interest, created = PublisherInterest.objects.get_or_create(
        publisher=publisher,
        book=book,
        defaults={'message': message}
    )

    if not created:
        return JsonResponse({'status': 'error', 'message': 'Você já expressou interesse neste livro.'}, status=400)

    # Atualizar contador
    publisher.authors_contacted += 1
    publisher.save()

    return JsonResponse({'status': 'success', 'message': 'Interesse enviado ao autor!'})


# ========== VIEWS DE BUSCA E FILTROS ==========

def search_books(request):
    """Busca avançada de livros"""
    query = request.GET.get('q', '')
    genre = request.GET.get('genre')
    min_rating = request.GET.get('min_rating')

    books = AuthorBook.objects.filter(status='published')

    if query:
        books = books.filter(
            Q(title__icontains=query) |
            Q(synopsis__icontains=query) |
            Q(description__icontains=query) |
            Q(author__user__username__icontains=query)
        )

    if genre:
        books = books.filter(genre=genre)

    if min_rating:
        try:
            min_rating_val = float(min_rating)
            books = books.filter(rating_average__gte=min_rating_val)
        except ValueError:
            pass

    books = books.order_by('-rating_average', '-views_count')

    # Paginação
    paginator = Paginator(books, 12)
    page = request.GET.get('page')
    books_page = paginator.get_page(page)

    context = {
        'books': books_page,
        'query': query,
        'genres': AuthorBook.GENRE_CHOICES,
        'selected_genre': genre,
        'min_rating': min_rating,
    }
    return render(request, 'new_authors/search_results.html', context)


def trending_books(request):
    """Livros em alta (mais vistos nos últimos 7 dias)"""
    # Esta implementação é simplificada
    # Em produção, você usaria um sistema de tracking temporal
    books = AuthorBook.objects.filter(
        status='published',
        published_at__gte=timezone.now() - timezone.timedelta(days=30)
    ).order_by('-views_count', '-rating_average')[:20]

    context = {
        'books': books,
        'title': 'Livros em Alta',
    }
    return render(request, 'new_authors/trending_books.html', context)


# ========== VIEWS DE GERENCIAMENTO DE LIVROS (AUTOR) ==========

@login_required
def manage_book(request, book_id=None):
    """Criar ou editar livro (apenas autores)"""
    from .forms import AuthorBookForm

    try:
        author = request.user.emerging_author_profile
    except EmergingAuthor.DoesNotExist:
        messages.error(request, 'Você precisa ser um autor para acessar esta página.')
        return redirect('new_authors:become_author')

    if book_id:
        book = get_object_or_404(AuthorBook, id=book_id, author=author)
        is_editing = True
    else:
        book = None
        is_editing = False

    if request.method == 'POST':
        form = AuthorBookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            book = form.save(commit=False)
            if not is_editing:
                book.author = author

            # Gerar slug automaticamente
            if not book.slug:
                base_slug = slugify(book.title)
                slug = base_slug
                counter = 1
                while AuthorBook.objects.filter(slug=slug).exists():
                    slug = f"{base_slug}-{counter}"
                    counter += 1
                book.slug = slug

            book.save()
            messages.success(request, 'Livro salvo com sucesso!' if is_editing else 'Livro criado com sucesso!')
            return redirect('new_authors:manage_chapters', book_id=book.id)
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = AuthorBookForm(instance=book)

    context = {
        'form': form,
        'book': book,
        'is_editing': is_editing,
    }
    return render(request, 'new_authors/manage_book.html', context)


@login_required
def manage_chapters(request, book_id):
    """Gerenciar capítulos de um livro (apenas autor do livro)"""
    try:
        author = request.user.emerging_author_profile
    except EmergingAuthor.DoesNotExist:
        messages.error(request, 'Você precisa ser um autor para acessar esta página.')
        return redirect('new_authors:become_author')

    book = get_object_or_404(AuthorBook, id=book_id, author=author)
    chapters = book.chapters.all().order_by('number')

    context = {
        'book': book,
        'chapters': chapters,
    }
    return render(request, 'new_authors/manage_chapters.html', context)


@login_required
def edit_chapter(request, book_id, chapter_id=None):
    """Criar ou editar capítulo (apenas autor do livro)"""
    from .forms import ChapterForm

    try:
        author = request.user.emerging_author_profile
    except EmergingAuthor.DoesNotExist:
        messages.error(request, 'Você precisa ser um autor para acessar esta página.')
        return redirect('new_authors:become_author')

    book = get_object_or_404(AuthorBook, id=book_id, author=author)

    if chapter_id:
        chapter = get_object_or_404(Chapter, id=chapter_id, book=book)
        is_editing = True
    else:
        chapter = None
        is_editing = False

    if request.method == 'POST':
        form = ChapterForm(request.POST, instance=chapter)
        if form.is_valid():
            chapter = form.save(commit=False)
            if not is_editing:
                chapter.book = book
                # Definir número do capítulo automaticamente
                last_chapter = book.chapters.order_by('-number').first()
                chapter.number = (last_chapter.number + 1) if last_chapter else 1

            chapter.save()
            messages.success(request, 'Capítulo salvo com sucesso!' if is_editing else 'Capítulo criado com sucesso!')
            return redirect('new_authors:manage_chapters', book_id=book.id)
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = ChapterForm(instance=chapter)

    context = {
        'form': form,
        'book': book,
        'chapter': chapter,
        'is_editing': is_editing,
    }
    return render(request, 'new_authors/edit_chapter.html', context)


@login_required
@require_POST
def delete_chapter(request, chapter_id):
    """Deletar capítulo (apenas autor do livro)"""
    try:
        author = request.user.emerging_author_profile
    except EmergingAuthor.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Acesso negado.'}, status=403)

    chapter = get_object_or_404(Chapter, id=chapter_id, book__author=author)
    book_id = chapter.book.id
    chapter.delete()

    # Renumerar capítulos
    chapters = Chapter.objects.filter(book_id=book_id).order_by('number')
    for idx, ch in enumerate(chapters, start=1):
        if ch.number != idx:
            ch.number = idx
            ch.save()

    messages.success(request, 'Capítulo deletado com sucesso!')
    return JsonResponse({'status': 'success', 'redirect': f'/novos-autores/livro/{book_id}/capitulos/'})


@login_required
@require_POST
def delete_book(request, book_id):
    """Deletar livro (apenas autor)"""
    try:
        author = request.user.emerging_author_profile
    except EmergingAuthor.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Acesso negado.'}, status=403)

    book = get_object_or_404(AuthorBook, id=book_id, author=author)
    book.delete()

    messages.success(request, 'Livro deletado com sucesso!')
    return JsonResponse({'status': 'success', 'redirect': '/novos-autores/dashboard/'})
