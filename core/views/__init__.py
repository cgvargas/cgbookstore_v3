# C:\Users\claud\OneDrive\ProjectsDjango\CGBookStore_v3\core\views\__init__.py

"""
Core Views Package
Centraliza todas as views do app core para facilitar imports
"""

from .home_view import HomeView
from .book_views import BookListView
from .search_view import SearchView
from .about_view import AboutView
from .contact_view import ContactView
from .library_view import LibraryView

__all__ = [
    'HomeView',
    'BookListView',
    'SearchView',
    'AboutView',
    'ContactView',
    'LibraryView',
]