"""
Admin para Author
"""
from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from core.models import Author, Book


class BookInline(admin.TabularInline):
    """
    Inline SOMENTE LEITURA para exibir livros do autor.
    
    IMPORTANTE: Este inline é apenas para visualização.
    Para associar um livro a um autor, edite o livro diretamente
    e selecione o autor no campo correspondente.
    
    Isso evita a criação acidental de livros duplicados.
    """

    model = Book
    extra = 0  # Não mostrar formulários vazios
    max_num = 0  # IMPEDE adicionar novos livros por este inline
    can_delete = False  # Não permitir deletar
    show_change_link = True  # Link para editar o livro
    verbose_name = "Livro do Autor"
    verbose_name_plural = "Livros do Autor (somente visualização)"
    
    # Todos os campos são somente leitura
    fields = ['title', 'isbn', 'publication_date', 'cover_thumbnail']
    readonly_fields = ['title', 'isbn', 'publication_date', 'cover_thumbnail']
    
    def cover_thumbnail(self, obj):
        """Miniatura da capa do livro."""
        if obj.cover_image:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 35px; object-fit: cover; border-radius: 4px;" />',
                obj.cover_image.url
            )
        return "-"
    cover_thumbnail.short_description = "Capa"
    
    def has_add_permission(self, request, obj=None):
        """Impede adicionar livros por este inline."""
        return False



@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    """Administração de Autores com inline de livros."""

    list_display = ['name', 'photo_preview', 'books_count', 'social_media_display', 'created_at']
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
        return mark_safe('<span style="color: gray;">0 livros</span>')

    books_count.short_description = "Livros"

    def social_media_display(self, obj):
        """Indica se tem redes sociais cadastradas."""
        if obj.website or obj.twitter or obj.instagram:
            return mark_safe('<span style="color: green;">✓</span>')
        return mark_safe('<span style="color: gray;">✗</span>')

    social_media_display.short_description = "Redes Sociais"