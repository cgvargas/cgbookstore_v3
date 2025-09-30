"""
Configuração do Django Admin para os models do Core.
"""

from django.contrib import admin
from core.models import Category, Author, Book


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Administração de Categorias."""

    list_display = ['name', 'slug', 'featured', 'created_at']
    list_filter = ['featured', 'created_at']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['featured']
    date_hierarchy = 'created_at'


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    """Administração de Autores."""

    list_display = ['name', 'slug', 'created_at']
    search_fields = ['name', 'bio']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """Administração de Livros com suporte a Google Books API."""

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
        return '✅' if obj.has_google_books_data else '❌'

    has_google_books_data.short_description = 'Google Books'