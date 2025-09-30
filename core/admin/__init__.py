"""
Configuração modular do Django Admin.
Cada model tem seu próprio arquivo admin para melhor organização.
"""

from .category_admin import CategoryAdmin
from .author_admin import AuthorAdmin
from .book_admin import BookAdmin
from .video_admin import VideoAdmin
from .section_admin import SectionAdmin, SectionItemAdmin
from .event_admin import EventAdmin

__all__ = [
    'CategoryAdmin',
    'AuthorAdmin',
    'BookAdmin',
    'VideoAdmin',
    'SectionAdmin',
    'SectionItemAdmin',
    'EventAdmin',
]