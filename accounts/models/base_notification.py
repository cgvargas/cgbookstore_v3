"""
Modelo Base Abstrato para Sistema de Notificações
CGBookStore v3

Este modelo serve como base para TODOS os tipos de notificação do sistema.
Permite extensibilidade e integração fácil de novos módulos.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class BaseNotification(models.Model):
    """
    Modelo abstrato base para todas as notificações do sistema.

    Qualquer novo tipo de notificação deve herdar desta classe.
    Isso garante consistência e facilita queries agregadas.

    Exemplo de uso:
        class CommentNotification(BaseNotification):
            comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
            NOTIFICATION_TYPES = [('reply', 'Resposta')]
    """

    # ========== CAMPOS PRINCIPAIS ==========

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='%(class)s_notifications',  # Evita conflito de related_name
        verbose_name='Usuário'
    )

    notification_type = models.CharField(
        max_length=50,
        verbose_name='Tipo de Notificação',
        db_index=True
    )

    message = models.TextField(
        verbose_name='Mensagem',
        help_text='Conteúdo da notificação'
    )

    # ========== CONTROLE DE LEITURA ==========

    is_read = models.BooleanField(
        default=False,
        verbose_name='Lida',
        db_index=True
    )

    read_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Lida em'
    )

    # ========== METADADOS ==========

    priority = models.IntegerField(
        default=1,
        choices=[(1, 'Baixa'), (2, 'Média'), (3, 'Alta')],
        verbose_name='Prioridade',
        db_index=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criada em',
        db_index=True
    )

    # Campos opcionais para link de ação
    action_url = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name='URL de Ação',
        help_text='Link para onde a notificação direciona'
    )

    action_text = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Texto do Botão',
        help_text='Texto do botão de ação (ex: "Ver Livro")'
    )

    # ========== CAMPOS PARA EXTENSÃO ==========

    extra_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Dados Extras',
        help_text='Dados adicionais específicos do tipo de notificação'
    )

    class Meta:
        abstract = True  # Modelo abstrato - não cria tabela própria
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read', '-created_at']),
            models.Index(fields=['user', 'notification_type']),
        ]

    def __str__(self):
        status = "✓" if self.is_read else "●"
        return f'[{status}] {self.user.username} - {self.notification_type}'

    # ========== PROPRIEDADES CALCULADAS ==========

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

    @property
    def priority_name(self):
        """Retorna o nome da prioridade."""
        priority_names = {
            1: 'Baixa',
            2: 'Média',
            3: 'Alta'
        }
        return priority_names.get(self.priority, 'Normal')

    # ========== MÉTODOS ==========

    def mark_as_read(self):
        """
        Marca a notificação como lida.

        Returns:
            bool: True se foi marcada, False se já estava lida
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
            bool: True se foi desmarcada, False se já estava não lida
        """
        if not self.is_read:
            return False

        self.is_read = False
        self.read_at = None
        self.save()
        return True

    # ========== MÉTODOS DE CLASSE ==========

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


class NotificationRegistry:
    """
    Registro centralizado de todos os tipos de notificação.

    Permite que o sistema descubra dinamicamente todos os tipos
    disponíveis e suas configurações.

    Uso:
        NotificationRegistry.register('reading', ReadingNotification)
        types = NotificationRegistry.get_all_types()
    """

    _registry = {}

    @classmethod
    def register(cls, category, notification_class, config=None):
        """
        Registra um novo tipo de notificação.

        Args:
            category (str): Categoria (ex: 'reading', 'comment', 'system')
            notification_class (class): Classe do modelo de notificação
            config (dict): Configurações opcionais (ícones, cores, etc)
        """
        cls._registry[category] = {
            'class': notification_class,
            'config': config or {}
        }

    @classmethod
    def get(cls, category):
        """Obtém informações de um tipo registrado."""
        return cls._registry.get(category)

    @classmethod
    def get_all_types(cls):
        """Retorna todos os tipos registrados."""
        return cls._registry.keys()

    @classmethod
    def get_all_notifications(cls, user, unread_only=False):
        """
        Busca notificações de TODOS os tipos registrados.

        Args:
            user (User): Usuário
            unread_only (bool): Se True, retorna apenas não lidas

        Returns:
            list: Lista de notificações de todos os tipos, ordenadas
        """
        all_notifications = []

        for category, info in cls._registry.items():
            notification_class = info['class']
            queryset = notification_class.objects.filter(user=user)

            if unread_only:
                queryset = queryset.filter(is_read=False)

            all_notifications.extend(queryset)

        # Ordenar por data de criação (mais recente primeiro)
        all_notifications.sort(key=lambda x: x.created_at, reverse=True)

        return all_notifications