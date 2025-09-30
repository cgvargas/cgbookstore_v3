"""
Admin para Author
"""
from django.contrib import admin
from django.utils.html import format_html
from core.models import Author, Book


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