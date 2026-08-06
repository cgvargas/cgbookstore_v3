"""
Model Video - Central de Mídias Externas Corporativa
Representa vídeos (YouTube, trailers, entrevistas, gameplays, podcasts, bastidores)
com suporte à auditoria de disponibilidade, oficialidade de canal e governança de imagens.
"""

from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError


class Video(models.Model):
    """
    Model para mídias externas relacionadas a livros, autores, universos literários e artigos.
    Integra-se nativamente ao ImageRightsRecord para governança da thumbnail customizada.
    """

    PLATFORM_CHOICES = [
        ('youtube', 'YouTube'),
        ('vimeo', 'Vimeo (Desabilitado)'),
        ('instagram', 'Instagram (Desabilitado)'),
        ('tiktok', 'TikTok (Desabilitado)'),
        ('upload', 'Upload de Arquivo (Desabilitado)'),
    ]

    MEDIA_TYPE_CHOICES = [
        ('official_trailer', '🎬 Trailer Oficial'),
        ('trailer', '📽️ Trailer / Teaser'),
        ('teaser', '⚡ Teaser'),
        ('adaptation', '🎥 Adaptação (Filme/Série/Anime)'),
        ('gameplay', '🎮 Gameplay / Trailer de Jogo'),
        ('interview', '🎙️ Entrevista / Q&A'),
        ('behind_the_scenes', '🎞️ Bastidores / Making Of'),
        ('documentary', '📖 Documentário / Especial'),
        ('podcast', '🎧 Podcast / Debate'),
        ('review', '✍️ Resenha em Vídeo / Critique'),
        ('live', '🔴 Live / Transmissão ao Vivo'),
        ('event', '🏛️ Evento / Painel'),
        ('announcement', '📢 Anúncio / Novidade'),
        ('other', '📌 Outro'),
    ]

    MEDIA_STATUS_CHOICES = [
        ('active', '🟢 Ativa e Disponível'),
        ('removed', '🔴 Removida da Plataforma'),
        ('private', '🔒 Privada / Restrita'),
        ('embed_blocked', '🚫 Incorporação Bloqueada pelo Criador'),
        ('unavailable', '⚠️ Indisponível'),
        ('unknown', '❓ Status Não Verificado'),
    ]

    HEALTH_CHECK_SOURCE_CHOICES = [
        ('youtube_api', 'YouTube Data API v3'),
        ('none', 'Nenhum / Não Auditado'),
    ]

    # Campos Básicos
    title = models.CharField(
        max_length=200,
        verbose_name="Título",
        help_text="Título da mídia ou vídeo."
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        blank=True,
        verbose_name="Slug",
        help_text="Gerado automaticamente a partir do título."
    )
    short_description = models.CharField(
        max_length=300,
        blank=True,
        default='',
        verbose_name="Descrição Curta",
        help_text="Resumo sutil para exibições em cards e previews."
    )
    description = models.TextField(
        blank=True,
        verbose_name="Conteúdo Editorial Completo",
        help_text="Texto editorial completo contextualizando o vídeo."
    )

    # Plataforma e Identificadores do Vídeo
    platform = models.CharField(
        max_length=20,
        choices=PLATFORM_CHOICES,
        default='youtube',
        verbose_name="Plataforma"
    )
    video_url = models.URLField(
        max_length=500,
        blank=True,
        verbose_name="URL do Vídeo",
        help_text="URL original informada pelo administrador."
    )
    embed_code = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="ID do Vídeo / Código de Embed",
        help_text="Identificador único limpo do vídeo na plataforma (ex: dQw4w9WgXcQ)."
    )
    video_file = models.FileField(
        upload_to='videos/uploads/',
        blank=True,
        null=True,
        verbose_name="Arquivo de Vídeo Local (Desabilitado)",
        validators=[FileExtensionValidator(allowed_extensions=['mp4', 'webm', 'mov', 'avi'])]
    )

    # Informações do Canal e Oficialidade Auditada
    channel_name = models.CharField(
        max_length=200,
        blank=True,
        default='',
        verbose_name="Nome do Canal / Criador Original"
    )
    channel_id = models.CharField(
        max_length=100,
        blank=True,
        default='',
        verbose_name="ID do Canal na Plataforma"
    )
    is_official_channel = models.BooleanField(
        default=False,
        verbose_name="Canal Oficial Verificado?",
        help_text="Selo de oficialidade (estúdio, editora, autor, desenvolvedora). Requer confirmação auditada."
    )
    official_status_verified_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Data da Verificação de Oficialidade"
    )
    official_status_verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Responsável pela Verificação de Oficialidade"
    )
    official_status_notes = models.TextField(
        blank=True,
        default='',
        verbose_name="Notas sobre a Oficialidade do Canal"
    )

    # Tipo e Idioma
    video_type = models.CharField(
        max_length=30,
        choices=MEDIA_TYPE_CHOICES,
        default='other',
        verbose_name="Tipo de Mídia / Conteúdo"
    )
    language = models.CharField(
        max_length=10,
        default='pt-br',
        verbose_name="Idioma Principal"
    )
    duration_td = models.DurationField(
        null=True,
        blank=True,
        verbose_name="Duração Estruturada",
        help_text="Duração em formato de tempo (DurationField)."
    )
    published_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data de Publicação Original"
    )

    # Thumbnails (Remota vs. Personalizada)
    thumbnail_image = models.ImageField(
        upload_to='videos/thumbnails/',
        blank=True,
        null=True,
        verbose_name="Thumbnail Customizada (Capas de Ativos Visuais)",
        help_text="Upload de capa própria. Reutilizará o ImageRightsRecord para governança visual."
    )
    thumbnail_url = models.URLField(
        max_length=500,
        blank=True,
        verbose_name="URL da Thumbnail Remota",
        help_text="URL oficial gerada pelo provedor (ex: img.youtube.com)."
    )

    # Auditoria de Saúde e Disponibilidade da Mídia
    media_status = models.CharField(
        max_length=20,
        choices=MEDIA_STATUS_CHOICES,
        default='unknown',
        db_index=True,
        verbose_name="Status de Disponibilidade da Mídia"
    )
    last_health_check = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Última Verificação de Saúde"
    )
    is_embeddable = models.BooleanField(
        null=True,
        blank=True,
        default=None,
        verbose_name="Permite Incorporação (Embed)?",
        help_text="None = Não verificado; True = Permitido; False = Bloqueado."
    )
    health_check_source = models.CharField(
        max_length=30,
        choices=HEALTH_CHECK_SOURCE_CHOICES,
        default='none',
        verbose_name="Fonte de Verificação de Saúde"
    )
    health_check_message = models.TextField(
        blank=True,
        default='',
        verbose_name="Mensagem da Última Verificação Técnica"
    )
    admin_notes = models.TextField(
        blank=True,
        default='',
        verbose_name="Observações Administrativas Internas"
    )

    # Relacionamentos Flexíveis M2M
    related_books = models.ManyToManyField(
        'core.Book',
        blank=True,
        related_name='videos',
        verbose_name="Livros Relacionados"
    )
    related_author = models.ForeignKey(
        'core.Author',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='videos',
        verbose_name="Autor Relacionado Principal"
    )
    related_universes = models.ManyToManyField(
        'core.LiteraryUniverse',
        blank=True,
        related_name='media_items',
        verbose_name="Universos Literários Relacionados"
    )
    related_articles = models.ManyToManyField(
        'news.Article',
        blank=True,
        related_name='related_videos',
        verbose_name="Artigos e Notícias Relacionados"
    )
    related_quizzes = models.ManyToManyField(
        'news.Quiz',
        blank=True,
        related_name='related_videos',
        verbose_name="Quizzes Relacionados"
    )
    categories = models.ManyToManyField(
        'core.Category',
        blank=True,
        related_name='videos',
        verbose_name="Categorias Literárias Relacionadas"
    )

    # Métricas e Controle de Exibição
    views_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Visualizações Internas"
    )
    featured = models.BooleanField(
        default=False,
        verbose_name="Destacado",
        help_text="Mídia será exibida em seções especiais da plataforma."
    )
    display_order = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordem de Exibição"
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
        verbose_name = "Central de Mídia / Vídeo"
        verbose_name_plural = "Central de Mídias Externas"
        ordering = ['display_order', '-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['platform', 'embed_code'],
                name='unique_video_per_platform',
                condition=models.Q(embed_code__gt='')
            )
        ]

    def clean(self):
        super().clean()
        # Validação de Selo Oficial: exige responsável e data de verificação
        if self.is_official_channel:
            if not self.official_status_verified_by or not self.official_status_verified_at:
                raise ValidationError(
                    "Para marcar o canal como 'Oficial', é obrigatório registrar o 'Responsável pela Verificação' e a 'Data da Verificação'."
                )

    def save(self, *args, **kwargs):
        """Gera slug automaticamente e limpa/extrai ID do vídeo"""
        if not self.slug:
            base_slug = slugify(self.title)[:200]
            if not base_slug:
                base_slug = 'video'
            slug = base_slug
            counter = 1
            while type(self).objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug[:190]}-{counter}"
                counter += 1
            self.slug = slug

        # Normalização do ID do YouTube (embed_code)
        if self.platform == 'youtube' and self.video_url:
            video_id = None
            if 'watch?v=' in self.video_url:
                video_id = self.video_url.split('watch?v=')[1].split('&')[0]
            elif 'youtu.be/' in self.video_url:
                video_id = self.video_url.split('youtu.be/')[1].split('?')[0]
            elif 'youtube.com/shorts/' in self.video_url:
                video_id = self.video_url.split('shorts/')[1].split('?')[0]
            elif 'youtube.com/embed/' in self.video_url:
                video_id = self.video_url.split('embed/')[1].split('?')[0]

            if video_id:
                self.embed_code = video_id
                if not self.thumbnail_url:
                    self.thumbnail_url = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} [{self.get_platform_display()}]"

    @property
    def formatted_duration(self):
        """Retorna a duração formatada em MM:SS ou HH:MM:SS."""
        if not self.duration_td:
            return ""
        total_seconds = int(self.duration_td.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        return f"{minutes:02d}:{seconds:02d}"

    def get_thumbnail(self):
        """Retorna a URL da thumbnail (customizada ou remota)."""
        if self.thumbnail_image:
            return self.thumbnail_image.url
        elif self.thumbnail_url:
            return self.thumbnail_url
        return None

    def get_embed_url(self):
        """Retorna a URL de incorporação em modo de alta privacidade (youtube-nocookie)."""
        if self.platform == 'youtube' and self.embed_code:
            clean_id = self.embed_code.strip()
            return f"https://www.youtube-nocookie.com/embed/{clean_id}"
        return None
