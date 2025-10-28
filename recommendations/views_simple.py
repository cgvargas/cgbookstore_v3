"""
Views simples (Django puro) para contornar problemas do DRF.
"""
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django_ratelimit.decorators import ratelimit
from .algorithms import (
    CollaborativeFilteringAlgorithm,
    ContentBasedFilteringAlgorithm,
    HybridRecommendationSystem
)
from .gemini_ai import GeminiRecommendationEngine
from .gemini_ai_enhanced import EnhancedGeminiRecommendationEngine
from .models import UserBookInteraction
from .serializers import BookMiniSerializer
import logging

logger = logging.getLogger(__name__)


@require_http_methods(["GET"])
@login_required
# @ratelimit(key='user', rate='30/h', method='GET')  # Temporariamente desabilitado para testes
def get_recommendations_simple(request):
    """
    View Django pura (sem DRF) para obter recomendações.

    Query params:
    - algorithm: 'collaborative', 'content', 'hybrid', 'ai' (default: hybrid)
    - limit: número de recomendações (default: 10, max: 50)
    """
    try:
        # Obter parâmetros
        algorithm = request.GET.get('algorithm', 'hybrid')
        limit = int(request.GET.get('limit', 10))
        limit = min(limit, 50)  # Max 50

        logger.info(f"Generating {algorithm} recommendations for {request.user.username}")

        # Selecionar algoritmo
        if algorithm == 'collaborative':
            engine = CollaborativeFilteringAlgorithm()
            recommendations = engine.recommend(request.user, n=limit)

        elif algorithm == 'content':
            engine = ContentBasedFilteringAlgorithm()
            recommendations = engine.recommend(request.user, n=limit)

        elif algorithm == 'hybrid':
            engine = HybridRecommendationSystem()
            recommendations = engine.recommend(request.user, n=limit)

        elif algorithm == 'ai':
            # Recomendações POTENCIALIZADAS com Gemini + Google Books
            engine = EnhancedGeminiRecommendationEngine()

            if not engine.is_available():
                return JsonResponse({
                    'error': 'Gemini AI não está configurado. Adicione GEMINI_API_KEY ao .env',
                    'algorithm': algorithm,
                    'count': 0,
                    'recommendations': []
                }, status=503)

            # Obter histórico COMPLETO do usuário (todas as interações)
            user_history = UserBookInteraction.objects.filter(
                user=request.user
            ).select_related('book').order_by('-created_at')

            history_data = [{
                'title': interaction.book.title,
                'author': str(interaction.book.author) if interaction.book.author else 'Desconhecido',
                'categories': getattr(interaction.book.category, 'name', '') if hasattr(interaction.book, 'category') else '',
                'interaction_type': interaction.interaction_type
            } for interaction in user_history]

            # Gerar recomendações potencializadas com Google Books
            enhanced_recommendations = engine.generate_enhanced_recommendations(
                request.user,
                history_data,
                n=limit
            )

            # Formatar resposta (livros do Google Books com imagens e descrições)
            books_data = []

            for rec in enhanced_recommendations:
                books_data.append({
                    'id': None,  # Livro externo (Google Books)
                    'slug': None,  # Não há slug (livro não está no banco)
                    'title': rec['title'],
                    'author': rec['author'],
                    'cover_image': rec.get('cover_image'),
                    'google_books_id': rec.get('google_books_id'),
                    'description': rec.get('description', rec.get('reason', '')),
                    'score': rec['score'],
                    'reason': rec['reason'],
                    'source': 'google_books'  # Indicar que é do Google Books
                })

            # Se não encontrou livros, usar algoritmo híbrido como fallback
            if not books_data:
                logger.warning("Enhanced AI found no books, using hybrid fallback")
                engine = HybridRecommendationSystem()
                recommendations = engine.recommend(request.user, n=limit)

                from core.models import Book
                for rec in recommendations:
                    book = rec['book']
                    author_name = 'Autor desconhecido'
                    if hasattr(book, 'author') and book.author:
                        author_name = str(book.author) if not isinstance(book.author, str) else book.author

                    books_data.append({
                        'id': book.id,
                        'slug': book.slug,
                        'title': book.title,
                        'author': author_name,
                        'cover_image': book.cover_image.url if hasattr(book, 'cover_image') and book.cover_image else None,
                        'description': book.description[:150] if hasattr(book, 'description') and book.description else '',
                        'score': rec['score'],
                        'reason': f"Baseado em suas preferências | {rec['reason']}",
                        'source': 'local_db'
                    })

            return JsonResponse({
                'algorithm': algorithm,
                'count': len(books_data),
                'recommendations': books_data
            })

        else:
            return JsonResponse({
                'error': f'Algoritmo inválido: {algorithm}',
                'algorithm': algorithm,
                'count': 0,
                'recommendations': []
            }, status=400)

        # Serializar livros (para algoritmos não-AI)
        books_data = []
        for rec in recommendations:
            book = rec['book']

            # Converter author para string (pode ser um objeto Author)
            author_name = 'Autor desconhecido'
            if hasattr(book, 'author') and book.author:
                author_name = str(book.author) if not isinstance(book.author, str) else book.author

            book_data = {
                'id': book.id,
                'slug': book.slug,
                'title': book.title,
                'author': author_name,
                'cover_image': book.cover_image.url if hasattr(book, 'cover_image') and book.cover_image else None,
                'score': rec['score'],
                'reason': rec['reason']
            }
            books_data.append(book_data)

        return JsonResponse({
            'algorithm': algorithm,
            'count': len(books_data),
            'recommendations': books_data
        })

    except Exception as e:
        logger.error(f"Error generating recommendations: {e}", exc_info=True)
        return JsonResponse({
            'error': 'Erro ao gerar recomendações',
            'detail': str(e),
            'algorithm': request.GET.get('algorithm', 'hybrid'),
            'count': 0,
            'recommendations': []
        }, status=500)
