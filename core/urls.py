from django.urls import path
from core.views import (
    HomeView,
    BookListView,
    BookDetailView,
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
)

app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('livros/', BookListView.as_view(), name='book_list'),
    path('livros/<slug:slug>/', BookDetailView.as_view(), name='book_detail'),
    path('buscar/', SearchView.as_view(), name='search'),
    path('sobre/', AboutView.as_view(), name='about'),
    path('contato/', ContactView.as_view(), name='contact'),
    path('biblioteca/', LibraryView.as_view(), name='library'),
    path('eventos/', EventListView.as_view(), name='events'),

    # APIs AJAX - Biblioteca Pessoal (Existentes)
    path('api/library/add-to-shelf/', add_to_shelf, name='add_to_shelf'),
    path('api/library/remove-from-shelf/', remove_from_shelf, name='remove_from_shelf'),
    path('api/library/get-book-shelves/<int:book_id>/', get_book_shelves, name='get_book_shelves'),
    path('api/library/create-custom-shelf/', create_custom_shelf, name='create_custom_shelf'),
    path('api/library/move-to-shelf/', move_to_shelf, name='move_to_shelf'),

    # ✅ ROTAS ADICIONADAS AQUI
    path('api/library/delete-custom-shelf/', delete_custom_shelf, name='delete_custom_shelf'),
    path('api/library/rename-custom-shelf/', rename_custom_shelf, name='rename_custom_shelf'),

    # APIs AJAX - Progresso de Leitura (NOVAS)
    path('api/reading/update-progress/', update_reading_progress, name='update_reading_progress'),
    path('api/reading/set-deadline/', set_reading_deadline, name='set_reading_deadline'),
    path('api/reading/remove-deadline/', remove_reading_deadline, name='remove_reading_deadline'),
    path('api/reading/abandon-book/', abandon_book_manual, name='abandon_book_manual'),
    path('api/reading/restore-book/', restore_book, name='restore_book'),
    path('api/reading/stats/<int:book_id>/', get_reading_stats, name='get_reading_stats'),

    # APIs AJAX - Busca e importação de livros locais e Google Books
    path('api/books/search-local/', book_search_views.local_books_search_api, name='api_search_local'),
    path('api/books/search-google/', book_search_views.google_books_search_user, name='api_search_google'),
    path('api/books/import-google/<str:google_book_id>/', book_search_views.import_google_book_user, name='api_import_google'),

    # APIs AJAX - Notificações (NOVAS)
    path('api/notifications/mark-read/', mark_notification_read, name='mark_notification_read'),
    path('api/notifications/mark-all-read/', mark_all_notifications_read, name='mark_all_notifications_read'),
    path('api/notifications/list/', get_notifications, name='get_notifications'),
]