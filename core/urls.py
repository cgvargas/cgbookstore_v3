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
]