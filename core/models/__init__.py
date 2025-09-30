"""
Models do app Core.
Estrutura modular para facilitar manutenção e escalabilidade.
"""

from .category import Category
from .author import Author
from .book import Book

__all__ = [
    'Category',
    'Author',
    'Book',
]