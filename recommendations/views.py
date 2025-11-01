"""
Views da API REST para Sistema de Recomendações.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from core.models import Book
from .models import UserProfile, UserBookInteraction, Recommendation
from .serializers import (
    UserProfileSerializer,
    UserBookInteractionSerializer,
    RecommendationSerializer,
    BookMiniSerializer,
    RecommendationRequestSerializer,
    SimilarBooksRequestSerializer
)
from .algorithms import (
    CollaborativeFilteringAlgorithm,
    ContentBasedFilteringAlgorithm,
    HybridRecommendationSystem
)
from .algorithms_preference_weighted import (
    PreferenceWeightedHybrid,
    PreferenceWeightedCollaborative,
    PreferenceWeightedContentBased
)
from .gemini_ai import GeminiRecommendationEngine
import logging

logger = logging.getLogger(__name__)


class UserProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar perfis de usuário.
    """
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Usuário só pode ver seu próprio perfil
        return UserProfile.objects.filter(user=self.request.user)

    def get_object(self):
        # Criar perfil se não existir
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Retorna o perfil do usuário autenticado."""
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(profile)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def update_statistics(self, request):
        """Atualiza estatísticas do perfil."""
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        profile.update_statistics()
        serializer = self.get_serializer(profile)
        return Response(serializer.data)


class UserBookInteractionViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar interações usuário-livro.
    """
    serializer_class = UserBookInteractionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Usuário só pode ver suas próprias interações
        return UserBookInteraction.objects.filter(user=self.request.user)

    @ratelimit(key='user', rate='100/h', method='POST')
    def create(self, request, *args, **kwargs):
        """Cria uma nova interação."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # Invalidar cache de recomendações
        cache_keys = [
            f'hybrid_rec:{request.user.id}:*',
            f'collab_filter:similar_users:{request.user.id}',
            f'gemini_rec:{request.user.id}:*'
        ]
        for key in cache_keys:
            cache.delete_pattern(key)

        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    @action(detail=False, methods=['get'])
    def history(self, request):
        """Retorna histórico de interações do usuário."""
        interaction_type = request.query_params.get('type', None)
        queryset = self.get_queryset()

        if interaction_type:
            queryset = queryset.filter(interaction_type=interaction_type)

        queryset = queryset.select_related('book').order_by('-created_at')[:50]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


@api_view(['GET'])
@ratelimit(key='user', rate='30/h', method='GET')
def get_recommendations(request):
    """
    Endpoint principal para obter recomendações.

    Query params:
    - algorithm: 'collaborative', 'content', 'hybrid', 'ai',
                 'preference_hybrid', 'preference_collab', 'preference_content' (default: hybrid)
    - limit: número de recomendações (default: 10, max: 50)
    """
    # Verificar se usuário está autenticado
    if not request.user.is_authenticated:
        return Response(
            {'error': 'Autenticação necessária. Faça login para ver recomendações.'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    serializer = RecommendationRequestSerializer(data=request.query_params)
    serializer.is_valid(raise_exception=True)

    algorithm = serializer.validated_data['algorithm']
    limit = serializer.validated_data['limit']

    try:
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

        elif algorithm == 'preference_hybrid':
            # Sistema ponderado por prateleiras (favoritos > lidos > lendo > quero ler)
            engine = PreferenceWeightedHybrid()
            recommendations = engine.recommend(request.user, n=limit)

        elif algorithm == 'preference_collab':
            # Collaborative ponderado por prateleiras
            engine = PreferenceWeightedCollaborative()
            recommendations = engine.recommend(request.user, n=limit)

        elif algorithm == 'preference_content':
            # Content-based ponderado por prateleiras
            engine = PreferenceWeightedContentBased()
            recommendations = engine.recommend(request.user, n=limit)

        elif algorithm == 'ai':
            # Recomendações com Google Gemini
            engine = GeminiRecommendationEngine()

            if not engine.is_available():
                return Response(
                    {'error': 'Gemini AI não está configurado. Adicione GEMINI_API_KEY ao .env'},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )

            # Obter histórico do usuário
            user_history = UserBookInteraction.objects.filter(
                user=request.user
            ).select_related('book').order_by('-created_at')[:20]

            history_data = [{
                'title': interaction.book.title,
                'author': interaction.book.author,
                'categories': getattr(interaction.book, 'categories', ''),
                'interaction_type': interaction.interaction_type
            } for interaction in user_history]

            # Pedir mais recomendações para compensar livros sem capa
            recommendations = engine.generate_recommendations(
                request.user,
                history_data,
                n=limit * 3  # Pedir 3x mais
            )

            # Tentar encontrar os livros no banco de dados e filtrar por capa
            filtered_recommendations = []

            for rec in recommendations:
                # Tentar encontrar o livro no banco
                try:
                    # Buscar por título (case insensitive)
                    from django.db.models import Q
                    book = Book.objects.filter(
                        Q(title__iexact=rec['title']) |
                        Q(title__icontains=rec['title'][:30])  # Parte do título
                    ).first()

                    if book and book.has_valid_cover:
                        # Livro encontrado E tem capa válida
                        book_data = BookMiniSerializer(book).data
                        book_data['score'] = rec['score']
                        book_data['reason'] = rec['reason']
                        filtered_recommendations.append(book_data)
                    elif not book:
                        # Livro não encontrado no banco - incluir como sugestão do Gemini
                        logger.info(f"Book not found in DB: {rec['title']} by {rec['author']}")
                        filtered_recommendations.append({
                            'book': None,
                            'score': rec['score'],
                            'reason': rec['reason'],
                            'title': rec['title'],
                            'author': rec['author'],
                            'cover_image': None,
                            'source': 'gemini_suggestion'
                        })
                    else:
                        # Livro sem capa - pular
                        logger.debug(f"Filtered AI book without cover: {rec['title']}")

                    # Parar quando atingir o limite
                    if len(filtered_recommendations) >= limit:
                        break

                except Exception as e:
                    logger.error(f"Error processing AI recommendation: {e}")
                    continue

            return Response({
                'algorithm': algorithm,
                'count': len(filtered_recommendations),
                'recommendations': filtered_recommendations
            })

        else:
            return Response(
                {'error': 'Algoritmo inválido'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Serializar livros
        books_data = []
        for rec in recommendations:
            book_data = BookMiniSerializer(rec['book']).data
            book_data['score'] = rec['score']
            book_data['reason'] = rec['reason']
            books_data.append(book_data)

        return Response({
            'algorithm': algorithm,
            'count': len(books_data),
            'recommendations': books_data
        })

    except Exception as e:
        logger.error(f"Error generating recommendations: {e}", exc_info=True)
        return Response(
            {'error': 'Erro ao gerar recomendações'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@ratelimit(key='user', rate='50/h', method='GET')
def get_similar_books(request, book_id):
    """
    Retorna livros similares a um livro específico.

    Path params:
    - book_id: ID do livro

    Query params:
    - limit: número de livros similares (default: 10, max: 50)
    """
    book = get_object_or_404(Book, id=book_id)
    limit = min(int(request.query_params.get('limit', 10)), 50)

    try:
        # Usar algoritmo baseado em conteúdo
        engine = ContentBasedFilteringAlgorithm()
        similar_books = engine.find_similar_books(book, n=limit)

        # Serializar resultados
        results = []
        for rec in similar_books:
            book_data = BookMiniSerializer(rec['book']).data
            book_data['similarity_score'] = rec['score']
            book_data['reason'] = rec['reason']
            results.append(book_data)

        return Response({
            'book': BookMiniSerializer(book).data,
            'similar_books': results,
            'count': len(results)
        })

    except Exception as e:
        logger.error(f"Error finding similar books: {e}", exc_info=True)
        return Response(
            {'error': 'Erro ao buscar livros similares'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@ratelimit(key='user', rate='10/h', method='POST')
def track_recommendation_click(request, recommendation_id):
    """
    Registra o clique em uma recomendação.
    """
    try:
        recommendation = Recommendation.objects.get(
            id=recommendation_id,
            user=request.user
        )
        recommendation.mark_clicked()

        return Response({
            'message': 'Clique registrado com sucesso',
            'recommendation_id': recommendation_id
        })

    except Recommendation.DoesNotExist:
        return Response(
            {'error': 'Recomendação não encontrada'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_insights(request):
    """
    Retorna insights sobre os hábitos de leitura do usuário usando Gemini AI.
    """
    gemini = GeminiRecommendationEngine()

    if not gemini.is_available():
        return Response(
            {'error': 'Gemini AI não está configurado'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )

    # Obter histórico
    user_history = UserBookInteraction.objects.filter(
        user=request.user
    ).select_related('book').order_by('-created_at')[:50]

    history_data = [{
        'title': interaction.book.title,
        'author': interaction.book.author,
        'categories': getattr(interaction.book, 'categories', ''),
        'interaction_type': interaction.interaction_type
    } for interaction in user_history]

    insights = gemini.generate_reading_insights(request.user, history_data)

    return Response(insights)
