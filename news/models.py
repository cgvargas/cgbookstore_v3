from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.urls import reverse
from ckeditor.fields import RichTextField

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
    content = RichTextField(verbose_name="Conteúdo Completo")

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
