"""
Model Section - Representa seções dinâmicas da home
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Section(models.Model):
    """
    Model para seções dinâmicas da página inicial.
    Permite criar diferentes tipos de prateleiras gerenciáveis pelo admin.
    """

    CONTENT_TYPE_CHOICES = [
        ('books', 'Livros'),
        ('authors', 'Autores'),
        ('videos', 'Vídeos'),
        ('news', 'Notícias'),
        ('mixed', 'Misto'),
    ]

    LAYOUT_CHOICES = [
        ('carousel', 'Carrossel'),
        ('grid', 'Grid'),
        ('list', 'Lista'),
        ('featured', 'Destaque Grande'),
        ('cards_large', 'Cards Grandes (2 colunas)'),
        ('cards_small', 'Cards Pequenos (6 colunas)'),
        ('banner_slider', 'Banner com Slider'),
        ('grid_masonry', 'Grid Masonry (Pinterest style)'),
        ('horizontal_scroll', 'Scroll Horizontal'),
        ('spotlight', 'Destaque com Overlay'),
        ('banner_only', 'Apenas Banner (sem itens)'),
        ('video_cards', 'Cards de Vídeo com Preview (YouTube style)'),
    ]

    # Campos básicos
    title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Título",
        help_text="Título da seção (ex: 'Mais Vendidos', 'Lançamentos'). Deixe vazio para seções apenas com banner."
    )

    subtitle = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Subtítulo",
        help_text="Texto descritivo opcional"
    )

    # Tipo e layout
    content_type = models.CharField(
        max_length=20,
        choices=CONTENT_TYPE_CHOICES,
        default='books',
        verbose_name="Tipo de Conteúdo"
    )

    layout = models.CharField(
        max_length=20,
        choices=LAYOUT_CHOICES,
        default='carousel',
        verbose_name="Layout de Exibição"
    )

    # Controle de exibição
    active = models.BooleanField(
        default=True,
        verbose_name="Ativa",
        help_text="Seção será exibida na home"
    )

    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordem",
        help_text="Ordem de exibição (menor = aparece primeiro)"
    )

    background_color = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Cor de Fundo",
        help_text="Ex: #f8f9fa, transparent"
    )

    background_image = models.ImageField(
        upload_to='sections/backgrounds/',
        blank=True,
        null=True,
        verbose_name="Imagem de Background",
        help_text="Imagem de fundo para o container da seção (recomendado: 1920x600px)"
    )

    banner_image = models.ImageField(
        upload_to='sections/banners/',
        blank=True,
        null=True,
        verbose_name="Imagem de Banner",
        help_text="Imagem de fundo ou banner promocional para a seção (recomendado: 1920x400px)"
    )

    # Posicionamento do banner
    BANNER_VERTICAL_CHOICES = [
        ('top', 'Topo'),
        ('center', 'Centro'),
        ('bottom', 'Inferior'),
    ]

    BANNER_HORIZONTAL_CHOICES = [
        ('left', 'Esquerda'),
        ('center', 'Centro'),
        ('right', 'Direita'),
    ]

    banner_position_vertical = models.CharField(
        max_length=10,
        choices=BANNER_VERTICAL_CHOICES,
        default='center',
        verbose_name="Posição Vertical do Banner",
        help_text="Onde a imagem do banner deve ser posicionada verticalmente"
    )

    banner_position_horizontal = models.CharField(
        max_length=10,
        choices=BANNER_HORIZONTAL_CHOICES,
        default='center',
        verbose_name="Posição Horizontal do Banner",
        help_text="Onde a imagem do banner deve ser posicionada horizontalmente"
    )

    banner_height = models.PositiveIntegerField(
        default=400,
        verbose_name="Altura do Banner (px)",
        help_text="Altura do banner em pixels (padrão: 400px, recomendado: 300-500px)"
    )

    # Efeitos visuais do banner
    banner_overlay_opacity = models.FloatField(
        default=0.5,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        verbose_name="Opacidade do Overlay do Banner",
        help_text="Escurecimento sobre a imagem do banner (0.0-1.0, recomendado: 0.4-0.6)"
    )

    banner_blur_edges = models.BooleanField(
        default=False,
        verbose_name="Desfocar Bordas do Banner",
        help_text="Aplica desfoque gradual nas bordas superior e inferior do banner"
    )

    banner_blur_intensity = models.PositiveIntegerField(
        default=80,
        verbose_name="Intensidade do Desfoque do Banner (px)",
        help_text="Tamanho da área de desfoque nas bordas (recomendado: 60-120px)"
    )

    css_class = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Classe CSS Personalizada"
    )

    custom_css = models.TextField(
        blank=True,
        verbose_name="CSS Personalizado",
        help_text="CSS customizado para esta seção (será inserido dentro de uma tag <style>)"
    )

    container_opacity = models.FloatField(
        default=1.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        verbose_name="Opacidade do Container",
        help_text="Transparência do container (0.0 = totalmente transparente, 1.0 = totalmente opaco)"
    )

    container_background_image = models.ImageField(
        upload_to='sections/backgrounds/',
        blank=True,
        null=True,
        verbose_name="Imagem de Fundo do Container",
        help_text="Imagem de fundo para o container da seção (aparece atrás dos cards)"
    )

    container_background_image_opacity = models.FloatField(
        default=0.3,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        verbose_name="Opacidade da Imagem de Fundo",
        help_text="Transparência da imagem de fundo (0.0 = invisível, 1.0 = totalmente visível). Recomendado: 0.2-0.5"
    )

    CONTAINER_BG_SIZE_CHOICES = [
        ('cover', 'Cobrir (Cover)'),
        ('contain', 'Conter (Contain)'),
        ('auto', 'Automático'),
    ]

    container_background_size = models.CharField(
        max_length=20,
        choices=CONTAINER_BG_SIZE_CHOICES,
        default='cover',
        verbose_name="Tamanho da Imagem de Fundo",
        help_text="Como a imagem de fundo deve ser dimensionada"
    )

    CONTAINER_BG_POSITION_CHOICES = [
        ('center center', 'Centro'),
        ('top center', 'Topo'),
        ('bottom center', 'Inferior'),
        ('left center', 'Esquerda'),
        ('right center', 'Direita'),
    ]

    container_background_position = models.CharField(
        max_length=20,
        choices=CONTAINER_BG_POSITION_CHOICES,
        default='center center',
        verbose_name="Posição da Imagem de Fundo",
        help_text="Posição da imagem de fundo no container"
    )

    # Configurações de layout avançadas
    card_style = models.CharField(
        max_length=50,
        blank=True,
        default='default',
        verbose_name="Estilo do Card",
        choices=[
            ('default', 'Padrão'),
            ('minimal', 'Minimalista'),
            ('shadow', 'Com Sombra'),
            ('bordered', 'Com Borda'),
            ('gradient', 'Com Gradiente'),
            ('overlay', 'Com Overlay'),
        ],
        help_text="Estilo visual dos cards nesta seção"
    )

    card_hover_effect = models.CharField(
        max_length=50,
        blank=True,
        default='scale',
        verbose_name="Efeito ao Passar Mouse",
        choices=[
            ('none', 'Nenhum'),
            ('scale', 'Aumentar'),
            ('lift', 'Elevar'),
            ('glow', 'Brilho'),
            ('tilt', 'Inclinação'),
        ],
        help_text="Efeito de hover nos cards"
    )

    show_price = models.BooleanField(
        default=True,
        verbose_name="Mostrar Preço",
        help_text="Exibir preço nos cards de livros"
    )

    show_rating = models.BooleanField(
        default=True,
        verbose_name="Mostrar Avaliação",
        help_text="Exibir estrelas de avaliação"
    )

    show_author = models.BooleanField(
        default=True,
        verbose_name="Mostrar Autor",
        help_text="Exibir nome do autor nos cards de livros"
    )

    # Configurações de exibição
    items_per_row = models.PositiveIntegerField(
        default=4,
        verbose_name="Itens por Linha",
        help_text="Aplicável para layout grid e carousel"
    )

    show_see_more = models.BooleanField(
        default=True,
        verbose_name="Mostrar 'Ver Mais'",
        help_text="Exibir link para ver todos os itens"
    )

    see_more_url = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="URL do 'Ver Mais'",
        help_text="Ex: /livros/?categoria=lancamentos"
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
        verbose_name = "Seção"
        verbose_name_plural = "Seções"
        ordering = ['order', '-created_at']

    def __str__(self):
        title_display = self.title if self.title else "Seção sem título"
        return f"{title_display} ({self.get_content_type_display()} - {self.get_layout_display()})"

    def get_items(self):
        """Retorna os itens da seção ordenados"""
        return self.items.filter(active=True).order_by('order')