"""
Tasks Celery para processamento assíncrono de recomendações.
"""
from celery import shared_task
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings
from django.core.cache import cache
from .models import UserBookInteraction, BookSimilarity, Recommendation
from .algorithms import ContentBasedFilteringAlgorithm, HybridRecommendationSystem
from core.models import Book
import logging

logger = logging.getLogger(__name__)


@shared_task
def compute_book_similarities():
    """
    Calcula e armazena similaridades entre todos os livros.
    Task pesada que deve rodar periodicamente (ex: 1x por dia).
    """
    try:
        logger.info("Starting book similarity computation...")

        engine = ContentBasedFilteringAlgorithm()
        engine.build_book_vectors()

        if engine.book_vectors is None:
            logger.warning("No book vectors available")
            return "No books to process"

        books = Book.objects.all()
        total_books = books.count()
        similarities_created = 0
        similarities_updated = 0

        # Processar cada livro
        for i, book in enumerate(books):
            if i % 10 == 0:
                logger.info(f"Processing book {i+1}/{total_books}: {book.title}")

            # Encontrar livros similares
            similar_books = engine.find_similar_books(book, n=20)

            # Salvar similaridades
            for similar in similar_books:
                similarity, created = BookSimilarity.objects.update_or_create(
                    book_a=book,
                    book_b=similar['book'],
                    method='content',
                    defaults={
                        'similarity_score': similar['score']
                    }
                )

                if created:
                    similarities_created += 1
                else:
                    similarities_updated += 1

        result = f"Similarities computed: {similarities_created} created, {similarities_updated} updated"
        logger.info(result)
        return result

    except Exception as e:
        logger.error(f"Error computing book similarities: {e}", exc_info=True)
        return f"Error: {str(e)}"


@shared_task
def generate_user_recommendations(user_id, algorithm='hybrid', limit=10):
    """
    Gera recomendações para um usuário específico e armazena no banco.

    Args:
        user_id: ID do usuário
        algorithm: Algoritmo a usar ('hybrid', 'collaborative', 'content')
        limit: Número de recomendações
    """
    try:
        user = User.objects.get(id=user_id)
        logger.info(f"Generating {algorithm} recommendations for user {user.username}")

        # Selecionar algoritmo
        if algorithm == 'hybrid':
            engine = HybridRecommendationSystem()
        elif algorithm == 'collaborative':
            from .algorithms import CollaborativeFilteringAlgorithm
            engine = CollaborativeFilteringAlgorithm()
        elif algorithm == 'content':
            engine = ContentBasedFilteringAlgorithm()
        else:
            logger.error(f"Invalid algorithm: {algorithm}")
            return f"Invalid algorithm: {algorithm}"

        # Gerar recomendações
        recommendations = engine.recommend(user, n=limit)

        if not recommendations:
            logger.warning(f"No recommendations generated for user {user.username}")
            return "No recommendations generated"

        # Salvar no banco
        expires_at = timezone.now() + timezone.timedelta(
            seconds=settings.RECOMMENDATIONS_CONFIG['CACHE_TIMEOUT']
        )

        saved_count = 0
        for rec in recommendations:
            Recommendation.objects.update_or_create(
                user=user,
                book=rec['book'],
                recommendation_type=algorithm,
                defaults={
                    'score': rec['score'],
                    'reason': rec['reason'],
                    'expires_at': expires_at
                }
            )
            saved_count += 1

        result = f"Generated {saved_count} recommendations for {user.username}"
        logger.info(result)
        return result

    except User.DoesNotExist:
        logger.error(f"User {user_id} not found")
        return f"User {user_id} not found"

    except Exception as e:
        logger.error(f"Error generating recommendations for user {user_id}: {e}", exc_info=True)
        return f"Error: {str(e)}"


@shared_task
def batch_generate_recommendations(algorithm='hybrid', limit=10):
    """
    Gera recomendações para todos os usuários ativos.
    Deve rodar periodicamente (ex: 1x por hora).
    """
    try:
        logger.info("Starting batch recommendation generation...")

        # Obter usuários ativos (com pelo menos 1 interação)
        active_users = User.objects.filter(
            book_interactions__isnull=False
        ).distinct()

        total_users = active_users.count()
        logger.info(f"Found {total_users} active users")

        success_count = 0
        error_count = 0

        for i, user in enumerate(active_users):
            if i % 10 == 0:
                logger.info(f"Processing user {i+1}/{total_users}")

            try:
                generate_user_recommendations.delay(user.id, algorithm, limit)
                success_count += 1
            except Exception as e:
                logger.error(f"Error queueing recommendations for user {user.id}: {e}")
                error_count += 1

        result = f"Queued recommendations for {success_count} users ({error_count} errors)"
        logger.info(result)
        return result

    except Exception as e:
        logger.error(f"Error in batch recommendation generation: {e}", exc_info=True)
        return f"Error: {str(e)}"


@shared_task
def cleanup_expired_recommendations():
    """
    Remove recomendações expiradas do banco.
    Deve rodar periodicamente (ex: 1x por dia).
    """
    try:
        logger.info("Cleaning up expired recommendations...")

        deleted_count, _ = Recommendation.objects.filter(
            expires_at__lt=timezone.now()
        ).delete()

        result = f"Deleted {deleted_count} expired recommendations"
        logger.info(result)
        return result

    except Exception as e:
        logger.error(f"Error cleaning up recommendations: {e}", exc_info=True)
        return f"Error: {str(e)}"


@shared_task
def update_user_profile_statistics(user_id):
    """
    Atualiza estatísticas do perfil do usuário.

    Args:
        user_id: ID do usuário
    """
    try:
        user = User.objects.get(id=user_id)
        from .models import UserProfile

        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.update_statistics()

        logger.info(f"Updated statistics for user {user.username}")
        return f"Statistics updated for {user.username}"

    except User.DoesNotExist:
        logger.error(f"User {user_id} not found")
        return f"User {user_id} not found"

    except Exception as e:
        logger.error(f"Error updating statistics for user {user_id}: {e}", exc_info=True)
        return f"Error: {str(e)}"


@shared_task
def precompute_trending_books():
    """
    Pré-calcula livros em alta e cacheia o resultado.
    Deve rodar periodicamente (ex: a cada 6 horas).
    """
    try:
        from datetime import timedelta

        logger.info("Computing trending books...")

        week_ago = timezone.now() - timedelta(days=7)

        # Livros mais interagidos nos últimos 7 dias
        from django.db.models import Count

        trending = (
            UserBookInteraction.objects
            .filter(created_at__gte=week_ago)
            .values('book_id')
            .annotate(interaction_count=Count('id'))
            .order_by('-interaction_count')[:50]
        )

        trending_book_ids = [t['book_id'] for t in trending]

        # Cachear por 6 horas
        cache.set('trending_books', trending_book_ids, timeout=21600)

        result = f"Cached {len(trending_book_ids)} trending books"
        logger.info(result)
        return result

    except Exception as e:
        logger.error(f"Error computing trending books: {e}", exc_info=True)
        return f"Error: {str(e)}"
