"""
Views do app Core.
Importa e expõe todas as views para uso nas URLs.
"""

from .home_view import HomeView
from .book_views import BookListView
from .book_detail_view import BookDetailView
from .search_view import SearchView
from .about_view import AboutView
from .contact_view import ContactView
from .library_view import LibraryView
from .event_views import EventListView
from .library_ajax_views import (
    add_to_shelf,
    remove_from_shelf,
    get_book_shelves,
    create_custom_shelf,
    move_to_shelf,
    delete_custom_shelf,
    rename_custom_shelf,
    update_book_notes,
)

__all__ = [
    'HomeView',
    'BookListView',
    'BookDetailView',
    'SearchView',
    'AboutView',
    'ContactView',
    'LibraryView',
    'EventListView',
]

