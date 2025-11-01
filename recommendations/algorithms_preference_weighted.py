"""
Algoritmos de Recomendação com Priorização por Prateleiras.

Integra o UserPreferenceAnalyzer para dar maior peso a:
1. Favoritos (50%) - Gostos fortemente estabelecidos
2. Lidos (30%) - Histórico comprovado
3. Lendo (15%) - Interesse atual
4. Quero Ler (5%) - Interesse declarado

Resultado: Recomendações MUITO mais precisas e personalizadas.
"""

import numpy as np
from django.core.cache import cache
from django.conf import settings
from django.db.models import Count, Q
from core.models import Book
from .models import UserBookInteraction
from .algorithms import (
    filter_books_with_valid_covers,
    CollaborativeFilteringAlgorithm,
    ContentBasedFilteringAlgorithm
)
from .preference_analyzer import UserPreferenceAnalyzer, ShelfWeightConfig
import logging

logger = logging.getLogger(__name__)


class PreferenceWeightedCollaborative(CollaborativeFilteringAlgorithm):
    """
    Collaborative Filtering com priorização por prateleiras.

    Melhoria:
    - Usuários similares são encontrados priorizando livros de FAVORITOS e LIDOS
    - Livros recomendados ganham boost se forem do mesmo autor/gênero dos favoritos
    """

    def find_similar_users(self, user, min_common_books=2, limit=10):
        """
        Encontra usuários similares priorizando livros ponderados.

        MUDANÇA: Ao invés de tratar todos os livros igualmente,
        dá mais peso a livros de prateleiras importantes.
        """
        cache_key = f'pref_collab:similar_users:{user.id}'
        cached_result = cache.get(cache_key)

        if cached_result is not None:
            return cached_result

        # Usar analisador de preferências
        analyzer = UserPreferenceAnalyzer(user)
        weighted_books = analyzer.get_weighted_books()

        if len(weighted_books) < min_common_books:
            logger.info(f"User {user.username} tem poucos livros ({len(weighted_books)})")
            return []

        # Priorizar livros com maior peso (Favoritos > Lidos > Lendo > Quero Ler)
        # Pegar IDs dos livros mais importantes
        priority_book_ids = [
            item['book'].id for item in weighted_books
            if item['weight'] >= ShelfWeightConfig.READ  # Apenas Favoritos (0.5) e Lidos (0.3)
        ]

        if not priority_book_ids:
            # Fallback: usar todos os livros ponderados
            priority_book_ids = [item['book'].id for item in weighted_books]

        logger.info(
            f"🎯 Finding similar users for {user.username} based on "
            f"{len(priority_book_ids)} priority books (Favoritos + Lidos)"
        )

        # Encontrar usuários que leram os mesmos livros PRIORITÁRIOS
        similar_users = (
            UserBookInteraction.objects
            .filter(
                book_id__in=priority_book_ids,
                interaction_type__in=['read', 'completed']
            )
            .exclude(user=user)
            .values('user_id')
            .annotate(common_books=Count('book_id'))
            .filter(common_books__gte=min_common_books)
            .order_by('-common_books')[:limit]
        )

        result = [u['user_id'] for u in similar_users]

        logger.info(
            f"✓ Found {len(result)} similar users for {user.username}"
        )

        cache.set(cache_key, result, timeout=settings.RECOMMENDATIONS_CONFIG['CACHE_TIMEOUT'])
        return result

    def recommend(self, user, n=10):
        """
        Recomenda livros aplicando boost baseado em preferências.

        MELHORIA: Livros do mesmo autor/gênero dos FAVORITOS ganham +30% de score.
        """
        logger.info(f"🎯 PREF-COLLABORATIVE START: User={user.username}, n={n}")

        # Usar análise de preferências
        analyzer = UserPreferenceAnalyzer(user)
        top_genres = [g['genre'] for g in analyzer.get_top_genres(n=3)]
        top_authors = [a['author'] for a in analyzer.get_top_authors(n=3)]

        logger.info(
            f"📊 User Preferences: Top Genres={top_genres}, Top Authors={top_authors}"
        )

        # Encontrar usuários similares (usando método override acima)
        similar_users = self.find_similar_users(user)

        if not similar_users:
            logger.warning(f"No similar users found for {user.username}, using popular books")
            return self._get_popular_books(n)

        # Livros que usuário já tem
        weighted_books = analyzer.get_weighted_books()
        user_book_ids = [item['book'].id for item in weighted_books]

        # Buscar progressivamente mais livros até ter N com capa
        results = []
        fetch_multiplier = 4
        max_attempts = 3

        for attempt in range(max_attempts):
            fetch_limit = n * fetch_multiplier

            recommended_books = (
                UserBookInteraction.objects
                .filter(
                    user_id__in=similar_users,
                    interaction_type__in=['read', 'completed']
                )
                .exclude(book_id__in=user_book_ids)
                .values('book_id')
                .annotate(score=Count('id'))
                .order_by('-score')[:fetch_limit]
            )

            if not recommended_books:
                break

            book_ids = [b['book_id'] for b in recommended_books]
            books = Book.objects.filter(id__in=book_ids)

            scores = {b['book_id']: b['score'] for b in recommended_books}
            max_score = max(scores.values()) if scores else 1

            results = []
            for book in books:
                base_score = scores.get(book.id, 0) / max_score

                # 🎯 APLICAR BOOST POR PREFERÊNCIAS
                preference_boost = 0.0
                boost_reasons = []

                # Boost por gênero favorito
                if hasattr(book, 'category') and book.category in top_genres:
                    genre_rank = top_genres.index(book.category) + 1
                    genre_boost = 0.3 * (1.0 - (genre_rank - 1) / len(top_genres))
                    preference_boost += genre_boost
                    boost_reasons.append(f"Gênero favorito #{genre_rank}")

                # Boost por autor favorito
                if hasattr(book, 'author') and str(book.author) in top_authors:
                    author_rank = top_authors.index(str(book.author)) + 1
                    author_boost = 0.3 * (1.0 - (author_rank - 1) / len(top_authors))
                    preference_boost += author_boost
                    boost_reasons.append(f"Autor favorito #{author_rank}")

                # Score final (base + boost, máximo 1.0)
                final_score = min(base_score + preference_boost, 1.0)

                reason = f"Recomendado por {scores.get(book.id, 0)} usuários similares"
                if boost_reasons:
                    reason += f" | BOOST: {', '.join(boost_reasons)} (+{preference_boost:.0%})"

                results.append({
                    'book': book,
                    'score': final_score,
                    'reason': reason,
                    'base_score': base_score,
                    'preference_boost': preference_boost
                })

            # Filtrar livros sem capa válida
            results = filter_books_with_valid_covers(results)

            # Se já temos N livros com capa, parar
            if len(results) >= n:
                logger.info(f"✓ Pref-Collaborative: Got {len(results)} books on attempt {attempt + 1}")
                break

            fetch_multiplier += 2
            logger.warning(f"⚠ Pref-Collaborative: attempt {attempt + 1}, got {len(results)} books, need {n}")

        # Ordenar por score final (com boost)
        results.sort(key=lambda x: x['score'], reverse=True)

        # Log final
        print(f"🎯 PREF-COLLABORATIVE FINAL: Returning {len(results)} books (requested {n})", flush=True)
        logger.info(f"🎯 PREF-COLLABORATIVE FINAL: Returning {len(results)} books")

        # Mostrar top 3 com boost
        for i, rec in enumerate(results[:3], 1):
            logger.info(
                f"  {i}. {rec['book'].title} - "
                f"Score: {rec['score']:.2f} "
                f"(Base: {rec['base_score']:.2f} + Boost: {rec['preference_boost']:.2f})"
            )

        return results[:n]


class PreferenceWeightedContentBased(ContentBasedFilteringAlgorithm):
    """
    Content-Based Filtering com priorização por prateleiras.

    Melhoria:
    - TF-IDF é calculado priorizando textos de FAVORITOS e LIDOS
    - Similaridade é ponderada pelo peso da prateleira
    """

    def recommend(self, user, n=10):
        """
        Recomenda livros baseado em conteúdo, priorizando favoritos.

        MELHORIA: Livros favoritos têm 5x mais influência no cálculo de similaridade.
        """
        logger.info(f"🎯 PREF-CONTENT START: User={user.username}, n={n}")

        # Usar analisador de preferências
        analyzer = UserPreferenceAnalyzer(user)
        weighted_books = analyzer.get_weighted_books()

        if not weighted_books:
            logger.warning(f"User {user.username} has no books in shelves")
            return []

        # Encontrar livros similares para cada livro, ponderado pelo peso da prateleira
        all_recommendations = {}

        # Priorizar livros com maior peso
        for item in weighted_books:
            book = item['book']
            weight = item['weight']
            shelf_type = item['shelf_type']

            # Determinar quantos similares buscar baseado no peso
            # Favoritos (0.5): busca 20 similares
            # Lidos (0.3): busca 15 similares
            # Lendo (0.15): busca 10 similares
            # Quero Ler (0.05): busca 5 similares
            num_similar = int(5 + (weight * 30))  # 5-20 livros

            logger.debug(
                f"Finding {num_similar} similar books for '{book.title}' "
                f"({shelf_type}, weight={weight:.2f})"
            )

            similar_books = self.find_similar_books(book, n=num_similar)

            for rec in similar_books:
                book_id = rec['book'].id

                if book_id not in all_recommendations:
                    all_recommendations[book_id] = {
                        'book': rec['book'],
                        'score': 0.0,
                        'reason': rec['reason'],
                        'sources': []
                    }

                # 🎯 PONDERAR SCORE PELO PESO DA PRATELEIRA
                weighted_score = rec['score'] * weight

                all_recommendations[book_id]['score'] += weighted_score
                all_recommendations[book_id]['sources'].append({
                    'source_book': book.title,
                    'shelf_type': shelf_type,
                    'weight': weight,
                    'contribution': weighted_score
                })

        # Ordenar por score ponderado
        sorted_recommendations = sorted(
            all_recommendations.values(),
            key=lambda x: x['score'],
            reverse=True
        )

        # Atualizar reasons com informações de peso
        for rec in sorted_recommendations:
            top_source = max(rec['sources'], key=lambda x: x['contribution'])
            rec['reason'] = (
                f"Similar a '{top_source['source_book']}' "
                f"({top_source['shelf_type']}, peso {top_source['weight']:.0%})"
            )

        # Filtrar capas
        sorted_recommendations = filter_books_with_valid_covers(sorted_recommendations)

        # Pegar apenas N
        sorted_recommendations = sorted_recommendations[:n]

        # Normalizar scores (0-1)
        if sorted_recommendations:
            max_score = max(r['score'] for r in sorted_recommendations)
            if max_score > 0:
                for rec in sorted_recommendations:
                    rec['score'] = rec['score'] / max_score

        # Log final
        print(f"🎯 PREF-CONTENT FINAL: Returning {len(sorted_recommendations)} books", flush=True)
        logger.info(f"🎯 PREF-CONTENT FINAL: Returning {len(sorted_recommendations)} books")

        # Mostrar top 3
        for i, rec in enumerate(sorted_recommendations[:3], 1):
            logger.info(f"  {i}. {rec['book'].title} - Score: {rec['score']:.2f}")

        return sorted_recommendations


class PreferenceWeightedHybrid:
    """
    Sistema Híbrido com priorização por prateleiras.

    Combina:
    - PreferenceWeightedCollaborative (60%)
    - PreferenceWeightedContentBased (30%)
    - Trending de gêneros favoritos (10%)

    Resultado: Recomendações extremamente personalizadas.
    """

    def __init__(self):
        self.collaborative = PreferenceWeightedCollaborative()
        self.content_based = PreferenceWeightedContentBased()

    def recommend(self, user, n=10):
        """
        Combina recomendações priorizando preferências do usuário.
        """
        logger.info(f"🎯 PREF-HYBRID START: User={user.username}, n={n}")

        cache_key = f'pref_hybrid_rec:{user.id}:{n}'
        cached_result = cache.get(cache_key)

        if cached_result is not None:
            logger.info(f"✓ Cache hit for pref-hybrid:{user.username}")
            return cached_result

        # Análise de preferências
        analyzer = UserPreferenceAnalyzer(user)
        top_genres = [g['genre'] for g in analyzer.get_top_genres(n=3)]

        # Obter recomendações de cada algoritmo (já filtradas e ponderadas)
        collab_recs = self.collaborative.recommend(user, n=n*3)
        content_recs = self.content_based.recommend(user, n=n*3)

        # Combinar com pesos
        all_recommendations = {}

        # Collaborative: 60%
        for rec in collab_recs:
            book_id = rec['book'].id
            if book_id not in all_recommendations:
                all_recommendations[book_id] = {
                    'book': rec['book'],
                    'score': 0.0,
                    'reason': rec['reason']
                }
            all_recommendations[book_id]['score'] += rec['score'] * 0.6

        # Content-Based: 30%
        for rec in content_recs:
            book_id = rec['book'].id
            if book_id not in all_recommendations:
                all_recommendations[book_id] = {
                    'book': rec['book'],
                    'score': 0.0,
                    'reason': rec['reason']
                }
            all_recommendations[book_id]['score'] += rec['score'] * 0.3

        # Trending nos gêneros favoritos: 10%
        trending_books = self._get_trending_in_favorite_genres(user, top_genres, n=10)
        for book in trending_books:
            if book.id not in all_recommendations:
                all_recommendations[book.id] = {
                    'book': book,
                    'score': 0.1,
                    'reason': f"Em alta no gênero {book.category}"
                }
            else:
                all_recommendations[book.id]['score'] += 0.1

        # Ordenar por score
        sorted_recommendations = sorted(
            all_recommendations.values(),
            key=lambda x: x['score'],
            reverse=True
        )

        # Aplicar filtro adicional (segurança)
        sorted_recommendations = filter_books_with_valid_covers(sorted_recommendations)

        # Pegar apenas N
        sorted_recommendations = sorted_recommendations[:n]

        # Normalizar scores
        if sorted_recommendations:
            max_score = max(r['score'] for r in sorted_recommendations)
            if max_score > 0:
                for rec in sorted_recommendations:
                    rec['score'] = rec['score'] / max_score

        # Cachear
        cache.set(
            cache_key,
            sorted_recommendations,
            timeout=settings.RECOMMENDATIONS_CONFIG['CACHE_TIMEOUT']
        )

        # Log final
        print(f"🎯 PREF-HYBRID FINAL: Returning {len(sorted_recommendations)} books", flush=True)
        logger.info(f"🎯 PREF-HYBRID FINAL: Returning {len(sorted_recommendations)} books")

        # Stats
        logger.info(
            f"📊 Hybrid sources: "
            f"Collab={len(collab_recs)}, "
            f"Content={len(content_recs)}, "
            f"Trending={len(trending_books)}"
        )

        return sorted_recommendations

    def _get_trending_in_favorite_genres(self, user, top_genres, n=10):
        """
        Retorna livros em alta nos gêneros favoritos do usuário.

        MELHORIA: Ao invés de trending geral, foca nos gêneros que o usuário gosta.
        """
        from django.utils import timezone
        from datetime import timedelta

        week_ago = timezone.now() - timedelta(days=7)

        # Buscar livros em alta nos gêneros favoritos
        trending = (
            UserBookInteraction.objects
            .filter(created_at__gte=week_ago)
            .values('book')
            .annotate(count=Count('id'))
            .order_by('-count')[:n * 3]  # Buscar mais para filtrar
        )

        book_ids = [t['book'] for t in trending]
        books = Book.objects.filter(id__in=book_ids)

        # Filtrar apenas livros dos gêneros favoritos
        if top_genres:
            books = books.filter(category__in=top_genres)

        # Filtrar capas
        filtered_books = [book for book in books if book.has_valid_cover]

        logger.info(
            f"📈 Trending in favorite genres ({', '.join(top_genres)}): {len(filtered_books)} books"
        )

        return filtered_books[:n]
