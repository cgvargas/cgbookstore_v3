from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class ChatConversation(models.Model):
    """
    Armazena o histórico de conversas do chatbot literário.
    Cada mensagem (usuário ou bot) é salva separadamente.
    """
    ROLE_CHOICES = [
        ('user', 'Usuário'),
        ('assistant', 'Assistente'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='chat_messages',
        verbose_name='Usuário'
    )
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        verbose_name='Papel',
        help_text='Quem enviou a mensagem: usuário ou assistente'
    )
    message = models.TextField(
        verbose_name='Mensagem',
        help_text='Conteúdo da mensagem'
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name='Criado em',
        db_index=True
    )
    session_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='ID da Sessão',
        help_text='Identifica sessões de conversa separadas',
        db_index=True
    )

    class Meta:
        verbose_name = 'Conversa do Chatbot'
        verbose_name_plural = 'Conversas do Chatbot'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['session_id', '-created_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()} - {self.created_at.strftime('%d/%m/%Y %H:%M')}"

    @classmethod
    def get_user_history(cls, user, limit=20, session_id=None):
        """
        Retorna o histórico de conversas de um usuário.

        Args:
            user: Usuário
            limit: Número máximo de mensagens a retornar
            session_id: ID da sessão (opcional, para filtrar por sessão)

        Returns:
            QuerySet de mensagens ordenadas por data
        """
        queryset = cls.objects.filter(user=user)

        if session_id:
            queryset = queryset.filter(session_id=session_id)

        return queryset.order_by('created_at')[:limit]

    @classmethod
    def clear_user_history(cls, user, session_id=None):
        """
        Limpa o histórico de conversas de um usuário.

        Args:
            user: Usuário
            session_id: ID da sessão (opcional, para limpar apenas uma sessão)

        Returns:
            Número de mensagens deletadas
        """
        queryset = cls.objects.filter(user=user)

        if session_id:
            queryset = queryset.filter(session_id=session_id)

        count = queryset.count()
        queryset.delete()
        return count
