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
    delete_custom_shelf,
    rename_custom_shelf,
    update_book_notes,
)
# NOVO: Importar views de busca do Google Books
from core.views.book_search_views import (
    google_books_search_user,
    import_google_book_user,
    local_books_search_api,
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

    # APIs AJAX - Biblioteca Pessoal
    path('api/library/add-to-shelf/', add_to_shelf, name='add_to_shelf'),
    path('api/library/remove-from-shelf/', remove_from_shelf, name='remove_from_shelf'),
    path('api/library/get-book-shelves/<int:book_id>/', get_book_shelves, name='get_book_shelves'),
    path('api/library/create-custom-shelf/', create_custom_shelf, name='create_custom_shelf'),
    path('api/library/move-to-shelf/', move_to_shelf, name='move_to_shelf'),
    path('api/library/delete-custom-shelf/', delete_custom_shelf, name='delete_custom_shelf'),
    path('api/library/rename-custom-shelf/', rename_custom_shelf, name='rename_custom_shelf'),
    path('api/library/update-book-notes/', update_book_notes, name='update_book_notes'),

    # APIs - Busca e Importação Google Books
    path('api/books/search-google/', google_books_search_user, name='search_google_books_user'),
    path('api/books/import-google/<str:google_book_id>/', import_google_book_user, name='import_google_book_user'),

    # ROTA DE API PARA BUSCA LOCAL
    path('api/books/search-local/', local_books_search_api, name='search_local_books_api'),
]