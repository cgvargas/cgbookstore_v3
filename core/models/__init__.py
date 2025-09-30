"""
Models do app Core.
Estrutura modular para facilitar manutenção e escalabilidade.
"""

from .category import Category
from .author import Author
from .book import Book
from .video import Video
from .section import Section
from .section_item import SectionItem

__all__ = [
    'Category',
    'Author',
    'Book',
    'Video',
    'Section',
    'SectionItem',
]