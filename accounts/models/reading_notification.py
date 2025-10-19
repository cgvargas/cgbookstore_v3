"""
Model: ReadingNotification
Sistema de notificações para prazos de leitura.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class ReadingNotification(models.Model):
    """
    Notificações relacionadas a prazos de leitura.

    Tipos de notificação:
    - deadline_warning: Prazo próximo (5 dias)
    - deadline_passed: Prazo vencido
    - book_abandoned: Livro abandonado automaticamente
    """

    NOTIFICATION_TYPES = [
        ('deadline_warning', 'Prazo Próximo'),
        ('deadline_passed', 'Prazo Vencido'),
        ('book_abandoned', 'Livro Abandonado'),
    ]

    PRIORITY_LEVELS = {
        'deadline_warning': 2,  # Média
        'deadline_passed': 3,  # Alta
        'book_abandoned': 1,  # Baixa
    }

    ICONS = {
        'deadline_warning': 'fas fa-clock text-warning',
        'deadline_passed': 'fas fa-exclamation-triangle text-danger',
        'book_abandoned': 'fas fa-bookmark text-muted',
    }

    # ========== CAMPOS PRINCIPAIS ==========

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reading_notifications',
        verbose_name='Usuário'
    )

    reading_progress = models.ForeignKey(
        'ReadingProgress',
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='Progresso de Leitura'
    )

    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPES,
        verbose_name='Tipo de Notificação'
    )

    message = models.TextField(
        verbose_name='Mensagem',
        help_text='Mensagem da notificação'
    )

    # ========== CONTROLE DE LEITURA ==========

    is_read = models.BooleanField(
        default=False,
        verbose_name='Lida',
        help_text='Se a notificação foi lida pelo usuário'
    )

    read_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Lida em',
        help_text='Data e hora em que foi marcada como lida'
    )

    # ========== METADADOS ==========

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criada em'
    )

    class Meta:
        verbose_name = 'Notificação de Leitura'
        verbose_name_plural = 'Notificações de Leitura'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['reading_progress']),
        ]

    def __str__(self):
        status = "✓" if self.is_read else "●"
        return f'[{status}] {self.user.username} - {self.get_notification_type_display()}'

    # ========== PROPRIEDADES ==========

    @property
    def book_title(self):
        """Retorna o título do livro relacionado."""
        return self.reading_progress.book.title

    @property
    def priority(self):
        """Retorna o nível de prioridade da notificação (1-3)."""
        return self.PRIORITY_LEVELS.get(self.notification_type, 1)

    @property
    def priority_name(self):
        """Retorna o nome da prioridade."""
        priority_names = {
            1: 'Baixa',
            2: 'Média',
            3: 'Alta'
        }
        return priority_names.get(self.priority, 'Normal')

    @property
    def icon_class(self):
        """Retorna a classe CSS do ícone FontAwesome."""
        return self.ICONS.get(self.notification_type, 'fas fa-bell')

    @property
    def age_in_hours(self):
        """Retorna quantas horas se passaram desde a criação."""
        now = timezone.now()
        delta = now - self.created_at
        return int(delta.total_seconds() / 3600)

    @property
    def is_recent(self):
        """Verifica se a notificação é recente (menos de 24h)."""
        return self.age_in_hours < 24

    @property
    def formatted_time(self):
        """Retorna tempo formatado de forma amigável."""
        hours = self.age_in_hours

        if hours == 0:
            return "Agora mesmo"
        elif hours == 1:
            return "Há 1 hora"
        elif hours < 24:
            return f"Há {hours} horas"
        else:
            days = hours // 24
            if days == 1:
                return "Há 1 dia"
            elif days < 7:
                return f"Há {days} dias"
            else:
                weeks = days // 7
                if weeks == 1:
                    return "Há 1 semana"
                else:
                    return f"Há {weeks} semanas"

    # ========== MÉTODOS ==========

    def mark_as_read(self):
        """
        Marca a notificação como lida.

        Returns:
            bool: True se foi marcada (estava não lida), False se já estava lida
        """
        if self.is_read:
            return False

        self.is_read = True
        self.read_at = timezone.now()
        self.save()
        return True

    def mark_as_unread(self):
        """
        Marca a notificação como não lida.

        Returns:
            bool: True se foi desmarcada (estava lida), False se já estava não lida
        """
        if not self.is_read:
            return False

        self.is_read = False
        self.read_at = None
        self.save()
        return True

    @classmethod
    def create_deadline_warning(cls, reading_progress):
        """
        Cria notificação de prazo próximo.

        Args:
            reading_progress (ReadingProgress): Progresso de leitura

        Returns:
            ReadingNotification: Notificação criada
        """
        days_left = reading_progress.days_until_deadline

        message = (
            f'O prazo para terminar "{reading_progress.book.title}" está próximo! '
            f'Faltam apenas {days_left} dia(s). '
            f'Você está na página {reading_progress.current_page} de {reading_progress.total_pages}.'
        )

        # Evitar duplicatas
        existing = cls.objects.filter(
            user=reading_progress.user,
            reading_progress=reading_progress,
            notification_type='deadline_warning',
            created_at__date=timezone.now().date()
        ).exists()

        if existing:
            return None

        notification = cls.objects.create(
            user=reading_progress.user,
            reading_progress=reading_progress,
            notification_type='deadline_warning',
            message=message
        )

        return notification

    @classmethod
    def create_deadline_passed(cls, reading_progress):
        """
        Cria notificação de prazo vencido.

        Args:
            reading_progress (ReadingProgress): Progresso de leitura

        Returns:
            ReadingNotification: Notificação criada
        """
        days_overdue = reading_progress.days_overdue

        message = (
            f'O prazo para terminar "{reading_progress.book.title}" venceu há {days_overdue} dia(s). '
            f'Você está na página {reading_progress.current_page} de {reading_progress.total_pages}. '
            f'Continue lendo ou atualize seu prazo!'
        )

        # Evitar duplicatas
        existing = cls.objects.filter(
            user=reading_progress.user,
            reading_progress=reading_progress,
            notification_type='deadline_passed',
            created_at__date=timezone.now().date()
        ).exists()

        if existing:
            return None

        notification = cls.objects.create(
            user=reading_progress.user,
            reading_progress=reading_progress,
            notification_type='deadline_passed',
            message=message
        )

        return notification

    @classmethod
    def create_book_abandoned(cls, reading_progress):
        """
        Cria notificação de livro abandonado.

        Args:
            reading_progress (ReadingProgress): Progresso de leitura

        Returns:
            ReadingNotification: Notificação criada
        """
        message = (
            f'O livro "{reading_progress.book.title}" foi movido para "Abandonados" '
            f'porque passou {reading_progress.days_overdue} dias do prazo sem progresso. '
            f'Você pode restaurá-lo a qualquer momento!'
        )

        notification = cls.objects.create(
            user=reading_progress.user,
            reading_progress=reading_progress,
            notification_type='book_abandoned',
            message=message
        )

        return notification

    @classmethod
    def get_unread_count(cls, user):
        """
        Retorna quantidade de notificações não lidas do usuário.

        Args:
            user (User): Usuário

        Returns:
            int: Quantidade de notificações não lidas
        """
        return cls.objects.filter(user=user, is_read=False).count()

    @classmethod
    def get_recent_unread(cls, user, limit=5):
        """
        Retorna notificações não lidas recentes do usuário.

        Args:
            user (User): Usuário
            limit (int): Quantidade máxima de notificações

        Returns:
            QuerySet: Notificações não lidas
        """
        return cls.objects.filter(
            user=user,
            is_read=False
        ).select_related('reading_progress', 'reading_progress__book')[:limit]

    @classmethod
    def mark_all_as_read(cls, user):
        """
        Marca todas as notificações do usuário como lidas.

        Args:
            user (User): Usuário

        Returns:
            int: Quantidade de notificações marcadas
        """
        return cls.objects.filter(
            user=user,
            is_read=False
        ).update(
            is_read=True,
            read_at=timezone.now()
        )

    @classmethod
    def delete_old_notifications(cls, days=30):
        """
        Deleta notificações lidas com mais de X dias.

        Args:
            days (int): Dias para considerar "antigas"

        Returns:
            int: Quantidade de notificações deletadas
        """
        from datetime import timedelta
        cutoff_date = timezone.now() - timedelta(days=days)

        count, _ = cls.objects.filter(
            is_read=True,
            read_at__lt=cutoff_date
        ).delete()

        return count