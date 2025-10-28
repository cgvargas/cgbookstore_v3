"""
Algoritmos de recomendação otimizados com filtro rigoroso de prateleiras.
"""
from core.models import Book
from accounts.models import BookShelf
from recommendations.models import UserBookInteraction
import logging

logger = logging.getLogger(__name__)


class ExclusionFilter:
    """
    Filtro rigoroso para excluir livros que o usuário já conhece.
    """

    @staticmethod
    def get_excluded_books(user):
        """
        Retorna set de IDs e títulos de livros que o usuário JÁ CONHECE.

        Verifica:
        1. Prateleiras: favorites, to_read, reading, read, abandoned, custom
        2. Interações: todos os tipos (click, read, review, wishlist, etc.)

        Returns:
            dict: {'ids': set(), 'titles': set()}
        """
        excluded_ids = set()
        excluded_titles = set()

        # 1. PRATELEIRAS (BookShelf) - TODAS as prateleiras
        shelves = BookShelf.objects.filter(user=user).select_related('book')

        for shelf in shelves:
            if shelf.book:
                excluded_ids.add(shelf.book.id)
                excluded_titles.add(shelf.book.title.lower().strip())

        # 2. INTERAÇÕES (UserBookInteraction) - TODAS as interações
        interactions = UserBookInteraction.objects.filter(
            user=user
        ).select_related('book')

        for interaction in interactions:
            if interaction.book:
                excluded_ids.add(interaction.book.id)
                excluded_titles.add(interaction.book.title.lower().strip())

        logger.info(
            f"Exclusion filter for {user.username}: "
            f"{len(excluded_ids)} book IDs, "
            f"{len(excluded_titles)} unique titles"
        )

        return {
            'ids': excluded_ids,
            'titles': excluded_titles
        }

    @staticmethod
    def filter_recommendations(recommendations, excluded_books):
        """
        Filtra recomendações removendo livros excluídos e duplicatas.

        Args:
            recommendations: Lista de dicts com recomendações
            excluded_books: Dict retornado por get_excluded_books()

        Returns:
            Lista filtrada sem duplicatas e sem livros conhecidos
        """
        excluded_ids = excluded_books['ids']
        excluded_titles = excluded_books['titles']

        filtered = []
        seen_ids = set()
        seen_titles = set()

        for rec in recommendations:
            # Obter dados do livro
            book = rec.get('book')
            book_id = None
            book_title = None

            if book:
                # Recomendação com objeto Book (algoritmos locais)
                book_id = book.id
                book_title = book.title.lower().strip()
            elif 'title' in rec:
                # Recomendação externa (Google Books)
                book_title = rec['title'].lower().strip()

            # Verificar se deve excluir
            if book_id and book_id in excluded_ids:
                logger.debug(f"Excluded by ID: {book_id}")
                continue

            if book_title and book_title in excluded_titles:
                logger.debug(f"Excluded by title: {book_title}")
                continue

            # Verificar duplicatas
            if book_id and book_id in seen_ids:
                logger.debug(f"Duplicate ID: {book_id}")
                continue

            if book_title and book_title in seen_titles:
                logger.debug(f"Duplicate title: {book_title}")
                continue

            # Adicionar à lista filtrada
            filtered.append(rec)

            # Marcar como visto
            if book_id:
                seen_ids.add(book_id)
            if book_title:
                seen_titles.add(book_title)

        logger.info(
            f"Filtered {len(recommendations)} → {len(filtered)} recommendations "
            f"(removed {len(recommendations) - len(filtered)})"
        )

        return filtered


class OptimizedHybridRecommendationSystem:
    """
    Sistema híbrido otimizado com filtro rigoroso de exclusão.
    """

    def __init__(self):
        from .algorithms import HybridRecommendationSystem
        self.engine = HybridRecommendationSystem()
        self.exclusion_filter = ExclusionFilter()

    def recommend(self, user, n=10):
        """
        Gera recomendações híbridas filtradas.

        Args:
            user: Objeto User
            n: Número de recomendações desejadas

        Returns:
            Lista de recomendações filtradas
        """
        # Obter livros excluídos
        excluded_books = self.exclusion_filter.get_excluded_books(user)

        # Gerar mais recomendações que o necessário (para compensar exclusões)
        raw_recommendations = self.engine.recommend(user, n=n * 3)

        # Filtrar
        filtered = self.exclusion_filter.filter_recommendations(
            raw_recommendations,
            excluded_books
        )

        # Retornar apenas n recomendações
        return filtered[:n]


class OptimizedCollaborativeFiltering:
    """
    Collaborative filtering otimizado com filtro rigoroso.
    """

    def __init__(self):
        from .algorithms import CollaborativeFilteringAlgorithm
        self.engine = CollaborativeFilteringAlgorithm()
        self.exclusion_filter = ExclusionFilter()

    def recommend(self, user, n=10):
        """Gera recomendações colaborativas filtradas."""
        excluded_books = self.exclusion_filter.get_excluded_books(user)
        raw_recommendations = self.engine.recommend(user, n=n * 3)
        filtered = self.exclusion_filter.filter_recommendations(
            raw_recommendations,
            excluded_books
        )
        return filtered[:n]


class OptimizedContentBased:
    """
    Content-based filtering otimizado com filtro rigoroso.
    """

    def __init__(self):
        from .algorithms import ContentBasedFilteringAlgorithm
        self.engine = ContentBasedFilteringAlgorithm()
        self.exclusion_filter = ExclusionFilter()

    def recommend(self, user, n=10):
        """Gera recomendações baseadas em conteúdo filtradas."""
        excluded_books = self.exclusion_filter.get_excluded_books(user)
        raw_recommendations = self.engine.recommend(user, n=n * 3)
        filtered = self.exclusion_filter.filter_recommendations(
            raw_recommendations,
            excluded_books
        )
        return filtered[:n]
