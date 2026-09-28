"""
Testes automatizados para a importação de livros do Google Books e prevenção de overflow de campos varchar(50).
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from unittest.mock import patch
from core.models import Book, Author, Category


class GoogleBooksImportSafetyTest(TestCase):
    """Testes de segurança na importação de livros do Google Books."""

    def setUp(self):
        User = get_user_model()
        self.staff_user = User.objects.create_superuser(
            username='staff_test_gb',
            email='staff_gb@test.com',
            password='password123'
        )
        self.client.login(username='staff_test_gb', password='password123')

    def test_category_long_name_and_slug(self):
        """Testa criação de categoria com nome longo (>50 chars e até >100 chars)."""
        long_name = "Juvenile Nonfiction / Social Science / Customs, Traditions, Anthropology / Extended Deep Niche"
        cat = Category.objects.create(name=long_name)
        self.assertEqual(cat.name, long_name)
        self.assertTrue(len(cat.slug) > 0)
        self.assertTrue(len(cat.slug) <= 220)

    def test_author_long_name_and_slug(self):
        """Testa criação de autor com nome longo (>50 chars)."""
        long_name = "Associação Brasileira de Pesquisadores e Escritores Científicos de Ficção e Tecnologia"
        author = Author.objects.create(name=long_name)
        self.assertEqual(author.name, long_name)
        self.assertTrue(len(author.slug) > 0)
        self.assertTrue(len(author.slug) <= 220)

    def test_import_book_with_very_long_category_and_author(self):
        """Testa importação de livro do Google Books com categorias e autores longos (>50 chars)."""
        mock_data = {
            'google_book_id': 'gb_test_long_cat_123',
            'title': 'Livro com Categoria e Autor Extensamente Longos do Google Books',
            'subtitle': 'Subtítulo Exemplo',
            'authors': ['Autor com Nome Extremamente Longo de Uma Instituição Acadêmica Internacional'],
            'publisher': 'Editora Teste',
            'published_date': '2023-05-10',
            'description': 'Descrição teste',
            'isbn_13': '9788532511010',
            'isbn_10': '8532511015',
            'page_count': 320,
            'categories': ['Juvenile Nonfiction / Social Science / Customs, Traditions, Anthropology / Extended'],
            'language': 'pt-BR',
            'thumbnail': None,
            'preview_link': 'https://books.google.com/preview',
            'info_link': 'https://books.google.com/info',
            'average_rating': 4.5,
            'ratings_count': 10,
            'price': 49.90
        }

        with patch('core.utils.google_books_api.get_book_by_id', return_value=mock_data), \
             patch('core.views.google_books_views.download_cover', return_value=None):
            resp = self.client.post(reverse('admin:google_books_import', args=['gb_test_long_cat_123']))
            self.assertEqual(resp.status_code, 302)
            self.assertRedirects(resp, reverse('admin:core_book_changelist'))

            book = Book.objects.get(google_books_id='gb_test_long_cat_123')
            self.assertIsNotNone(book)
            self.assertIsNotNone(book.category)
            self.assertTrue(len(book.category.slug) <= 220)
            self.assertIsNotNone(book.author)
            self.assertTrue(len(book.author.slug) <= 220)

    def test_import_book_with_duplicate_category_does_not_fail(self):
        """Garante que reutilizar categoria existente longa funciona perfeitamente."""
        cat_name = "Young Adult Nonfiction / Biography & Autobiography / General"
        cat = Category.objects.create(name=cat_name)

        mock_data = {
            'google_book_id': 'gb_test_dup_cat_456',
            'title': 'Segundo Livro na Mesma Categoria Longa',
            'subtitle': '',
            'authors': ['Autor Teste'],
            'publisher': 'Editora Teste',
            'published_date': '2024-01-01',
            'description': 'Desc',
            'isbn_13': '9788532511099',
            'isbn_10': None,
            'page_count': 200,
            'categories': [cat_name],
            'language': 'pt',
            'thumbnail': None,
            'preview_link': '',
            'info_link': '',
            'average_rating': 4.0,
            'ratings_count': 5,
            'price': 39.90
        }

        with patch('core.utils.google_books_api.get_book_by_id', return_value=mock_data), \
             patch('core.views.google_books_views.download_cover', return_value=None):
            resp = self.client.post(reverse('admin:google_books_import', args=['gb_test_dup_cat_456']))
            self.assertEqual(resp.status_code, 302)

            book = Book.objects.get(google_books_id='gb_test_dup_cat_456')
            self.assertEqual(book.category, cat)
