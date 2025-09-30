"""
Model Video - Representa vídeos (YouTube, entrevistas, book trailers, resenhas)
"""
from django.db import models
from django.utils.text import slugify


class Video(models.Model):
    """
    Model para vídeos relacionados a livros e literatura.
    Exemplos: book trailers, entrevistas com autores, resenhas em vídeo.
    """

    PLATFORM_CHOICES = [
        ('youtube', 'YouTube'),
        ('vimeo', 'Vimeo'),
        ('instagram', 'Instagram'),
        ('tiktok', 'TikTok'),
    ]

    VIDEO_TYPE_CHOICES = [
        ('trailer', 'Book Trailer'),
        ('interview', 'Entrevista'),
        ('review', 'Resenha'),
        ('tutorial', 'Tutorial'),
        ('discussion', 'Discussão'),
        ('other', 'Outro'),
    ]

    # Campos básicos
    title = models.CharField(
        max_length=200,
        verbose_name="Título",
        help_text="Título do vídeo"
    )

    slug = models.SlugField(
        unique=True,
        blank=True,
        verbose_name="Slug",
        help_text="Gerado automaticamente a partir do título"
    )

    description = models.TextField(
        blank=True,
        verbose_name="Descrição",
        help_text="Descrição do conteúdo do vídeo"
    )

    # Plataforma e URL
    platform = models.CharField(
        max_length=20,
        choices=PLATFORM_CHOICES,
        default='youtube',
        verbose_name="Plataforma"
    )

    video_url = models.URLField(
        verbose_name="URL do Vídeo",
        help_text="URL completa do vídeo (ex: https://www.youtube.com/watch?v=...)"
    )

    embed_code = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Código de Embed",
        help_text="ID do vídeo para embed (ex: dQw4w9WgXcQ para YouTube)"
    )

    # Tipo e categorização
    video_type = models.CharField(
        max_length=20,
        choices=VIDEO_TYPE_CHOICES,
        default='other',
        verbose_name="Tipo de Vídeo"
    )

    # Thumbnail
    thumbnail_url = models.URLField(
        blank=True,
        verbose_name="URL da Thumbnail",
        help_text="URL da imagem de preview (gerada automaticamente para YouTube)"
    )

    # Relacionamentos
    related_book = models.ForeignKey(
        'core.Book',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='videos',
        verbose_name="Livro Relacionado"
    )

    related_author = models.ForeignKey(
        'core.Author',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='videos',
        verbose_name="Autor Relacionado"
    )

    # Metadados
    duration = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Duração",
        help_text="Duração do vídeo (ex: 10:25)"
    )

    views_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Visualizações"
    )

    published_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data de Publicação"
    )

    # Controle
    featured = models.BooleanField(
        default=False,
        verbose_name="Destacado",
        help_text="Vídeo será exibido em seções especiais"
    )

    active = models.BooleanField(
        default=True,
        verbose_name="Ativo"
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
        verbose_name = "Vídeo"
        verbose_name_plural = "Vídeos"
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        """Gera slug automaticamente e extrai embed_code do YouTube"""
        if not self.slug:
            self.slug = slugify(self.title)

        # Extrair código de embed do YouTube
        if self.platform == 'youtube' and not self.embed_code and self.video_url:
            if 'youtube.com/watch?v=' in self.video_url:
                self.embed_code = self.video_url.split('watch?v=')[1].split('&')[0]
            elif 'youtu.be/' in self.video_url:
                self.embed_code = self.video_url.split('youtu.be/')[1].split('?')[0]

            # Gerar thumbnail automaticamente para YouTube
            if self.embed_code and not self.thumbnail_url:
                self.thumbnail_url = f"https://img.youtube.com/vi/{self.embed_code}/maxresdefault.jpg"

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_embed_url(self):
        """Retorna URL para embed baseado na plataforma"""
        if self.platform == 'youtube' and self.embed_code:
            return f"https://www.youtube.com/embed/{self.embed_code}"
        elif self.platform == 'vimeo' and self.embed_code:
            return f"https://player.vimeo.com/video/{self.embed_code}"
        return None