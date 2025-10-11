"""
Model: BookShelf
Prateleiras de livros do usuário (Favoritos, Lendo, Lidos, etc).
"""

from django.db import models
from django.contrib.auth.models import User
from core.models import Book
from django.utils import timezone


class BookShelf(models.Model):
    """
    Prateleira de livros do usuário.

    Tipos de prateleira:
    - favorites: Favoritos
    - to_read: Quero Ler
    - reading: Lendo
    - read: Lidos
    - abandoned: Abandonados
    - custom: Prateleira personalizada
    """

    SHELF_TYPES = [
        ('favorites', 'Favoritos'),
        ('to_read', 'Quero Ler'),
        ('reading', 'Lendo'),
        ('read', 'Lidos'),
        ('abandoned', 'Abandonados'),
        ('custom', 'Personalizada'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='bookshelves',
        verbose_name='Usuário'
    )

    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='in_shelves',
        verbose_name='Livro'
    )

    shelf_type = models.CharField(
        max_length=20,
        choices=SHELF_TYPES,
        default='to_read',
        verbose_name='Tipo de Prateleira'
    )

    custom_shelf_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='Nome da Prateleira Personalizada',
        help_text='Obrigatório se tipo = Personalizada'
    )

    notes = models.TextField(
        blank=True,
        verbose_name='Notas Pessoais',
        help_text='Anotações privadas sobre o livro'
    )

    is_public = models.BooleanField(
        default=False,
        verbose_name='Público',
        help_text='Permitir que outros vejam este livro na sua biblioteca'
    )

    date_added = models.DateTimeField(
        default=timezone.now,
        verbose_name='Data de Adição'
    )

    # Datas específicas para tracking
    started_reading = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Início da Leitura'
    )

    finished_reading = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Término da Leitura'
    )

    class Meta:
        verbose_name = 'Prateleira de Livros'
        verbose_name_plural = 'Prateleiras de Livros'
        ordering = ['-date_added']
        unique_together = ['user', 'book', 'shelf_type', 'custom_shelf_name']
        indexes = [
            models.Index(fields=['user', 'shelf_type']),
            models.Index(fields=['user', 'book']),
        ]

    def __str__(self):
        shelf_name = self.get_shelf_display()
        if self.shelf_type == 'custom' and self.custom_shelf_name:
            shelf_name = self.custom_shelf_name
        return f'{self.user.username} - {self.book.title} ({shelf_name})'

    def get_shelf_display(self):
        """Retorna o nome da prateleira."""
        if self.shelf_type == 'custom' and self.custom_shelf_name:
            return self.custom_shelf_name
        return dict(self.SHELF_TYPES).get(self.shelf_type, self.shelf_type)

    def save(self, *args, **kwargs):
        """Override save para adicionar lógica de datas e gamificação."""
        # Se mudou para "reading" e ainda não tem data de início
        if self.shelf_type == 'reading' and not self.started_reading:
            self.started_reading = timezone.now()

        # Se mudou para "read" e ainda não tem data de término
        if self.shelf_type == 'read' and not self.finished_reading:
            self.finished_reading = timezone.now()

            # Adiciona XP ao usuário (gamificação)
            if hasattr(self.user, 'profile'):
                new_level, leveled_up = self.user.profile.add_xp(10)  # 10 XP por livro lido

                # Atualizar contadores
                self.user.profile.books_read_count += 1
                if self.book.page_count:
                    self.user.profile.total_pages_read += self.book.page_count

                # Atualizar streak
                self.user.profile.update_streak()

                self.user.profile.save()

        super().save(*args, **kwargs)