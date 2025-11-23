"""
Models para o Chatbot Literário do CG.BookStore.

Gerencia sessões de conversa, mensagens e contexto das conversas com a IA.
"""
from django.db import models
from django.conf import settings
from django.utils import timezone


class ChatSession(models.Model):
    """
    Representa uma sessão de conversa de um usuário com o chatbot.

    Uma sessão agrupa múltiplas mensagens de uma conversa contínua.
    Cada usuário pode ter múltiplas sessões ao longo do tempo.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='chat_sessions',
        verbose_name='Usuário'
    )
    title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Título da Conversa',
        help_text='Título gerado automaticamente baseado na primeira mensagem'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criado em'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Atualizado em'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Sessão Ativa',
        help_text='Se False, a sessão foi encerrada pelo usuário'
    )

    class Meta:
        verbose_name = 'Sessão de Chat'
        verbose_name_plural = 'Sessões de Chat'
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['user', '-updated_at']),
            models.Index(fields=['user', 'is_active']),
        ]

    def __str__(self):
        return f"Chat de {self.user.username} - {self.title[:50] or 'Sem título'}"

    def get_messages_count(self):
        """Retorna o número de mensagens na sessão."""
        return self.messages.count()

    def get_last_message_time(self):
        """Retorna o timestamp da última mensagem."""
        last_msg = self.messages.order_by('-created_at').first()
        return last_msg.created_at if last_msg else self.created_at

    def generate_title(self):
        """Gera título baseado na primeira mensagem do usuário."""
        first_user_msg = self.messages.filter(role='user').first()
        if first_user_msg:
            # Pega até 50 caracteres da primeira mensagem
            self.title = first_user_msg.content[:50]
            if len(first_user_msg.content) > 50:
                self.title += "..."
            self.save(update_fields=['title'])


class ChatMessage(models.Model):
    """
    Representa uma mensagem individual em uma sessão de chat.

    Pode ser do usuário ou do assistente (chatbot).
    """
    ROLE_CHOICES = [
        ('user', 'Usuário'),
        ('assistant', 'Assistente'),
    ]

    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name='Sessão'
    )
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        verbose_name='Papel',
        help_text='Quem enviou a mensagem'
    )
    content = models.TextField(
        verbose_name='Conteúdo',
        help_text='Texto da mensagem'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Enviado em'
    )
    tokens_used = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='Tokens Utilizados',
        help_text='Número de tokens gastos (apenas mensagens do assistente)'
    )
    response_time = models.FloatField(
        null=True,
        blank=True,
        verbose_name='Tempo de Resposta (segundos)',
        help_text='Tempo que a IA levou para responder (apenas mensagens do assistente)'
    )

    class Meta:
        verbose_name = 'Mensagem de Chat'
        verbose_name_plural = 'Mensagens de Chat'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['session', 'created_at']),
            models.Index(fields=['role']),
        ]

    def __str__(self):
        preview = self.content[:50]
        if len(self.content) > 50:
            preview += "..."
        return f"{self.get_role_display()}: {preview}"

    def is_from_user(self):
        """Verifica se a mensagem é do usuário."""
        return self.role == 'user'

    def is_from_assistant(self):
        """Verifica se a mensagem é do assistente."""
        return self.role == 'assistant'


class ConversationContext(models.Model):
    """
    Armazena informações de contexto sobre as preferências do usuário
    descobertas ao longo das conversas.

    Isso ajuda o chatbot a fornecer respostas cada vez mais personalizadas.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='conversation_context',
        verbose_name='Usuário'
    )
    favorite_genres = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Gêneros Favoritos',
        help_text='Lista de gêneros literários mencionados pelo usuário'
    )
    favorite_authors = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Autores Favoritos',
        help_text='Lista de autores mencionados pelo usuário'
    )
    reading_preferences = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Preferências de Leitura',
        help_text='Outras preferências (e.g., tamanho de livro, complexidade, etc.)'
    )
    interests = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Interesses',
        help_text='Tópicos de interesse do usuário (cinema, animes, games, etc.)'
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
        verbose_name = 'Contexto de Conversa'
        verbose_name_plural = 'Contextos de Conversa'

    def __str__(self):
        return f"Contexto de {self.user.username}"

    def add_genre(self, genre: str):
        """Adiciona um gênero aos favoritos (se ainda não existir)."""
        if genre and genre not in self.favorite_genres:
            self.favorite_genres.append(genre)
            self.save(update_fields=['favorite_genres', 'updated_at'])

    def add_author(self, author: str):
        """Adiciona um autor aos favoritos (se ainda não existir)."""
        if author and author not in self.favorite_authors:
            self.favorite_authors.append(author)
            self.save(update_fields=['favorite_authors', 'updated_at'])

    def add_interest(self, interest: str):
        """Adiciona um interesse (se ainda não existir)."""
        if interest and interest not in self.interests:
            self.interests.append(interest)
            self.save(update_fields=['interests', 'updated_at'])

    def set_preference(self, key: str, value):
        """Define uma preferência de leitura."""
        self.reading_preferences[key] = value
        self.save(update_fields=['reading_preferences', 'updated_at'])
