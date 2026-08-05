# core/models/literary_universe.py
"""
Modelos para Universos Literários - Sistema CMS para páginas temáticas de autores lendários.
Permite gerenciar páginas como "Mundo de Tolkien", "Nárnia de C.S. Lewis", etc.

Evolução v2: HUB de conhecimento com ordem de leitura, cronologia, FAQ, adaptações,
personagens, coleções e sistema de qualidade Bronze/Prata/Ouro/Platina.
"""

from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
import json


class LiteraryUniverse(models.Model):
    """
    Universo literário gerenciável via Admin.
    Representa uma página temática dedicada a um autor e seu universo de obras.
    Funciona como HUB central de conhecimento reunindo livros, autores, artigos,
    vídeos, quizzes, cronologia, ordem de leitura e demais conteúdos relacionados.
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
        verbose_name="Autor Principal",
        help_text="Autor principal deste universo"
    )
    
    # NOVO: Autores adicionais para universos multi-autor (ex: Roda do Tempo)
    additional_authors = models.ManyToManyField(
        'core.Author',
        blank=True,
        related_name='literary_universes_additional',
        verbose_name="Autores Adicionais",
        help_text="Outros autores deste universo (ex: Brandon Sanderson em A Roda do Tempo)"
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name="Ativo",
        help_text="Se ativo, a página será acessível"
    )
    
    # NOVO: Destaque na home
    featured_on_home = models.BooleanField(
        default=False,
        verbose_name="Destaque na Home",
        help_text="Se marcado, o universo poderá aparecer em destaque na página inicial"
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
    
    # NOVO: Logo do universo
    logo = models.ImageField(
        upload_to='literary_universes/logos/',
        blank=True,
        null=True,
        verbose_name="Logo do Universo",
        help_text="Logotipo ou imagem de identidade do universo (recomendado: 400x400)"
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
        blank=True,
        verbose_name="Ícone do Hero",
        help_text="Classe Font Awesome (ex: fa-ring, fa-dragon). Deixe em branco se não quiser nenhum ícone."
    )
    
    hero_banner_image = models.ImageField(
        upload_to='literary_universes/banners/',
        blank=True,
        null=True,
        verbose_name="Banner do Hero",
        help_text="Imagem de fundo do hero (recomendado: 1920x600)"
    )
    
    # Posicionamento do banner hero
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
    
    hero_banner_position_vertical = models.CharField(
        max_length=10,
        choices=BANNER_VERTICAL_CHOICES,
        default='center',
        verbose_name="Posição Vertical do Banner",
        help_text="Onde a imagem deve ser posicionada verticalmente"
    )
    
    hero_banner_position_horizontal = models.CharField(
        max_length=10,
        choices=BANNER_HORIZONTAL_CHOICES,
        default='center',
        verbose_name="Posição Horizontal do Banner",
        help_text="Onde a imagem deve ser posicionada horizontalmente"
    )
    
    hero_banner_overlay_opacity = models.FloatField(
        default=0.5,
        verbose_name="Opacidade do Overlay",
        help_text="0.0 = totalmente transparente, 1.0 = totalmente escuro (recomendado: 0.3-0.6)"
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
    
    # NOVO: Open Graph & Social
    og_title = models.CharField(
        max_length=95,
        blank=True,
        verbose_name="Título Open Graph",
        help_text="Título para compartilhamento em redes sociais (máx 95 caracteres)"
    )
    
    og_description = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Descrição Open Graph",
        help_text="Descrição para compartilhamento em redes sociais"
    )
    
    og_image = models.ImageField(
        upload_to='literary_universes/og/',
        blank=True,
        null=True,
        verbose_name="Imagem Open Graph",
        help_text="Imagem para compartilhamento em redes sociais (recomendado: 1200x630)"
    )
    
    canonical_url = models.URLField(
        blank=True,
        verbose_name="URL Canônica",
        help_text="URL canônica personalizada (deixe em branco para usar a URL padrão)"
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
    
    # Relacionamento ManyToMany com artigos do módulo news
    articles = models.ManyToManyField(
        'news.Article',
        blank=True,
        related_name='literary_universes',
        verbose_name="Artigos Associados",
        help_text="Artigos/notícias relacionados a este universo (além da busca automática por tag)"
    )
    
    # NOVO: Relacionamento direto com livros
    books = models.ManyToManyField(
        'core.Book',
        blank=True,
        related_name='literary_universes',
        verbose_name="Livros do Universo",
        help_text="Livros que pertencem a este universo (combinados automaticamente com os do autor principal)"
    )
    
    # NOVO: Relacionamento com quizzes
    quizzes = models.ManyToManyField(
        'news.Quiz',
        blank=True,
        related_name='literary_universes',
        verbose_name="Quizzes Associados",
        help_text="Quizzes e testes interativos relacionados a este universo"
    )
    
    # NOVO: Universos relacionados (simétrico)
    related_universes = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=True,
        verbose_name="Universos Relacionados",
        help_text="Outros universos literários semelhantes para cross-linking"
    )
    
    # NOVO: Categorias relacionadas
    related_categories = models.ManyToManyField(
        'core.Category',
        blank=True,
        related_name='literary_universes',
        verbose_name="Categorias Relacionadas",
        help_text="Categorias de livros associadas a este universo"
    )
    
    # NOVO: Coleção (agrupamento de universos)
    collection = models.ForeignKey(
        'core.UniverseCollection',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='universes',
        verbose_name="Coleção",
        help_text="Agrupamento temático (ex: Fantasia, Ficção Científica, Mangás)"
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
    
    # === MÉTODOS DE CONTEÚDO ===
    
    def get_books(self):
        """Retorna todos os livros do autor deste universo (retrocompatibilidade)."""
        from core.models import Book
        return Book.objects.filter(author=self.author).select_related('category')
    
    def get_all_books(self):
        """
        Retorna todos os livros do universo, combinando:
        1. Livros selecionados manualmente (M2M books)
        2. Livros do autor principal (FK author)
        3. Livros dos autores adicionais (M2M additional_authors)
        Remove duplicatas e ordena por título.
        """
        from core.models import Book
        
        # IDs de livros selecionados manualmente
        manual_ids = set(self.books.values_list('id', flat=True))
        
        # IDs de livros do autor principal
        author_ids = set(
            Book.objects.filter(author=self.author).values_list('id', flat=True)
        )
        
        # IDs de livros dos autores adicionais
        additional_ids = set(
            Book.objects.filter(
                author__in=self.additional_authors.all()
            ).values_list('id', flat=True)
        )
        
        # Combinar todos os IDs
        all_ids = manual_ids | author_ids | additional_ids
        
        return Book.objects.filter(
            id__in=all_ids
        ).select_related('author', 'category').order_by('title')
    
    def get_all_authors(self):
        """Retorna autor principal em 1º lugar, seguido pelos autores adicionais."""
        from core.models import Author
        authors = [self.author]
        additional = list(self.additional_authors.exclude(id=self.author_id).order_by('name'))
        authors.extend(additional)
        return authors
    
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
    
    def get_active_faqs(self):
        """Retorna FAQs ativas ordenadas."""
        return self.faqs.filter(is_active=True).order_by('display_order')
    
    def get_faq_schema_json(self):
        """Gera JSON-LD de FAQ Schema para SEO."""
        faqs = self.get_active_faqs()
        if not faqs.exists():
            return ''
        
        schema = {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": faq.question,
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": faq.answer
                    }
                }
                for faq in faqs
            ]
        }
        return json.dumps(schema, ensure_ascii=False)
    
    # === ESTATÍSTICAS ===
    
    def get_stats(self):
        """Retorna todas as contagens calculadas automaticamente."""
        all_books = self.get_all_books()
        total_pages = sum(b.page_count or 0 for b in all_books)
        
        return {
            'books_count': all_books.count(),
            'authors_count': len(self.get_all_authors()),
            'articles_count': self.articles.count(),
            'videos_count': self.videos.count(),
            'quizzes_count': self.quizzes.count(),
            'faqs_count': self.faqs.filter(is_active=True).count(),
            'timeline_count': self.timeline_events.filter(is_active=True).count(),
            'reading_order_count': self.reading_order.count(),
            'adaptations_count': self.content_items.filter(
                content_type__in=['adaptation', 'game'], is_active=True
            ).count(),
            'characters_count': self.characters.filter(is_active=True).count(),
            'total_pages': total_pages,
        }
    
    # === SISTEMA DE QUALIDADE ===
    
    QUALITY_TIERS = {
        'bronze': {'min': 0, 'label': 'Bronze', 'color': '#cd7f32', 'icon': '🥉'},
        'silver': {'min': 30, 'label': 'Prata', 'color': '#c0c0c0', 'icon': '🥈'},
        'gold': {'min': 60, 'label': 'Ouro', 'color': '#ffd700', 'icon': '🥇'},
        'platinum': {'min': 85, 'label': 'Platina', 'color': '#e5e4e2', 'icon': '💎'},
    }
    
    def get_quality_checklist(self):
        """
        Retorna checklist com status de cada critério de qualidade.
        Cada item: (nome, atendido, peso, grupo)
        """
        stats = self.get_stats()
        
        checklist = [
            # Identidade Visual (20 pontos)
            ('Banner do hero', bool(self.hero_banner_image), 5, 'Visual'),
            ('Logo do universo', bool(self.logo), 5, 'Visual'),
            ('Cores personalizadas', self.theme_color_primary != '#f4d03f', 5, 'Visual'),
            ('Descrição da página', len(self.page_description or '') > 50, 5, 'Visual'),
            
            # Conteúdo Essencial (35 pontos)
            ('Pelo menos 3 livros', stats['books_count'] >= 3, 10, 'Conteúdo'),
            ('Autor(es) cadastrado(s)', stats['authors_count'] >= 1, 5, 'Conteúdo'),
            ('Pelo menos 1 artigo', stats['articles_count'] >= 1, 5, 'Conteúdo'),
            ('Pelo menos 1 vídeo', stats['videos_count'] >= 1, 5, 'Conteúdo'),
            ('Ordem de leitura', stats['reading_order_count'] >= 1, 5, 'Conteúdo'),
            ('Cronologia', stats['timeline_count'] >= 1, 5, 'Conteúdo'),
            
            # Engajamento (20 pontos)
            ('Pelo menos 3 FAQs', stats['faqs_count'] >= 3, 7, 'Engajamento'),
            ('Pelo menos 1 quiz', stats['quizzes_count'] >= 1, 7, 'Engajamento'),
            ('Adaptações cadastradas', stats['adaptations_count'] >= 1, 6, 'Engajamento'),
            
            # SEO (25 pontos)
            ('Meta title', bool(self.meta_title), 5, 'SEO'),
            ('Meta description', bool(self.meta_description), 5, 'SEO'),
            ('Open Graph title', bool(self.og_title), 5, 'SEO'),
            ('Open Graph image', bool(self.og_image), 5, 'SEO'),
            ('Universos relacionados', self.related_universes.exists(), 5, 'SEO'),
        ]
        
        return checklist
    
    def get_quality_score(self):
        """Calcula pontuação de qualidade (0-100) e retorna tier."""
        checklist = self.get_quality_checklist()
        total_weight = sum(item[2] for item in checklist)
        achieved = sum(item[2] for item in checklist if item[1])
        score = int((achieved / total_weight) * 100) if total_weight > 0 else 0
        
        # Determinar tier
        tier = 'bronze'
        for tier_key in ['platinum', 'gold', 'silver', 'bronze']:
            if score >= self.QUALITY_TIERS[tier_key]['min']:
                tier = tier_key
                break
        
        tier_info = self.QUALITY_TIERS[tier]
        
        return {
            'score': score,
            'tier': tier,
            'label': tier_info['label'],
            'color': tier_info['color'],
            'icon': tier_info['icon'],
            'checklist': checklist,
        }


class UniverseContentItem(models.Model):
    """
    Item de conteúdo adicional do universo (games, adaptações, podcasts, etc.).
    Modelo flexível para representar filmes, séries, jogos, HQs, animes,
    podcasts e futuras mídias sem necessidade de modelos separados.
    """
    
    CONTENT_TYPES = [
        ('review', '✍️ Resenha'),
        ('game', '🎮 Game'),
        ('adaptation', '🎬 Adaptação (Filme/Série)'),
        ('anime', '🎌 Anime'),
        ('hq', '📚 HQ / Quadrinhos'),
        ('podcast', '🎙️ Podcast'),
        ('article', '📄 Artigo Externo'),
        ('merchandise', '🛍️ Merchandise'),
        ('event', '📅 Evento'),
        ('musical', '🎵 Musical / Trilha Sonora'),
        ('audiobook', '🎧 Audiobook'),
        ('link', '🔗 Link Externo'),
    ]
    
    MEDIA_STATUS_CHOICES = [
        ('released', '✅ Lançado'),
        ('in_production', '🎬 Em Produção'),
        ('announced', '📢 Anunciado'),
        ('rumored', '💬 Rumores'),
        ('cancelled', '❌ Cancelado'),
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
    
    # Campos extras para games (existentes — preservados)
    platform = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Plataforma",
        help_text="Ex: PC, PS5, Xbox, Netflix, HBO, etc."
    )
    
    release_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data de Lançamento"
    )
    
    # NOVOS: Campos para adaptações e mídias
    year = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Ano",
        help_text="Ano de lançamento ou estreia"
    )
    
    studio = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Estúdio / Produtora",
        help_text="Ex: Amazon Studios, Warner Bros, CD Projekt RED"
    )
    
    media_status = models.CharField(
        max_length=20,
        choices=MEDIA_STATUS_CHOICES,
        blank=True,
        verbose_name="Status",
        help_text="Status atual da produção"
    )
    
    seasons = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Temporadas / Volumes",
        help_text="Número de temporadas (séries) ou volumes (HQs)"
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


# ==============================================================================
# NOVOS MODELOS — Evolução v2
# ==============================================================================


class UniverseReadingOrder(models.Model):
    """
    Ordem de leitura de um universo literário.
    Permite cadastrar romances, prelúdios, contos, companions, graphic novels
    e demais formatos com ordem recomendada e cronológica.
    """
    
    BOOK_TYPE_CHOICES = [
        ('novel', '📖 Romance'),
        ('prelude', '📜 Prelúdio'),
        ('short_story', '📝 Conto'),
        ('novella', '📕 Novela'),
        ('companion', '📚 Companion / Guia'),
        ('graphic_novel', '🎨 Graphic Novel / HQ'),
        ('anthology', '📗 Antologia'),
        ('other', '📄 Outro'),
    ]
    
    universe = models.ForeignKey(
        LiteraryUniverse,
        on_delete=models.CASCADE,
        related_name='reading_order',
        verbose_name="Universo"
    )
    
    order_number = models.PositiveIntegerField(
        verbose_name="Ordem Recomendada",
        help_text="Posição na ordem de leitura recomendada (1, 2, 3...)"
    )
    
    title = models.CharField(
        max_length=300,
        verbose_name="Título",
        help_text="Nome do livro/obra"
    )
    
    book = models.ForeignKey(
        'core.Book',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reading_order_entries',
        verbose_name="Livro Vinculado",
        help_text="Vincular ao livro no catálogo (opcional — cria link na página)"
    )
    
    book_type = models.CharField(
        max_length=20,
        choices=BOOK_TYPE_CHOICES,
        default='novel',
        verbose_name="Tipo da Obra"
    )
    
    chronological_order = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Ordem Cronológica",
        help_text="Posição na ordem cronológica da história (opcional)"
    )
    
    publication_year = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Ano de Publicação"
    )
    
    is_essential = models.BooleanField(
        default=True,
        verbose_name="Leitura Essencial",
        help_text="Se marcado, indica que é uma leitura fundamental para a série"
    )
    
    notes = models.TextField(
        blank=True,
        verbose_name="Observações",
        help_text="Notas adicionais (ex: 'Pode ser lido antes ou depois do volume 3')"
    )
    
    class Meta:
        verbose_name = "Item da Ordem de Leitura"
        verbose_name_plural = "Ordem de Leitura"
        ordering = ['order_number']
        unique_together = ['universe', 'order_number']
    
    def __str__(self):
        return f'#{self.order_number} — {self.title}'


class UniverseTimelineEvent(models.Model):
    """
    Evento importante na cronologia de um universo literário.
    Permite criar uma timeline visual de eventos da história do universo.
    """
    
    IMPORTANCE_CHOICES = [
        ('critical', '🔴 Crítico (evento que muda tudo)'),
        ('major', '🟠 Importante'),
        ('minor', '🟡 Secundário'),
        ('trivia', '🔵 Curiosidade'),
    ]
    
    universe = models.ForeignKey(
        LiteraryUniverse,
        on_delete=models.CASCADE,
        related_name='timeline_events',
        verbose_name="Universo"
    )
    
    title = models.CharField(
        max_length=200,
        verbose_name="Título do Evento"
    )
    
    description = models.TextField(
        blank=True,
        verbose_name="Descrição"
    )
    
    image = models.ImageField(
        upload_to='literary_universes/timeline/',
        blank=True,
        null=True,
        verbose_name="Imagem"
    )
    
    era = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Era / Período",
        help_text="Ex: Primeira Era, Anos das Árvores, Terceira Era, etc."
    )
    
    approximate_date = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Data Aproximada",
        help_text="Ex: '3019 TE', '~500 anos antes', 'Início da Primeira Era'"
    )
    
    chronological_position = models.IntegerField(
        default=0,
        verbose_name="Posição Cronológica",
        help_text="Número para ordenação cronológica (valores negativos = passado distante)"
    )
    
    importance = models.CharField(
        max_length=10,
        choices=IMPORTANCE_CHOICES,
        default='major',
        verbose_name="Importância"
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name="Ativo"
    )
    
    class Meta:
        verbose_name = "Evento da Cronologia"
        verbose_name_plural = "Cronologia"
        ordering = ['chronological_position']
    
    def __str__(self):
        return f'{self.title} ({self.era or "sem era"})'


class UniverseFAQ(models.Model):
    """
    Pergunta frequente de um universo literário.
    Preparado para geração automática de FAQ Schema (JSON-LD) para SEO.
    """
    
    universe = models.ForeignKey(
        LiteraryUniverse,
        on_delete=models.CASCADE,
        related_name='faqs',
        verbose_name="Universo"
    )
    
    question = models.CharField(
        max_length=300,
        verbose_name="Pergunta",
        help_text="Pergunta frequente dos leitores"
    )
    
    answer = models.TextField(
        verbose_name="Resposta",
        help_text="Resposta completa à pergunta"
    )
    
    display_order = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordem"
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name="Ativo"
    )
    
    class Meta:
        verbose_name = "Pergunta Frequente"
        verbose_name_plural = "Perguntas Frequentes (FAQ)"
        ordering = ['display_order']
    
    def __str__(self):
        return self.question[:80]


class UniverseCharacter(models.Model):
    """
    Personagem importante de um universo literário.
    Exibido na página pública do universo em formato de galeria de cards.
    """
    
    ROLE_CHOICES = [
        ('protagonist', '⭐ Protagonista'),
        ('supporting', '🤝 Coadjuvante'),
        ('mentor', '🎓 Mentor'),
        ('antagonist', '😈 Antagonista'),
        ('ruler', '👑 Governante'),
        ('warrior', '⚔️ Guerreiro'),
        ('mage', '🧙 Mago'),
        ('leader', '🧝 Líder'),
        ('ally', '🛡️ Aliado'),
        ('other', '❓ Outro'),
    ]
    
    universe = models.ForeignKey(
        LiteraryUniverse,
        on_delete=models.CASCADE,
        related_name='characters',
        verbose_name="Universo"
    )
    
    name = models.CharField(
        max_length=200,
        verbose_name="Nome do Personagem"
    )
    
    description = models.TextField(
        blank=True,
        verbose_name="Descrição",
        help_text="Breve descrição do personagem (cuidado com spoilers!)"
    )
    
    image = models.ImageField(
        upload_to='literary_universes/characters/',
        blank=True,
        null=True,
        verbose_name="Imagem"
    )
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='supporting',
        verbose_name="Papel"
    )
    
    display_order = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordem"
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name="Ativo"
    )
    
    class Meta:
        verbose_name = "Personagem"
        verbose_name_plural = "Personagens"
        ordering = ['display_order', 'name']
    
    def __str__(self):
        return f'{self.name} ({self.get_role_display()})'


class UniverseCollection(models.Model):
    """
    Coleção / agrupamento temático de universos literários.
    Permite organizar universos em grupos como "Fantasia", "Ficção Científica",
    "Mangás", "Universos da Marvel", etc.
    Preparação futura para quando houver dezenas/centenas de universos.
    """
    
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nome da Coleção",
        help_text='Ex: "Fantasia Épica", "Ficção Científica", "Mangás"'
    )
    
    slug = models.SlugField(
        unique=True,
        verbose_name="Slug",
        help_text="Identificador na URL"
    )
    
    description = models.TextField(
        blank=True,
        verbose_name="Descrição"
    )
    
    icon = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Ícone",
        help_text="Classe Font Awesome (ex: fa-dragon, fa-rocket)"
    )
    
    cover_image = models.ImageField(
        upload_to='literary_universes/collections/',
        blank=True,
        null=True,
        verbose_name="Imagem de Capa"
    )
    
    display_order = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordem"
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name="Ativo"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em"
    )
    
    class Meta:
        verbose_name = "Coleção de Universos"
        verbose_name_plural = "Coleções de Universos"
        ordering = ['display_order', 'name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
