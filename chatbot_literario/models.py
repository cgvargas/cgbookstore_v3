"""
Models para o Chatbot Literário do CG.BookStore.

Gerencia sessões de conversa, mensagens e contexto das conversas com a IA.
Inclui sistema de Knowledge Base para aprendizado contínuo através de correções.
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
from core.models import Book, Author


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

    # === CAMPOS PARA KNOWLEDGE BASE ===

    # Metadados RAG
    rag_intent_detected = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Intent RAG Detectado',
        help_text="Intent RAG detectado (author_query, book_search, etc)"
    )

    rag_data_used = models.JSONField(
        null=True,
        blank=True,
        verbose_name='Dados RAG Usados',
        help_text="Dados que o RAG injetou no prompt"
    )

    knowledge_base_used = models.ForeignKey(
        'ChatbotKnowledge',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='usage_instances',
        verbose_name='Knowledge Base Usado',
        help_text="Conhecimento da base que foi usado (se aplicável)"
    )

    # Correções
    has_correction = models.BooleanField(
        default=False,
        verbose_name='Tem Correção',
        help_text="Se esta mensagem foi corrigida por um admin"
    )

    corrected_content = models.TextField(
        blank=True,
        verbose_name='Conteúdo Corrigido',
        help_text="Conteúdo corrigido pelo admin"
    )

    corrected_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='message_corrections',
        verbose_name='Corrigido Por'
    )

    corrected_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Corrigido em'
    )

    # Feedback do usuário
    user_feedback = models.CharField(
        max_length=20,
        blank=True,
        choices=[
            ('helpful', 'Útil'),
            ('not_helpful', 'Não Útil'),
            ('incorrect', 'Incorreto'),
        ],
        verbose_name='Feedback do Usuário',
        help_text="Feedback do usuário sobre esta resposta"
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


# ==============================================================================
# KNOWLEDGE BASE - Sistema de Aprendizado Contínuo
# ==============================================================================


class ChatbotKnowledge(models.Model):
    """
    Base de conhecimento aprendida através de correções de admins.

    Este modelo permite que o chatbot aprenda com correções e melhore
    continuamente suas respostas. Quando um admin corrige uma resposta,
    essa correção é armazenada e usada automaticamente para perguntas
    similares no futuro.

    Workflow:
    1. Usuário faz pergunta → Chatbot responde incorretamente
    2. Admin corrige resposta em ChatMessage
    3. Sistema cria entrada em ChatbotKnowledge
    4. Próxima pergunta similar → Usa conhecimento aprendido
    """

    KNOWLEDGE_TYPES = [
        ('author_query', 'Pergunta sobre Autor'),
        ('book_info', 'Informação sobre Livro'),
        ('recommendation', 'Recomendação'),
        ('series_info', 'Informação sobre Série'),
        ('category_search', 'Busca por Categoria'),
        ('general', 'Conhecimento Geral'),
    ]

    # Tipo de conhecimento
    knowledge_type = models.CharField(
        max_length=50,
        choices=KNOWLEDGE_TYPES,
        default='general',
        verbose_name='Tipo de Conhecimento'
    )

    # Pergunta original
    original_question = models.TextField(
        verbose_name='Pergunta Original',
        help_text="Pergunta original do usuário que gerou a correção"
    )

    # Resposta incorreta (para referência)
    incorrect_response = models.TextField(
        blank=True,
        verbose_name='Resposta Incorreta',
        help_text="Resposta incorreta original da IA (para referência)"
    )

    # Resposta correta
    correct_response = models.TextField(
        verbose_name='Resposta Correta',
        help_text="Resposta correta fornecida/aprovada pelo admin"
    )

    # Relacionamentos com livros/autores
    related_book = models.ForeignKey(
        Book,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='knowledge_entries',
        verbose_name='Livro Relacionado',
        help_text="Livro relacionado a esta correção"
    )

    related_author = models.ForeignKey(
        Author,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='knowledge_entries',
        verbose_name='Autor Relacionado',
        help_text="Autor relacionado a esta correção"
    )

    # Palavras-chave para matching inteligente
    keywords = models.JSONField(
        default=list,
        verbose_name='Palavras-chave',
        help_text="Lista de palavras-chave extraídas automaticamente da pergunta"
    )

    # Metadados
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='knowledge_corrections',
        verbose_name='Criado Por',
        help_text="Admin que criou esta correção"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criado em'
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Atualizado em'
    )

    # Estatísticas de uso
    times_used = models.IntegerField(
        default=0,
        verbose_name='Vezes Usado',
        help_text="Quantas vezes este conhecimento foi utilizado em conversas"
    )

    last_used_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Último Uso',
        help_text="Última vez que este conhecimento foi usado"
    )

    # Controle de qualidade
    is_active = models.BooleanField(
        default=True,
        verbose_name='Ativo',
        help_text="Se este conhecimento está ativo e deve ser usado pelo chatbot"
    )

    confidence_score = models.FloatField(
        default=1.0,
        verbose_name='Confiança',
        help_text="Confiança nesta correção (0.0 a 1.0). Quanto maior, mais prioritário"
    )

    # Notas do admin
    admin_notes = models.TextField(
        blank=True,
        verbose_name='Notas do Admin',
        help_text="Notas internas do admin sobre esta correção"
    )

    class Meta:
        verbose_name = "Conhecimento do Chatbot"
        verbose_name_plural = "Base de Conhecimento do Chatbot"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['knowledge_type', 'is_active']),
            models.Index(fields=['related_book']),
            models.Index(fields=['related_author']),
            models.Index(fields=['is_active', 'confidence_score']),
        ]

    def __str__(self):
        return f"{self.get_knowledge_type_display()} - {self.original_question[:50]}"

    def increment_usage(self):
        """Incrementa contador de uso e atualiza timestamp."""
        self.times_used += 1
        self.last_used_at = timezone.now()
        self.save(update_fields=['times_used', 'last_used_at'])
