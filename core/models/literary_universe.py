# core/models/literary_universe.py
"""
Modelos para Universos Literários - Sistema CMS para páginas temáticas de autores lendários.
Permite gerenciar páginas como "Mundo de Tolkien", "Nárnia de C.S. Lewis", etc.
"""

from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify


class LiteraryUniverse(models.Model):
    """
    Universo literário gerenciável via Admin.
    Representa uma página temática dedicada a um autor e seu universo de obras.
    """
    
    # === OPÇÕES DE LAYOUT ===
    CARD_STYLES = [
        ('default', 'Padrão'),
        ('compact', 'Compacto'),
        ('expanded', 'Expandido'),
        ('minimal', 'Minimalista'),
    ]
    
    CONTAINER_STYLES = [
        ('grid', 'Grid (padrão)'),
        ('carousel', 'Carrossel'),
        ('masonry', 'Masonry'),
        ('list', 'Lista'),
    ]
    
    # === IDENTIFICAÇÃO ===
    title = models.CharField(
        max_length=100,
        verbose_name="Título",
        help_text='Título do universo (ex: "Mundo de Tolkien")'
    )
    
    slug = models.SlugField(
        unique=True,
        verbose_name="Slug",
        help_text='Identificador na URL (ex: tolkien -> /universo/tolkien/)'
    )
    
    author = models.ForeignKey(
        'core.Author',
        on_delete=models.CASCADE,
        related_name='literary_universes',
        verbose_name="Autor",
        help_text="Autor principal deste universo"
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name="Ativo",
        help_text="Se ativo, a página será acessível"
    )
    
    display_order = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordem de Exibição",
        help_text="Usado para ordenar na listagem"
    )
    
    show_in_menu = models.BooleanField(
        default=False,
        verbose_name="Mostrar no Menu",
        help_text="Exibir link no menu principal"
    )
    
    # === VISUAL/TEMA ===
    theme_color_primary = models.CharField(
        max_length=7,
        default='#f4d03f',
        verbose_name="Cor Primária",
        help_text="Cor em hexadecimal (ex: #f4d03f)"
    )
    
    theme_color_secondary = models.CharField(
        max_length=7,
        default='#c9a227',
        verbose_name="Cor Secundária",
        help_text="Cor secundária em hexadecimal"
    )
    
    hero_icon = models.CharField(
        max_length=50,
        default='fa-ring',
        verbose_name="Ícone do Hero",
        help_text="Classe Font Awesome (ex: fa-ring, fa-dragon)"
    )
    
    hero_banner_image = models.ImageField(
        upload_to='literary_universes/banners/',
        blank=True,
        null=True,
        verbose_name="Banner do Hero",
        help_text="Imagem de fundo do hero (recomendado: 1920x600)"
    )
    
    # === OPÇÕES DE LAYOUT ===
    books_card_style = models.CharField(
        max_length=20,
        choices=CARD_STYLES,
        default='default',
        verbose_name="Estilo Cards de Livros"
    )
    
    books_container_style = models.CharField(
        max_length=20,
        choices=CONTAINER_STYLES,
        default='grid',
        verbose_name="Container de Livros"
    )
    
    articles_card_style = models.CharField(
        max_length=20,
        choices=CARD_STYLES,
        default='default',
        verbose_name="Estilo Cards de Artigos"
    )
    
    articles_container_style = models.CharField(
        max_length=20,
        choices=CONTAINER_STYLES,
        default='grid',
        verbose_name="Container de Artigos"
    )
    
    videos_card_style = models.CharField(
        max_length=20,
        choices=CARD_STYLES,
        default='default',
        verbose_name="Estilo Cards de Vídeos"
    )
    
    videos_container_style = models.CharField(
        max_length=20,
        choices=CONTAINER_STYLES,
        default='grid',
        verbose_name="Container de Vídeos"
    )
    
    content_card_style = models.CharField(
        max_length=20,
        choices=CARD_STYLES,
        default='default',
        verbose_name="Estilo Cards de Conteúdo"
    )
    
    content_container_style = models.CharField(
        max_length=20,
        choices=CONTAINER_STYLES,
        default='grid',
        verbose_name="Container de Conteúdo"
    )
    
    # === TEXTOS DA PÁGINA ===
    page_title = models.CharField(
        max_length=200,
        verbose_name="Título da Página",
        help_text="Título exibido no hero da página"
    )
    
    page_subtitle = models.CharField(
        max_length=100,
        default='Explore o Mundo de',
        verbose_name="Subtítulo",
        help_text="Texto acima do título principal"
    )
    
    page_description = models.TextField(
        verbose_name="Descrição da Página",
        help_text="Descrição exibida abaixo do título"
    )
    
    # === SEO ===
    meta_title = models.CharField(
        max_length=70,
        blank=True,
        verbose_name="Meta Title (SEO)",
        help_text="Título para SEO (máx 70 caracteres)"
    )
    
    meta_description = models.CharField(
        max_length=160,
        blank=True,
        verbose_name="Meta Description (SEO)",
        help_text="Descrição para SEO (máx 160 caracteres)"
    )
    
    # === INTEGRAÇÃO COM VÍDEOS ===
    # Relacionamento ManyToMany com o modelo Video existente
    videos = models.ManyToManyField(
        'core.Video',
        blank=True,
        related_name='literary_universes',
        verbose_name="Vídeos Associados",
        help_text="Vídeos relacionados a este universo"
    )
    
    # === TIMESTAMPS ===
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Atualizado em"
    )
    
    class Meta:
        verbose_name = "Universo Literário"
        verbose_name_plural = "Universos Literários"
        ordering = ['display_order', 'title']
    
    def __str__(self):
        status = '✓' if self.is_active else '✗'
        return f'{status} {self.title}'
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if not self.page_title:
            self.page_title = self.title
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('core:literary_universe', kwargs={'slug': self.slug})
    
    def get_books(self):
        """Retorna todos os livros do autor deste universo."""
        from core.models import Book
        return Book.objects.filter(author=self.author).select_related('category')
    
    def get_active_banners(self, position=None):
        """Retorna banners ativos, opcionalmente filtrados por posição."""
        now = timezone.now()
        banners = self.banners.filter(is_active=True)
        
        # Filtrar por data de início/fim
        banners = banners.filter(
            models.Q(start_date__isnull=True) | models.Q(start_date__lte=now)
        ).filter(
            models.Q(end_date__isnull=True) | models.Q(end_date__gte=now)
        )
        
        if position:
            banners = banners.filter(position=position)
        
        return banners.order_by('display_order')
    
    def get_all_videos(self):
        """Retorna vídeos do related M2M + vídeos do autor."""
        from core.models import Video
        
        # Vídeos selecionados manualmente
        manual_videos = self.videos.filter(active=True)
        
        # Vídeos do autor
        author_videos = Video.objects.filter(
            related_author=self.author,
            active=True
        )
        
        # Combinar e remover duplicatas
        all_video_ids = set(manual_videos.values_list('id', flat=True))
        all_video_ids.update(author_videos.values_list('id', flat=True))
        
        return Video.objects.filter(id__in=all_video_ids).order_by('-created_at')


class UniverseContentItem(models.Model):
    """
    Item de conteúdo adicional do universo (games, adaptações, podcasts, etc.).
    """
    
    CONTENT_TYPES = [
        ('game', 'Game'),
        ('adaptation', 'Adaptação (Filme/Série)'),
        ('podcast', 'Podcast'),
        ('article', 'Artigo Externo'),
        ('merchandise', 'Merchandise'),
        ('event', 'Evento'),
        ('link', 'Link Externo'),
    ]
    
    universe = models.ForeignKey(
        LiteraryUniverse,
        on_delete=models.CASCADE,
        related_name='content_items',
        verbose_name="Universo"
    )
    
    content_type = models.CharField(
        max_length=20,
        choices=CONTENT_TYPES,
        verbose_name="Tipo de Conteúdo"
    )
    
    title = models.CharField(
        max_length=200,
        verbose_name="Título"
    )
    
    description = models.TextField(
        blank=True,
        verbose_name="Descrição"
    )
    
    thumbnail = models.ImageField(
        upload_to='literary_universes/content/',
        blank=True,
        null=True,
        verbose_name="Thumbnail"
    )
    
    url = models.URLField(
        blank=True,
        verbose_name="URL",
        help_text="Link externo (site oficial, loja, etc.)"
    )
    
    display_order = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordem"
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name="Ativo"
    )
    
    # Campos extras para games
    platform = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Plataforma",
        help_text="Ex: PC, PS5, Xbox, etc. (para games)"
    )
    
    release_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data de Lançamento"
    )
    
    class Meta:
        verbose_name = "Item de Conteúdo"
        verbose_name_plural = "Itens de Conteúdo"
        ordering = ['content_type', 'display_order']
    
    def __str__(self):
        return f'{self.get_content_type_display()}: {self.title}'


class UniverseBanner(models.Model):
    """
    Banner promocional dentro do universo literário.
    Permite adicionar banners em diferentes posições da página.
    """
    
    BANNER_POSITIONS = [
        ('after_hero', 'Após o Hero'),
        ('before_books', 'Antes dos Livros'),
        ('after_books', 'Após os Livros'),
        ('before_articles', 'Antes dos Artigos'),
        ('after_articles', 'Após os Artigos'),
        ('before_videos', 'Antes dos Vídeos'),
        ('after_videos', 'Após os Vídeos'),
        ('footer', 'Rodapé da Página'),
    ]
    
    BANNER_SIZES = [
        ('full', 'Largura Total'),
        ('large', 'Grande (3/4)'),
        ('medium', 'Médio (2/3)'),
        ('small', 'Pequeno (1/2)'),
    ]
    
    universe = models.ForeignKey(
        LiteraryUniverse,
        on_delete=models.CASCADE,
        related_name='banners',
        verbose_name="Universo"
    )
    
    title = models.CharField(
        max_length=100,
        verbose_name="Título (interno)",
        help_text="Identificação no admin"
    )
    
    image = models.ImageField(
        upload_to='literary_universes/banners/',
        verbose_name="Imagem Desktop"
    )
    
    image_mobile = models.ImageField(
        upload_to='literary_universes/banners/',
        blank=True,
        null=True,
        verbose_name="Imagem Mobile",
        help_text="Versão otimizada para dispositivos móveis"
    )
    
    alt_text = models.CharField(
        max_length=200,
        verbose_name="Texto Alternativo",
        help_text="Descrição para acessibilidade"
    )
    
    link_url = models.URLField(
        blank=True,
        verbose_name="URL do Link",
        help_text="Link ao clicar no banner"
    )
    
    link_target = models.CharField(
        max_length=20,
        default='_self',
        choices=[('_self', 'Mesma aba'), ('_blank', 'Nova aba')],
        verbose_name="Abrir em"
    )
    
    position = models.CharField(
        max_length=20,
        choices=BANNER_POSITIONS,
        default='after_hero',
        verbose_name="Posição na Página"
    )
    
    size = models.CharField(
        max_length=20,
        choices=BANNER_SIZES,
        default='full',
        verbose_name="Tamanho"
    )
    
    display_order = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordem",
        help_text="Para múltiplos banners na mesma posição"
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name="Ativo"
    )
    
    # Agendamento
    start_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Data de Início",
        help_text="Deixe em branco para exibir imediatamente"
    )
    
    end_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Data de Fim",
        help_text="Deixe em branco para exibir indefinidamente"
    )
    
    class Meta:
        verbose_name = "Banner do Universo"
        verbose_name_plural = "Banners do Universo"
        ordering = ['position', 'display_order']
    
    def __str__(self):
        return f'{self.title} ({self.get_position_display()})'
    
    def is_visible(self):
        """Verifica se o banner está visível (ativo + dentro do período)."""
        if not self.is_active:
            return False
        
        now = timezone.now()
        
        if self.start_date and now < self.start_date:
            return False
        
        if self.end_date and now > self.end_date:
            return False
        
        return True
    
    def get_size_class(self):
        """Retorna classe CSS baseada no tamanho."""
        size_classes = {
            'full': 'col-12',
            'large': 'col-lg-9 col-12',
            'medium': 'col-lg-8 col-12',
            'small': 'col-lg-6 col-12',
        }
        return size_classes.get(self.size, 'col-12')
