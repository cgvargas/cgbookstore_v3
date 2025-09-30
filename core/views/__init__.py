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