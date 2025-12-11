"""
Testes automatizados para os models do app Core.
Cobertura: Book, Author, Category
"""
from django.test import TestCase
from datetime import date
from core.models import Book, Author, Category


class CategoryModelTest(TestCase):
    """Testes para o model Category."""

    def setUp(self):
        """Configuração inicial para os testes."""
        self.category = Category.objects.create(
            name="Ficção Científica",
            slug="ficcao-cientifica"
        )

    def test_category_creation(self):
        """Testa criação de categoria."""
        self.assertEqual(self.category.name, "Ficção Científica")
        self.assertEqual(self.category.slug, "ficcao-cientifica")

    def test_category_str(self):
        """Testa representação string da categoria."""
        self.assertEqual(str(self.category), "Ficção Científica")


class AuthorModelTest(TestCase):
    """Testes para o model Author."""

    def setUp(self):
        """Configuração inicial para os testes."""
        self.author = Author.objects.create(
            name="Isaac Asimov",
            bio="Escritor de ficção científica."
        )

    def test_author_creation(self):
        """Testa criação de autor."""
        self.assertEqual(self.author.name, "Isaac Asimov")
        self.assertIn("ficção científica", self.author.bio)

    def test_author_str(self):
        """Testa representação string do autor."""
        self.assertEqual(str(self.author), "Isaac Asimov")


class BookModelTest(TestCase):
    """Testes para o model Book."""

    def setUp(self):
        """Configuração inicial para os testes."""
        self.category = Category.objects.create(
            name="Ficção Científica",
            slug="ficcao-cientifica"
        )
        self.author = Author.objects.create(
            name="Isaac Asimov",
            bio="Escritor de ficção científica."
        )
        self.book = Book.objects.create(
            title="Fundação",
            author=self.author,
            category=self.category,
            description="Uma série clássica de ficção científica.",
            publication_date=date(1951, 5, 1),
            isbn="9780553293357",
            publisher="Bantam Books",
            price=49.90,
            language="pt"
        )

    def test_book_creation(self):
        """Testa criação de livro."""
        self.assertEqual(self.book.title, "Fundação")
        self.assertEqual(self.book.author.name, "Isaac Asimov")
        self.assertEqual(self.book.category.name, "Ficção Científica")
        self.assertEqual(self.book.isbn, "9780553293357")

    def test_book_str(self):
        """Testa representação string do livro."""
        self.assertEqual(str(self.book), "Fundação")

    def test_book_slug_auto_generation(self):
        """Testa geração automática de slug."""
        self.assertEqual(self.book.slug, "fundacao")

    def test_book_rating_stars_with_rating(self):
        """Testa cálculo de estrelas com avaliação."""
        self.book.average_rating = 4.5
        self.book.save()
        self.assertEqual(self.book.rating_stars, 4)

    def test_book_rating_stars_without_rating(self):
        """Testa cálculo de estrelas sem avaliação."""
        self.assertEqual(self.book.rating_stars, 0)

    def test_book_rating_percentage(self):
        """Testa cálculo de porcentagem da avaliação."""
        self.book.average_rating = 4.0
        self.book.save()
        self.assertEqual(self.book.rating_percentage, 80.0)

    def test_book_has_google_books_data_false(self):
        """Testa verificação de dados do Google Books (sem dados)."""
        self.assertFalse(self.book.has_google_books_data)

    def test_book_has_google_books_data_true(self):
        """Testa verificação de dados do Google Books (com dados)."""
        self.book.google_books_id = "abc123"
        self.book.save()
        self.assertTrue(self.book.has_google_books_data)

    def test_book_has_valid_cover_without_image(self):
        """Testa verificação de capa válida (sem imagem)."""
        self.assertFalse(self.book.has_valid_cover)

    def test_book_get_absolute_url(self):
        """Testa URL absoluta do livro."""
        url = self.book.get_absolute_url()
        self.assertIn(self.book.slug, url)

    def test_book_with_optional_fields(self):
        """Testa criação de livro com campos opcionais."""
        book = Book.objects.create(
            title="Livro Simples",
            publication_date=date(2024, 1, 1),
        )
        self.assertIsNone(book.author)
        self.assertIsNone(book.category)
        self.assertIsNone(book.isbn)
        self.assertEqual(book.language, "pt")

    def test_book_ordering(self):
        """Testa ordenação padrão dos livros (mais recentes primeiro)."""
        book2 = Book.objects.create(
            title="Segundo Livro",
            publication_date=date(2024, 1, 1),
        )
        books = Book.objects.all()
        self.assertEqual(books[0], book2)
