"""
Model Video - Representa vídeos (YouTube, entrevistas, book trailers, resenhas)
"""
from django.db import models
from django.utils.text import slugify
from django.core.validators import FileExtensionValidator


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
        ('upload', 'Upload de Arquivo'),
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
        blank=True,
        verbose_name="URL do Vídeo",
        help_text="URL completa do vídeo (para YouTube, Vimeo, Instagram, TikTok)"
    )

    video_file = models.FileField(
        upload_to='videos/uploads/',
        blank=True,
        null=True,
        verbose_name="Arquivo de Vídeo",
        help_text="Upload de arquivo MP4 ou WebM (máx. 100MB recomendado)",
        validators=[
            FileExtensionValidator(allowed_extensions=['mp4', 'webm', 'mov', 'avi'])
        ]
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
    thumbnail_image = models.ImageField(
        upload_to='videos/thumbnails/',
        blank=True,
        null=True,
        verbose_name="Thumbnail Customizada",
        help_text="Upload de thumbnail para Instagram, Vimeo, TikTok, etc."
    )

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
        if self.platform == 'youtube' and self.video_url:
            # Limpar embed_code e thumbnail_url para reprocessar
            video_id = None

            # Tentar extrair ID de diferentes formatos de URL
            if 'youtube.com/watch?v=' in self.video_url:
                video_id = self.video_url.split('watch?v=')[1].split('&')[0]
            elif 'youtu.be/' in self.video_url:
                video_id = self.video_url.split('youtu.be/')[1].split('?')[0]
            elif 'youtube.com/shorts/' in self.video_url:
                # YouTube Shorts
                video_id = self.video_url.split('shorts/')[1].split('?')[0]

            # Salvar embed_code
            if video_id:
                self.embed_code = video_id
                # Gerar thumbnail automaticamente para YouTube
                self.thumbnail_url = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_thumbnail(self):
        """
        Retorna a URL da thumbnail do vídeo.
        Prioriza: 1) thumbnail_image (upload), 2) thumbnail_url (YouTube)
        """
        if self.thumbnail_image:
            return self.thumbnail_image.url
        elif self.thumbnail_url:
            return self.thumbnail_url
        return None

    def get_embed_url(self):
        """Retorna URL para embed baseado na plataforma"""
        if self.platform == 'youtube' and self.embed_code:
            return f"https://www.youtube.com/embed/{self.embed_code}"
        elif self.platform == 'vimeo' and self.embed_code:
            return f"https://player.vimeo.com/video/{self.embed_code}"
        elif self.platform == 'upload' and self.video_file:
            return self.video_file.url
        return None

    def get_embed_html(self):
        """Retorna código HTML iframe para embed do vídeo"""
        if self.platform == 'youtube' and self.embed_code:
            return f'''<iframe width="100%" height="100%"
                        src="https://www.youtube.com/embed/{self.embed_code}"
                        frameborder="0"
                        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                        allowfullscreen>
                       </iframe>'''
        elif self.platform == 'vimeo' and self.embed_code:
            return f'''<iframe width="100%" height="100%"
                        src="https://player.vimeo.com/video/{self.embed_code}"
                        frameborder="0"
                        allow="autoplay; fullscreen; picture-in-picture"
                        allowfullscreen>
                       </iframe>'''
        elif self.platform == 'upload' and self.video_file:
            # Player HTML5 nativo para arquivos upados
            file_ext = self.video_file.name.split('.')[-1].lower()
            mime_types = {
                'mp4': 'video/mp4',
                'webm': 'video/webm',
                'mov': 'video/quicktime',
                'avi': 'video/x-msvideo'
            }
            mime_type = mime_types.get(file_ext, 'video/mp4')
            return f'''<video width="100%" height="100%" controls>
                        <source src="{self.video_file.url}" type="{mime_type}">
                        Seu navegador não suporta o elemento de vídeo.
                       </video>'''
        return None

    def is_uploaded_video(self):
        """Retorna True se o vídeo é um arquivo upado localmente"""
        return self.platform == 'upload' and self.video_file

    def get_video_source(self):
        """
        Retorna a fonte do vídeo (URL ou arquivo).
        Prioriza: 1) video_file (upload), 2) video_url
        """
        if self.video_file:
            return self.video_file.url
        return self.video_url
