"""
Importações dos modelos da app accounts.
"""

from .user_profile import UserProfile
from .book_shelf import BookShelf
from .reading_progress import ReadingProgress
from .book_review import BookReview
from .base_notification import BaseNotification, NotificationRegistry
from .reading_notification import ReadingNotification, SystemNotification
from .campaign_notification import CampaignNotification

# Novos models de gamificação
from .achievement import Achievement
from .user_achievement import UserAchievement
from .badge import Badge
from .user_badge import UserBadge
from .monthly_ranking import MonthlyRanking
from .xp_multiplier import XPMultiplier

# Modelo de exclusão de conta
from .account_deletion import AccountDeletion

__all__ = [
    'UserProfile',
    'BookShelf',
    'ReadingProgress',
    'BookReview',
    'BaseNotification',
    'NotificationRegistry',
    'ReadingNotification',
    'SystemNotification',
    'CampaignNotification',
    # Gamificação
    'Achievement',
    'UserAchievement',
    'Badge',
    'UserBadge',
    'MonthlyRanking',
    'XPMultiplier',
    # Exclusão de conta
    'AccountDeletion',
]