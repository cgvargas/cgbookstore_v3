"""
Admin para Category
"""
from django.contrib import admin
from core.models import Category


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