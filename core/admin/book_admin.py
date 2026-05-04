"""
Admin para Book
"""
from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from core.models import Book, Video
from news.models import Article


class BookAdminForm(forms.ModelForm):
    existing_articles = forms.ModelMultipleChoiceField(
        queryset=Article.objects.all(),
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
        'title',
        'subtitle',
        'author__name',
        'isbn',
        'google_books_id',
        'description'
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
                'cover_image'
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