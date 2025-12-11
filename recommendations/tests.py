"""
Testes automatizados para o app Recommendations.
Cobertura: SimpleRecommendationEngine, UserBookInteraction, BookSimilarity
"""
from django.test import TestCase
from django.contrib.auth.models import User
from datetime import date
from django.utils import timezone
from recommendations.models import UserBookInteraction, BookSimilarity, Recommendation
from recommendations.algorithms_simple import SimpleRecommendationEngine, get_simple_recommendation_engine
from core.models import Book, Category, Author
from accounts.models import BookShelf


class UserBookInteractionModelTest(TestCase):
    """Testes para o model UserBookInteraction."""

    def setUp(self):
        """Configuração inicial para os testes."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.book = Book.objects.create(
            title="Test Book",
            publication_date=date(2024, 1, 1),
        )

    def test_interaction_creation(self):
        """Testa criação de interação."""
        interaction = UserBookInteraction.objects.create(
            user=self.user,
            book=self.book,
            interaction_type='view'
        )
        self.assertEqual(interaction.user, self.user)
        self.assertEqual(interaction.book, self.book)
        self.assertEqual(interaction.interaction_type, 'view')

    def test_interaction_types(self):
        """Testa diferentes tipos de interação."""
        types = ['view', 'click', 'wishlist', 'reading', 'read', 'completed']
        for i, itype in enumerate(types):
            book = Book.objects.create(
                title=f"Book {i}",
                publication_date=date(2024, 1, 1),
            )
            interaction = UserBookInteraction.objects.create(
                user=self.user,
                book=book,
                interaction_type=itype
            )
            self.assertEqual(interaction.interaction_type, itype)

    def test_interaction_with_rating(self):
        """Testa interação com rating."""
        interaction = UserBookInteraction.objects.create(
            user=self.user,
            book=self.book,
            interaction_type='review',
            rating=5
        )
        self.assertEqual(interaction.rating, 5)

    def test_interaction_str(self):
        """Testa representação string da interação."""
        interaction = UserBookInteraction.objects.create(
            user=self.user,
            book=self.book,
            interaction_type='read'
        )
        self.assertIn(self.user.username, str(interaction))
        self.assertIn(self.book.title, str(interaction))


class BookSimilarityModelTest(TestCase):
    """Testes para o model BookSimilarity."""

    def setUp(self):
        """Configuração inicial para os testes."""
        self.book1 = Book.objects.create(
            title="Book 1",
            publication_date=date(2024, 1, 1),
        )
        self.book2 = Book.objects.create(
            title="Book 2",
            publication_date=date(2024, 1, 1),
        )

    def test_similarity_creation(self):
        """Testa criação de similaridade."""
        similarity = BookSimilarity.objects.create(
            book_a=self.book1,
            book_b=self.book2,
            similarity_score=0.85,
            method='content'
        )
        self.assertEqual(similarity.book_a, self.book1)
        self.assertEqual(similarity.book_b, self.book2)
        self.assertEqual(similarity.similarity_score, 0.85)

    def test_similarity_methods(self):
        """Testa diferentes métodos de similaridade."""
        methods = ['content', 'collaborative', 'hybrid']
        for method in methods:
            # Deletar similaridades anteriores
            BookSimilarity.objects.filter(book_a=self.book1, book_b=self.book2).delete()
            
            similarity = BookSimilarity.objects.create(
                book_a=self.book1,
                book_b=self.book2,
                similarity_score=0.75,
                method=method
            )
            self.assertEqual(similarity.method, method)


class RecommendationModelTest(TestCase):
    """Testes para o model Recommendation."""

    def setUp(self):
        """Configuração inicial para os testes."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.book = Book.objects.create(
            title="Recommended Book",
            publication_date=date(2024, 1, 1),
        )

    def test_recommendation_creation(self):
        """Testa criação de recomendação."""
        rec = Recommendation.objects.create(
            user=self.user,
            book=self.book,
            recommendation_type='hybrid',
            score=0.92,
            reason="Baseado nas suas leituras anteriores"
        )
        self.assertEqual(rec.user, self.user)
        self.assertEqual(rec.book, self.book)
        self.assertEqual(rec.score, 0.92)

    def test_recommendation_auto_expiration(self):
        """Testa expiração automática de recomendação."""
        rec = Recommendation.objects.create(
            user=self.user,
            book=self.book,
            recommendation_type='popular',
            score=0.5
        )
        # expires_at deve ser definido automaticamente
        self.assertIsNotNone(rec.expires_at)
        self.assertGreater(rec.expires_at, timezone.now())

    def test_recommendation_mark_clicked(self):
        """Testa marcação de recomendação como clicada."""
        rec = Recommendation.objects.create(
            user=self.user,
            book=self.book,
            recommendation_type='ai',
            score=0.88
        )
        self.assertFalse(rec.is_clicked)
        rec.mark_clicked()
        self.assertTrue(rec.is_clicked)
        self.assertIsNotNone(rec.clicked_at)

    def test_recommendation_types(self):
        """Testa diferentes tipos de recomendação."""
        types = ['collaborative', 'content', 'hybrid', 'ai', 'trending', 'popular']
        for i, rtype in enumerate(types):
            book = Book.objects.create(
                title=f"Book {i}",
                publication_date=date(2024, 1, 1),
            )
            rec = Recommendation.objects.create(
                user=self.user,
                book=book,
                recommendation_type=rtype,
                score=0.7
            )
            self.assertEqual(rec.recommendation_type, rtype)


class SimpleRecommendationEngineTest(TestCase):
    """Testes para o SimpleRecommendationEngine."""

    def setUp(self):
        """Configuração inicial para os testes."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name="Ficção",
            slug="ficcao"
        )
        self.author = Author.objects.create(
            name="Autor Teste"
        )
        # Criar alguns livros
        self.books = []
        for i in range(5):
            book = Book.objects.create(
                title=f"Livro {i}",
                publication_date=date(2024, 1, 1),
                category=self.category,
                author=self.author
            )
            self.books.append(book)

    def test_engine_singleton(self):
        """Testa que engine é singleton."""
        engine1 = get_simple_recommendation_engine()
        engine2 = get_simple_recommendation_engine()
        self.assertIs(engine1, engine2)

    def test_recommend_without_shelves(self):
        """Testa recomendações para usuário sem prateleiras (cold start)."""
        engine = SimpleRecommendationEngine()
        recommendations = engine.recommend(self.user, n=5)
        # Deve retornar lista (pode estar vazia se não houver dados populares)
        self.assertIsInstance(recommendations, list)

    def test_recommend_with_shelves(self):
        """Testa recomendações para usuário com prateleiras."""
        # Adicionar livros às prateleiras
        BookShelf.objects.create(
            user=self.user,
            book=self.books[0],
            shelf_type='favoritos'
        )
        BookShelf.objects.create(
            user=self.user,
            book=self.books[1],
            shelf_type='lidos'
        )
        
        engine = SimpleRecommendationEngine()
        recommendations = engine.recommend(self.user, n=5)
        
        self.assertIsInstance(recommendations, list)
        # Livros na prateleira não devem ser recomendados
        rec_book_ids = {rec['book'].id for rec in recommendations}
        self.assertNotIn(self.books[0].id, rec_book_ids)
        self.assertNotIn(self.books[1].id, rec_book_ids)

    def test_recommendation_format(self):
        """Testa formato das recomendações."""
        BookShelf.objects.create(
            user=self.user,
            book=self.books[0],
            shelf_type='lendo'
        )
        
        engine = SimpleRecommendationEngine()
        recommendations = engine.recommend(self.user, n=3)
        
        for rec in recommendations:
            self.assertIn('book', rec)
            self.assertIn('score', rec)
            self.assertIn('reason', rec)
            self.assertIsInstance(rec['score'], (int, float))
