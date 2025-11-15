"""
Model Video - Representa vídeos (YouTube, entrevistas, book trailers, resenhas)
"""
from django.db import models
from django.utils.text import slugify
from core.utils.video_utils import extract_video_thumbnail
import logging

logger = logging.getLogger(__name__)


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
        help_text="URL da imagem de preview (gerada automaticamente para YouTube, Instagram, Vimeo e TikTok quando possível)"
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
        """
        Gera slug automaticamente e extrai embed_code e thumbnail_url
        para diferentes plataformas (YouTube, Instagram, Vimeo, TikTok).
        """
        if not self.slug:
            self.slug = slugify(self.title)

        # Extrair embed_code e thumbnail automaticamente baseado na plataforma
        if self.video_url and self.platform:
            try:
                # Usar utilitário para extrair informações do vídeo
                embed_code, thumbnail_url = extract_video_thumbnail(
                    self.platform,
                    self.video_url
                )

                # Atualizar embed_code se foi extraído
                if embed_code and not self.embed_code:
                    self.embed_code = embed_code
                    logger.info(f"Embed code extraído para {self.platform}: {embed_code}")

                # Atualizar thumbnail_url se foi extraído
                # Só sobrescreve se estiver vazio (permite edição manual)
                if thumbnail_url and not self.thumbnail_url:
                    self.thumbnail_url = thumbnail_url
                    logger.info(f"Thumbnail extraída para {self.platform}: {thumbnail_url}")

            except Exception as e:
                logger.error(f"Erro ao extrair informações do vídeo ({self.platform}): {e}")

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
        return None