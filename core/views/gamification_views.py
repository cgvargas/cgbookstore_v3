"""
Views principais para o Sistema de Gamificação v3.0
Responsável por renderizar dashboards, conquistas, badges e rankings.
"""

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Q, Avg, F
from django.utils import timezone
from datetime import datetime, timedelta
from calendar import monthrange

# Models do sistema de gamificação
from accounts.models import (
    UserProfile,
    Achievement,
    UserAchievement,
    Badge,
    UserBadge,
    MonthlyRanking,
    XPMultiplier,
    ReadingProgress,
    BookReview,
    BookShelf
)


@login_required
def dashboard_view(request):
    """
    Dashboard principal do sistema de gamificação.
    Exibe resumo de XP, nível, conquistas recentes, badges, ranking e progresso.
    """
    user = request.user
    profile = user.profile

    # Informações básicas do usuário
    total_xp = profile.total_xp
    current_level = profile.level
    xp_for_next_level = profile.xp_for_next_level
    xp_progress_percentage = profile.xp_progress_percentage

    # Conquistas do usuário
    total_achievements = Achievement.objects.filter(is_active=True).count()
    user_achievements = UserAchievement.objects.filter(user=user).select_related('achievement')
    unlocked_achievements_count = user_achievements.count()
    achievements_percentage = round((unlocked_achievements_count / total_achievements * 100),
                                    1) if total_achievements > 0 else 0

    # Últimas 5 conquistas desbloqueadas
    recent_achievements = user_achievements.order_by('-earned_at')[:5]

    # Badges do usuário
    total_badges = Badge.objects.filter(is_active=True).count()
    user_badges = UserBadge.objects.filter(user=user).select_related('badge')
    unlocked_badges_count = user_badges.count()
    badges_percentage = round((unlocked_badges_count / total_badges * 100), 1) if total_badges > 0 else 0

    # Badges em destaque (showcaseados)
    showcased_badges = user_badges.filter(is_showcased=True).order_by('-earned_at')[:3]

    # Ranking mensal
    now = timezone.now()
    current_month = now.month
    current_year = now.year

    try:
        user_ranking = MonthlyRanking.objects.get(
            user=user,
            month=current_month,
            year=current_year
        )
        ranking_position = user_ranking.rank_position
        monthly_xp = user_ranking.total_xp
    except MonthlyRanking.DoesNotExist:
        ranking_position = None
        monthly_xp = 0

    # Top 5 do ranking mensal
    top_5_ranking = MonthlyRanking.objects.filter(
        month=current_month,
        year=current_year
    ).select_related('user', 'user__profile').order_by('rank_position')[:5]

    # Multiplicadores ativos
    active_multipliers = XPMultiplier.objects.filter(
        is_active=True,
        start_date__lte=now,
        end_date__gte=now
    ).order_by('-multiplier_value')

    # Estatísticas de leitura
    books_read = ReadingProgress.objects.filter(
        user=user,
        finished_at__isnull=False,
        is_abandoned=False
    ).count()

    books_reading = ReadingProgress.objects.filter(
        user=user,
        finished_at__isnull=True,
        is_abandoned=False
    ).count()

    total_pages_read = ReadingProgress.objects.filter(
        user=user,
        finished_at__isnull=False,
        is_abandoned=False
    ).aggregate(total=Sum('current_page'))['total'] or 0

    reviews_count = BookReview.objects.filter(user=user).count()

    # Conquistas próximas de desbloquear (progresso >= 50%)
    all_achievements = Achievement.objects.filter(is_active=True).exclude(
        id__in=user_achievements.values_list('achievement_id', flat=True)
    )

    near_achievements = []
    for achievement in all_achievements[:10]:  # Verificar apenas 10 para performance
        progress = calculate_achievement_progress(user, achievement)
        if progress >= 50:
            near_achievements.append({
                'achievement': achievement,
                'progress': progress
            })

    # Ordenar por progresso (maior primeiro)
    near_achievements.sort(key=lambda x: x['progress'], reverse=True)
    near_achievements = near_achievements[:3]  # Apenas top 3

    context = {
        'profile': profile,
        'total_xp': total_xp,
        'current_level': current_level,
        'xp_for_next_level': xp_for_next_level,
        'xp_progress_percentage': xp_progress_percentage,

        'total_achievements': total_achievements,
        'unlocked_achievements_count': unlocked_achievements_count,
        'achievements_percentage': achievements_percentage,
        'recent_achievements': recent_achievements,

        'total_badges': total_badges,
        'unlocked_badges_count': unlocked_badges_count,
        'badges_percentage': badges_percentage,
        'showcased_badges': showcased_badges,

        'ranking_position': ranking_position,
        'monthly_xp': monthly_xp,
        'top_5_ranking': top_5_ranking,

        'active_multipliers': active_multipliers,

        'books_read': books_read,
        'books_reading': books_reading,
        'total_pages_read': total_pages_read,
        'reviews_count': reviews_count,

        'near_achievements': near_achievements,

        'current_month_name': now.strftime('%B'),
        'current_year': current_year,
    }

    return render(request, 'gamification/dashboard.html', context)


@login_required
def achievements_list_view(request):
    """
    Lista todas as conquistas disponíveis com progresso do usuário.
    Permite filtrar por categoria e dificuldade.
    """
    user = request.user

    # Filtros da URL
    category_filter = request.GET.get('category', 'all')
    difficulty_filter = request.GET.get('difficulty', 'all')
    status_filter = request.GET.get('status', 'all')  # all, unlocked, locked

    # Query base
    achievements = Achievement.objects.filter(is_active=True)

    # Aplicar filtro de categoria
    if category_filter != 'all':
        achievements = achievements.filter(category=category_filter)

    # Aplicar filtro de dificuldade
    if difficulty_filter != 'all':
        achievements = achievements.filter(difficulty_level=difficulty_filter)

    # Conquistas do usuário
    user_achievements_ids = UserAchievement.objects.filter(user=user).values_list('achievement_id', flat=True)

    # Aplicar filtro de status
    if status_filter == 'unlocked':
        achievements = achievements.filter(id__in=user_achievements_ids)
    elif status_filter == 'locked':
        achievements = achievements.exclude(id__in=user_achievements_ids)

    # Ordenar por dificuldade e XP
    achievements = achievements.order_by('difficulty_level', '-xp_reward')

    # Preparar dados com progresso
    achievements_data = []
    for achievement in achievements:
        is_unlocked = achievement.id in user_achievements_ids

        if is_unlocked:
            user_achievement = UserAchievement.objects.get(user=user, achievement=achievement)
            earned_at = user_achievement.earned_at
            progress = 100
        else:
            earned_at = None
            progress = calculate_achievement_progress(user, achievement)

        achievements_data.append({
            'achievement': achievement,
            'is_unlocked': is_unlocked,
            'progress': progress,
            'earned_at': earned_at,
        })

    # Estatísticas gerais
    total_achievements = Achievement.objects.filter(is_active=True).count()
    unlocked_count = len(user_achievements_ids)
    locked_count = total_achievements - unlocked_count
    total_xp_earned = UserAchievement.objects.filter(user=user).aggregate(
        total=Sum('achievement__xp_reward')
    )['total'] or 0

    # Categorias disponíveis para filtro
    categories = Achievement.objects.filter(is_active=True).values_list('category', flat=True).distinct()

    context = {
        'achievements_data': achievements_data,
        'total_achievements': total_achievements,
        'unlocked_count': unlocked_count,
        'locked_count': locked_count,
        'total_xp_earned': total_xp_earned,
        'categories': categories,
        'category_filter': category_filter,
        'difficulty_filter': difficulty_filter,
        'status_filter': status_filter,
    }

    return render(request, 'gamification/achievements.html', context)


@login_required
def badges_collection_view(request):
    """
    Exibe a coleção de badges do usuário.
    Permite filtrar por raridade e categoria.
    """
    user = request.user

    # Filtros da URL
    rarity_filter = request.GET.get('rarity', 'all')
    category_filter = request.GET.get('category', 'all')
    status_filter = request.GET.get('status', 'all')  # all, unlocked, locked

    # Query base
    badges = Badge.objects.filter(is_active=True)

    # Aplicar filtro de raridade
    if rarity_filter != 'all':
        badges = badges.filter(rarity=rarity_filter)

    # Aplicar filtro de categoria
    if category_filter != 'all':
        badges = badges.filter(category=category_filter)

    # Badges do usuário
    user_badges_ids = UserBadge.objects.filter(user=user).values_list('badge_id', flat=True)

    # Aplicar filtro de status
    if status_filter == 'unlocked':
        badges = badges.filter(id__in=user_badges_ids)
    elif status_filter == 'locked':
        badges = badges.exclude(id__in=user_badges_ids)

    # Ordenar por raridade (lendário primeiro) e nome
    rarity_order = {
        'legendary': 1,
        'epic': 2,
        'rare': 3,
        'uncommon': 4,
        'common': 5,
        'event': 6
    }
    badges = sorted(badges, key=lambda b: (rarity_order.get(b.rarity, 999), b.name))

    # Preparar dados
    badges_data = []
    for badge in badges:
        is_unlocked = badge.id in user_badges_ids

        if is_unlocked:
            user_badge = UserBadge.objects.get(user=user, badge=badge)
            earned_at = user_badge.earned_at
            is_showcased = user_badge.is_showcased
        else:
            earned_at = None
            is_showcased = False

        badges_data.append({
            'badge': badge,
            'is_unlocked': is_unlocked,
            'earned_at': earned_at,
            'is_showcased': is_showcased,
        })

    # Estatísticas
    total_badges = Badge.objects.filter(is_active=True).count()
    unlocked_count = len(user_badges_ids)
    locked_count = total_badges - unlocked_count
    collection_percentage = round((unlocked_count / total_badges * 100), 1) if total_badges > 0 else 0

    # Badges em destaque
    showcased_badges = UserBadge.objects.filter(user=user, is_showcased=True).select_related('badge')

    # Raridades e categorias disponíveis
    rarities = Badge.objects.filter(is_active=True).values_list('rarity', flat=True).distinct()
    categories = Badge.objects.filter(is_active=True).values_list('category', flat=True).distinct()

    context = {
        'badges_data': badges_data,
        'total_badges': total_badges,
        'unlocked_count': unlocked_count,
        'locked_count': locked_count,
        'collection_percentage': collection_percentage,
        'showcased_badges': showcased_badges,
        'rarities': rarities,
        'categories': categories,
        'rarity_filter': rarity_filter,
        'category_filter': category_filter,
        'status_filter': status_filter,
    }

    return render(request, 'gamification/badges_collection.html', context)


@login_required
def monthly_ranking_view(request):
    """
    Exibe o ranking mensal de leitores.
    Mostra top 100 e posição do usuário atual.
    """
    user = request.user

    # Mês e ano (padrão: atual)
    year = request.GET.get('year')
    month = request.GET.get('month')

    now = timezone.now()

    if year and month:
        try:
            year = int(year)
            month = int(month)
        except ValueError:
            year = now.year
            month = now.month
    else:
        year = now.year
        month = now.month

    # Validar mês
    if month < 1 or month > 12:
        month = now.month

    # Query do ranking
    rankings = MonthlyRanking.objects.filter(
        year=year,
        month=month
    ).select_related('user', 'user__profile').order_by('rank_position')[:100]

    # Posição do usuário
    try:
        user_ranking = MonthlyRanking.objects.get(
            user=user,
            year=year,
            month=month
        )
        user_position = user_ranking.rank_position
        user_in_top_100 = user_position <= 100
    except MonthlyRanking.DoesNotExist:
        user_ranking = None
        user_position = None
        user_in_top_100 = False

    # Estatísticas do ranking
    total_participants = MonthlyRanking.objects.filter(year=year, month=month).count()

    if rankings.exists():
        top_xp = rankings.first().total_xp
        avg_xp = MonthlyRanking.objects.filter(year=year, month=month).aggregate(
            avg=Avg('total_xp')
        )['avg'] or 0
        avg_books = MonthlyRanking.objects.filter(year=year, month=month).aggregate(
            avg=Avg('books_read')
        )['avg'] or 0
    else:
        top_xp = 0
        avg_xp = 0
        avg_books = 0

    # Meses disponíveis para navegação
    available_months = MonthlyRanking.objects.values('year', 'month').annotate(
        count=Count('id')
    ).order_by('-year', '-month')

    # Nome do mês em português
    month_names = [
        '', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ]
    current_month_name = month_names[month]

    context = {
        'rankings': rankings,
        'user_ranking': user_ranking,
        'user_position': user_position,
        'user_in_top_100': user_in_top_100,
        'total_participants': total_participants,
        'top_xp': top_xp,
        'avg_xp': round(avg_xp, 0),
        'avg_books': round(avg_books, 1),
        'available_months': available_months,
        'current_year': year,
        'current_month': month,
        'current_month_name': current_month_name,
        'is_current_month': (year == now.year and month == now.month),
    }

    return render(request, 'gamification/monthly_ranking.html', context)


@login_required
def user_profile_stats(request):
    """
    Exibe estatísticas detalhadas do perfil do usuário.
    Inclui gráficos de progresso, XP por mês, conquistas por categoria, etc.
    """
    user = request.user
    profile = user.profile

    # Informações básicas
    total_xp = profile.total_xp
    current_level = profile.level
    member_since = user.date_joined
    days_as_member = (timezone.now() - member_since).days

    # Conquistas por categoria
    achievements_by_category = Achievement.objects.filter(
        is_active=True,
        user_achievements__user=user
    ).values('category').annotate(count=Count('id')).order_by('-count')

    # Badges por raridade
    badges_by_rarity = Badge.objects.filter(
        is_active=True,
        user_badges__user=user
    ).values('rarity').annotate(count=Count('id')).order_by('-count')

    # XP por mês (últimos 12 meses)
    xp_by_month = []
    now = timezone.now()

    for i in range(11, -1, -1):
        date = now - timedelta(days=30 * i)
        month = date.month
        year = date.year

        try:
            ranking = MonthlyRanking.objects.get(user=user, month=month, year=year)
            xp = ranking.total_xp
        except MonthlyRanking.DoesNotExist:
            xp = 0

        month_names = [
            '', 'Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
            'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'
        ]

        xp_by_month.append({
            'month_name': month_names[month],
            'year': year,
            'xp': xp
        })

    # Estatísticas de leitura
    total_books_read = ReadingProgress.objects.filter(
        user=user,
        finished_at__isnull=False,
        is_abandoned=False
    ).count()
    total_books_reading = ReadingProgress.objects.filter(
        user=user,
        finished_at__isnull=True,
        is_abandoned=False
    ).count()

    total_books_want = BookShelf.objects.filter(
        user=user,
        shelf_type='want_to_read'
    ).count()

    total_pages = ReadingProgress.objects.filter(
        user=user,
        finished_at__isnull=False,
        is_abandoned=False
    ).aggregate(total=Sum('current_page'))['total'] or 0

    avg_pages_per_book = round(total_pages / total_books_read, 0) if total_books_read > 0 else 0

    # Reviews
    total_reviews = BookReview.objects.filter(user=user).count()
    avg_rating = BookReview.objects.filter(user=user).aggregate(avg=Avg('rating'))['avg'] or 0

    # Streaks (sequências de leitura)
    # TODO: Implementar cálculo de streak quando houver sistema de daily check-in
    current_streak = 0
    longest_streak = 0

    # Ranking histórico
    best_position = MonthlyRanking.objects.filter(user=user).aggregate(
        best=Count('rank_position')
    )['best'] or None

    # Conquistas raras: Difícil (3), Muito Difícil (4) e Legendário (5)
    rare_achievements = UserAchievement.objects.filter(
        user=user,
        achievement__difficulty_level__in=[3, 4, 5]
    ).select_related('achievement').order_by('-achievement__xp_reward')[:5]

    # Badges legendários
    legendary_badges = UserBadge.objects.filter(
        user=user,
        badge__rarity='legendary'
    ).select_related('badge')

    context = {
        'profile': profile,
        'total_xp': total_xp,
        'current_level': current_level,
        'member_since': member_since,
        'days_as_member': days_as_member,

        'achievements_by_category': achievements_by_category,
        'badges_by_rarity': badges_by_rarity,
        'xp_by_month': xp_by_month,

        'total_books_read': total_books_read,
        'total_books_reading': total_books_reading,
        'total_books_want': total_books_want,
        'total_pages': total_pages,
        'avg_pages_per_book': avg_pages_per_book,

        'total_reviews': total_reviews,
        'avg_rating': round(avg_rating, 1),

        'current_streak': current_streak,
        'longest_streak': longest_streak,

        'best_position': best_position,
        'rare_achievements': rare_achievements,
        'legendary_badges': legendary_badges,
    }

    return render(request, 'gamification/user_profile_stats.html', context)


# ==========================================
# FUNÇÕES AUXILIARES
# ==========================================

def calculate_achievement_progress(user, achievement):
    """
    Calcula o progresso do usuário em uma conquista específica.
    Retorna valor de 0 a 100.
    """
    import json

    try:
        requirements = json.loads(achievement.requirements_json)
    except (json.JSONDecodeError, TypeError):
        return 0

    requirement_type = requirements.get('type')
    target_value = requirements.get('value', 1)

    current_value = 0

    # Conquistas de leitura
    if requirement_type == 'books_read':
        current_value = ReadingProgress.objects.filter(
            user=user,
            finished_at__isnull=False,
            is_abandoned=False
        ).count()

    elif requirement_type == 'books_finished_before_deadline':
        current_value = ReadingProgress.objects.filter(
            user=user,
            finished_at__isnull=False,
            is_abandoned=False,
            deadline__isnull=False,
            finished_at__date__lt=F('deadline')
        ).count()

    elif requirement_type == 'pages_read_in_day':
        # Páginas lidas hoje (exemplo simplificado)
        today = timezone.now().date()
        current_value = ReadingProgress.objects.filter(
            user=user,
            updated_at__date=today
        ).aggregate(total=Sum('current_page'))['total'] or 0

    # Conquistas de reviews
    elif requirement_type == 'reviews_written':
        current_value = BookReview.objects.filter(user=user).count()

    elif requirement_type == 'review_likes':
        # TODO: Implementar sistema de likes em reviews
        current_value = 0

    # Conquistas de diversidade
    elif requirement_type == 'different_categories':
        current_value = ReadingProgress.objects.filter(
            user=user,
            finished_at__isnull=False,
            is_abandoned=False
        ).values('book__category').distinct().count()

    elif requirement_type == 'different_authors':
        current_value = ReadingProgress.objects.filter(
            user=user,
            finished_at__isnull=False,
            is_abandoned=False
        ).values('book__author').distinct().count()

    # Calcular percentual
    if target_value > 0:
        progress = min(100, round((current_value / target_value) * 100, 1))
    else:
        progress = 0

    return progress