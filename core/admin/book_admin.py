"""
Admin para Book
"""
from django.contrib import admin
from core.models import Book


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """Administração de Livros com autocomplete de autor."""

    list_display = [
        'title',
        'author',
        'category',
        'price',
        'purchase_partner_name',
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
        ('Compra e Imagens', {  # ← TÍTULO ATUALIZADO
            'fields': (
                'price',
                'purchase_partner_name',  # ← NOVO CAMPO
                'purchase_partner_url',  # ← NOVO CAMPO
                'cover_image'
            ),
            'description': 'Configure o preço médio de mercado e o parceiro comercial onde o livro pode ser adquirido'
            # ← NOVA DESCRIÇÃO
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