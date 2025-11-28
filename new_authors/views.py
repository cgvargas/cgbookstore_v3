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

from .models import (
    EmergingAuthor,
    AuthorBook,
    Chapter,
    AuthorBookReview,
    BookFollower,
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
    book = get_object_or_404(
        AuthorBook.objects.select_related('author__user'),
        slug=slug,
        status='published'
    )

    # Incrementa visualizações
    book.increment_views()

    # Capítulos publicados
    chapters = book.chapters.filter(is_published=True).order_by('number')

    # Reviews aprovadas
    reviews = book.reviews.filter(is_approved=True).select_related('user').order_by('-created_at')[:10]

    # Verificar se usuário já segue o livro
    is_following = False
    user_review = None
    if request.user.is_authenticated:
        is_following = BookFollower.objects.filter(book=book, user=request.user).exists()
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
        'user_review': user_review,
        'related_books': related_books,
    }
    return render(request, 'new_authors/book_detail.html', context)


def chapter_read(request, book_slug, chapter_number):
    """Visualizador de capítulo"""
    book = get_object_or_404(AuthorBook, slug=book_slug, status='published')
    chapter = get_object_or_404(
        Chapter,
        book=book,
        number=chapter_number,
        is_published=True
    )

    # Verificar se capítulo é gratuito ou requer login
    if not chapter.is_free and not request.user.is_authenticated:
        messages.warning(request, 'Você precisa estar logado para ler este capítulo.')
        return redirect('accounts:login')

    # Incrementa visualizações
    chapter.increment_views()

    # Capítulo anterior e próximo
    prev_chapter = Chapter.objects.filter(
        book=book,
        number__lt=chapter_number,
        is_published=True
    ).order_by('-number').first()

    next_chapter = Chapter.objects.filter(
        book=book,
        number__gt=chapter_number,
        is_published=True
    ).order_by('number').first()

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
def publisher_dashboard(request):
    """Dashboard para editoras"""
    try:
        publisher = request.user.publisher_profile
    except PublisherProfile.DoesNotExist:
        messages.warning(request, 'Você não tem um perfil de editora.')
        return redirect('new_authors:books_list')

    # Livros mais bem avaliados
    top_books = AuthorBook.objects.filter(
        status='published',
        rating_count__gte=5
    ).order_by('-rating_average', '-views_count')[:20]

    # Interesses da editora
    interests = publisher.interests.all().select_related('book__author__user').order_by('-created_at')[:10]

    context = {
        'publisher': publisher,
        'top_books': top_books,
        'interests': interests,
    }
    return render(request, 'new_authors/publisher_dashboard.html', context)


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
