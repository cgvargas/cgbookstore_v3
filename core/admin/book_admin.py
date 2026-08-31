"""
Admin para Book
"""
import logging
from django import forms
from django.contrib import admin, messages
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.contenttypes.models import ContentType
from django.db.models.functions import ExtractYear
from core.models import Book, Video, Section, SectionItem
from core.admin.image_rights_admin import ImageRightsRecordInline
from core.services.image_rights_service import ImageRightsAuditService
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
    existing_videos = forms.ModelMultipleChoiceField(
        queryset=Video.objects.only('id', 'title').order_by('title'),
        required=False,
        widget=FilteredSelectMultiple("Vídeos/Adaptações", is_stacked=False),
        label="🎬 Vídeos e Adaptações Vinculados",
        help_text="Selecione ou pesquise vídeos já cadastrados no banco de dados para vinculá-los a este livro (digite as iniciais no filtro para localizar)."
    )
    target_section = forms.ModelChoiceField(
        queryset=Section.objects.none(),
        required=False,
        label="📌 Destacar na Seção da Home",
        help_text="Selecione uma seção da Home Page para colocar este livro em 1º lugar (o último livro será rotacionado/removido se a seção atingir o limite)."
    )

    class Meta:
        model = Book
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['target_section'].queryset = Section.objects.filter(
            active=True,
            content_type__in=['books', 'mixed']
        ).order_by('order', 'title')

        if self.instance and self.instance.pk:
            self.fields['existing_articles'].initial = self.instance.articles.all()
            self.fields['existing_videos'].initial = self.instance.videos.all()
            # Tentar pré-selecionar a seção atual do livro se já estiver em alguma
            try:
                book_ct = ContentType.objects.get_for_model(Book)
                item = SectionItem.objects.filter(
                    content_type=book_ct,
                    object_id=self.instance.pk,
                    active=True
                ).select_related('section').first()
                if item:
                    self.fields['target_section'].initial = item.section
            except Exception as e:
                logger.debug(f"[BOOK ADMIN FORM] Não foi possível carregar seção inicial: {e}")

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
        
        def save_m2m_relations():
            if book.pk:
                book.articles.set(self.cleaned_data['existing_articles'])
                book.videos.set(self.cleaned_data['existing_videos'])

        if commit:
            book.save()
            self.save_m2m()
            save_m2m_relations()
        else:
            old_save_m2m = self.save_m2m
            def new_save_m2m():
                old_save_m2m()
                save_m2m_relations()
            self.save_m2m = new_save_m2m
            
        return book


class VideoInline(admin.TabularInline):
    """Inline para vincular/criar novos vídeos diretamente no livro."""
    model = Video.related_books.through
    extra = 0
    min_num = 0
    verbose_name = '🎬 Criar Novo Vídeo'
    verbose_name_plural = '🎬 Criar Novos Vídeos Vinculados'
    classes = ['collapse']



@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """Administração de Livros com autocomplete de autor."""

    form = BookAdminForm
    inlines = [VideoInline, ImageRightsRecordInline]

    # Otimização: Evitar N+1 queries ao listar livros
    list_select_related = ['author', 'category']

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
        'title',
        'subtitle',
        'author__name',
        'isbn',
        'google_books_id',
    ]
    actions = ['sync_metadata_with_amazon']

    @admin.action(description="📦 Sincronizar metadados com Amazon Brasil e Google Books")
    def sync_metadata_with_amazon(self, request, queryset):
        """Ação administrativa para enriched metadata."""
        from core.services.book_metadata_aggregator import BookMetadataAggregator
        count = 0
        for book in queryset:
            res = BookMetadataAggregator.fetch_and_enrich_book(book)
            if res.get('changes'):
                count += 1
        self.message_user(
            request,
            f"✅ {count} de {queryset.count()} livro(s) foram sincronizados com sucesso via Amazon Brasil e fontes agregadas."
        )

    # Autocomplete para Author e Category
    autocomplete_fields = ['author', 'category']

    # Gerar slug automaticamente a partir do título
    prepopulated_fields = {'slug': ('title',)}

    # Campos somente leitura (necessário para listar auto_now_add/auto_now em fieldsets)
    readonly_fields = ('created_at', 'updated_at')



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
        ('📌 Destaque na Seção da Home', {
            'fields': (
                'target_section',
            ),
            'description': '💡 Selecione a seção da Home Page onde este livro deve entrar em 1º lugar (ex: Lançamentos, Mais Vendidos). O último livro da seção será rotacionado/removido se atingir o limite.',
        }),
        ('🎬 Vídeos e Adaptações Vinculados', {
            'fields': (
                'existing_videos',
            ),
            'description': 'Pesquise por iniciais ou título na caixa da esquerda para vincular vídeos já cadastrados no banco de dados a este livro.'
        }),
        ('📰 Artigos e Notícias Vinculados', {
            'fields': (
                'existing_articles',
            ),
            'description': 'Pesquise por iniciais ou título na caixa da esquerda para vincular notícias ou artigos já cadastrados a este livro.'
        }),
        ('Detalhes de Publicação e Créditos', {
            'fields': (
                'publication_date',
                'isbn',
                'publisher',
                'page_count',
                'language',
                'reading_age',
                ('has_illustrator', 'illustrator_name')
            ),
            'description': 'Informações de catálogo, faixa etária e créditos legais do ilustrador.'
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
        ('Análise de IA & Metadados', {
            'classes': ('collapse',),
            'fields': (
                'ai_expanded_analysis',
                'created_at',
                'updated_at'
            ),
            'description': '💡 Conteúdo da Análise Expandida da IA (JSON) editável diretamente pelo administrador.'
        }),
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

        anos = (
            Book.objects
            .annotate(ano=ExtractYear('publication_date'))
            .values_list('ano', flat=True)
            .distinct()
            .order_by('-ano')
        )
        extra_context['anos_disponiveis'] = [a for a in anos if a]
        extra_context['ano_selecionado'] = request.GET.get('publication_date__year', '')

        return super().changelist_view(request, extra_context=extra_context)

    def save_model(self, request, obj, form, change):
        """Sobrescreve save_model para associar capa de IA e automatizar inserção em Seção da Home."""
        temp_cover_image = form.cleaned_data.get('temp_cover_image') or request.POST.get('temp_cover_image')
        logger.info("ADMIN SAVE MODEL - temp_cover_image resolved: %s", temp_cover_image)
        logger.info("ADMIN SAVE MODEL - current obj.cover_image: %s (bool: %s)", obj.cover_image, bool(obj.cover_image))
        
        if temp_cover_image:
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
                    default_storage.delete(temp_cover_image)
                except Exception as e:
                    logger.error("ADMIN SAVE MODEL - Erro ao salvar capa da IA: %s", e, exc_info=True)
                    self.message_user(request, f"Aviso: Não foi possível salvar a imagem da capa do livro via IA: {e}", level=messages.WARNING)
            else:
                logger.warning("ADMIN SAVE MODEL - Arquivo temporário de capa não existe no storage: %s", temp_cover_image)
        
        super().save_model(request, obj, form, change)
        ImageRightsAuditService.audit_model_admin_save(request, obj)

        # Automação de inserção/rotação em Seção da Home
        target_section = form.cleaned_data.get('target_section')
        if target_section:
            from core.services.section_service import insert_book_into_section
            success, msg = insert_book_into_section(obj, target_section)
            if success:
                self.message_user(request, f"✅ {msg}", level=messages.SUCCESS)
            else:
                self.message_user(request, f"⚠️ {msg}", level=messages.WARNING)
        elif not change:
            # Ao criar um novo livro sem seção manual selecionada, tentar auto-detectar categoria 'Lançamentos'
            from core.services.section_service import auto_detect_and_insert_book_section
            processed, msg = auto_detect_and_insert_book_section(obj)
            if processed:
                self.message_user(request, f"🚀 [Auto-Seção] {msg}", level=messages.SUCCESS)