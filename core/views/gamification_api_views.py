"""
APIs REST para o Sistema de Gamificação v3.0
Endpoints JSON para comunicação AJAX com frontend.
"""

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods, require_POST, require_GET
from django.db.models import Count, Sum, Q, Avg, F
from django.utils import timezone
from datetime import datetime, timedelta
import json

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
    BookShelf,
)


@login_required
@require_GET
def get_user_achievements(request):
    """
    API: Retorna todas as conquistas do usuário em formato JSON.

    GET /api/gamification/achievements/

    Query params opcionais:
    - category: Filtrar por categoria
    - status: 'unlocked' ou 'locked'
    - difficulty: Filtrar por dificuldade

    Response:
    {
        "success": true,
        "total_achievements": 20,
        "unlocked_count": 5,
        "locked_count": 15,
        "total_xp_earned": 450,
        "achievements": [
            {
                "id": 1,
                "name": "Primeiro Livro",
                "description": "Termine seu primeiro livro",
                "category": "leitura",
                "difficulty": "easy",
                "xp_reward": 50,
                "icon": "📖",
                "is_unlocked": true,
                "progress": 100,
                "earned_at": "2025-10-20T10:30:00Z"
            },
            ...
        ]
    }
    """
    user = request.user

    # Filtros opcionais
    category_filter = request.GET.get('category')
    status_filter = request.GET.get('status')
    difficulty_filter = request.GET.get('difficulty')

    # Query base
    achievements = Achievement.objects.filter(is_active=True)

    # Aplicar filtros
    if category_filter:
        achievements = achievements.filter(category=category_filter)
    if difficulty_filter:
        achievements = achievements.filter(difficulty_level=difficulty_filter)

    # Conquistas do usuário
    user_achievements_dict = {}
    for ua in UserAchievement.objects.filter(user=user, is_completed=True).select_related('achievement'):
        user_achievements_dict[ua.achievement_id] = {
            'earned_at': ua.earned_at.isoformat() if ua.earned_at else None,
            'progress': 100
        }

    # Filtrar por status
    if status_filter == 'unlocked':
        achievements = achievements.filter(id__in=user_achievements_dict.keys())
    elif status_filter == 'locked':
        achievements = achievements.exclude(id__in=user_achievements_dict.keys())

    # Preparar dados
    achievements_data = []
    for achievement in achievements:
        is_unlocked = achievement.id in user_achievements_dict

        if is_unlocked:
            earned_at = user_achievements_dict[achievement.id]['earned_at']
            progress = 100
        else:
            earned_at = None
            progress = calculate_achievement_progress_api(user, achievement)

        achievements_data.append({
            'id': achievement.id,
            'name': achievement.name,
            'description': achievement.description,
            'category': achievement.category,
            'difficulty': achievement.difficulty_level,
            'xp_reward': achievement.xp_reward,
            'icon': achievement.icon,
            'is_unlocked': is_unlocked,
            'progress': progress,
            'earned_at': earned_at,
        })

    # Estatísticas
    total_achievements = Achievement.objects.filter(is_active=True).count()
    unlocked_count = len(user_achievements_dict)
    locked_count = total_achievements - unlocked_count
    total_xp_earned = UserAchievement.objects.filter(user=user).aggregate(
        total=Sum('achievement__xp_reward')
    )['total'] or 0

    return JsonResponse({
        'success': True,
        'total_achievements': total_achievements,
        'unlocked_count': unlocked_count,
        'locked_count': locked_count,
        'total_xp_earned': total_xp_earned,
        'achievements': achievements_data,
    })


@login_required
@require_GET
def get_achievement_progress(request, achievement_id):
    """
    API: Retorna o progresso detalhado de uma conquista específica.

    GET /api/gamification/achievement-progress/<achievement_id>/

    Response:
    {
        "success": true,
        "achievement": {
            "id": 1,
            "name": "Leitor Iniciante",
            "description": "Leia 5 livros",
            "xp_reward": 100,
            "is_unlocked": false,
            "progress": 60,
            "current_value": 3,
            "target_value": 5,
            "requirements": {
                "type": "books_read",
                "value": 5
            }
        }
    }
    """
    user = request.user

    try:
        achievement = Achievement.objects.get(id=achievement_id, is_active=True)
    except Achievement.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Conquista não encontrada'
        }, status=404)

    # Verificar se está desbloqueada
    is_unlocked = UserAchievement.objects.filter(
        user=user,
        achievement=achievement
    ).exists()

    if is_unlocked:
        user_achievement = UserAchievement.objects.get(user=user, achievement=achievement)
        progress = 100
        earned_at = user_achievement.earned_at.isoformat()
    else:
        progress = calculate_achievement_progress_api(user, achievement)
        earned_at = None

    # Parsear requirements
    try:
        requirements = json.loads(achievement.requirements_json)
        requirement_type = requirements.get('type')
        target_value = requirements.get('value', 1)

        # Calcular valor atual baseado no tipo
        current_value = get_current_value_for_requirement(user, requirement_type)
    except (json.JSONDecodeError, TypeError):
        requirements = {}
        target_value = 1
        current_value = 0

    return JsonResponse({
        'success': True,
        'achievement': {
            'id': achievement.id,
            'name': achievement.name,
            'description': achievement.description,
            'category': achievement.category,
            'difficulty': achievement.difficulty_level,
            'xp_reward': achievement.xp_reward,
            'icon': achievement.icon,
            'is_unlocked': is_unlocked,
            'progress': progress,
            'current_value': current_value,
            'target_value': target_value,
            'requirements': requirements,
            'earned_at': earned_at,
        }
    })


@login_required
@require_GET
def get_user_badges(request):
    """
    API: Retorna todos os badges do usuário em formato JSON.

    GET /api/gamification/badges/

    Query params opcionais:
    - rarity: Filtrar por raridade
    - status: 'unlocked' ou 'locked'
    - showcased: 'true' para apenas showcaseados

    Response:
    {
        "success": true,
        "total_badges": 15,
        "unlocked_count": 3,
        "locked_count": 12,
        "collection_percentage": 20.0,
        "showcased_count": 2,
        "badges": [
            {
                "id": 1,
                "name": "Iniciante",
                "description": "Complete seu cadastro",
                "rarity": "common",
                "category": "especial",
                "icon": "🥉",
                "is_unlocked": true,
                "is_showcased": true,
                "earned_at": "2025-10-15T08:00:00Z"
            },
            ...
        ]
    }
    """
    user = request.user

    # Filtros opcionais
    rarity_filter = request.GET.get('rarity')
    status_filter = request.GET.get('status')
    showcased_only = request.GET.get('showcased') == 'true'

    # Query base
    badges = Badge.objects.filter(is_active=True)

    # Aplicar filtros
    if rarity_filter:
        badges = badges.filter(rarity=rarity_filter)

    # Badges do usuário
    user_badges_dict = {}
    for ub in UserBadge.objects.filter(user=user).select_related('badge'):
        user_badges_dict[ub.badge_id] = {
            'earned_at': ub.earned_at.isoformat(),
            'is_showcased': ub.is_showcased,
        }

    # Filtrar por status
    if status_filter == 'unlocked':
        badges = badges.filter(id__in=user_badges_dict.keys())
    elif status_filter == 'locked':
        badges = badges.exclude(id__in=user_badges_dict.keys())

    # Filtrar por showcased
    if showcased_only:
        badges = badges.filter(id__in=[
            badge_id for badge_id, data in user_badges_dict.items()
            if data['is_showcased']
        ])

    # Preparar dados
    badges_data = []
    for badge in badges:
        is_unlocked = badge.id in user_badges_dict

        if is_unlocked:
            earned_at = user_badges_dict[badge.id]['earned_at']
            is_showcased = user_badges_dict[badge.id]['is_showcased']
        else:
            earned_at = None
            is_showcased = False

        badges_data.append({
            'id': badge.id,
            'name': badge.name,
            'description': badge.description,
            'rarity': badge.rarity,
            'category': badge.category,
            'icon': badge.icon,
            'is_unlocked': is_unlocked,
            'is_showcased': is_showcased,
            'earned_at': earned_at,
        })

    # Estatísticas
    total_badges = Badge.objects.filter(is_active=True).count()
    unlocked_count = len(user_badges_dict)
    locked_count = total_badges - unlocked_count
    collection_percentage = round((unlocked_count / total_badges * 100), 1) if total_badges > 0 else 0
    showcased_count = sum(1 for data in user_badges_dict.values() if data['is_showcased'])

    return JsonResponse({
        'success': True,
        'total_badges': total_badges,
        'unlocked_count': unlocked_count,
        'locked_count': locked_count,
        'collection_percentage': collection_percentage,
        'showcased_count': showcased_count,
        'badges': badges_data,
    })


@login_required
@require_POST
def showcase_badge(request):
    """
    API: Define um badge como showcased (em destaque).
    Máximo de 3 badges showcaseados por usuário.

    POST /api/gamification/showcase-badge/
    Body: {"badge_id": 1}

    Response:
    {
        "success": true,
        "message": "Badge colocado em destaque!",
        "showcased_badges": [
            {"id": 1, "name": "Iniciante", "icon": "🥉"},
            ...
        ]
    }
    """
    user = request.user

    try:
        data = json.loads(request.body)
        badge_id = data.get('badge_id')

        if not badge_id:
            return JsonResponse({
                'success': False,
                'error': 'badge_id é obrigatório'
            }, status=400)

        # Verificar se o badge existe e está desbloqueado
        try:
            user_badge = UserBadge.objects.get(user=user, badge_id=badge_id)
        except UserBadge.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Badge não encontrado ou não desbloqueado'
            }, status=404)

        # Verificar limite de 3 showcased
        showcased_count = UserBadge.objects.filter(
            user=user,
            is_showcased=True
        ).exclude(id=user_badge.id).count()

        if showcased_count >= 3 and not user_badge.is_showcased:
            return JsonResponse({
                'success': False,
                'error': 'Você já tem 3 badges em destaque. Remova um antes de adicionar outro.'
            }, status=400)

        # Colocar em destaque
        user_badge.is_showcased = True
        user_badge.save()

        # Retornar badges showcaseados
        showcased_badges = UserBadge.objects.filter(
            user=user,
            is_showcased=True
        ).select_related('badge').order_by('-earned_at')[:3]

        showcased_data = [
            {
                'id': ub.badge.id,
                'name': ub.badge.name,
                'icon': ub.badge.icon,
                'rarity': ub.badge.rarity,
            }
            for ub in showcased_badges
        ]

        return JsonResponse({
            'success': True,
            'message': 'Badge colocado em destaque!',
            'showcased_badges': showcased_data,
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'JSON inválido'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_POST
def remove_showcase_badge(request):
    """
    API: Remove um badge do showcase (destaque).

    POST /api/gamification/remove-showcase-badge/
    Body: {"badge_id": 1}

    Response:
    {
        "success": true,
        "message": "Badge removido do destaque",
        "showcased_badges": [...]
    }
    """
    user = request.user

    try:
        data = json.loads(request.body)
        badge_id = data.get('badge_id')

        if not badge_id:
            return JsonResponse({
                'success': False,
                'error': 'badge_id é obrigatório'
            }, status=400)

        # Verificar se o badge existe
        try:
            user_badge = UserBadge.objects.get(user=user, badge_id=badge_id)
        except UserBadge.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Badge não encontrado'
            }, status=404)

        # Remover do destaque
        user_badge.is_showcased = False
        user_badge.save()

        # Retornar badges showcaseados atualizados
        showcased_badges = UserBadge.objects.filter(
            user=user,
            is_showcased=True
        ).select_related('badge').order_by('-earned_at')[:3]

        showcased_data = [
            {
                'id': ub.badge.id,
                'name': ub.badge.name,
                'icon': ub.badge.icon,
                'rarity': ub.badge.rarity,
            }
            for ub in showcased_badges
        ]

        return JsonResponse({
            'success': True,
            'message': 'Badge removido do destaque',
            'showcased_badges': showcased_data,
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'JSON inválido'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_GET
def get_monthly_ranking(request):
    """
    API: Retorna o ranking mensal completo em formato JSON.

    GET /api/gamification/ranking/

    Query params opcionais:
    - year: Ano do ranking (padrão: atual)
    - month: Mês do ranking (padrão: atual)
    - limit: Número de resultados (padrão: 100, máx: 500)

    Response:
    {
        "success": true,
        "year": 2025,
        "month": 10,
        "month_name": "Outubro",
        "total_participants": 150,
        "user_position": 25,
        "user_in_list": true,
        "top_xp": 5000,
        "avg_xp": 1200,
        "ranking": [
            {
                "position": 1,
                "user_id": 123,
                "username": "leitor_pro",
                "avatar_url": "...",
                "total_xp": 5000,
                "books_read": 15,
                "pages_read": 4500,
                "achievements_earned": 18,
                "level": 12
            },
            ...
        ]
    }
    """
    user = request.user

    # Parâmetros opcionais
    now = timezone.now()
    year = int(request.GET.get('year', now.year))
    month = int(request.GET.get('month', now.month))
    limit = min(int(request.GET.get('limit', 100)), 500)

    # Se for o mês atual, garantir e recalcular estatísticas/posições
    if year == now.year and month == now.month:
        MonthlyRanking.get_or_create_current(user)
        MonthlyRanking.recalculate_positions(month, year)

    # Query do ranking
    rankings = MonthlyRanking.objects.filter(
        year=year,
        month=month
    ).select_related('user', 'user__profile').order_by('rank_position')[:limit]

    # Preparar dados
    ranking_data = []
    for rank in rankings:
        ranking_data.append({
            'position': rank.rank_position,
            'user_id': rank.user.id,
            'username': rank.user.username,
            'avatar_url': rank.user.profile.avatar.url if rank.user.profile.avatar else None,
            'total_xp': rank.total_xp,
            'books_read': rank.books_read,
            'pages_read': rank.pages_read,
            'achievements_earned': rank.achievements_earned,
            'level': rank.user.profile.level,
        })

    # Posição do usuário
    try:
        user_ranking = MonthlyRanking.objects.get(
            user=user,
            year=year,
            month=month
        )
        user_position = user_ranking.rank_position
        user_in_list = user_position <= limit
    except MonthlyRanking.DoesNotExist:
        user_position = None
        user_in_list = False

    # Estatísticas
    total_participants = MonthlyRanking.objects.filter(year=year, month=month).count()

    if rankings.exists():
        top_xp = rankings.first().total_xp
        avg_xp = MonthlyRanking.objects.filter(year=year, month=month).aggregate(
            avg=Avg('total_xp')
        )['avg'] or 0
    else:
        top_xp = 0
        avg_xp = 0

    # Nome do mês
    month_names = [
        '', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ]

    return JsonResponse({
        'success': True,
        'year': year,
        'month': month,
        'month_name': month_names[month],
        'total_participants': total_participants,
        'user_position': user_position,
        'user_in_list': user_in_list,
        'top_xp': top_xp,
        'avg_xp': round(avg_xp, 0),
        'ranking': ranking_data,
    })


@login_required
@require_GET
def get_user_stats(request):
    """
    API: Retorna estatísticas detalhadas do usuário em formato JSON.

    GET /api/gamification/user-stats/

    Response:
    {
        "success": true,
        "profile": {
            "user_id": 123,
            "username": "leitor_pro",
            "total_xp": 2500,
            "level": 8,
            "xp_for_next_level": 3000,
            "xp_progress_percentage": 83.3,
            "member_since": "2024-01-15",
            "days_as_member": 283
        },
        "achievements": {
            "total": 20,
            "unlocked": 12,
            "locked": 8,
            "percentage": 60.0,
            "total_xp_earned": 950
        },
        "badges": {
            "total": 15,
            "unlocked": 5,
            "locked": 10,
            "percentage": 33.3,
            "showcased_count": 3
        },
        "reading": {
            "books_read": 25,
            "books_reading": 3,
            "books_want": 15,
            "total_pages": 7500,
            "avg_pages_per_book": 300
        },
        "reviews": {
            "total": 18,
            "avg_rating": 4.2
        },
        "ranking": {
            "current_position": 25,
            "best_position": 12,
            "monthly_xp": 450
        }
    }
    """
    user = request.user
    profile = user.profile

    # Informações do perfil
    member_since = user.date_joined
    days_as_member = (timezone.now() - member_since).days

    profile_data = {
        'user_id': user.id,
        'username': user.username,
        'total_xp': profile.total_xp,
        'level': profile.level,
        'xp_for_next_level': profile.xp_for_next_level,
        'xp_progress_percentage': profile.xp_progress_percentage,
        'member_since': member_since.date().isoformat(),
        'days_as_member': days_as_member,
    }

    # Conquistas
    total_achievements = Achievement.objects.filter(is_active=True).count()
    unlocked_achievements = UserAchievement.objects.filter(user=user, is_completed=True).count()
    locked_achievements = total_achievements - unlocked_achievements
    achievements_percentage = round((unlocked_achievements / total_achievements * 100),
                                    1) if total_achievements > 0 else 0
    total_xp_earned = UserAchievement.objects.filter(user=user, is_completed=True).aggregate(
        total=Sum('achievement__xp_reward')
    )['total'] or 0

    achievements_data = {
        'total': total_achievements,
        'unlocked': unlocked_achievements,
        'locked': locked_achievements,
        'percentage': achievements_percentage,
        'total_xp_earned': total_xp_earned,
    }

    # Badges
    total_badges = Badge.objects.filter(is_active=True).count()
    unlocked_badges = UserBadge.objects.filter(user=user).count()
    locked_badges = total_badges - unlocked_badges
    badges_percentage = round((unlocked_badges / total_badges * 100), 1) if total_badges > 0 else 0
    showcased_count = UserBadge.objects.filter(user=user, is_showcased=True).count()

    badges_data = {
        'total': total_badges,
        'unlocked': unlocked_badges,
        'locked': locked_badges,
        'percentage': badges_percentage,
        'showcased_count': showcased_count,
    }

    # Leitura
    books_read = ReadingProgress.objects.filter(user=user, finished_at__isnull=False, is_abandoned=False).count()
    books_reading = ReadingProgress.objects.filter(user=user, finished_at__isnull=True, is_abandoned=False).count()
    books_want = BookShelf.objects.filter(user=user, shelf_type='want_to_read').count()
    total_pages = ReadingProgress.objects.filter(user=user, finished_at__isnull=False, is_abandoned=False).aggregate(
        total=Sum('current_page')
    )['total'] or 0
    avg_pages_per_book = round(total_pages / books_read, 0) if books_read > 0 else 0

    reading_data = {
        'books_read': books_read,
        'books_reading': books_reading,
        'books_want': books_want,
        'total_pages': total_pages,
        'avg_pages_per_book': avg_pages_per_book,
    }

    # Reviews
    total_reviews = BookReview.objects.filter(user=user).count()
    avg_rating = BookReview.objects.filter(user=user).aggregate(avg=Avg('rating'))['avg'] or 0

    reviews_data = {
        'total': total_reviews,
        'avg_rating': round(avg_rating, 1),
    }

    # Ranking
    now = timezone.now()
    user_ranking = MonthlyRanking.get_or_create_current(user)
    MonthlyRanking.recalculate_positions(now.month, now.year)
    user_ranking.refresh_from_db()
    
    current_position = user_ranking.rank_position
    monthly_xp = user_ranking.total_xp

    best_position = MonthlyRanking.objects.filter(user=user, rank_position__gt=0).order_by('rank_position').first()
    best_position_value = best_position.rank_position if best_position else None

    ranking_data = {
        'current_position': current_position,
        'best_position': best_position_value,
        'monthly_xp': monthly_xp,
    }

    return JsonResponse({
        'success': True,
        'profile': profile_data,
        'achievements': achievements_data,
        'badges': badges_data,
        'reading': reading_data,
        'reviews': reviews_data,
        'ranking': ranking_data,
    })


@login_required
@require_POST
def claim_achievement(request):
    """
    API: Reivindica uma conquista manual (usado para conquistas especiais).

    POST /api/gamification/claim-achievement/
    Body: {"achievement_id": 1}

    Response:
    {
        "success": true,
        "message": "Conquista desbloqueada!",
        "achievement": {
            "id": 1,
            "name": "Especial",
            "xp_reward": 100
        },
        "new_xp": 2600,
        "new_level": 8
    }
    """
    user = request.user

    try:
        data = json.loads(request.body)
        achievement_id = data.get('achievement_id')

        if not achievement_id:
            return JsonResponse({
                'success': False,
                'error': 'achievement_id é obrigatório'
            }, status=400)

        # Verificar se a conquista existe
        try:
            achievement = Achievement.objects.get(id=achievement_id, is_active=True)
        except Achievement.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Conquista não encontrada'
            }, status=404)

        # Verificar se já está desbloqueada
        if UserAchievement.objects.filter(user=user, achievement=achievement).exists():
            return JsonResponse({
                'success': False,
                'error': 'Conquista já desbloqueada'
            }, status=400)

        # Verificar progresso (deve estar 100%)
        progress = calculate_achievement_progress_api(user, achievement)
        if progress < 100:
            return JsonResponse({
                'success': False,
                'error': f'Requisitos não cumpridos. Progresso: {progress}%'
            }, status=400)

        # Desbloquear conquista
        UserAchievement.objects.create(
            user=user,
            achievement=achievement,
            earned_at=timezone.now()
        )

        # Adicionar XP
        profile = user.profile
        old_xp = profile.total_xp
        profile.add_xp(achievement.xp_reward)
        new_xp = profile.total_xp
        new_level = profile.level

        # TODO: Criar notificação de conquista desbloqueada

        return JsonResponse({
            'success': True,
            'message': 'Conquista desbloqueada!',
            'achievement': {
                'id': achievement.id,
                'name': achievement.name,
                'description': achievement.description,
                'xp_reward': achievement.xp_reward,
                'icon': achievement.icon,
            },
            'xp_earned': achievement.xp_reward,
            'old_xp': old_xp,
            'new_xp': new_xp,
            'new_level': new_level,
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'JSON inválido'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_POST
def check_new_achievements(request):
    """
    API: Verifica se há novas conquistas e badges desbloqueados.
    Deve ser chamada após ações importantes (finalizar livro, criar review, etc).
    """
    user = request.user

    try:
        # Verificar e conceder novas conquistas e badges usando lógica do modelo
        newly_awarded_achievements = UserAchievement.check_and_award_achievements(user)
        newly_awarded_badges = UserBadge.check_and_award_badges(user)

        new_achievements = []
        total_xp_earned = 0
        for ua in newly_awarded_achievements:
            new_achievements.append({
                'id': ua.achievement.id,
                'name': ua.achievement.name,
                'description': ua.achievement.description,
                'xp_reward': ua.achievement.xp_reward,
                'icon': ua.achievement.icon,
                'category': ua.achievement.category,
            })
            total_xp_earned += ua.achievement.xp_reward

        new_badges = []
        for ub in newly_awarded_badges:
            new_badges.append({
                'id': ub.badge.id,
                'name': ub.badge.name,
                'description': ub.badge.description,
                'icon': ub.badge.icon,
                'rarity': ub.badge.rarity,
                'category': ub.badge.category,
            })

        # Recarregar perfil para pegar novo nível/XP
        user.profile.refresh_from_db()

        return JsonResponse({
            'success': True,
            'new_achievements': new_achievements,
            'new_badges': new_badges,
            'total_xp_earned': total_xp_earned,
            'new_level': user.profile.level,
            'new_xp': user.profile.total_xp,
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erro ao verificar conquistas e badges: {str(e)}'
        }, status=500)


@login_required
@require_GET
def get_achievement_details(request, achievement_id):
    """
    API: Retorna detalhes completos de uma conquista.
    Usado para exibir modal de detalhes.

    GET /api/gamification/achievement-details/<achievement_id>/

    Response:
    {
        "success": true,
        "achievement": {
            "id": 1,
            "name": "Primeiro Livro",
            "description": "Termine seu primeiro livro",
            "category": "leitura",
            "difficulty": "easy",
            "xp_reward": 50,
            "icon": "📖",
            "requirements": {...},
            "is_unlocked": true,
            "progress": 100,
            "earned_at": "2025-10-20T10:30:00Z",
            "total_unlocked_by": 1250,
            "unlock_percentage": 62.5
        }
    }
    """
    user = request.user

    try:
        achievement = Achievement.objects.get(id=achievement_id, is_active=True)
    except Achievement.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Conquista não encontrada'
        }, status=404)

    # Verificar se está desbloqueada
    is_unlocked = UserAchievement.objects.filter(user=user, achievement=achievement).exists()

    if is_unlocked:
        user_achievement = UserAchievement.objects.get(user=user, achievement=achievement)
        earned_at = user_achievement.earned_at.isoformat()
        progress = 100
    else:
        earned_at = None
        progress = calculate_achievement_progress_api(user, achievement)

    # Estatísticas globais
    total_unlocked_by = UserAchievement.objects.filter(achievement=achievement).count()
    total_users = UserProfile.objects.count()
    unlock_percentage = round((total_unlocked_by / total_users * 100), 1) if total_users > 0 else 0

    # Parsear requirements
    try:
        requirements = json.loads(achievement.requirements_json)
    except (json.JSONDecodeError, TypeError):
        requirements = {}

    return JsonResponse({
        'success': True,
        'achievement': {
            'id': achievement.id,
            'name': achievement.name,
            'description': achievement.description,
            'category': achievement.category,
            'difficulty': achievement.difficulty_level,
            'xp_reward': achievement.xp_reward,
            'icon': achievement.icon,
            'requirements': requirements,
            'is_unlocked': is_unlocked,
            'progress': progress,
            'earned_at': earned_at,
            'total_unlocked_by': total_unlocked_by,
            'unlock_percentage': unlock_percentage,
        }
    })


# ==========================================
# FUNÇÕES AUXILIARES
# ==========================================

def calculate_achievement_progress_api(user, achievement):
    """
    Calcula o progresso do usuário em uma conquista.
    Retorna valor de 0 a 100.
    Versão otimizada para APIs.
    """
    try:
        requirements = json.loads(achievement.requirements_json)
    except (json.JSONDecodeError, TypeError):
        return 0

    requirement_type = requirements.get('type')
    target_value = requirements.get('value', 1)

    current_value = get_current_value_for_requirement(user, requirement_type)

    # Calcular percentual
    if target_value > 0:
        progress = min(100, round((current_value / target_value) * 100, 1))
    else:
        progress = 0

    return progress


def get_current_value_for_requirement(user, requirement_type):
    """
    Retorna o valor atual do usuário para um tipo de requisito.
    """
    if requirement_type == 'books_read':
        return max(
            user.profile.books_read_count if hasattr(user, 'profile') else 0,
            ReadingProgress.objects.filter(user=user, finished_at__isnull=False, is_abandoned=False).count()
        )

    elif requirement_type == 'books_finished_before_deadline':
        return ReadingProgress.objects.filter(
            user=user,
            finished_at__isnull=False,
            is_abandoned=False,
            deadline__isnull=False,
            finished_at__date__lt=F('deadline')
        ).count()

    elif requirement_type == 'pages_read_in_day':
        today = timezone.now().date()
        return ReadingProgress.objects.filter(
            user=user,
            last_updated__date=today
        ).aggregate(total=Sum('current_page'))['total'] or 0

    elif requirement_type == 'reviews_written':
        return BookReview.objects.filter(user=user).count()

    elif requirement_type == 'review_likes':
        # TODO: Implementar quando houver sistema de likes
        return 0

    elif requirement_type == 'different_categories':
        shelf_categories = BookShelf.objects.filter(user=user, shelf_type='read').values('book__category').distinct().count()
        progress_categories = ReadingProgress.objects.filter(
            user=user,
            finished_at__isnull=False,
            is_abandoned=False
        ).values('book__category').distinct().count()
        return max(shelf_categories, progress_categories)

    elif requirement_type == 'different_authors':
        shelf_authors = BookShelf.objects.filter(user=user, shelf_type='read').values('book__author').distinct().count()
        progress_authors = ReadingProgress.objects.filter(
            user=user,
            finished_at__isnull=False,
            is_abandoned=False
        ).values('book__author').distinct().count()
        return max(shelf_authors, progress_authors)

    elif requirement_type == 'reading_streak_days':
        if hasattr(user, 'profile'):
            return user.profile.streak_days
        return 0

    else:
        return 0