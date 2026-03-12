"""
Model: BookReview
Sistema de avaliações e resenhas de livros pelos usuários.
"""

from django.db import models
from django.contrib.auth.models import User
from core.models import Book
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class BookReview(models.Model):
    """
    Avaliação e resenha de livro pelo usuário.

    Permite:
    - Avaliação com estrelas (1-5)
    - Resenha escrita
    - Público ou privado
    - Reações de outros usuários (futuro)
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='book_reviews',
        verbose_name='Usuário'
    )

    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='user_reviews',
        verbose_name='Livro'
    )

    rating = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
        verbose_name='Avaliação',
        help_text='Nota de 0.0 a 5.0'
    )

    title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Título da Resenha'
    )

    review_text = models.TextField(
        blank=True,
        verbose_name='Resenha',
        help_text='Sua opinião sobre o livro'
    )

    # Configurações
    is_public = models.BooleanField(
        default=False,
        verbose_name='Resenha Pública',
        help_text='Permitir que outros usuários vejam sua resenha'
    )

    contains_spoilers = models.BooleanField(
        default=False,
        verbose_name='Contém Spoilers',
        help_text='Marque se sua resenha revela partes da história'
    )

    # Recomendação
    would_recommend = models.BooleanField(
        default=True,
        verbose_name='Recomendaria',
        help_text='Você recomendaria este livro?'
    )

    # Datas
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criado em'
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Atualizado em'
    )

    # Estatísticas (para futuro sistema de reações)
    helpful_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Úteis',
        help_text='Quantas pessoas acharam esta resenha útil'
    )

    class Meta:
        verbose_name = 'Avaliação de Livro'
        verbose_name_plural = 'Avaliações de Livros'
        ordering = ['-created_at']
        unique_together = ['user', 'book']
        indexes = [
            models.Index(fields=['user', 'book']),
            models.Index(fields=['book', 'created_at']),
            models.Index(fields=['is_public', 'created_at']),
        ]

    def __str__(self):
        stars = '⭐' * self.rating
        return f'{self.user.username} - {self.book.title} ({stars})'

    @property
    def rating_stars(self):
        """Retorna representação visual das estrelas."""
        return '⭐' * self.rating + '☆' * (5 - self.rating)

    @property
    def short_review(self):
        """Retorna versão curta da resenha (primeiros 150 caracteres)."""
        if len(self.review_text) > 150:
            return self.review_text[:147] + '...'
        return self.review_text

    def save(self, *args, **kwargs):
        """Override save para adicionar pontos."""
        is_new = self.pk is None

        super().save(*args, **kwargs)

        # Adiciona pontos ao usuário por criar resenha
        if is_new and hasattr(self.user, 'profile'):
            xp_amount = 25 if self.review_text else 10  # Mais XP se escreveu resenha
            self.user.profile.add_xp(xp_amount)


class ReviewLike(models.Model):
    """
    Representa uma curtida (like) dada por um usuário a uma resenha.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='review_likes',
        verbose_name='Usuário'
    )
    review = models.ForeignKey(
        'BookReview',
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name='Resenha'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criado em'
    )

    class Meta:
        verbose_name = 'Curtida em Resenha'
        verbose_name_plural = 'Curtidas em Resenhas'
        unique_together = ['user', 'review']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} curtiu resenha {self.review.id}"


class ReviewComment(models.Model):
    """
    Representa um comentário feito por um usuário em uma resenha de outro.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='review_comments',
        verbose_name='Autor'
    )
    review = models.ForeignKey(
        'BookReview',
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Resenha'
    )
    content = models.TextField(
        verbose_name='Comentário'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Ativo'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criado em'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Atualizado em'
    )

    class Meta:
        verbose_name = 'Comentário em Resenha'
        verbose_name_plural = 'Comentários em Resenhas'
        ordering = ['created_at']

    def __str__(self):
        return f"Comentário de {self.user.username} na resenha {self.review.id}"
