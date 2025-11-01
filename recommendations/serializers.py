"""
Serializers para a API REST de Recomendações.
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from core.models import Book
from .models import UserProfile, UserBookInteraction, BookSimilarity, Recommendation


class BookMiniSerializer(serializers.ModelSerializer):
    """Serializer simplificado para livros nas recomendações."""

    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'cover_image', 'average_rating', 'categories']


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer para o perfil do usuário."""
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'username',
            'favorite_genres',
            'favorite_authors',
            'total_books_read',
            'total_pages_read',
            'avg_reading_time',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class UserBookInteractionSerializer(serializers.ModelSerializer):
    """Serializer para interações usuário-livro."""
    book = BookMiniSerializer(read_only=True)
    book_id = serializers.PrimaryKeyRelatedField(
        queryset=Book.objects.all(),
        source='book',
        write_only=True
    )

    class Meta:
        model = UserBookInteraction
        fields = [
            'id',
            'book',
            'book_id',
            'interaction_type',
            'rating',
            'duration',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        # Adicionar o usuário automaticamente do request
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class RecommendationSerializer(serializers.ModelSerializer):
    """Serializer para recomendações."""
    book = BookMiniSerializer(read_only=True)

    class Meta:
        model = Recommendation
        fields = [
            'id',
            'book',
            'recommendation_type',
            'score',
            'reason',
            'is_clicked',
            'created_at',
            'expires_at'
        ]
        read_only_fields = ['id', 'created_at', 'expires_at']


class RecommendationRequestSerializer(serializers.Serializer):
    """Serializer para requisições de recomendação."""
    algorithm = serializers.ChoiceField(
        choices=[
            'collaborative', 'content', 'hybrid', 'ai',
            'preference_hybrid', 'preference_collab', 'preference_content'
        ],
        default='hybrid'
    )
    limit = serializers.IntegerField(default=10, min_value=1, max_value=50)


class SimilarBooksRequestSerializer(serializers.Serializer):
    """Serializer para requisições de livros similares."""
    book_id = serializers.IntegerField(required=True)
    limit = serializers.IntegerField(default=10, min_value=1, max_value=50)


class BookSimilaritySerializer(serializers.ModelSerializer):
    """Serializer para similaridade entre livros."""
    book_a = BookMiniSerializer(read_only=True)
    book_b = BookMiniSerializer(read_only=True)

    class Meta:
        model = BookSimilarity
        fields = [
            'book_a',
            'book_b',
            'similarity_score',
            'method',
            'updated_at'
        ]
        read_only_fields = ['updated_at']
