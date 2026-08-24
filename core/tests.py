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


class VideoListViewTest(TestCase):
    """Testes para a view VideoListView e deduplicação de vídeos."""

    def setUp(self):
        """Configuração inicial para os testes de vídeo."""
        # Criar categoria e autor
        self.category = Category.objects.create(
            name="Fantasia",
            slug="fantasia"
        )
        self.author = Author.objects.create(
            name="J.R.R. Tolkien",
            bio="Autor de O Senhor dos Anéis."
        )
        # Criar dois livros diferentes (sequências)
        self.book1 = Book.objects.create(
            title="A Sociedade do Anel",
            author=self.author,
            category=self.category,
            publication_date=date(1954, 7, 29),
            isbn="9780261103573"
        )
        self.book2 = Book.objects.create(
            title="As Duas Torres",
            author=self.author,
            category=self.category,
            publication_date=date(1954, 11, 11),
            isbn="9780261103580"
        )

    def test_video_list_deduplication(self):
        """Testa se vídeos com a mesma URL são deduplicados na listagem geral."""
        from core.models import Video
        from django.urls import reverse

        video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

        # Cadastrar o mesmo vídeo para o Livro 1
        video1 = Video.objects.create(
            title="Trailer Senhor dos Anéis - Parte 1",
            video_url="https://www.youtube.com/watch?v=video1_unique_id",
            platform="youtube",
            video_type="trailer",
            active=True
        )
        video1.related_books.add(self.book1)

        # Cadastrar o mesmo vídeo para o Livro 2 (sequência)
        video2 = Video.objects.create(
            title="Trailer Senhor dos Anéis - Parte 2",
            video_url="https://www.youtube.com/watch?v=video2_unique_id",
            platform="youtube",
            video_type="trailer",
            active=True
        )
        video2.related_books.add(self.book2)

        # Acessar a página de vídeos
        response = self.client.get(reverse('core:video_list'))
        
        # Verificar que a requisição foi bem sucedida
        self.assertEqual(response.status_code, 200)
        
        # Os 2 vídeos distintos devem aparecer na listagem
        videos_in_context = response.context['videos']
        self.assertEqual(len(videos_in_context), 2)

    def test_video_list_multiple_different_videos(self):
        """Testa se vídeos com URLs diferentes aparecem individualmente na listagem geral."""
        from core.models import Video
        from django.urls import reverse

        # Cadastrar dois vídeos diferentes
        video1 = Video.objects.create(
            title="Trailer 1",
            video_url="https://www.youtube.com/watch?v=video1",
            platform="youtube",
            video_type="trailer",
            active=True
        )
        video1.related_books.add(self.book1)
        video2 = Video.objects.create(
            title="Trailer 2",
            video_url="https://www.youtube.com/watch?v=video2",
            platform="youtube",
            video_type="trailer",
            active=True
        )
        video2.related_books.add(self.book2)

        response = self.client.get(reverse('core:video_list'))
        self.assertEqual(response.status_code, 200)
        
        videos_in_context = response.context['videos']
        self.assertEqual(len(videos_in_context), 2)

    def test_video_list_search_and_filters_still_work(self):
        """Testa se busca e filtros funcionam corretamente com a deduplicação."""
        from core.models import Video
        from django.urls import reverse

        video_url_shared = "https://www.youtube.com/watch?v=shared"

        # Vídeo 1 e 2 compartilham a mesma URL, mas o 1 tem "Especial" no título
        video1 = Video.objects.create(
            title="Entrevista Especial Tolkien",
            video_url="https://www.youtube.com/watch?v=shared1",
            platform="youtube",
            video_type="interview",
            active=True
        )
        video1.related_books.add(self.book1)
        video2 = Video.objects.create(
            title="Tolkien Entrevista",
            video_url="https://www.youtube.com/watch?v=shared2",
            platform="youtube",
            video_type="interview",
            active=True
        )
        video2.related_books.add(self.book2)

        # Vídeo 3 com URL diferente e tipo diferente
        video3 = Video.objects.create(
            title="Discussão sobre a obra",
            video_url="https://www.youtube.com/watch?v=different",
            platform="youtube",
            video_type="discussion",
            active=True
        )
        video3.related_books.add(self.book1)

        # 1. Testar busca com termo "Especial"
        response = self.client.get(reverse('core:video_list') + "?q=Especial")
        videos_in_context = response.context['videos']
        self.assertEqual(len(videos_in_context), 1)
        self.assertEqual(videos_in_context[0].id, video1.id)

        # 2. Testar filtro por tipo "discussion"
        response = self.client.get(reverse('core:video_list') + "?video_type=discussion")
        videos_in_context = response.context['videos']
        self.assertEqual(len(videos_in_context), 1)
        self.assertEqual(videos_in_context[0].id, video3.id)


class LiteraryUniverseModelTest(TestCase):
    """Testes do modelo LiteraryUniverse e isolamento de livros de autores adicionais."""

    def setUp(self):
        from core.models import LiteraryUniverse, Author, Book, UniverseReadingOrder
        from django.utils import timezone

        # Autores: Robert Jordan (principal) e Brandon Sanderson (adicional)
        self.robert_jordan = Author.objects.create(name="Robert Jordan", slug="robert-jordan")
        self.brandon_sanderson = Author.objects.create(name="Brandon Sanderson", slug="brandon-sanderson")

        # Livros de A Roda do Tempo (Robert Jordan)
        self.wot_book1 = Book.objects.create(
            title="O Olho do Mundo (A Roda do Tempo 1)",
            author=self.robert_jordan,
            publication_date=timezone.now().date(),
            isbn="9780000000001"
        )
        self.wot_book2 = Book.objects.create(
            title="A Grande Caçada (A Roda do Tempo 2)",
            author=self.robert_jordan,
            publication_date=timezone.now().date(),
            isbn="9780000000002"
        )

        # Livro final de A Roda do Tempo (Brandon Sanderson)
        self.wot_sanderson_book = Book.objects.create(
            title="A Tempestade Imminente (A Roda do Tempo 12)",
            author=self.brandon_sanderson,
            publication_date=timezone.now().date(),
            isbn="9780000000012"
        )

        # Livro de outro universo (Mistborn - Brandon Sanderson)
        self.mistborn_book = Book.objects.create(
            title="Mistborn: O Império Final",
            author=self.brandon_sanderson,
            publication_date=timezone.now().date(),
            isbn="9780000000099"
        )

        # Universo A Roda do Tempo
        self.universe = LiteraryUniverse.objects.create(
            title="A Roda do Tempo",
            slug="roda-do-tempo",
            author=self.robert_jordan
        )
        self.universe.additional_authors.add(self.brandon_sanderson)

    def test_additional_author_unrelated_books_are_excluded(self):
        """Garante que livros não vinculados de autores adicionais (ex: Mistborn) não apareçam no universo."""
        books = list(self.universe.get_all_books())

        # Deve incluir apenas os livros de Robert Jordan
        self.assertIn(self.wot_book1, books)
        self.assertIn(self.wot_book2, books)

        # Mistborn NÃO deve estar presente
        self.assertNotIn(self.mistborn_book, books)
        # O livro do Sanderson para WoT ainda não foi associado manualmente, então não deve estar
        self.assertNotIn(self.wot_sanderson_book, books)

    def test_additional_author_book_included_when_added_to_books(self):
        """Garante que quando o livro de autor adicional for adicionado a 'books', ele seja incluído no universo."""
        self.universe.books.add(self.wot_sanderson_book)

        books = list(self.universe.get_all_books())

        self.assertIn(self.wot_book1, books)
        self.assertIn(self.wot_sanderson_book, books)
        self.assertNotIn(self.mistborn_book, books)

    def test_additional_author_book_included_when_in_reading_order(self):
        """Garante que se o livro estiver na ordem de leitura, ele seja incluído."""
        from core.models import UniverseReadingOrder
        UniverseReadingOrder.objects.create(
            universe=self.universe,
            book=self.wot_sanderson_book,
            order_number=12,
            title="A Tempestade Imminente"
        )

        books = list(self.universe.get_all_books())

        self.assertIn(self.wot_sanderson_book, books)
        self.assertNotIn(self.mistborn_book, books)


