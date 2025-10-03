"""
View para Dashboard Admin personalizada.
"""

from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.db.models import Count, Q, Avg
from django.utils import timezone
from datetime import timedelta
from core.models import Book, Author, Category, Event, Section, Video


@staff_member_required
def admin_dashboard(request):
    """
    Dashboard personalizada do admin com estatísticas e gráficos.
    """

    # Estatísticas básicas
    stats = {
        'total_books': Book.objects.count(),
        'total_authors': Author.objects.count(),
        'total_categories': Category.objects.count(),
        'total_events': Event.objects.count(),
        'total_sections': Section.objects.filter(active=True).count(),  # ✅ CORRIGIDO
        'total_videos': Video.objects.count(),
    }

    # Estatísticas de capas
    books_with_cover = Book.objects.filter(cover_image__isnull=False).exclude(cover_image='').count()
    books_without_cover = stats['total_books'] - books_with_cover

    # Estatísticas Google Books (livros com google_books_id)
    books_from_google = Book.objects.exclude(Q(google_books_id='') | Q(google_books_id__isnull=True)).count()

    cover_stats = {
        'with_cover': books_with_cover,
        'without_cover': books_without_cover,
        'from_google': books_from_google,
        'percentage': round((books_with_cover / stats['total_books'] * 100), 1) if stats['total_books'] > 0 else 0
    }

    # Livros por categoria (top 10)
    books_by_category = Category.objects.annotate(
        book_count=Count('books')
    ).order_by('-book_count')[:10]

    # Eventos por status
    now = timezone.now()
    events_upcoming = Event.objects.filter(start_date__gt=now, active=True).count()  # ✅ CORRIGIDO
    events_happening = Event.objects.filter(
        start_date__lte=now,
        end_date__gte=now,
        active=True  # ✅ CORRIGIDO
    ).count()
    events_finished = Event.objects.filter(end_date__lt=now).count()

    event_stats = {
        'upcoming': events_upcoming,
        'happening': events_happening,
        'finished': events_finished,
    }

    # Últimos livros adicionados (5)
    recent_books = Book.objects.select_related('author', 'category').order_by('-id')[:5]

    # Próximos eventos (3)
    upcoming_events = Event.objects.filter(
        start_date__gt=now,
        active=True  # ✅ CORRIGIDO
    ).order_by('start_date')[:3]

    # Média de avaliação
    avg_rating = Book.objects.aggregate(avg=Avg('average_rating'))['avg']
    avg_rating = round(avg_rating, 1) if avg_rating else 0

    # Livros adicionados nos últimos 30 dias
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_books_count = Book.objects.filter(id__gte=Book.objects.order_by('-id').first().id - 30).count() if Book.objects.exists() else 0

    context = {
        'title': 'Dashboard',
        'stats': stats,
        'cover_stats': cover_stats,
        'books_by_category': books_by_category,
        'event_stats': event_stats,
        'recent_books': recent_books,
        'upcoming_events': upcoming_events,
        'avg_rating': avg_rating,
        'recent_books_count': recent_books_count,
    }

    return render(request, 'admin/dashboard.html', context)