"""
Admin para Book
"""
import logging
from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.db.models.functions import ExtractYear
from core.models import Book, Video
from news.models import Article

logger = logging.getLogger(__name__)


class BookAdminForm(forms.ModelForm):
    temp_cover_image = forms.CharField(widget=forms.HiddenInput(), required=False)
    existing_articles = forms.ModelMultipleChoiceField(
        # Otimização: only() carrega apenas os campos necessários para o widget,
        # evitando trazer o body/conteúdo completo de cada artigo.
        queryset=Article.objects.only('id', 'title').order_by('title'),
        required=False,
        widget=FilteredSelectMultiple("Artigos/Notícias", is_stacked=False),
        label="Artigos e Notícias Vinculados",
        help_text="Selecione os artigos/notícias já criados para vinculá-los a este livro."
    )

    class Meta:
        model = Book
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['existing_articles'].initial = self.instance.articles.all()

    def clean_purchase_partner_url(self):
        url = self.cleaned_data.get('purchase_partner_url')
        partner_name = (self.cleaned_data.get('purchase_partner_name') or '').strip()

        if url:
            from partners.services.amazon_service import AmazonURLNormalizer

            is_amazon_partner = partner_name.lower() == 'amazon'
            is_amazon_domain = AmazonURLNormalizer.is_amazon_url(url)

            if is_amazon_partner or is_amazon_domain:
                try:
                    return AmazonURLNormalizer.normalize(url)
                except ValueError as exc:
                    raise forms.ValidationError(
                        f"URL da Amazon inválida ou ASIN não localizado: {exc}"
                    )
        return url


    def save(self, commit=True):
        book = super().save(commit=False)
        
        def save_m2m_articles():
            if book.pk:
                book.articles.set(self.cleaned_data['existing_articles'])

        if commit:
            book.save()
            self.save_m2m()
            save_m2m_articles()
        else:
            old_save_m2m = self.save_m2m
            def new_save_m2m():
                old_save_m2m()
                save_m2m_articles()
            self.save_m2m = new_save_m2m
            
        return book


class VideoInline(admin.TabularInline):
    """Inline para vincular vídeos ao livro."""
    model = Video
    fk_name = 'related_book'
    extra = 0
    min_num = 0
    fields = ['title', 'platform', 'video_url', 'video_type', 'thumbnail_image', 'active']
    verbose_name = '🎬 Vídeo Vinculado'
    verbose_name_plural = '🎬 Vídeos Vinculados (Adaptações, Trailers, Entrevistas)'
    classes = ['collapse']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('related_book')





@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """Administração de Livros com autocomplete de autor."""

    form = BookAdminForm

    # Otimização: Evitar N+1 queries ao listar livros
    list_select_related = ['author', 'category']

    # Inlines para vincular vídeos
    inlines = [VideoInline]

    list_display = [
        'title',
        'author',
        'category',
        'price',
        'is_presale',
        'purchase_partner_name',
        'average_rating',
        'has_google_books_data',
        'publication_date',
        'created_at'
    ]
    list_filter = [
        'category',
        'language',
        'is_presale',
        'publication_date',
        'created_at',
        'author'
    ]
    search_fields = [
        # PERFORMANCE: Prefixo '^' usa LIKE 'texto%' (pode usar índice B-tree)
        # vs busca padrão que usa LIKE '%texto%' (full scan, sem índice)
        '^title',
        'subtitle',
        'author__name',
        'isbn',
        'google_books_id',
        # REMOVIDO: 'description' — TextField longo sem índice.
        # Busca com LIKE '%...%' em TextField causava queries de 60+ segundos.
        # Para busca full-text em descrições, considere PostgreSQL SearchVector + GIN index.
    ]
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'publication_date'

    # Autocomplete para Author e Category
    autocomplete_fields = ['author', 'category']

    fieldsets = (
        ('Informações Principais', {
            'fields': (
                'title',
                'subtitle',
                'slug',
                'author',
                'category',
                'description'
            )
        }),
        ('Detalhes de Publicação', {
            'fields': (
                'publication_date',
                'isbn',
                'publisher',
                'page_count',
                'language'
            )
        }),
        ('Compra e Imagens', {
            'fields': (
                'price',
                'purchase_partner_name',
                'purchase_partner_url',
                'cover_image',
                'temp_cover_image'
            ),
            'description': 'Configure o preço médio de mercado e o parceiro comercial onde o livro pode ser adquirido'
        }),
        ('Formatos de Leitura Disponíveis', {
            'fields': (
                ('available_print', 'available_kindle',
                 'available_audiobook', 'available_pdf'),
            ),
            'description': 'Selecione os formatos em que este livro está disponível para o leitor'
        }),
        ('Integração Google Books', {
            'classes': ('collapse',),
            'fields': (
                'google_books_id',
                'average_rating',
                'ratings_count',
                'preview_link',
                'info_link'
            ),
            'description': 'Campos preenchidos automaticamente ao importar do Google Books API'
        }),
        ('Pré-Venda / Lançamento', {
            'fields': (
                'is_presale',
                'presale_release_date',
                'presale_info',
            ),
            'description': '✅ Ative para exibir o banner verde de pré-venda na página do livro',
        }),
        ('Destaque e Mensagens', {
            'fields': (
                'show_highlight',
                'highlight_message',
            ),
            'description': '💡 Use para exibir anúncios ou informações importantes em destaque (cor verde).',
        }),
        ('Artigos e Notícias', {
            'fields': (
                'existing_articles',
            ),
            'description': 'Selecione as notícias ou artigos deste livro.'
        }),
        ('Metadados', {
            'classes': ('collapse',),
            'fields': (
                'created_at',
                'updated_at'
            )
        })
    )

    def has_google_books_data(self, obj):
        """Indica se o livro tem dados do Google Books."""
        return '✓' if obj.has_google_books_data else '✗'

    has_google_books_data.short_description = 'Google Books'

    def changelist_view(self, request, extra_context=None):
        """
        Injeta no contexto a lista de anos disponíveis e o ano
        atualmente selecionado para o dropdown de filtro rápido por ano.
        """
        extra_context = extra_context or {}

        # Anos distintos de publication_date presentes no banco
        anos = (
            Book.objects
            .annotate(ano=ExtractYear('publication_date'))
            .values_list('ano', flat=True)
            .distinct()
            .order_by('-ano')
        )
        extra_context['anos_disponiveis'] = [a for a in anos if a]

        # Ano atualmente filtrado (via GET ?publication_date__year=XXXX)
        extra_context['ano_selecionado'] = request.GET.get('publication_date__year', '')

        return super().changelist_view(request, extra_context=extra_context)

    def save_model(self, request, obj, form, change):
        """Sobrescreve save_model para associar a imagem de capa baixada temporariamente pela IA."""
        temp_cover_image = form.cleaned_data.get('temp_cover_image') or request.POST.get('temp_cover_image')
        logger.info("ADMIN SAVE MODEL - temp_cover_image resolved: %s", temp_cover_image)
        logger.info("ADMIN SAVE MODEL - current obj.cover_image: %s (bool: %s)", obj.cover_image, bool(obj.cover_image))
        
        if temp_cover_image:
            # Se o usuário não enviou um arquivo manualmente e temos capa da IA
            if not obj.cover_image:
                from django.core.files.storage import default_storage
                import os
                
                logger.info("ADMIN SAVE MODEL - temp_cover_image: %s (exists in storage: %s)", 
                            temp_cover_image, default_storage.exists(temp_cover_image))
                
                if default_storage.exists(temp_cover_image):
                    try:
                        with default_storage.open(temp_cover_image) as f:
                            base_name = os.path.basename(temp_cover_image).replace('temp_', '')
                            obj.cover_image.save(base_name, f, save=False)
                        logger.info("ADMIN SAVE MODEL - Capa da IA salva com sucesso: %s", obj.cover_image)
                        # Tentar remover o arquivo temporário do storage
                        default_storage.delete(temp_cover_image)
                    except Exception as e:
                        logger.error("ADMIN SAVE MODEL - Erro ao salvar capa da IA: %s", e, exc_info=True)
                        self.message_user(request, f"Aviso: Não foi possível salvar a imagem da capa do livro via IA: {e}", level='WARNING')
                else:
                    logger.warning("ADMIN SAVE MODEL - Arquivo temporário de capa não existe no storage: %s", temp_cover_image)
            else:
                logger.info("ADMIN SAVE MODEL - Capa do livro já estava preenchida pelo usuário: %s", obj.cover_image)
        
        super().save_model(request, obj, form, change)