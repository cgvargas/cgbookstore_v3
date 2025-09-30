"""
Configuração do Django Admin para os models do Core.
"""

from django.contrib import admin
from django.utils.html import format_html
from core.models import Category, Author, Book, Video, Section, SectionItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Administração de Categorias."""

    list_display = ['name', 'slug', 'featured', 'books_count', 'created_at']
    list_filter = ['featured', 'created_at']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['featured']
    date_hierarchy = 'created_at'

    def books_count(self, obj):
        """Quantidade de livros na categoria."""
        return obj.books.count()

    books_count.short_description = "Livros"


class BookInline(admin.TabularInline):
    """Inline para exibir livros do autor."""

    model = Book
    extra = 0
    fields = ['title', 'price', 'publication_date', 'cover_image']
    readonly_fields = ['cover_image']
    can_delete = False
    show_change_link = True
    verbose_name = "Livro do Autor"
    verbose_name_plural = "Livros do Autor"


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    """Administração de Autores com inline de livros."""

    list_display = ['name', 'photo_preview', 'books_count', 'has_social_media', 'created_at']
    search_fields = ['name', 'bio']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'photo_preview']
    date_hierarchy = 'created_at'
    inlines = [BookInline]

    fieldsets = (
        ('Informações Básicas', {
            'fields': ('name', 'slug', 'bio')
        }),
        ('Foto', {
            'fields': ('photo', 'photo_preview')
        }),
        ('Redes Sociais', {
            'classes': ('collapse',),
            'fields': ('website', 'twitter', 'instagram')
        }),
        ('Metadados', {
            'classes': ('collapse',),
            'fields': ('created_at',)
        })
    )

    def photo_preview(self, obj):
        """Preview da foto do autor."""
        if obj.photo:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 100px; border-radius: 50%;" />',
                obj.photo.url
            )
        return "Sem foto"

    photo_preview.short_description = "Preview"

    def books_count(self, obj):
        """Quantidade de livros do autor."""
        count = obj.books.count()
        if count > 0:
            return format_html(
                '<span style="color: green; font-weight: bold;">{} livros</span>',
                count
            )
        return format_html('<span style="color: gray;">0 livros</span>')

    books_count.short_description = "Livros"

    def has_social_media(self, obj):
        """Indica se tem redes sociais cadastradas."""
        if obj.website or obj.twitter or obj.instagram:
            return format_html('<span style="color: green;">✓</span>')
        return format_html('<span style="color: gray;">✗</span>')

    has_social_media.short_description = "Redes Sociais"


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """Administração de Livros com autocomplete de autor."""

    list_display = [
        'title',
        'author',
        'category',
        'price',
        'average_rating',
        'has_google_books_data',
        'publication_date',
        'created_at'
    ]
    list_filter = [
        'category',
        'language',
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

    # Autocomplete para Author
    autocomplete_fields = ['author', 'category']

    # Raw ID fields como alternativa (comentado)
    # raw_id_fields = ['author']

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
        ('Precificação e Imagens', {
            'fields': (
                'price',
                'cover_image'
            )
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


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    """Administração de Vídeos."""

    list_display = [
        'title',
        'platform',
        'video_type',
        'related_book',
        'related_author',
        'featured',
        'active',
        'created_at'
    ]
    list_filter = [
        'platform',
        'video_type',
        'featured',
        'active',
        'created_at'
    ]
    search_fields = [
        'title',
        'description',
        'related_book__title',
        'related_author__name'
    ]
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created_at', 'updated_at', 'embed_code', 'thumbnail_url']
    list_editable = ['featured', 'active']
    date_hierarchy = 'created_at'

    # Autocomplete
    autocomplete_fields = ['related_book', 'related_author']

    fieldsets = (
        ('Informações Básicas', {
            'fields': (
                'title',
                'slug',
                'description',
                'video_type'
            )
        }),
        ('Vídeo', {
            'fields': (
                'platform',
                'video_url',
                'embed_code',
                'thumbnail_url',
                'duration'
            )
        }),
        ('Relacionamentos', {
            'fields': (
                'related_book',
                'related_author'
            )
        }),
        ('Metadados', {
            'fields': (
                'views_count',
                'published_date',
                'featured',
                'active'
            )
        }),
        ('Timestamps', {
            'classes': ('collapse',),
            'fields': (
                'created_at',
                'updated_at'
            )
        })
    )


class SectionItemInline(admin.TabularInline):
    """Inline para gerenciar itens dentro de uma seção."""

    model = SectionItem
    extra = 1
    fields = ['content_type', 'object_id', 'order', 'active', 'custom_title']
    readonly_fields = []

    def get_queryset(self, request):
        """Retorna queryset ordenado."""
        qs = super().get_queryset(request)
        return qs.order_by('order')


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    """Administração de Seções da Home com inline para itens."""

    list_display = [
        'title',
        'content_type',
        'layout',
        'active',
        'order',
        'items_count',
        'created_at'
    ]
    list_filter = [
        'content_type',
        'layout',
        'active',
        'created_at'
    ]
    search_fields = ['title', 'subtitle']
    list_editable = ['active', 'order']
    date_hierarchy = 'created_at'
    inlines = [SectionItemInline]

    fieldsets = (
        ('Informações Básicas', {
            'fields': (
                'title',
                'subtitle',
                'content_type',
                'layout'
            )
        }),
        ('Configurações de Exibição', {
            'fields': (
                'active',
                'order',
                'items_per_row',
                'show_see_more',
                'see_more_url'
            )
        }),
        ('Estilo Visual', {
            'classes': ('collapse',),
            'fields': (
                'background_color',
                'css_class'
            )
        }),
        ('Timestamps', {
            'classes': ('collapse',),
            'fields': (
                'created_at',
                'updated_at'
            )
        })
    )

    readonly_fields = ['created_at', 'updated_at']

    def items_count(self, obj):
        """Retorna quantidade de itens ativos na seção."""
        return obj.items.filter(active=True).count()

    items_count.short_description = 'Itens Ativos'


@admin.register(SectionItem)
class SectionItemAdmin(admin.ModelAdmin):
    """Administração individual de itens de seção (backup, raramente usado)."""

    list_display = [
        'section',
        'content_object',
        'order',
        'active',
        'created_at'
    ]
    list_filter = [
        'section',
        'content_type',
        'active',
        'created_at'
    ]
    search_fields = [
        'section__title',
        'custom_title',
        'custom_description'
    ]
    list_editable = ['order', 'active']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Seção', {
            'fields': ('section',)
        }),
        ('Conteúdo', {
            'fields': (
                'content_type',
                'object_id'
            )
        }),
        ('Customização', {
            'fields': (
                'custom_title',
                'custom_description'
            )
        }),
        ('Controle', {
            'fields': (
                'order',
                'active'
            )
        })
    )


# Configurar autocomplete search para Category também
CategoryAdmin.search_fields = ['name']
AuthorAdmin.search_fields = ['name', 'bio']