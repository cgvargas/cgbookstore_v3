"""
Serviço de Badges - CGBookStore v3

Responsável por criar e conceder badges de conquistas aos usuários:
  - 'Membro Premium'  → assinantes Premium (pagos ou campanha)
  - 'Voz do Debate'   → participar pela 1ª vez de um debate (criar tópico ou responder)
  - 'Mestre do Quiz'  → completar um quiz pela 1ª vez
"""

import logging
from django.conf import settings

logger = logging.getLogger(__name__)


# ─── Configurações dos badges ───────────────────────────────────────────────

PREMIUM_BADGE_CONFIG = {
    'name': 'Membro Premium',
    'slug': 'membro-premium',
    'description': 'Concedido a membros que apoiam a CGBookStore com uma assinatura Premium.',
    'icon': '👑',
    'rarity': 'gold',
    'category': 'special_event',
    'display_order': 1,
    'is_active': True,
    'requirements_json': {'premium_subscriber': True},
}

DEBATE_BADGE_CONFIG = {
    'name': 'Voz do Debate',
    'slug': 'voz-do-debate',
    'description': 'Concedido a quem participa pela primeira vez de um debate literário na CGBookStore.',
    'icon': '💬',
    'rarity': 'silver',
    'category': 'social',
    'display_order': 2,
    'is_active': True,
    'requirements_json': {'debate_participant': True},
}

QUIZ_BADGE_CONFIG = {
    'name': 'Mestre do Quiz',
    'slug': 'mestre-do-quiz',
    'description': 'Concedido a quem completa um quiz literário pela primeira vez na CGBookStore.',
    'icon': '🧠',
    'rarity': 'silver',
    'category': 'achievement',
    'display_order': 3,
    'is_active': True,
    'requirements_json': {'quiz_participant': True},
}


# ─── Funções auxiliares ─────────────────────────────────────────────────────

def _get_static_badge_url(filename):
    """Retorna a URL absoluta de uma imagem de badge nos statics."""
    site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000').rstrip('/')
    return f"{site_url}/static/images/badges/{filename}"


def _ensure_badge_exists(config):
    """
    Garante que um badge existe no banco de dados (get_or_create pelo slug).

    Args:
        config (dict): Dicionário de configuração do badge (ex: DEBATE_BADGE_CONFIG)

    Returns:
        Badge: Instância do badge
    """
    from accounts.models import Badge

    badge, created = Badge.objects.get_or_create(
        slug=config['slug'],
        defaults={
            'name': config['name'],
            'description': config['description'],
            'icon': config['icon'],
            'rarity': config['rarity'],
            'category': config['category'],
            'display_order': config['display_order'],
            'is_active': config['is_active'],
            'requirements_json': config['requirements_json'],
        }
    )

    if created:
        logger.info(f"Badge '{config['name']}' criado no banco de dados.")
    else:
        logger.debug(f"Badge '{config['name']}' já existe no banco de dados.")

    return badge


def _grant_badge(user, config):
    """
    Função genérica para conceder um badge a um usuário.

    Args:
        user: Instância do modelo User do Django
        config (dict): Dicionário de configuração do badge

    Returns:
        tuple: (user_badge, created)
    """
    try:
        from accounts.models import UserBadge

        badge = _ensure_badge_exists(config)
        user_badge, created = UserBadge.award_badge(user=user, badge=badge)

        if created:
            logger.info(f"Badge '{config['name']}' concedido a {user.username} ({user.email})")
        else:
            logger.debug(f"Usuário {user.username} já possui o badge '{config['name']}'.")

        return user_badge, created

    except Exception as e:
        logger.error(f"Erro ao conceder badge '{config['name']}' para {user.username}: {e}")
        return None, False


# ─── API pública ─────────────────────────────────────────────────────────────

def ensure_premium_badge_exists():
    """Garante que o badge 'Membro Premium' existe no banco. Retorna a instância."""
    return _ensure_badge_exists(PREMIUM_BADGE_CONFIG)


def grant_premium_badge(user):
    """
    Concede o badge 'Membro Premium' a um usuário (assinantes pagos e campanhas).

    Returns:
        tuple: (user_badge, created)
    """
    return _grant_badge(user, PREMIUM_BADGE_CONFIG)


def grant_debate_badge(user):
    """
    Concede o badge 'Voz do Debate' ao usuário na primeira participação em debate.

    Deve ser chamado em: create_topic() e create_post() no debates/views.py.

    Returns:
        tuple: (user_badge, created)
    """
    return _grant_badge(user, DEBATE_BADGE_CONFIG)


def grant_quiz_badge(user):
    """
    Concede o badge 'Mestre do Quiz' ao usuário na primeira vez que completa um quiz.

    Deve ser chamado em: submit_quiz() no news/views.py.

    Returns:
        tuple: (user_badge, created)
    """
    return _grant_badge(user, QUIZ_BADGE_CONFIG)


def get_premium_badge_context():
    """
    Retorna dicionário com dados do badge Premium para templates de e-mail.

    Returns:
        dict: Contexto do badge
    """
    return {
        'badge_name': PREMIUM_BADGE_CONFIG['name'],
        'badge_icon': PREMIUM_BADGE_CONFIG['icon'],
        'badge_rarity': 'Ouro',
        'badge_rarity_emoji': '🥇',
        'badge_description': PREMIUM_BADGE_CONFIG['description'],
        'badge_image_url': _get_static_badge_url('premium_badge.png'),
    }
