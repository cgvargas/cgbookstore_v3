"""
Models do app Core.
Estrutura modular para facilitar manutenção e escalabilidade.
"""

from .category import Category
from .author import Author
from .author_work import AuthorWork
from .book import Book
from .video import Video
from .section import Section
from .section_item import SectionItem
from .event import Event
from .banner import Banner
from .featured_author_settings import FeaturedAuthorSettings
from .literary_universe import LiteraryUniverse, UniverseContentItem, UniverseBanner

__all__ = [
    'Category',
    'Author',
    'AuthorWork',
    'Book',
    'Video',
    'Section',
    'SectionItem',
    'Event',
    'Banner',
    'FeaturedAuthorSettings',
    'LiteraryUniverse',
    'UniverseContentItem',
    'UniverseBanner',
]

