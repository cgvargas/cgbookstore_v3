"""
Management command para testar a integração com Google Books API.
"""

from django.core.management.base import BaseCommand
from core.utils.google_books_api import (
    search_books,
    get_book_by_isbn,
    search_books_by_author,
    search_books_by_publisher
)
import json


class Command(BaseCommand):
    help = 'Testa a integração com Google Books API'

    def add_arguments(self, parser):
        parser.add_argument(
            '--title',
            type=str,
            help='Buscar por título',
        )
        parser.add_argument(
            '--author',
            type=str,
            help='Buscar por autor',
        )
        parser.add_argument(
            '--isbn',
            type=str,
            help='Buscar por ISBN',
        )
        parser.add_argument(
            '--publisher',
            type=str,
            help='Buscar por editora',
        )
        parser.add_argument(
            '--query',
            type=str,
            help='Busca geral',
        )
        parser.add_argument(
            '--max-results',
            type=int,
            default=5,
            help='Número máximo de resultados (padrão: 5)',
        )

    def handle(self, *args, **options):
        title = options.get('title')
        author = options.get('author')
        isbn = options.get('isbn')
        publisher = options.get('publisher')
        query = options.get('query')
        max_results = options['max_results']

        self.stdout.write(self.style.SUCCESS('🔍 TESTE - Google Books API'))
        self.stdout.write('=' * 60)
        self.stdout.write('')

        # Teste de busca por ISBN
        if isbn:
            self.stdout.write(self.style.WARNING(f'📖 Buscando ISBN: {isbn}'))
            result = get_book_by_isbn(isbn)

            if result:
                self.print_book_info(result)
            else:
                self.stdout.write(self.style.ERROR('❌ Nenhum resultado encontrado'))
            return

        # Teste de busca geral
        self.stdout.write(self.style.WARNING('🔎 Parâmetros de busca:'))
        if query:
            self.stdout.write(f'  Query: {query}')
        if title:
            self.stdout.write(f'  Título: {title}')
        if author:
            self.stdout.write(f'  Autor: {author}')
        if publisher:
            self.stdout.write(f'  Editora: {publisher}')
        self.stdout.write(f'  Max resultados: {max_results}')
        self.stdout.write('')

        # Realizar busca
        results = search_books(
            query=query,
            title=title,
            author=author,
            publisher=publisher,
            max_results=max_results
        )

        # Verificar erros
        if 'error' in results:
            self.stdout.write(self.style.ERROR(f'❌ Erro: {results["error"]}'))
            return

        # Mostrar resultados
        total = results.get('total_items', 0)
        books = results.get('books', [])

        self.stdout.write(self.style.SUCCESS(f'📚 Total de itens encontrados: {total}'))
        self.stdout.write(self.style.SUCCESS(f'📋 Mostrando {len(books)} resultados:'))
        self.stdout.write('')

        if not books:
            self.stdout.write(self.style.WARNING('⚠️  Nenhum livro encontrado'))
            return

        # Exibir cada livro
        for index, book in enumerate(books, start=1):
            self.stdout.write(self.style.SUCCESS(f'--- LIVRO {index} ---'))
            self.print_book_info(book)
            self.stdout.write('')

    def print_book_info(self, book):
        """Imprime informações de um livro de forma formatada."""

        self.stdout.write(f'📕 Título: {book.get("title", "N/A")}')

        if book.get('subtitle'):
            self.stdout.write(f'   Subtítulo: {book.get("subtitle")}')

        authors = book.get('authors', [])
        if authors:
            self.stdout.write(f'✍️  Autores: {", ".join(authors)}')

        if book.get('publisher'):
            self.stdout.write(f'🏢 Editora: {book.get("publisher")}')

        if book.get('published_date'):
            self.stdout.write(f'📅 Data de publicação: {book.get("published_date")}')

        if book.get('isbn_13'):
            self.stdout.write(f'🔢 ISBN-13: {book.get("isbn_13")}')

        if book.get('isbn_10'):
            self.stdout.write(f'🔢 ISBN-10: {book.get("isbn_10")}')

        if book.get('page_count'):
            self.stdout.write(f'📄 Páginas: {book.get("page_count")}')

        categories = book.get('categories', [])
        if categories:
            self.stdout.write(f'🏷️  Categorias: {", ".join(categories)}')

        if book.get('language'):
            self.stdout.write(f'🌐 Idioma: {book.get("language")}')

        if book.get('average_rating'):
            rating = book.get('average_rating')
            count = book.get('ratings_count', 0)
            self.stdout.write(f'⭐ Avaliação: {rating}/5 ({count} avaliações)')

        if book.get('thumbnail'):
            self.stdout.write(f'🖼️  Capa: {book.get("thumbnail")}')

        if book.get('description'):
            desc = book.get('description', '')[:150]
            self.stdout.write(f'📝 Descrição: {desc}...')

        if book.get('google_book_id'):
            self.stdout.write(f'🆔 Google Book ID: {book.get("google_book_id")}')