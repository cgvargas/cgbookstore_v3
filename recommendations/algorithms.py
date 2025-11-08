"""
Algoritmos de Recomendação usando Machine Learning.
"""
import numpy as np
import pandas as pd
from django.core.cache import cache
from django.conf import settings
from django.db.models import Count, Q, Avg
from core.models import Book
from .models import UserBookInteraction, BookSimilarity, Recommendation, UserProfile
import logging

logger = logging.getLogger(__name__)

# Lazy imports para sklearn (economiza memória no startup do Gunicorn)
_sklearn_loaded = False
TfidfVectorizer = None
cosine_similarity = None

def _load_sklearn():
    """Carrega sklearn apenas quando necessário (lazy loading)."""
    global _sklearn_loaded, TfidfVectorizer, cosine_similarity
    if not _sklearn_loaded:
        from sklearn.feature_extraction.text import TfidfVectorizer as _TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity as _cosine_similarity
        TfidfVectorizer = _TfidfVectorizer
        cosine_similarity = _cosine_similarity
        _sklearn_loaded = True
        logger.info("sklearn loaded successfully (lazy loading)")


def filter_books_with_valid_covers(recommendations):
    """
    Filtra recomendações removendo livros sem capa válida.

    Args:
        recommendations: Lista de dicts com formato {'book': Book, 'score': float, 'reason': str}

    Returns:
        Lista filtrada contendo apenas livros com capas válidas
    """
    filtered = []
    removed_count = 0
    removed_titles = []

    for rec in recommendations:
        book = rec.get('book')
        if book and book.has_valid_cover:
            filtered.append(rec)
        else:
            removed_count += 1
            if book:
                removed_titles.append(f"{book.title} (ID: {book.id})")

    if removed_count > 0:
        print(f"🚫 FILTER: Removed {removed_count} books without covers from {len(recommendations)} total", flush=True)
        logger.error(f"🚫 FILTER DEBUG: Removed {removed_count} books without covers from {len(recommendations)} total")
        logger.warning(f"🚫 Filtered out {removed_count} books without covers: {', '.join(removed_titles[:3])}")

    return filtered


class CollaborativeFilteringAlgorithm:
    """
    Filtragem Colaborativa baseada em usuários similares.
    "Usuários que leram X também leram Y"
    """

    def __init__(self):
        self.cache_key_prefix = 'collab_filter'

    def find_similar_users(self, user, min_common_books=2, limit=10):
        """
        Encontra usuários com gostos similares baseado em livros em comum.
        """
        cache_key = f'{self.cache_key_prefix}:similar_users:{user.id}'
        cached_result = cache.get(cache_key)

        if cached_result is not None:
            return cached_result

        # Livros que o usuário já interagiu
        user_books = set(
            UserBookInteraction.objects.filter(
                user=user,
                interaction_type__in=['read', 'completed', 'wishlist']
            ).values_list('book_id', flat=True)
        )

        if len(user_books) < min_common_books:
            return []

        # Encontrar usuários que leram os mesmos livros
        similar_users = (
            UserBookInteraction.objects
            .filter(book_id__in=user_books, interaction_type__in=['read', 'completed'])
            .exclude(user=user)
            .values('user_id')
            .annotate(common_books=Count('book_id'))
            .filter(common_books__gte=min_common_books)
            .order_by('-common_books')[:limit]
        )

        result = [u['user_id'] for u in similar_users]
        cache.set(cache_key, result, timeout=settings.RECOMMENDATIONS_CONFIG['CACHE_TIMEOUT'])

        return result

    def recommend(self, user, n=10):
        """
        Recomenda livros baseado em usuários similares.
        Filtra livros sem capa válida e busca mais se necessário.
        """
        logger.info(f"COLLABORATIVE START: User={user.username}, n={n}")
        similar_users = self.find_similar_users(user)

        if not similar_users:
            logger.info(f"No similar users found for {user.username}. Returning popular books.")
            return self._get_popular_books(n)

        # Livros que usuários similares leram, mas o usuário atual não
        user_books = set(
            UserBookInteraction.objects.filter(user=user)
            .values_list('book_id', flat=True)
        )

        # Buscar progressivamente mais livros até ter N livros com capa
        results = []
        fetch_multiplier = 4  # Começar com 4x (24 livros para 6)
        max_attempts = 3

        for attempt in range(max_attempts):
            fetch_limit = n * fetch_multiplier

            recommended_books = (
                UserBookInteraction.objects
                .filter(
                    user_id__in=similar_users,
                    interaction_type__in=['read', 'completed']
                )
                .exclude(book_id__in=user_books)
                .values('book_id')
                .annotate(score=Count('id'))
                .order_by('-score')[:fetch_limit]
            )

            if not recommended_books:
                break

            book_ids = [b['book_id'] for b in recommended_books]
            books = Book.objects.filter(id__in=book_ids)

            # Mapear scores
            scores = {b['book_id']: b['score'] for b in recommended_books}
            max_score = max(scores.values()) if scores else 1

            results = []
            for book in books:
                normalized_score = scores.get(book.id, 0) / max_score
                results.append({
                    'book': book,
                    'score': normalized_score,
                    'reason': f"Recomendado por {scores.get(book.id, 0)} usuários similares"
                })

            # Filtrar livros sem capa válida
            results = filter_books_with_valid_covers(results)

            # Se já temos N livros com capa, parar
            if len(results) >= n:
                logger.info(f"✓ Collaborative: Got {len(results)} books with covers on attempt {attempt + 1}")
                break

            # Aumentar multiplicador para próxima tentativa
            fetch_multiplier += 2
            logger.warning(f"⚠ Collaborative: attempt {attempt + 1}, got {len(results)} books, need {n}. Trying again...")

        # Log final (sempre visível)
        print(f"🔍 COLLABORATIVE FINAL: Returning {len(results)} books (requested {n})", flush=True)
        logger.error(f"🔍 COLLABORATIVE DEBUG: Returning {len(results)} books (requested {n})")
        if len(results) < n:
            print(f"⚠️ WARNING: Only {len(results)} books with covers found!", flush=True)
            logger.error(f"⚠️ WARNING: Only {len(results)} books with covers found!")

        # Retornar apenas N livros
        return results[:n]

    def _get_popular_books(self, n=10):
        """
        Retorna livros populares (fallback para cold start).
        Filtra livros sem capa válida.
        """
        # Buscar progressivamente mais livros até ter N com capa
        fetch_multiplier = 3

        popular_books = (
            UserBookInteraction.objects
            .values('book')
            .annotate(count=Count('id'))
            .order_by('-count')[:n * fetch_multiplier]
        )

        book_ids = [b['book'] for b in popular_books]
        books = Book.objects.filter(id__in=book_ids)

        results = []
        for book in books:
            results.append({
                'book': book,
                'score': 0.5,  # Score médio para populares
                'reason': "Livro popular entre usuários"
            })

        # Filtrar livros sem capa válida
        results = filter_books_with_valid_covers(results)

        return results[:n]


class ContentBasedFilteringAlgorithm:
    """
    Filtragem baseada em conteúdo usando TF-IDF.
    Recomenda livros similares baseado em título, descrição e gênero.
    """

    def __init__(self):
        self.cache_key_prefix = 'content_filter'
        self.tfidf_vectorizer = None
        self.book_vectors = None
        self.book_ids = None

    def build_book_vectors(self):
        """
        Constrói vetores TF-IDF para todos os livros.
        """
        # Carregar sklearn apenas quando necessário
        _load_sklearn()

        cache_key = f'{self.cache_key_prefix}:vectors'
        cached_vectors = cache.get(cache_key)

        if cached_vectors is not None:
            self.book_vectors, self.book_ids, self.tfidf_vectorizer = cached_vectors
            return

        books = Book.objects.all()

        if not books.exists():
            logger.warning("No books found to build vectors")
            return

        # Combinar título, descrição e categorias
        texts = []
        book_ids = []

        for book in books:
            text_parts = [book.title]

            if book.description:
                text_parts.append(book.description)

            if hasattr(book, 'categories') and book.categories:
                text_parts.append(book.categories)

            texts.append(' '.join(text_parts))
            book_ids.append(book.id)

        # Criar vetores TF-IDF
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=500,
            stop_words='english',
            ngram_range=(1, 2)
        )

        self.book_vectors = self.tfidf_vectorizer.fit_transform(texts)
        self.book_ids = np.array(book_ids)

        # Cachear por 24 horas
        cache_data = (self.book_vectors, self.book_ids, self.tfidf_vectorizer)
        cache.set(
            cache_key,
            cache_data,
            timeout=settings.RECOMMENDATIONS_CONFIG['SIMILARITY_CACHE_TIMEOUT']
        )

        logger.info(f"Built TF-IDF vectors for {len(book_ids)} books")

    def find_similar_books(self, book, n=10):
        """
        Encontra livros similares baseado em conteúdo.
        """
        # Garantir que sklearn está carregado
        _load_sklearn()

        self.build_book_vectors()

        if self.book_vectors is None:
            return []

        # Encontrar índice do livro
        try:
            book_idx = np.where(self.book_ids == book.id)[0][0]
        except IndexError:
            logger.warning(f"Book {book.id} not found in vectors")
            return []

        # Calcular similaridade de cosseno
        book_vector = self.book_vectors[book_idx]
        similarities = cosine_similarity(book_vector, self.book_vectors).flatten()

        # Obter top N mais similares (excluindo o próprio livro)
        similar_indices = similarities.argsort()[::-1][1:n+1]

        results = []
        for idx in similar_indices:
            similar_book_id = self.book_ids[idx]
            similarity_score = similarities[idx]

            try:
                similar_book = Book.objects.get(id=similar_book_id)
                results.append({
                    'book': similar_book,
                    'score': float(similarity_score),
                    'reason': f"Similaridade de conteúdo: {similarity_score:.0%}"
                })
            except Book.DoesNotExist:
                continue

        return results

    def recommend(self, user, n=10):
        """
        Recomenda livros baseado nos livros que o usuário já interagiu.
        Filtra livros sem capa válida.
        """
        # Obter livros que o usuário já leu/gostou
        user_books = (
            UserBookInteraction.objects
            .filter(
                user=user,
                interaction_type__in=['read', 'completed', 'wishlist']
            )
            .select_related('book')
            .order_by('-created_at')[:5]  # Últimos 5 livros
        )

        if not user_books:
            logger.info(f"No interactions found for {user.username}")
            return []

        # Encontrar livros similares para cada livro do usuário
        # Buscar mais para compensar filtros (15 ao invés de 10)
        all_recommendations = {}

        for interaction in user_books:
            similar_books = self.find_similar_books(interaction.book, n=15)

            for rec in similar_books:
                book_id = rec['book'].id

                if book_id not in all_recommendations:
                    all_recommendations[book_id] = rec
                else:
                    # Incrementar score se o livro já foi recomendado
                    all_recommendations[book_id]['score'] += rec['score']

        # Ordenar por score
        sorted_recommendations = sorted(
            all_recommendations.values(),
            key=lambda x: x['score'],
            reverse=True
        )

        # Filtrar livros sem capa válida
        sorted_recommendations = filter_books_with_valid_covers(sorted_recommendations)

        # Pegar apenas N livros
        sorted_recommendations = sorted_recommendations[:n]

        # Normalizar scores
        if sorted_recommendations:
            max_score = sorted_recommendations[0]['score']
            for rec in sorted_recommendations:
                rec['score'] = rec['score'] / max_score

        return sorted_recommendations


class HybridRecommendationSystem:
    """
    Sistema Híbrido que combina Filtragem Colaborativa e Baseada em Conteúdo.
    """

    def __init__(self):
        self.collaborative = CollaborativeFilteringAlgorithm()
        self.content_based = ContentBasedFilteringAlgorithm()
        self.weights = settings.RECOMMENDATIONS_CONFIG['HYBRID_WEIGHTS']

    def recommend(self, user, n=10):
        """
        Combina recomendações de múltiplos algoritmos.
        Filtra livros sem capa válida.
        """
        cache_key = f'hybrid_rec:{user.id}:{n}'
        cached_result = cache.get(cache_key)

        if cached_result is not None:
            return cached_result

        # Obter recomendações de cada algoritmo (já filtradas)
        # Os algoritmos já retornam livros filtrados
        # Pedir 3x mais para garantir diversidade após filtragem
        collab_recs = self.collaborative.recommend(user, n=n*3)
        content_recs = self.content_based.recommend(user, n=n*3)

        # Combinar recomendações com pesos
        all_recommendations = {}

        for rec in collab_recs:
            book_id = rec['book'].id
            all_recommendations[book_id] = {
                'book': rec['book'],
                'score': rec['score'] * self.weights['collaborative'],
                'reason': rec['reason']
            }

        for rec in content_recs:
            book_id = rec['book'].id
            if book_id in all_recommendations:
                # Combinar scores
                all_recommendations[book_id]['score'] += rec['score'] * self.weights['content']
                all_recommendations[book_id]['reason'] += f" | {rec['reason']}"
            else:
                all_recommendations[book_id] = {
                    'book': rec['book'],
                    'score': rec['score'] * self.weights['content'],
                    'reason': rec['reason']
                }

        # Adicionar componente de trending (livros em alta)
        trending_books = self._get_trending_books(n=10)
        for book in trending_books:
            if book.id not in all_recommendations:
                all_recommendations[book.id] = {
                    'book': book,
                    'score': self.weights['trending'],
                    'reason': "Livro em alta no momento"
                }

        # Ordenar por score
        sorted_recommendations = sorted(
            all_recommendations.values(),
            key=lambda x: x['score'],
            reverse=True
        )

        # Aplicar filtro adicional (por segurança, caso trending não esteja filtrado)
        sorted_recommendations = filter_books_with_valid_covers(sorted_recommendations)

        # Pegar apenas N livros
        sorted_recommendations = sorted_recommendations[:n]

        # Normalizar scores
        if sorted_recommendations:
            max_score = sorted_recommendations[0]['score']
            for rec in sorted_recommendations:
                rec['score'] = min(rec['score'] / max_score, 1.0)

        cache.set(cache_key, sorted_recommendations, timeout=settings.RECOMMENDATIONS_CONFIG['CACHE_TIMEOUT'])

        return sorted_recommendations

    def _get_trending_books(self, n=5):
        """
        Retorna livros em alta (mais interações nos últimos 7 dias).
        Filtra livros sem capa válida.
        """
        from django.utils import timezone
        from datetime import timedelta

        week_ago = timezone.now() - timedelta(days=7)

        # Buscar mais para compensar filtros
        fetch_limit = n * 2

        trending = (
            UserBookInteraction.objects
            .filter(created_at__gte=week_ago)
            .values('book')
            .annotate(count=Count('id'))
            .order_by('-count')[:fetch_limit]
        )

        book_ids = [t['book'] for t in trending]
        books = Book.objects.filter(id__in=book_ids)

        # Filtrar apenas livros com capa válida
        filtered_books = [book for book in books if book.has_valid_cover]

        return filtered_books[:n]
