"""
Configuração modular do Django Admin.
Cada model tem seu próprio arquivo admin para melhor organização.
"""

from .category_admin import CategoryAdmin
from .author_admin import AuthorAdmin
from .book_admin import BookAdmin
from .video_admin import VideoAdmin
from .section_admin import SectionAdmin
from .event_admin import EventAdmin
from .banner_admin import BannerAdmin

__all__ = [
    'CategoryAdmin',
    'AuthorAdmin',
    'BookAdmin',
    'VideoAdmin',
    'SectionAdmin',
    'EventAdmin',
    'BannerAdmin',
]

# URLs customizadas para Google Books
from django.urls import path
from django.contrib import admin as django_admin
from core.views import google_books_views

# Salvar referência original
_original_get_urls = django_admin.site.get_urls

def get_urls():
    custom_urls = [
        path('google-books/search/',
             google_books_views.google_books_search,
             name='google_books_search'),
        path('google-books/import/<str:google_book_id>/',
             google_books_views.google_books_import,
             name='google_books_import'),
    ]
    return custom_urls + _original_get_urls()

django_admin.site.get_urls = get_urls


# Dashboard personalizada
from core.views.dashboard_view import admin_dashboard
from django.views.generic import RedirectView

# Adicionar URL da dashboard e redirecionar index
_original_get_urls_2 = django_admin.site.get_urls

def get_urls_with_dashboard():
    from django.urls import path
    custom_urls = [
        path('', admin_dashboard, name='index'),  # ✅ Substitui a home padrão
        path('dashboard/', admin_dashboard, name='dashboard'),  # ✅ Mantém URL alternativa
    ]
    return custom_urls + _original_get_urls_2()

django_admin.site.get_urls = get_urls_with_dashboard