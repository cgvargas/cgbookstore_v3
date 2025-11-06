"""
View para Dashboard Admin personalizada.
"""

from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.db.models import Count, Q, Avg, Sum
from django.utils import timezone
from datetime import timedelta
from core.models import Book, Author, Category, Event, Section, Video

# Importar modelos do Finance
try:
    from finance.models import Subscription, Campaign, CampaignGrant, Order
except ImportError:
    Subscription = None
    Campaign = None
    CampaignGrant = None
    Order = None


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

    # ============================================
    # ESTATÍSTICAS DO FINANCE MODULE
    # ============================================
    finance_stats = {}
    campaign_stats = {}
    recent_subscriptions = []
    active_campaigns = []
    subscription_chart_data = {}

    if Subscription and Campaign and CampaignGrant:
        # Estatísticas de Assinaturas
        total_subscriptions = Subscription.objects.count()
        active_subscriptions = Subscription.objects.filter(
            status='ativa',
            expiration_date__gte=now
        ).count()

        # Usuários Premium (incluindo campanhas)
        from accounts.models import UserProfile
        premium_users = UserProfile.objects.filter(is_premium=True).count()

        # Receita total (apenas assinaturas pagas)
        total_revenue = Subscription.objects.filter(
            status='ativa'
        ).aggregate(total=Sum('price'))['total'] or 0

        finance_stats = {
            'total_subscriptions': total_subscriptions,
            'active_subscriptions': active_subscriptions,
            'premium_users': premium_users,
            'total_revenue': total_revenue,
        }

        # Estatísticas de Campanhas
        total_campaigns = Campaign.objects.count()
        active_campaigns_count = Campaign.objects.filter(
            status='active',
            start_date__lte=now,
            end_date__gte=now
        ).count()

        total_grants = CampaignGrant.objects.count()
        active_grants = CampaignGrant.objects.filter(
            is_active=True,
            expires_at__gte=now
        ).count()

        campaign_stats = {
            'total_campaigns': total_campaigns,
            'active_campaigns': active_campaigns_count,
            'total_grants': total_grants,
            'active_grants': active_grants,
        }

        # Últimas 5 assinaturas
        recent_subscriptions = Subscription.objects.select_related('user').order_by('-created_at')[:5]

        # Campanhas ativas
        active_campaigns = Campaign.objects.filter(
            status='active',
            start_date__lte=now,
            end_date__gte=now
        ).order_by('-created_at')[:5]

        # Dados para gráfico: Assinaturas nos últimos 6 meses
        six_months_ago = now - timedelta(days=180)
        subscriptions_by_month = []

        for i in range(6):
            month_start = now - timedelta(days=30 * (5 - i))
            month_end = now - timedelta(days=30 * (4 - i))
            count = Subscription.objects.filter(
                created_at__gte=month_start,
                created_at__lt=month_end
            ).count()
            subscriptions_by_month.append({
                'month': month_start.strftime('%b/%y'),
                'count': count
            })

        subscription_chart_data = subscriptions_by_month

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
        # Finance data
        'finance_stats': finance_stats,
        'campaign_stats': campaign_stats,
        'recent_subscriptions': recent_subscriptions,
        'active_campaigns': active_campaigns,
        'subscription_chart_data': subscription_chart_data,
    }

    return render(request, 'admin/dashboard.html', context)