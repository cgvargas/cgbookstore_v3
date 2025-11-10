"""
Model: ReadingProgress
Acompanhamento do progresso de leitura de cada livro.
Versão 2.0 - Com sistema de prazos e gestão de abandono.
"""

from django.db import models
from django.contrib.auth.models import User
from core.models import Book
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import timedelta


class ReadingProgress(models.Model):
    """
    Progresso de leitura do usuário para um livro específico.

    Acompanha:
    - Página atual
    - Total de páginas
    - Percentual (calculado automaticamente)
    - Datas de início e término
    - Tempo de leitura
    - Prazo e notificações
    - Status de abandono
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

    # ========== NOVOS CAMPOS - SISTEMA DE PRAZOS ==========

    deadline = models.DateField(
        null=True,
        blank=True,
        verbose_name='Prazo de Leitura',
        help_text='Data limite para terminar o livro'
    )

    deadline_notified = models.BooleanField(
        default=False,
        verbose_name='Notificação de Prazo Enviada',
        help_text='Se já foi notificado sobre o prazo se aproximando'
    )

    is_abandoned = models.BooleanField(
        default=False,
        verbose_name='Livro Abandonado',
        help_text='Se o livro foi marcado como abandonado'
    )

    abandoned_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Data de Abandono',
        help_text='Quando o livro foi abandonado'
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
            models.Index(fields=['deadline']),
            models.Index(fields=['is_abandoned']),
        ]

    def __str__(self):
        return f'{self.user.username} - {self.book.title} ({self.percentage}%)'

    # ========== PROPRIEDADES EXISTENTES ==========

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
            return timezone.now() + timedelta(days=days_remaining)
        return None

    # ========== NOVAS PROPRIEDADES - SISTEMA DE PRAZOS ==========

    @property
    def days_until_deadline(self):
        """
        Retorna quantos dias faltam até o prazo.
        Negativo se passou do prazo.
        None se não há prazo definido.
        """
        if not self.deadline:
            return None

        today = timezone.now().date()
        delta = self.deadline - today
        return delta.days

    @property
    def is_deadline_approaching(self):
        """Verifica se o prazo está próximo (5 dias ou menos)."""
        if not self.deadline or self.is_finished:
            return False

        days_left = self.days_until_deadline
        return days_left is not None and 0 <= days_left <= 5

    @property
    def is_overdue(self):
        """Verifica se passou do prazo."""
        if not self.deadline or self.is_finished:
            return False

        days_left = self.days_until_deadline
        return days_left is not None and days_left < 0

    @property
    def days_overdue(self):
        """Retorna quantos dias passou do prazo."""
        if not self.is_overdue:
            return 0
        return abs(self.days_until_deadline)

    @property
    def should_notify_deadline(self):
        """
        Verifica se deve enviar notificação de prazo.
        Notifica quando faltam 5 dias ou menos e ainda não foi notificado.
        """
        return (
            self.is_deadline_approaching and
            not self.deadline_notified and
            not self.is_finished and
            not self.is_abandoned
        )

    @property
    def should_auto_abandon(self):
        """
        Verifica se deve abandonar automaticamente.
        Abandona se passou 5 dias do prazo sem progresso.
        """
        if not self.deadline or self.is_finished or self.is_abandoned:
            return False

        return self.days_overdue >= 5

    @property
    def deadline_status(self):
        """
        Retorna status do prazo para exibição.
        Retorna: 'no_deadline', 'on_track', 'approaching', 'overdue', 'abandoned'
        """
        if self.is_abandoned:
            return 'abandoned'
        if not self.deadline:
            return 'no_deadline'
        if self.is_finished:
            return 'finished'
        if self.is_overdue:
            return 'overdue'
        if self.is_deadline_approaching:
            return 'approaching'
        return 'on_track'

    @property
    def deadline_status_display(self):
        """Retorna descrição amigável do status do prazo."""
        status_map = {
            'no_deadline': 'Sem prazo definido',
            'on_track': 'No prazo',
            'approaching': f'Prazo próximo ({self.days_until_deadline} dias)',
            'overdue': f'Atrasado ({self.days_overdue} dias)',
            'abandoned': 'Abandonado',
            'finished': 'Concluído'
        }
        return status_map.get(self.deadline_status, 'Desconhecido')

    # ========== MÉTODOS EXISTENTES (ATUALIZADOS) ==========

    def update_progress(self, current_page):
        """
        Atualiza o progresso de leitura.

        Se o usuário atingir a última página, o livro é automaticamente
        movido da prateleira "Lendo" para "Lidos".
        """
        self.current_page = min(current_page, self.total_pages)

        # Se terminou de ler
        if self.current_page >= self.total_pages and not self.finished_at:
            self.finished_at = timezone.now()
            self.is_abandoned = False  # Remove flag de abandonado se completou

            # Adiciona XP por conclusão
            if hasattr(self.user, 'profile'):
                self.user.profile.add_xp(50)  # 50 XP por completar livro

            # Move automaticamente para prateleira "Lidos"
            self._move_to_read_shelf()

        self.save()

    def _move_to_read_shelf(self):
        """
        Move o livro da prateleira "Lendo" para "Lidos" automaticamente
        quando a leitura é concluída.
        """
        from accounts.models import BookShelf

        # Remove da prateleira "Lendo"
        BookShelf.objects.filter(
            user=self.user,
            book=self.book,
            shelf_type='reading'
        ).delete()

        # Adiciona na prateleira "Lidos" (se ainda não estiver)
        BookShelf.objects.get_or_create(
            user=self.user,
            book=self.book,
            shelf_type='read',
            defaults={
                'notes': f'Concluído em {timezone.now().strftime("%d/%m/%Y")}'
            }
        )

    # ========== NOVOS MÉTODOS - GESTÃO DE ABANDONO ==========

    def mark_as_abandoned(self, auto=False):
        """
        Marca o livro como abandonado.

        Args:
            auto (bool): Se foi abandono automático pelo sistema

        Returns:
            bool: Se a operação foi bem-sucedida
        """
        if self.is_finished:
            return False

        self.is_abandoned = True
        self.abandoned_at = timezone.now()
        self.save()

        # Move para prateleira de abandonados
        from accounts.models import BookShelf

        # Remove de "reading" se estiver lá
        BookShelf.objects.filter(
            user=self.user,
            book=self.book,
            shelf_type='reading'
        ).delete()

        # Adiciona em "abandoned"
        BookShelf.objects.get_or_create(
            user=self.user,
            book=self.book,
            shelf_type='abandoned',
            defaults={
                'notes': f'Abandonado automaticamente em {timezone.now().strftime("%d/%m/%Y")}' if auto
                         else f'Abandonado manualmente em {timezone.now().strftime("%d/%m/%Y")}'
            }
        )

        return True

    def restore_from_abandoned(self):
        """
        Restaura livro abandonado para status de leitura.

        Returns:
            bool: Se a operação foi bem-sucedida
        """
        if not self.is_abandoned:
            return False

        self.is_abandoned = False
        self.abandoned_at = None
        self.deadline_notified = False  # Reseta notificação
        self.save()

        # Move de volta para prateleira "reading"
        from accounts.models import BookShelf

        # Remove de "abandoned"
        BookShelf.objects.filter(
            user=self.user,
            book=self.book,
            shelf_type='abandoned'
        ).delete()

        # Adiciona em "reading"
        BookShelf.objects.get_or_create(
            user=self.user,
            book=self.book,
            shelf_type='reading',
            defaults={
                'started_reading': timezone.now(),
                'notes': f'Restaurado de abandonados em {timezone.now().strftime("%d/%m/%Y")}'
            }
        )

        return True

    def set_deadline(self, deadline_date):
        """
        Define prazo para leitura.

        Args:
            deadline_date (date): Data do prazo

        Returns:
            bool: Se a operação foi bem-sucedida
        """
        if self.is_finished or self.is_abandoned:
            return False

        self.deadline = deadline_date
        self.deadline_notified = False  # Reseta notificação ao mudar prazo
        self.save()
        return True

    def mark_deadline_notified(self):
        """Marca que a notificação de prazo foi enviada."""
        self.deadline_notified = True
        self.save()

    # ========== SAVE OVERRIDE (ATUALIZADO) ==========

    def save(self, *args, **kwargs):
        """Override save para validações e lógica automática."""
        # Garante que current_page não ultrapasse total_pages
        if self.total_pages and self.current_page > self.total_pages:
            self.current_page = self.total_pages

        # Se atingiu 100%, marca como finalizado
        if self.total_pages and self.current_page >= self.total_pages and not self.finished_at:
            self.finished_at = timezone.now()
            self.is_abandoned = False  # Remove flag de abandonado

        # Se está abandonado, não pode estar finalizado
        if self.is_abandoned and self.finished_at:
            self.finished_at = None

        super().save(*args, **kwargs)