from django.urls import path
from core.views import (
    HomeView,
    BookListView,
    BookDetailView,
    AuthorListView,
    AuthorDetailView,
    SearchView,
    AboutView,
    ContactView,
    LibraryView,
    EventListView,
    # Views AJAX - Biblioteca Pessoal
    add_to_shelf,
    remove_from_shelf,
    get_book_shelves,
    create_custom_shelf,
    move_to_shelf,
    book_search_views,
    delete_custom_shelf,
    rename_custom_shelf,
)

# Progresso de Leitura e Notificações
from core.views.reading_progress_views import (
    update_reading_progress,
    set_reading_deadline,
    remove_reading_deadline,
    abandon_book_manual,
    restore_book,
    get_reading_stats,
    mark_notification_read,
    mark_all_notifications_read,
    get_notifications,
    delete_selected_notifications,
    get_unread_notifications_count,
    get_all_notifications_unified,
    mark_notification_read_unified,
    delete_selected_notifications_unified,
    mark_all_notifications_as_read,
)

# GAMIFICAÇÃO - Views Principais (FASE 2.1)
from core.views.gamification_views import (
    dashboard_view,
    achievements_list_view,
    badges_collection_view,
    monthly_ranking_view,
    user_profile_stats,
)

# GAMIFICAÇÃO - APIs REST (FASE 2.2)
from core.views.gamification_api_views import (
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

app_name = 'core'

urlpatterns = [
    # ==========================================
    # ROTAS PRINCIPAIS DO SITE
    # ==========================================
    path('', HomeView.as_view(), name='home'),
    path('livros/', BookListView.as_view(), name='book_list'),
    path('livros/<slug:slug>/', BookDetailView.as_view(), name='book_detail'),
    path('autores/', AuthorListView.as_view(), name='author_list'),
    path('autores/<slug:slug>/', AuthorDetailView.as_view(), name='author_detail'),
    path('buscar/', SearchView.as_view(), name='search'),
    path('sobre/', AboutView.as_view(), name='about'),
    path('contato/', ContactView.as_view(), name='contact'),
    path('biblioteca/', LibraryView.as_view(), name='library'),
    path('eventos/', EventListView.as_view(), name='events'),

    # ==========================================
    # APIs AJAX - BIBLIOTECA PESSOAL
    # ==========================================
    path('api/library/add-to-shelf/', add_to_shelf, name='add_to_shelf'),
    path('api/library/remove-from-shelf/', remove_from_shelf, name='remove_from_shelf'),
    path('api/library/get-book-shelves/<int:book_id>/', get_book_shelves, name='get_book_shelves'),
    path('api/library/create-custom-shelf/', create_custom_shelf, name='create_custom_shelf'),
    path('api/library/move-to-shelf/', move_to_shelf, name='move_to_shelf'),
    path('api/library/delete-custom-shelf/', delete_custom_shelf, name='delete_custom_shelf'),
    path('api/library/rename-custom-shelf/', rename_custom_shelf, name='rename_custom_shelf'),

    # ==========================================
    # APIs AJAX - PROGRESSO DE LEITURA
    # ==========================================
    path('api/reading/update-progress/', update_reading_progress, name='update_reading_progress'),
    path('api/reading/set-deadline/', set_reading_deadline, name='set_reading_deadline'),
    path('api/reading/remove-deadline/', remove_reading_deadline, name='remove_reading_deadline'),
    path('api/reading/abandon-book/', abandon_book_manual, name='abandon_book_manual'),
    path('api/reading/restore-book/', restore_book, name='restore_book'),
    path('api/reading/stats/<int:book_id>/', get_reading_stats, name='get_reading_stats'),

    # ==========================================
    # APIs AJAX - BUSCA E IMPORTAÇÃO DE LIVROS
    # ==========================================
    path('api/books/search-local/', book_search_views.local_books_search_api, name='api_search_local'),
    path('api/books/search-google/', book_search_views.google_books_search_user, name='api_search_google'),
    path('api/books/import-google/<str:google_book_id>/', book_search_views.import_google_book_user,
         name='api_import_google'),

    # ==========================================
    # APIs AJAX - NOTIFICAÇÕES
    # ==========================================
    path('api/notifications/mark-read/', mark_notification_read, name='mark_notification_read'),
    path('api/notifications/mark-all-read/', mark_all_notifications_read, name='mark_all_notifications_read'),
    path('api/notifications/list/', get_notifications, name='get_notifications'),
    path('api/notifications/delete-selected/', delete_selected_notifications, name='delete_selected_notifications'),
    path('api/notifications/unread-count/', get_unread_notifications_count, name='notifications_unread_count'),
    path('api/notifications/unified/', get_all_notifications_unified, name='notifications_unified'),
    path('api/notifications/unified/mark-read/', mark_notification_read_unified, name='mark_notification_read_unified'),
    path('api/notifications/unified/delete-selected/', delete_selected_notifications_unified,
         name='delete_selected_notifications_unified'),
    path('api/notifications/unified/mark-all-read/', mark_all_notifications_as_read,
         name='mark_all_notifications_as_read'),

    # ==========================================
    # GAMIFICAÇÃO - VIEWS PRINCIPAIS (FASE 2.1)
    # ==========================================
    path('gamificacao/', dashboard_view, name='gamification_dashboard'),
    path('gamificacao/conquistas/', achievements_list_view, name='achievements_list'),
    path('gamificacao/badges/', badges_collection_view, name='badges_collection'),
    path('gamificacao/ranking/', monthly_ranking_view, name='monthly_ranking'),
    path('gamificacao/perfil-stats/', user_profile_stats, name='user_profile_stats'),

    # ==========================================
    # GAMIFICAÇÃO - APIs REST (FASE 2.2)
    # ==========================================

    # Conquistas
    path('api/gamification/achievements/', get_user_achievements, name='api_user_achievements'),
    path('api/gamification/achievement-progress/<int:achievement_id>/', get_achievement_progress,
         name='api_achievement_progress'),
    path('api/gamification/achievement-details/<int:achievement_id>/', get_achievement_details,
         name='api_achievement_details'),
    path('api/gamification/claim-achievement/', claim_achievement, name='api_claim_achievement'),
    path('api/gamification/check-new-achievements/', check_new_achievements, name='api_check_new_achievements'),

    # Badges
    path('api/gamification/badges/', get_user_badges, name='api_user_badges'),
    path('api/gamification/showcase-badge/', showcase_badge, name='api_showcase_badge'),
    path('api/gamification/remove-showcase-badge/', remove_showcase_badge, name='api_remove_showcase_badge'),

    # Ranking e Estatísticas
    path('api/gamification/ranking/', get_monthly_ranking, name='api_monthly_ranking'),
    path('api/gamification/user-stats/', get_user_stats, name='api_user_stats'),
]