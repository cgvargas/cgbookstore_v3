"""
Model: ReadingProgress
Acompanhamento do progresso de leitura de cada livro.
"""

from django.db import models
from django.contrib.auth.models import User
from core.models import Book
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class ReadingProgress(models.Model):
    """
    Progresso de leitura do usuário para um livro específico.

    Acompanha:
    - Página atual
    - Total de páginas
    - Percentual (calculado automaticamente)
    - Datas de início e término
    - Tempo de leitura
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reading_progress',
        verbose_name='Usuário'
    )

    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='reading_progress',
        verbose_name='Livro'
    )

    current_page = models.PositiveIntegerField(
        default=0,
        verbose_name='Página Atual',
        help_text='Última página lida'
    )

    total_pages = models.PositiveIntegerField(
        verbose_name='Total de Páginas',
        help_text='Total de páginas do livro'
    )

    started_at = models.DateTimeField(
        default=timezone.now,
        verbose_name='Início da Leitura'
    )

    finished_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Término da Leitura'
    )

    last_updated = models.DateTimeField(
        auto_now=True,
        verbose_name='Última Atualização'
    )

    # Notas sobre a leitura
    reading_notes = models.TextField(
        blank=True,
        verbose_name='Notas de Leitura',
        help_text='Anotações, reflexões, citações...'
    )

    class Meta:
        verbose_name = 'Progresso de Leitura'
        verbose_name_plural = 'Progressos de Leitura'
        ordering = ['-last_updated']
        unique_together = ['user', 'book']
        indexes = [
            models.Index(fields=['user', 'book']),
            models.Index(fields=['user', 'last_updated']),
        ]

    def __str__(self):
        return f'{self.user.username} - {self.book.title} ({self.percentage}%)'

    @property
    def percentage(self):
        """Calcula o percentual de leitura."""
        if self.total_pages and self.total_pages > 0:
            return round((self.current_page / self.total_pages) * 100, 1)
        return 0.0

    @property
    def is_finished(self):
        """Verifica se a leitura foi concluída."""
        if not self.total_pages:
            return False
        return self.current_page >= self.total_pages or self.finished_at is not None

    @property
    def reading_time_days(self):
        """Retorna o tempo de leitura em dias."""
        end_date = self.finished_at or timezone.now()
        delta = end_date - self.started_at
        return delta.days

    @property
    def pages_per_day(self):
        """Calcula média de páginas lidas por dia."""
        days = self.reading_time_days
        if days > 0:
            return round(self.current_page / days, 1)
        return 0

    @property
    def estimated_finish_date(self):
        """Estima data de conclusão baseada no ritmo atual."""
        if self.pages_per_day > 0 and not self.is_finished:
            remaining_pages = self.total_pages - self.current_page
            days_remaining = remaining_pages / self.pages_per_day
            from datetime import timedelta
            return timezone.now() + timedelta(days=days_remaining)
        return None

    def update_progress(self, current_page):
        """Atualiza o progresso de leitura."""
        self.current_page = min(current_page, self.total_pages)

        # Se terminou de ler
        if self.current_page >= self.total_pages and not self.finished_at:
            self.finished_at = timezone.now()

            # Adiciona pontos extras por conclusão
            if hasattr(self.user, 'profile'):
                self.user.profile.add_points(5)  # 5 pontos extras

        self.save()

    def save(self, *args, **kwargs):
        """Override save para validações."""
        # Garante que current_page não ultrapasse total_pages
        if self.total_pages and self.current_page > self.total_pages:
            self.current_page = self.total_pages

        # Se atingiu 100%, marca como finalizado
        if self.total_pages and self.current_page >= self.total_pages and not self.finished_at:
            self.finished_at = timezone.now()

        super().save(*args, **kwargs)