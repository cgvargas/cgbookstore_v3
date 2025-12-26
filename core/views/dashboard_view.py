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

# Importar modelos do New Authors
try:
    from new_authors.models import EmergingAuthor, AuthorBook, Chapter
except ImportError:
    EmergingAuthor = None
    AuthorBook = None
    Chapter = None

# Importar modelos do Chatbot Literário
try:
    from chatbot_literario.models import ChatSession, ChatMessage, ChatbotKnowledge
except ImportError:
    ChatSession = None
    ChatMessage = None
    ChatbotKnowledge = None

# Importar modelos do News (Jornal Literário)
try:
    from news.models import Article, Quiz, Category as NewsCategory, Newsletter
except ImportError:
    Article = None
    Quiz = None
    NewsCategory = None
    Newsletter = None


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

    # ============================================
    # ESTATÍSTICAS DO NEW AUTHORS MODULE
    # ============================================
    new_authors_stats = {}

    if EmergingAuthor and AuthorBook and Chapter:
        total_authors = EmergingAuthor.objects.filter(is_active=True).count()
        total_books = AuthorBook.objects.filter(status='published').count()
        total_chapters = Chapter.objects.filter(is_published=True).count()

        new_authors_stats = {
            'total_authors': total_authors,
            'total_books': total_books,
            'total_chapters': total_chapters,
        }

    # ============================================
    # ESTATÍSTICAS DO CHATBOT LITERÁRIO
    # ============================================
    chatbot_stats = {}
    recent_chat_sessions = []

    if ChatSession and ChatMessage and ChatbotKnowledge:
        # Estatísticas de conversas
        total_sessions = ChatSession.objects.count()
        active_sessions = ChatSession.objects.filter(is_active=True).count()
        total_messages = ChatMessage.objects.count()

        # Mensagens nos últimos 7 dias
        seven_days_ago = now - timedelta(days=7)
        recent_messages_count = ChatMessage.objects.filter(
            created_at__gte=seven_days_ago
        ).count()

        # Estatísticas de Knowledge Base
        total_knowledge = ChatbotKnowledge.objects.count()
        active_knowledge = ChatbotKnowledge.objects.filter(is_active=True).count()

        # Correções feitas
        corrected_messages = ChatMessage.objects.filter(has_correction=True).count()

        # Knowledge Base mais usado
        top_knowledge = ChatbotKnowledge.objects.filter(
            is_active=True
        ).order_by('-times_used').first()

        # Total de usos de Knowledge Base
        total_kb_usage = ChatbotKnowledge.objects.aggregate(
            total=Sum('times_used')
        )['total'] or 0

        chatbot_stats = {
            'total_sessions': total_sessions,
            'active_sessions': active_sessions,
            'total_messages': total_messages,
            'recent_messages': recent_messages_count,
            'total_knowledge': total_knowledge,
            'active_knowledge': active_knowledge,
            'corrected_messages': corrected_messages,
            'top_knowledge': top_knowledge,
            'total_kb_usage': total_kb_usage,
        }

        # Últimas 5 sessões
        recent_chat_sessions = ChatSession.objects.select_related('user').order_by('-updated_at')[:5]

    # ============================================
    # ESTATÍSTICAS DO NEWS (JORNAL LITERÁRIO)
    # ============================================
    news_stats = {}

    if Article and Quiz:
        # Estatísticas de Artigos
        total_articles = Article.objects.count()
        published_articles = Article.objects.filter(is_published=True).count()
        breaking_news_count = Article.objects.filter(is_breaking=True, is_published=True).count()

        # Artigos por tipo
        articles_by_type = Article.objects.values('content_type').annotate(
            count=Count('id')
        ).order_by('-count')

        # Estatísticas de Quizzes
        total_quizzes = Quiz.objects.count()
        active_quizzes = Quiz.objects.filter(is_active=True).count()
        total_quiz_completions = Quiz.objects.aggregate(total=Sum('times_completed'))['total'] or 0

        # Newsletter
        if Newsletter:
            total_subscribers = Newsletter.objects.filter(is_active=True).count()
        else:
            total_subscribers = 0

        # Visualizações totais
        total_views = Article.objects.aggregate(total=Sum('views_count'))['total'] or 0

        news_stats = {
            'total_articles': total_articles,
            'published_articles': published_articles,
            'breaking_news_count': breaking_news_count,
            'total_quizzes': total_quizzes,
            'active_quizzes': active_quizzes,
            'total_quiz_completions': total_quiz_completions,
            'total_subscribers': total_subscribers,
            'total_views': total_views,
            'articles_by_type': articles_by_type,
        }

    context = {
        'title': '',  # Removido para não mostrar texto 'Dashboard' extra
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
        # New Authors data
        'new_authors_stats': new_authors_stats,
        # Chatbot data
        'chatbot_stats': chatbot_stats,
        'recent_chat_sessions': recent_chat_sessions,
        # News data
        'news_stats': news_stats,
    }

    return render(request, 'admin/dashboard.html', context)