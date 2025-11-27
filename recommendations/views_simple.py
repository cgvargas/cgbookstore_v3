"""
Views SIMPLIFICADAS (Django puro) para Sistema de Recomendações.

DESIGN:
- Django puro (sem DRF)
- Algoritmo único e simples
- Cache eficiente
- Rate limiting condicional (apenas em produção)
"""
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django_ratelimit.decorators import ratelimit
from django.utils import timezone
from django.conf import settings
from .algorithms_simple import get_simple_recommendation_engine
from .models import UserBookInteraction
from core.models import Book
import logging

logger = logging.getLogger(__name__)


def conditional_ratelimit(rate, method='GET'):
    """
    Aplica rate limiting apenas se DEBUG=False.
    Em desenvolvimento (DEBUG=True), permite requisições ilimitadas.
    """
    def decorator(func):
        if settings.DEBUG:
            # Em DEBUG mode, não aplicar rate limiting
            return func
        else:
            # Em produção, aplicar rate limiting
            return ratelimit(key='user', rate=rate, method=method, block=True)(func)
    return decorator


@require_http_methods(["GET"])
@login_required
@conditional_ratelimit(rate='30/h')
def get_recommendations_simple(request):
    """
    Endpoint SIMPLIFICADO para obter recomendações.

    Query params:
    - limit: número de recomendações (default: 10, max: 50)

    Returns:
        JSON com recomendações personalizadas
    """
    try:
        # Obter parâmetros
        limit = int(request.GET.get('limit', 10))
        limit = min(limit, 50)  # Max 50

        logger.info(f"🎯 Generating {limit} recommendations for {request.user.username}")

        # Obter recomendações do motor simplificado
        engine = get_simple_recommendation_engine()
        recommendations = engine.recommend(request.user, n=limit)

        # Serializar livros
        books_data = []
        for rec in recommendations:
            book = rec['book']

            # Converter author para string
            author_name = 'Autor desconhecido'
            if hasattr(book, 'author') and book.author:
                author_name = str(book.author)

            book_data = {
                'id': book.id,
                'slug': book.slug,
                'title': book.title,
                'author': author_name,
                'cover_image': book.cover_image.url if book.cover_image else None,
                'score': rec['score'],
                'reason': rec['reason'],
                'source': 'local_db'
            }
            books_data.append(book_data)

        response_data = {
            'algorithm': 'simple_unified',
            'count': len(books_data),
            'recommendations': books_data
        }

        logger.info(f"✓ Returning {len(books_data)} recommendations for {request.user.username}")

        return JsonResponse(response_data)

    except Exception as e:
        logger.error(f"Error generating recommendations: {e}", exc_info=True)
        return JsonResponse({
            'error': 'Erro ao gerar recomendações',
            'detail': str(e),
            'algorithm': 'simple_unified',
            'count': 0,
            'recommendations': []
        }, status=500)


@require_http_methods(["POST"])
@login_required
@conditional_ratelimit(rate='100/h', method='POST')
def track_click_simple(request):
    """
    Registra clique em uma recomendação.

    POST body (JSON):
    - book_id: ID do livro (obrigatório)
    - algorithm: Algoritmo usado (opcional, para analytics)

    Returns:
        JSON com confirmação do tracking
    """
    try:
        import json

        # Parse do body JSON
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({
                'error': 'JSON inválido'
            }, status=400)

        book_id = data.get('book_id')
        algorithm = data.get('algorithm', 'simple_unified')

        if not book_id:
            return JsonResponse({
                'error': 'book_id é obrigatório'
            }, status=400)

        # Buscar livro
        try:
            book = Book.objects.get(id=book_id)
        except Book.DoesNotExist:
            return JsonResponse({
                'error': f'Livro não encontrado: {book_id}'
            }, status=404)

        # Criar ou atualizar interação
        interaction, created = UserBookInteraction.objects.get_or_create(
            user=request.user,
            book=book,
            interaction_type='click',
            defaults={'created_at': timezone.now()}
        )

        if not created:
            # Atualizar timestamp
            interaction.created_at = timezone.now()
            interaction.save()

        logger.info(
            f"Click tracked: user={request.user.username}, "
            f"book={book.title}, algorithm={algorithm}"
        )

        return JsonResponse({
            'success': True,
            'message': 'Clique registrado com sucesso',
            'book_id': book_id,
            'book_title': book.title,
            'algorithm': algorithm,
            'interaction_created': created
        })

    except Exception as e:
        logger.error(f"Error tracking click: {e}", exc_info=True)
        return JsonResponse({
            'error': 'Erro ao registrar clique',
            'detail': str(e)
        }, status=500)
