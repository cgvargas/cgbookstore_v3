"""
Modelos para o Sistema de Recomendações Inteligente.
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from core.models import Book


class UserProfile(models.Model):
    """
    Perfil estendido do usuário com preferências e estatísticas.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='recommendation_profile')

    # Preferências
    favorite_genres = models.JSONField(default=list, blank=True)
    favorite_authors = models.JSONField(default=list, blank=True)

    # Estatísticas de leitura
    total_books_read = models.IntegerField(default=0)
    total_pages_read = models.IntegerField(default=0)
    avg_reading_time = models.FloatField(default=0.0, help_text="Tempo médio de leitura em minutos")

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'recommendations_userprofile'
        verbose_name = 'Perfil de Usuário'
        verbose_name_plural = 'Perfis de Usuários'
        indexes = [
            models.Index(fields=['user'], name='idx_userprofile_user'),
        ]

    def __str__(self):
        return f"Profile: {self.user.username}"

    def update_statistics(self):
        """
        Atualiza estatísticas baseadas nas interações do usuário.
        """
        interactions = self.user.book_interactions.filter(
            interaction_type__in=['read', 'completed']
        )
        self.total_books_read = interactions.count()
        self.save()


class UserBookInteraction(models.Model):
    """
    Registra todas as interações do usuário com livros.
    """
    INTERACTION_TYPES = [
        ('view', 'Visualização'),
        ('click', 'Clique'),
        ('wishlist', 'Lista de Desejos'),
        ('reading', 'Lendo'),
        ('read', 'Lido'),
        ('completed', 'Finalizado'),
        ('review', 'Avaliado'),
        ('share', 'Compartilhado'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='book_interactions')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='user_interactions')
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_TYPES)

    # Rating (1-5 estrelas) - opcional
    rating = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    # Tempo de interação (em segundos)
    duration = models.IntegerField(default=0, help_text="Duração da interação em segundos")

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'recommendations_interaction'
        verbose_name = 'Interação Usuário-Livro'
        verbose_name_plural = 'Interações Usuário-Livro'
        indexes = [
            models.Index(fields=['user', '-created_at'], name='idx_interaction_user_date'),
            models.Index(fields=['book', '-created_at'], name='idx_interaction_book_date'),
            models.Index(fields=['interaction_type'], name='idx_interaction_type'),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.interaction_type} - {self.book.title}"


class BookSimilarity(models.Model):
    """
    Matriz de similaridade entre livros (pré-computada).
    """
    book_a = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='similarities_from')
    book_b = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='similarities_to')

    # Score de similaridade (0.0 a 1.0)
    similarity_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )

    # Método usado para calcular similaridade
    method = models.CharField(
        max_length=20,
        choices=[
            ('content', 'Conteúdo'),
            ('collaborative', 'Colaborativo'),
            ('hybrid', 'Híbrido'),
        ],
        default='content'
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'recommendations_similarity'
        verbose_name = 'Similaridade entre Livros'
        verbose_name_plural = 'Similaridades entre Livros'
        unique_together = ['book_a', 'book_b', 'method']
        indexes = [
            models.Index(fields=['book_a', '-similarity_score'], name='idx_similarity_book_a'),
            models.Index(fields=['book_b', '-similarity_score'], name='idx_similarity_book_b'),
            models.Index(fields=['method'], name='idx_similarity_method'),
        ]
        ordering = ['-similarity_score']

    def __str__(self):
        return f"{self.book_a.title} <-> {self.book_b.title} ({self.similarity_score:.2f})"


class Recommendation(models.Model):
    """
    Recomendações geradas para usuários (cache).
    """
    RECOMMENDATION_TYPES = [
        ('collaborative', 'Filtragem Colaborativa'),
        ('content', 'Baseado em Conteúdo'),
        ('hybrid', 'Sistema Híbrido'),
        ('ai', 'IA Premium (Gemini)'),
        ('trending', 'Em Alta'),
        ('popular', 'Popular'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recommendations')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='recommendations')

    recommendation_type = models.CharField(max_length=20, choices=RECOMMENDATION_TYPES)

    # Score da recomendação (0.0 a 1.0)
    score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )

    # Justificativa da recomendação (gerada por IA)
    reason = models.TextField(blank=True, help_text="Por que esse livro foi recomendado")

    # Controle de exibição
    is_clicked = models.BooleanField(default=False)
    clicked_at = models.DateTimeField(null=True, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        db_table = 'recommendations_recommendation'
        verbose_name = 'Recomendação'
        verbose_name_plural = 'Recomendações'
        indexes = [
            models.Index(fields=['user', '-score', 'expires_at'], name='idx_rec_user_score'),
            models.Index(fields=['book'], name='idx_rec_book'),
            models.Index(fields=['recommendation_type'], name='idx_rec_type'),
            models.Index(fields=['expires_at'], name='idx_rec_expires'),
        ]
        ordering = ['-score', '-created_at']

    def __str__(self):
        return f"{self.user.username} -> {self.book.title} ({self.recommendation_type})"

    def save(self, *args, **kwargs):
        # Define expiração padrão de 1 hora se não especificado
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(hours=1)
        super().save(*args, **kwargs)

    def mark_clicked(self):
        """Marca a recomendação como clicada."""
        self.is_clicked = True
        self.clicked_at = timezone.now()
        self.save()

    @classmethod
    def get_valid_recommendations(cls, user, recommendation_type=None):
        """
        Retorna recomendações válidas (não expiradas) para um usuário.
        """
        queryset = cls.objects.filter(
            user=user,
            expires_at__gt=timezone.now()
        ).select_related('book')

        if recommendation_type:
            queryset = queryset.filter(recommendation_type=recommendation_type)

        return queryset
