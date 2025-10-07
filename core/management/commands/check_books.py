"""
Management command para diagnosticar livros no banco.
Uso: python manage.py check_books
"""

from django.core.management.base import BaseCommand
from core.models import Book, Author, Category


class Command(BaseCommand):
    help = 'Diagnostica livros no banco de dados'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('DIAGNOSTICO DE LIVROS'))
        self.stdout.write(self.style.SUCCESS('=' * 60))

        # Contadores gerais
        total_books = Book.objects.count()
        total_authors = Author.objects.count()
        total_categories = Category.objects.count()

        self.stdout.write(f'\nTOTAIS:')
        self.stdout.write(f'  Livros: {total_books}')
        self.stdout.write(f'  Autores: {total_authors}')
        self.stdout.write(f'  Categorias: {total_categories}')

        # Livros com e sem capa
        books_with_cover = Book.objects.exclude(cover_image='').exclude(cover_image__isnull=True).count()
        books_without_cover = total_books - books_with_cover

        self.stdout.write(f'\nCAPAS:')
        self.stdout.write(f'  Com capa: {books_with_cover}')
        self.stdout.write(f'  Sem capa: {books_without_cover}')

        # Livros sem autor
        books_without_author = Book.objects.filter(author__isnull=True).count()
        self.stdout.write(f'\nAUTORES:')
        self.stdout.write(f'  Sem autor: {books_without_author}')

        # Livros sem categoria
        books_without_category = Book.objects.filter(category__isnull=True).count()
        self.stdout.write(f'\nCATEGORIAS:')
        self.stdout.write(f'  Sem categoria: {books_without_category}')

        # Últimos 10 livros criados
        self.stdout.write(f'\nULTIMOS 10 LIVROS CRIADOS:')
        latest_books = Book.objects.select_related('author', 'category').order_by('-created_at')[:10]

        for i, book in enumerate(latest_books, 1):
            author_name = book.author.name if book.author else 'SEM AUTOR'
            category_name = book.category.name if book.category else 'SEM CATEGORIA'
            has_cover = 'SIM' if book.cover_image else 'NAO'

            self.stdout.write(
                f'  {i}. {book.title[:40]:40} | '
                f'Autor: {author_name[:20]:20} | '
                f'Cat: {category_name[:15]:15} | '
                f'Capa: {has_cover}'
            )

        # Livros por origem
        self.stdout.write(f'\nORIGEM DOS LIVROS:')
        google_books = Book.objects.exclude(google_books_id='').exclude(google_books_id__isnull=True).count()
        manual = total_books - google_books

        self.stdout.write(f'  Google Books: {google_books}')
        self.stdout.write(f'  Manual/Populate: {manual}')

        self.stdout.write(self.style.SUCCESS('\n' + '=' * 60))