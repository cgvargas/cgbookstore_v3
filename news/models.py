from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.urls import reverse
from django_ckeditor_5.fields import CKEditor5Field

User = get_user_model()


class Category(models.Model):
    """Categorias para organizar o conteúdo (Notícias, Entrevistas, Eventos, etc.)"""
    name = models.CharField(max_length=100, unique=True, verbose_name="Nome")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="Slug")
    description = models.TextField(blank=True, verbose_name="Descrição")
    icon = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Ícone",
        help_text="Ex: fas fa-newspaper, fas fa-calendar, fas fa-microphone"
    )
    color = models.CharField(
        max_length=7,
        default="#3498db",
        verbose_name="Cor",
        help_text="Código hexadecimal da cor (ex: #3498db)"
    )
    order = models.PositiveIntegerField(default=0, verbose_name="Ordem de exibição")
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Tag(models.Model):
    """Tags para classificação adicional"""
    name = models.CharField(max_length=50, unique=True, verbose_name="Nome")
    slug = models.SlugField(max_length=50, unique=True, verbose_name="Slug")

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Article(models.Model):
    """Artigo principal - serve para Notícias, Entrevistas, Guias, etc."""

    CONTENT_TYPE_CHOICES = [
        ('news', '📰 Notícia'),
        ('interview', '🎤 Entrevista'),
        ('event', '📅 Evento'),
        ('announcement', '📢 Anúncio'),
        ('tip', '💡 Dica da Semana'),
        ('highlight', '⭐ Destaque'),
        ('schedule', '📆 Programação'),
        ('article', '📝 Artigo'),
        ('guide', '📖 Guia'),
        ('review', '⭐ Resenha'),
    ]

    PRIORITY_CHOICES = [
        (1, 'Baixa'),
        (2, 'Normal'),
        (3, 'Alta'),
        (4, 'Urgente'),
        (5, 'Destaque Principal'),
    ]

    # Informações Básicas
    title = models.CharField(max_length=200, verbose_name="Título")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="Slug")
    subtitle = models.CharField(max_length=300, blank=True, verbose_name="Subtítulo/Chamada")
    content_type = models.CharField(
        max_length=20,
        choices=CONTENT_TYPE_CHOICES,
        default='news',
        verbose_name="Tipo de Conteúdo"
    )

    # Conteúdo
    excerpt = models.TextField(
        max_length=500,
        verbose_name="Resumo",
        help_text="Texto curto para exibição em cards e listas (máx 500 caracteres)"
    )
    content = CKEditor5Field(verbose_name="Conteúdo Completo", config_name='extends')

    # Mídia
    featured_image = models.ImageField(
        upload_to='news/featured/',
        verbose_name="Imagem de Destaque",
        help_text="Imagem principal do artigo (recomendado: 1200x630px)"
    )
    image_caption = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Legenda da Imagem"
    )
    video_url = models.URLField(
        blank=True,
        verbose_name="URL do Vídeo",
        help_text="URL do YouTube ou Vimeo (opcional)"
    )

    # Relacionamentos
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='articles',
        verbose_name="Categoria"
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name='articles', verbose_name="Tags")
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='articles',
        verbose_name="Autor"
    )
    related_book = models.ForeignKey(
        'core.Book',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='articles',
        verbose_name="Livro Relacionado"
    )

    # Prioridade e Destaque
    priority = models.IntegerField(
        choices=PRIORITY_CHOICES,
        default=2,
        verbose_name="Prioridade"
    )
    is_featured = models.BooleanField(
        default=False,
        verbose_name="Destaque na Home",
        help_text="Aparecer em destaque na página principal"
    )
    is_breaking = models.BooleanField(
        default=False,
        verbose_name="Notícia de Última Hora",
        help_text="Badge especial de 'ÚLTIMA HORA'"
    )

    # Publicação
    is_published = models.BooleanField(default=False, verbose_name="Publicado")
    published_at = models.DateTimeField(null=True, blank=True, verbose_name="Data de Publicação")

    # Evento (campos opcionais para tipo 'event')
    event_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Data do Evento"
    )
    event_location = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Local do Evento"
    )
    event_link = models.URLField(
        blank=True,
        verbose_name="Link do Evento",
        help_text="Link para inscrição/mais informações"
    )

    # Campos de IA (para geração automática)
    ai_generated = models.BooleanField(
        default=False,
        verbose_name="Gerado por IA",
        help_text="Indica se o artigo foi gerado automaticamente por IA"
    )
    ai_model = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Modelo IA",
        help_text="Ex: gemini-pro, gemini-1.5-flash"
    )
    ai_processing_time = models.FloatField(
        null=True,
        blank=True,
        verbose_name="Tempo de Processamento (segundos)"
    )
    source_url = models.URLField(
        blank=True,
        verbose_name="URL da Fonte Original",
        help_text="Link para a notícia original"
    )
    source_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Nome da Fonte"
    )
    meta_description = models.CharField(
        max_length=160,
        blank=True,
        verbose_name="Meta Descrição (SEO)",
        help_text="Descrição para mecanismos de busca (máx 160 caracteres)"
    )

    # Estatísticas
    views_count = models.PositiveIntegerField(default=0, verbose_name="Visualizações")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Artigo"
        verbose_name_plural = "Artigos"
        ordering = ['-published_at', '-created_at']
        indexes = [
            models.Index(fields=['-published_at']),
            models.Index(fields=['content_type', '-published_at']),
            models.Index(fields=['is_featured', '-published_at']),
        ]

    def __str__(self):
        return f"{self.get_content_type_display()} - {self.title}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('news:article_detail', kwargs={'slug': self.slug})

    def increment_views(self):
        """Incrementa contador de visualizações"""
        self.views_count += 1
        self.save(update_fields=['views_count'])


class Quiz(models.Model):
    """Quizzes e Testes Interativos"""
    title = models.CharField(max_length=200, verbose_name="Título do Quiz")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="Slug")
    description = models.TextField(verbose_name="Descrição")
    featured_image = models.ImageField(
        upload_to='news/quizzes/',
        blank=True,
        verbose_name="Imagem de Destaque"
    )

    # Relacionamentos
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='quizzes',
        verbose_name="Categoria"
    )
    related_article = models.ForeignKey(
        Article,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='quizzes',
        verbose_name="Artigo Relacionado"
    )

    # Configurações
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    show_results_immediately = models.BooleanField(
        default=True,
        verbose_name="Mostrar Resultado Imediatamente",
        help_text="Mostrar resultado após cada resposta ou apenas no final"
    )

    # Estatísticas
    times_completed = models.PositiveIntegerField(default=0, verbose_name="Vezes Completado")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Quiz"
        verbose_name_plural = "Quizzes"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class QuizQuestion(models.Model):
    """Perguntas do Quiz"""
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name="Quiz"
    )
    question_text = models.CharField(max_length=300, verbose_name="Pergunta")
    question_image = models.ImageField(
        upload_to='news/quiz_questions/',
        blank=True,
        verbose_name="Imagem da Pergunta"
    )
    explanation = models.TextField(
        blank=True,
        verbose_name="Explicação",
        help_text="Explicação mostrada após responder (opcional)"
    )
    order = models.PositiveIntegerField(default=0, verbose_name="Ordem")

    class Meta:
        verbose_name = "Pergunta do Quiz"
        verbose_name_plural = "Perguntas do Quiz"
        ordering = ['quiz', 'order']

    def __str__(self):
        return f"{self.quiz.title} - Pergunta {self.order}"


class QuizOption(models.Model):
    """Opções de resposta para cada pergunta"""
    question = models.ForeignKey(
        QuizQuestion,
        on_delete=models.CASCADE,
        related_name='options',
        verbose_name="Pergunta"
    )
    option_text = models.CharField(max_length=200, verbose_name="Opção")
    is_correct = models.BooleanField(default=False, verbose_name="Resposta Correta")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordem")

    class Meta:
        verbose_name = "Opção de Resposta"
        verbose_name_plural = "Opções de Resposta"
        ordering = ['question', 'order']

    def __str__(self):
        return f"{self.question.question_text[:30]}... - {self.option_text}"


class QuizAttempt(models.Model):
    """Registro de tentativas de quiz com pontuação e XP ganho"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='quiz_attempts',
        verbose_name="Usuário"
    )
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='attempts',
        verbose_name="Quiz"
    )

    # Resultados
    score = models.PositiveIntegerField(verbose_name="Pontuação (acertos)")
    total_questions = models.PositiveIntegerField(verbose_name="Total de Perguntas")
    score_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Percentual de Acertos"
    )

    # Gamificação
    xp_earned = models.PositiveIntegerField(default=0, verbose_name="XP Ganho")
    leveled_up = models.BooleanField(default=False, verbose_name="Subiu de Nível")
    level_before = models.PositiveIntegerField(default=1, verbose_name="Nível Anterior")
    level_after = models.PositiveIntegerField(default=1, verbose_name="Nível Após")

    # Timestamp
    completed_at = models.DateTimeField(auto_now_add=True, verbose_name="Completado em")

    class Meta:
        verbose_name = "Tentativa de Quiz"
        verbose_name_plural = "Tentativas de Quiz"
        ordering = ['-completed_at']
        indexes = [
            models.Index(fields=['user', '-completed_at']),
            models.Index(fields=['quiz', '-completed_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.quiz.title} - {self.score_percentage}%"


class Newsletter(models.Model):
    """Inscrições na newsletter"""
    email = models.EmailField(unique=True, verbose_name="E-mail")
    name = models.CharField(max_length=100, blank=True, verbose_name="Nome")
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    subscribed_at = models.DateTimeField(auto_now_add=True, verbose_name="Inscrito em")
    unsubscribed_at = models.DateTimeField(null=True, blank=True, verbose_name="Desinscrito em")

    class Meta:
        verbose_name = "Inscrição Newsletter"
        verbose_name_plural = "Inscrições Newsletter"
        ordering = ['-subscribed_at']

    def __str__(self):
        return self.email


class NewsSource(models.Model):
    """Fontes RSS para agregação automática de notícias literárias"""
    
    SOURCE_TYPE_CHOICES = [
        ('rss', 'RSS Feed'),
        ('atom', 'Atom Feed'),
        ('json', 'JSON Feed'),
    ]
    
    # Informações básicas
    name = models.CharField(
        max_length=100,
        verbose_name="Nome da Fonte"
    )
    url = models.URLField(
        unique=True,
        verbose_name="URL do Feed"
    )
    source_type = models.CharField(
        max_length=10,
        choices=SOURCE_TYPE_CHOICES,
        default='rss',
        verbose_name="Tipo de Feed"
    )
    
    # Configurações
    is_active = models.BooleanField(
        default=True,
        verbose_name="Ativo"
    )
    priority = models.IntegerField(
        default=5,
        verbose_name="Prioridade",
        help_text="1-10, quanto maior mais importante"
    )
    
    # Filtros de palavras-chave
    keywords_include = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Palavras-chave (incluir)",
        help_text="Notícias devem conter pelo menos uma dessas palavras"
    )
    keywords_exclude = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Palavras-chave (excluir)",
        help_text="Notícias com essas palavras serão ignoradas"
    )
    
    # Estatísticas de fetch
    last_fetch_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Última Busca"
    )
    last_fetch_status = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Status da Última Busca"
    )
    total_items_fetched = models.IntegerField(
        default=0,
        verbose_name="Total de Itens Buscados"
    )
    total_items_published = models.IntegerField(
        default=0,
        verbose_name="Total de Itens Publicados"
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Atualizado em"
    )
    
    class Meta:
        verbose_name = "Fonte de Notícias"
        verbose_name_plural = "Fontes de Notícias"
        ordering = ['-priority', 'name']
    
    def __str__(self):
        status = "✓" if self.is_active else "✗"
        return f"{status} {self.name} (Prioridade: {self.priority})"
    
    @property
    def success_rate(self):
        """Calcula taxa de sucesso (publicados/buscados)"""
        if self.total_items_fetched == 0:
            return 0
        return (self.total_items_published / self.total_items_fetched) * 100


class NewsAgentConfig(models.Model):
    """
    Configuração centralizada do Agente de Notícias.
    Singleton - apenas uma instância ativa por vez.
    """
    
    MODE_CHOICES = [
        ('manual', '🔧 Manual'),
        ('automatic', '🤖 Automático'),
        ('paused', '⏸️ Pausado'),
    ]
    
    SCHEDULE_CHOICES = [
        ('hourly', 'A cada hora'),
        ('every_6h', 'A cada 6 horas'),
        ('every_12h', 'A cada 12 horas'),
        ('daily', 'Diário'),
        ('twice_daily', '2x ao dia'),
        ('weekly', 'Semanal'),
    ]
    
    # Configurações de Modo
    name = models.CharField(
        max_length=100,
        default="Configuração Principal",
        verbose_name="Nome da Configuração"
    )
    mode = models.CharField(
        max_length=20,
        choices=MODE_CHOICES,
        default='manual',
        verbose_name="Modo de Operação"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Configuração Ativa",
        help_text="Apenas uma configuração pode estar ativa"
    )
    
    # Configurações de Pesquisa
    articles_per_run = models.PositiveIntegerField(
        default=5,
        verbose_name="Artigos por Execução",
        help_text="Quantos artigos gerar por vez"
    )
    hours_lookback = models.PositiveIntegerField(
        default=24,
        verbose_name="Período de Busca (horas)",
        help_text="Buscar notícias das últimas X horas"
    )
    include_images = models.BooleanField(
        default=True,
        verbose_name="Incluir Imagens",
        help_text="Buscar imagens do Unsplash para os artigos"
    )
    
    # Agendamento
    schedule = models.CharField(
        max_length=20,
        choices=SCHEDULE_CHOICES,
        default='daily',
        verbose_name="Frequência"
    )
    schedule_hour = models.PositiveIntegerField(
        default=6,
        verbose_name="Horário (hora)",
        help_text="Hora do dia para execução automática (0-23)"
    )
    schedule_minute = models.PositiveIntegerField(
        default=0,
        verbose_name="Horário (minuto)",
        help_text="Minuto da hora (0-59)"
    )
    
    # Temas Específicos
    specific_themes = models.TextField(
        blank=True,
        verbose_name="Temas Específicos",
        help_text="Um tema por linha. Ex: Stephen King, Tolkien, Manga"
    )
    category_filter = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Filtrar por Categoria",
        help_text="Gerar artigos apenas para esta categoria"
    )
    
    # Estatísticas
    last_run = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Última Execução"
    )
    last_run_articles = models.PositiveIntegerField(
        default=0,
        verbose_name="Artigos na Última Execução"
    )
    total_articles_generated = models.PositiveIntegerField(
        default=0,
        verbose_name="Total de Artigos Gerados"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "⚙️ Configuração do Agente"
        verbose_name_plural = "⚙️ Configurações do Agente"
    
    def __str__(self):
        mode_icon = dict(self.MODE_CHOICES).get(self.mode, '')
        return f"{self.name} - {mode_icon}"
    
    def save(self, *args, **kwargs):
        # Garantir apenas uma configuração ativa
        if self.is_active:
            NewsAgentConfig.objects.exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)
    
    @classmethod
    def get_active(cls):
        """Retorna a configuração ativa ou cria uma padrão."""
        config, created = cls.objects.get_or_create(
            is_active=True,
            defaults={'name': 'Configuração Principal'}
        )
        return config
    
    def get_themes_list(self):
        """Retorna lista de temas específicos."""
        if not self.specific_themes:
            return []
        return [t.strip() for t in self.specific_themes.split('\n') if t.strip()]
