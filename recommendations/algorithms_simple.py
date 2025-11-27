"""
Sistema de Recomendações SIMPLIFICADO - Rápido, Eficiente e Sem Dependências Pesadas.

DESIGN PRINCIPLES:
1. SQL puro (sem sklearn, sem TF-IDF, sem machine learning complexo)
2. Filtro de capas DIRETO na query (não em Python)
3. Cache simples e eficiente
4. Prioridade por prateleiras (favoritos > lidos > lendo > quer ler)
5. Colaborativo básico (usuários similares)
6. Popularidade como fallback
"""
import logging
from typing import List, Dict
from django.db.models import Count, Q, F, Exists, OuterRef
from django.core.cache import cache
from django.conf import settings
from core.models import Book, BookShelf
from .models import UserBookInteraction

logger = logging.getLogger(__name__)


class SimpleRecommendationEngine:
    """
    Sistema de recomendações simples e eficiente baseado em:
    1. Prateleiras do usuário (favoritos, lidos, lendo, quer ler)
    2. Colaborativo básico (usuários com livros em comum)
    3. Popularidade (fallback)
    """

    # Pesos das prateleiras (quanto maior, mais importante)
    SHELF_WEIGHTS = {
        'favoritos': 5.0,
        'lidos': 3.0,
        'lendo': 4.0,
        'quer-ler': 2.0,
    }

    def __init__(self):
        self.cache_timeout = settings.RECOMMENDATIONS_CONFIG.get('CACHE_TIMEOUT', 21600)  # 6 horas

    def recommend(self, user, n=10) -> List[Dict]:
        """
        Gera recomendações personalizadas para o usuário.

        Args:
            user: Usuário Django
            n: Número de recomendações desejadas

        Returns:
            Lista de dicts com formato: {'book': Book, 'score': float, 'reason': str}
        """
        logger.info(f"🎯 Generating {n} recommendations for {user.username}")

        # Verificar cache
        cache_key = f'simple_rec:{user.id}:{n}:{self._get_user_hash(user)}'
        cached = cache.get(cache_key)
        if cached is not None:
            logger.info(f"✓ Cache hit for {user.username}")
            return cached

        # Obter livros das prateleiras do usuário
        user_books = self._get_user_books(user)

        if not user_books:
            logger.info(f"No shelves for {user.username}, using popular books")
            recommendations = self._get_popular_books(n)
        else:
            # 1. Recomendações baseadas em prateleiras (70%)
            shelf_based = self._get_shelf_based_recommendations(user, user_books, n=int(n * 0.7))

            # 2. Recomendações colaborativas (30%)
            collab_based = self._get_collaborative_recommendations(user, user_books, n=int(n * 0.3))

            # Combinar e ordenar
            recommendations = self._merge_recommendations(shelf_based, collab_based, n)

        # Se ainda não temos N recomendações, completar com populares
        if len(recommendations) < n:
            missing = n - len(recommendations)
            logger.info(f"Only {len(recommendations)} recommendations, adding {missing} popular books")

            # Livros já recomendados
            recommended_ids = {rec['book'].id for rec in recommendations}

            # Buscar populares que não foram recomendados
            popular = self._get_popular_books(missing * 2)  # Buscar 2x para garantir
            for pop in popular:
                if pop['book'].id not in recommended_ids:
                    recommendations.append(pop)
                    recommended_ids.add(pop['book'].id)
                    if len(recommendations) >= n:
                        break

        # Cachear resultado
        cache.set(cache_key, recommendations[:n], timeout=self.cache_timeout)
        logger.info(f"✓ Returning {len(recommendations[:n])} recommendations for {user.username}")

        return recommendations[:n]

    def _get_user_books(self, user) -> set:
        """Retorna IDs dos livros nas prateleiras do usuário."""
        shelf_books = BookShelf.objects.filter(user=user).values_list('book_id', flat=True)
        return set(shelf_books)

    def _get_user_hash(self, user) -> str:
        """Gera hash das prateleiras do usuário para invalidar cache."""
        from hashlib import md5

        # Contar livros por prateleira
        shelves = BookShelf.objects.filter(user=user).values('shelf_type').annotate(count=Count('id'))
        shelf_data = ''.join(f"{s['shelf_type']}:{s['count']}" for s in shelves)

        return md5(shelf_data.encode()).hexdigest()[:8]

    def _get_shelf_based_recommendations(self, user, user_books: set, n=10) -> List[Dict]:
        """
        Recomenda livros baseado nas prateleiras do usuário.

        Lógica:
        - Busca livros da MESMA CATEGORIA dos livros nas prateleiras
        - Busca livros do MESMO AUTOR dos livros nas prateleiras
        - Pondera pela importância da prateleira (favoritos > lidos > lendo > quer ler)
        """
        # Buscar prateleiras do usuário com pesos
        user_shelves = BookShelf.objects.filter(user=user).select_related('book__category', 'book__author')

        # Coletar categorias e autores com pesos
        categories_weighted = {}
        authors_weighted = {}

        for shelf in user_shelves:
            weight = self.SHELF_WEIGHTS.get(shelf.shelf_type, 1.0)

            # Categoria
            if shelf.book.category:
                cat_id = shelf.book.category.id
                categories_weighted[cat_id] = categories_weighted.get(cat_id, 0) + weight

            # Autor
            if shelf.book.author:
                author_id = shelf.book.author.id
                authors_weighted[author_id] = authors_weighted.get(author_id, 0) + weight

        if not categories_weighted and not authors_weighted:
            return []

        # Buscar livros similares (mesma categoria OU mesmo autor)
        # FILTRO DIRETO: apenas livros com capa válida
        similar_books = Book.objects.filter(
            Q(category_id__in=categories_weighted.keys()) |
            Q(author_id__in=authors_weighted.keys())
        ).exclude(
            id__in=user_books  # Excluir livros que o usuário já tem
        ).filter(
            # CRITICAL: Filtro de capa direto na query
            Q(cover_image__isnull=False) & ~Q(cover_image='')
        ).select_related('category', 'author')[:n * 3]  # Buscar 3x mais

        # Calcular scores
        recommendations = []
        for book in similar_books:
            score = 0.0
            reasons = []

            # Score por categoria
            if book.category and book.category.id in categories_weighted:
                cat_score = categories_weighted[book.category.id]
                score += cat_score * 0.6  # Categoria vale 60%
                reasons.append(f"Categoria: {book.category.name}")

            # Score por autor
            if book.author and book.author.id in authors_weighted:
                author_score = authors_weighted[book.author.id]
                score += author_score * 0.4  # Autor vale 40%
                reasons.append(f"Autor: {book.author.name}")

            if score > 0:
                recommendations.append({
                    'book': book,
                    'score': score,
                    'reason': ' | '.join(reasons)
                })

        # Ordenar por score
        recommendations.sort(key=lambda x: x['score'], reverse=True)

        return recommendations[:n]

    def _get_collaborative_recommendations(self, user, user_books: set, n=10) -> List[Dict]:
        """
        Recomenda livros baseado em usuários similares (collaborative filtering simples).

        Lógica:
        - Encontra usuários que têm livros em comum
        - Recomenda livros que esses usuários têm, mas o usuário atual não
        """
        if not user_books:
            return []

        # Encontrar usuários com livros em comum
        similar_users = (
            BookShelf.objects
            .filter(book_id__in=user_books)
            .exclude(user=user)
            .values('user_id')
            .annotate(common_books=Count('id'))
            .filter(common_books__gte=2)  # Pelo menos 2 livros em comum
            .order_by('-common_books')[:20]  # Top 20 usuários similares
        )

        similar_user_ids = [u['user_id'] for u in similar_users]

        if not similar_user_ids:
            return []

        # Buscar livros desses usuários que o usuário atual não tem
        # FILTRO DIRETO: apenas livros com capa válida
        recommended_books = (
            BookShelf.objects
            .filter(user_id__in=similar_user_ids)
            .exclude(book_id__in=user_books)
            .values('book_id')
            .annotate(count=Count('id'))
            .order_by('-count')[:n * 2]  # Buscar 2x mais
        )

        # Buscar os objetos Book
        book_ids = [b['book_id'] for b in recommended_books]
        books = Book.objects.filter(
            id__in=book_ids
        ).filter(
            # CRITICAL: Filtro de capa direto na query
            Q(cover_image__isnull=False) & ~Q(cover_image='')
        ).select_related('category', 'author')

        # Mapear counts
        counts = {b['book_id']: b['count'] for b in recommended_books}
        max_count = max(counts.values()) if counts else 1

        # Criar recomendações
        recommendations = []
        for book in books:
            count = counts.get(book.id, 0)
            score = count / max_count  # Normalizar

            recommendations.append({
                'book': book,
                'score': score,
                'reason': f"Recomendado por {count} leitor{'es' if count > 1 else ''} similar{'es' if count > 1 else ''}"
            })

        return recommendations[:n]

    def _get_popular_books(self, n=10) -> List[Dict]:
        """
        Retorna livros populares (mais adicionados às prateleiras).
        Fallback para cold start.
        """
        # Livros mais populares (mais vezes adicionados às prateleiras)
        # FILTRO DIRETO: apenas livros com capa válida
        popular = (
            BookShelf.objects
            .values('book')
            .annotate(count=Count('id'))
            .order_by('-count')[:n * 2]  # Buscar 2x mais
        )

        book_ids = [p['book'] for p in popular]
        books = Book.objects.filter(
            id__in=book_ids
        ).filter(
            # CRITICAL: Filtro de capa direto na query
            Q(cover_image__isnull=False) & ~Q(cover_image='')
        ).select_related('category', 'author')

        recommendations = []
        for book in books:
            recommendations.append({
                'book': book,
                'score': 0.5,  # Score médio
                'reason': "Livro popular na comunidade"
            })

        return recommendations[:n]

    def _merge_recommendations(self, shelf_based: List[Dict], collab_based: List[Dict], n=10) -> List[Dict]:
        """
        Combina recomendações de diferentes fontes, evitando duplicatas.
        """
        # Usar dict para evitar duplicatas
        merged = {}

        # Adicionar shelf-based (prioridade maior)
        for rec in shelf_based:
            book_id = rec['book'].id
            merged[book_id] = rec

        # Adicionar collaborative (combinando scores se já existe)
        for rec in collab_based:
            book_id = rec['book'].id
            if book_id in merged:
                # Livro já recomendado, combinar scores
                merged[book_id]['score'] += rec['score'] * 0.5  # Collab conta 50%
                merged[book_id]['reason'] += f" | {rec['reason']}"
            else:
                merged[book_id] = rec

        # Ordenar por score
        sorted_recommendations = sorted(
            merged.values(),
            key=lambda x: x['score'],
            reverse=True
        )

        # Normalizar scores (0.0 a 1.0)
        if sorted_recommendations:
            max_score = sorted_recommendations[0]['score']
            for rec in sorted_recommendations:
                rec['score'] = min(rec['score'] / max_score, 1.0)

        return sorted_recommendations[:n]


# Singleton
_simple_recommendation_engine = None


def get_simple_recommendation_engine() -> SimpleRecommendationEngine:
    """Retorna instância singleton do motor de recomendações."""
    global _simple_recommendation_engine
    if _simple_recommendation_engine is None:
        _simple_recommendation_engine = SimpleRecommendationEngine()
    return _simple_recommendation_engine
