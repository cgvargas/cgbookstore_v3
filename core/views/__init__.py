"""
Views do aplicativo core.
Inclui views principais, AJAX, gamificação e APIs REST.
"""

# Views principais do site
from .home_view import HomeView
from .book_views import BookListView
from .book_redirect_view import BookRedirectView
from .book_detail_view import BookDetailView
from .author_views import AuthorListView, AuthorDetailView
from .video_views import VideoListView
from .search_view import SearchView
from .about_view import AboutView
from .contact_view import ContactView
from .faq_view import FAQView
from .library_view import LibraryView
from .event_views import EventListView, EventDetailView
from .tolkien_view import TolkienWorldView
from .universe_view import LiteraryUniverseView
from .terms_view import TermsOfServiceView
from .privacy_view import PrivacyPolicyView

# Views AJAX - Biblioteca Pessoal
from .library_ajax_views import (
    add_to_shelf,
    remove_from_shelf,
    get_book_shelves,
    create_custom_shelf,
    move_to_shelf,
    delete_custom_shelf,
    rename_custom_shelf,
)

# Views de Busca de Livros
from . import book_search_views

# Views de Dashboard Admin
from .dashboard_view import admin_dashboard

# Views de Relatórios (Reports Dashboard)
from .reports_dashboard import (
    reports_dashboard,
    export_books_csv,
    export_authors_csv,
    export_videos_csv,
    export_books_markdown,
    export_authors_markdown,
    export_videos_markdown,
    export_finance_markdown,
)

# Gamificação - Views Principais (FASE 2.1)
from .gamification_views import (
    dashboard_view,
    achievements_list_view,
    badges_collection_view,
    monthly_ranking_view,
    user_profile_stats,
)

# Gamificação - APIs REST (FASE 2.2)
from .gamification_api_views import (
    get_user_achievements,
    get_achievement_progress,
    get_user_badges,
    showcase_badge,
    remove_showcase_badge,
    get_monthly_ranking,
    get_user_stats,
    claim_achievement,
    check_new_achievements,
    get_achievement_details,
)

__all__ = [
    # Views principais
    'HomeView',
    'BookRedirectView',
    'BookListView',
    'BookDetailView',
    'AuthorListView',
    'AuthorDetailView',
    'VideoListView',
    'SearchView',
    'AboutView',
    'ContactView',
    'FAQView',
    'LibraryView',
    'EventListView',
    'EventDetailView',
    'TolkienWorldView',
    'LiteraryUniverseView',
    'TermsOfServiceView',
    'PrivacyPolicyView',

    # AJAX - Biblioteca
    'add_to_shelf',
    'remove_from_shelf',
    'get_book_shelves',
    'create_custom_shelf',
    'move_to_shelf',
    'delete_custom_shelf',
    'rename_custom_shelf',

    # Busca de livros
    'book_search_views',

    # Dashboard admin
    'admin_dashboard',

    # Gamificação - Views (FASE 2.1)
    'dashboard_view',
    'achievements_list_view',
    'badges_collection_view',
    'monthly_ranking_view',
    'user_profile_stats',

    # Gamificação - APIs (FASE 2.2)
    'get_user_achievements',
    'get_achievement_progress',
    'get_user_badges',
    'showcase_badge',
    'remove_showcase_badge',
    'get_monthly_ranking',
    'get_user_stats',
    'claim_achievement',
    'check_new_achievements',
    'get_achievement_details',
]