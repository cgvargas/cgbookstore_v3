"""
Modelos de Notificação: Reading e System
CGBookStore v3

ReadingNotification: Notificações relacionadas a progresso de leitura
SystemNotification: Notificações do sistema (upgrades, lançamentos, eventos)
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from .base_notification import BaseNotification, NotificationRegistry


class ReadingNotification(BaseNotification):
    """
    Notificações relacionadas a prazos de leitura e progresso.

    Tipos de notificação:
    - deadline_set: Prazo definido
    - deadline_warning: Prazo próximo (5 dias)
    - deadline_passed: Prazo vencido
    - book_abandoned: Livro abandonado automaticamente
    - book_completed: Livro finalizado
    """

    NOTIFICATION_TYPES = [
        ('deadline_set', 'Prazo Definido'),
        ('deadline_warning', 'Prazo Próximo'),
        ('deadline_passed', 'Prazo Vencido'),
        ('book_abandoned', 'Livro Abandonado'),
        ('book_completed', 'Livro Concluído'),
    ]

    PRIORITY_LEVELS = {
        'deadline_set': 1,      # Baixa
        'deadline_warning': 2,  # Média
        'deadline_passed': 3,   # Alta
        'book_abandoned': 1,    # Baixa
        'book_completed': 1,    # Baixa (informativa)
    }

    ICONS = {
        'deadline_set': 'fas fa-calendar-check text-success',
        'deadline_warning': 'fas fa-clock text-warning',
        'deadline_passed': 'fas fa-exclamation-triangle text-danger',
        'book_abandoned': 'fas fa-bookmark text-muted',
        'book_completed': 'fas fa-trophy text-warning',
    }

    # ========== CAMPOS ESPECÍFICOS ==========

    reading_progress = models.ForeignKey(
        'ReadingProgress',
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='Progresso de Leitura'
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
    def icon_class(self):
        """Retorna a classe CSS do ícone FontAwesome."""
        return self.ICONS.get(self.notification_type, 'fas fa-bell')

    def get_notification_type_display(self):
        """Retorna o nome amigável do tipo de notificação."""
        for code, display in self.NOTIFICATION_TYPES:
            if code == self.notification_type:
                return display
        return self.notification_type

    # ========== MÉTODOS DE CRIAÇÃO ==========

    @classmethod
    def create_deadline_warning(cls, reading_progress):
        """
        Cria notificação de prazo próximo.

        Args:
            reading_progress (ReadingProgress): Progresso de leitura

        Returns:
            ReadingNotification: Notificação criada ou None se já existe
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
            message=message,
            priority=cls.PRIORITY_LEVELS['deadline_warning'],
            action_url=reading_progress.book.get_absolute_url(),
            action_text='Continuar Lendo'
        )

        return notification

    @classmethod
    def create_deadline_passed(cls, reading_progress):
        """
        Cria notificação de prazo vencido.

        Args:
            reading_progress (ReadingProgress): Progresso de leitura

        Returns:
            ReadingNotification: Notificação criada ou None se já existe
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
            message=message,
            priority=cls.PRIORITY_LEVELS['deadline_passed'],
            action_url=reading_progress.book.get_absolute_url(),
            action_text='Atualizar Prazo'
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
            message=message,
            priority=cls.PRIORITY_LEVELS['book_abandoned'],
            action_url='/library/?shelf=abandoned',
            action_text='Ver Abandonados'
        )

        return notification

    @classmethod
    def create_book_completed(cls, reading_progress):
        """
        Cria notificação de livro concluído.

        Args:
            reading_progress (ReadingProgress): Progresso de leitura

        Returns:
            ReadingNotification: Notificação criada
        """
        message = (
            f'🎉 Parabéns! Você terminou de ler "{reading_progress.book.title}"! '
            f'Que tal deixar uma avaliação?'
        )

        notification = cls.objects.create(
            user=reading_progress.user,
            reading_progress=reading_progress,
            notification_type='book_completed',
            message=message,
            priority=cls.PRIORITY_LEVELS['book_completed'],
            action_url=reading_progress.book.get_absolute_url() + '#reviews',
            action_text='Avaliar Livro'
        )

        return notification

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


class SystemNotification(BaseNotification):
    """
    Notificações do sistema (administrativas e informativas).

    Tipos de notificação:
    - system_upgrade: Atualização do sistema
    - book_launch: Novo livro disponível
    - literary_event: Evento literário
    - promotion: Promoção especial
    - maintenance: Manutenção programada
    """

    NOTIFICATION_TYPES = [
        ('system_upgrade', 'Atualização do Sistema'),
        ('book_launch', 'Novo Livro Disponível'),
        ('literary_event', 'Evento Literário'),
        ('promotion', 'Promoção Especial'),
        ('maintenance', 'Manutenção Programada'),
    ]

    PRIORITY_LEVELS = {
        'system_upgrade': 2,      # Média
        'book_launch': 1,         # Baixa
        'literary_event': 2,      # Média
        'promotion': 1,           # Baixa
        'maintenance': 3,         # Alta
    }

    ICONS = {
        'system_upgrade': 'fas fa-sync text-info',
        'book_launch': 'fas fa-book-open text-success',
        'literary_event': 'fas fa-calendar-alt text-primary',
        'promotion': 'fas fa-tag text-warning',
        'maintenance': 'fas fa-tools text-danger',
    }

    class Meta:
        verbose_name = 'Notificação do Sistema'
        verbose_name_plural = 'Notificações do Sistema'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['user', 'notification_type']),
        ]

    def __str__(self):
        status = "✓" if self.is_read else "●"
        return f'[{status}] {self.user.username} - {self.get_notification_type_display()}'

    # ========== PROPRIEDADES ==========

    @property
    def book_title(self):
        """Retorna None para notificações de sistema (compatibilidade)."""
        return None

    @property
    def icon_class(self):
        """Retorna a classe CSS do ícone FontAwesome."""
        return self.ICONS.get(self.notification_type, 'fas fa-bell')

    def get_notification_type_display(self):
        """Retorna o nome amigável do tipo de notificação."""
        for code, display in self.NOTIFICATION_TYPES:
            if code == self.notification_type:
                return display
        return self.notification_type

    # ========== MÉTODOS DE CRIAÇÃO ==========

    @classmethod
    def create_system_upgrade(cls, message, action_url=None):
        """
        Cria notificação de atualização do sistema para TODOS os usuários.

        Args:
            message (str): Mensagem da notificação
            action_url (str): URL de ação (opcional)

        Returns:
            int: Quantidade de notificações criadas
        """
        users = User.objects.filter(is_active=True)
        notifications = []

        for user in users:
            notifications.append(
                cls(
                    user=user,
                    notification_type='system_upgrade',
                    message=message,
                    priority=cls.PRIORITY_LEVELS['system_upgrade'],
                    action_url=action_url or '/about/',
                    action_text='Ver Novidades'
                )
            )

        cls.objects.bulk_create(notifications)
        return len(notifications)

    @classmethod
    def create_book_launch(cls, book, users=None):
        """
        Cria notificação de lançamento de livro.

        Args:
            book (Book): Livro lançado
            users (QuerySet): Usuários a notificar (None = todos)

        Returns:
            int: Quantidade de notificações criadas
        """
        if users is None:
            users = User.objects.filter(is_active=True)

        message = f'📚 Novo livro disponível: "{book.title}" de {book.author}. Confira agora!'

        notifications = []
        for user in users:
            notifications.append(
                cls(
                    user=user,
                    notification_type='book_launch',
                    message=message,
                    priority=cls.PRIORITY_LEVELS['book_launch'],
                    action_url=book.get_absolute_url(),
                    action_text='Ver Livro',
                    extra_data={'book_id': book.id}
                )
            )

        cls.objects.bulk_create(notifications)
        return len(notifications)

    @classmethod
    def create_literary_event(cls, event_name, event_date, event_url, users=None):
        """
        Cria notificação de evento literário.

        Args:
            event_name (str): Nome do evento
            event_date (date): Data do evento
            event_url (str): URL do evento
            users (QuerySet): Usuários a notificar (None = todos)

        Returns:
            int: Quantidade de notificações criadas
        """
        if users is None:
            users = User.objects.filter(is_active=True)

        message = (
            f'📅 Evento literário: {event_name} '
            f'em {event_date.strftime("%d/%m/%Y")}. '
            f'Não perca!'
        )

        notifications = []
        for user in users:
            notifications.append(
                cls(
                    user=user,
                    notification_type='literary_event',
                    message=message,
                    priority=cls.PRIORITY_LEVELS['literary_event'],
                    action_url=event_url,
                    action_text='Ver Evento',
                    extra_data={
                        'event_name': event_name,
                        'event_date': event_date.isoformat()
                    }
                )
            )

        cls.objects.bulk_create(notifications)
        return len(notifications)


# ========== REGISTRO DE TIPOS ==========

# Registrar tipos de notificação no sistema
NotificationRegistry.register('reading', ReadingNotification, {
    'category_name': 'Leitura',
    'icon': 'fas fa-book',
    'color': '#4CAF50'
})

NotificationRegistry.register('system', SystemNotification, {
    'category_name': 'Sistema',
    'icon': 'fas fa-cog',
    'color': '#2196F3'
})