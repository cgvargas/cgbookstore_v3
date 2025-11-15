"""
Admin para Video
"""
from django.contrib import admin
from django.utils.html import format_html
from core.models import Video


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    """Administração de Vídeos."""

    list_display = [
        'thumbnail_preview',
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
    readonly_fields = ['thumbnail_preview_large', 'created_at', 'updated_at']
    list_editable = ['featured', 'active']
    date_hierarchy = 'created_at'

    # Autocomplete
    autocomplete_fields = ['related_book', 'related_author']

    def thumbnail_preview(self, obj):
        """Preview pequeno da thumbnail na lista."""
        if obj.thumbnail_url:
            return format_html(
                '<img src="{}" style="width: 80px; height: 45px; object-fit: cover; border-radius: 4px;" />',
                obj.thumbnail_url
            )
        return format_html('<span style="color: #999;">Sem thumbnail</span>')
    thumbnail_preview.short_description = 'Preview'

    def thumbnail_preview_large(self, obj):
        """Preview grande da thumbnail no formulário de edição."""
        if obj.thumbnail_url:
            return format_html(
                '<div style="margin: 10px 0;">'
                '<img src="{}" style="max-width: 400px; max-height: 225px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);" />'
                '<p style="margin-top: 8px; color: #666; font-size: 12px;">Preview da Thumbnail</p>'
                '</div>',
                obj.thumbnail_url
            )
        return format_html('<p style="color: #999;">Nenhuma thumbnail disponível</p>')
    thumbnail_preview_large.short_description = 'Preview da Thumbnail'

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
                'duration'
            )
        }),
        ('Thumbnail', {
            'fields': (
                'thumbnail_image',
                'thumbnail_url',
                'thumbnail_preview_large',
            ),
            'description': (
                '<strong>Como adicionar thumbnail:</strong><br>'
                '<strong>Opção 1 (Upload Manual):</strong> Envie uma imagem do seu computador usando o campo "Upload de Thumbnail" '
                '(recomendado para Instagram).<br>'
                '<strong>Opção 2 (Automático):</strong> Deixe vazio e a thumbnail será extraída automaticamente da URL do vídeo '
                '(funciona melhor para YouTube e Vimeo).<br>'
                '<strong>Opção 3 (URL Manual):</strong> Cole a URL de uma imagem externa no campo "URL da Thumbnail".<br>'
                '<em>Nota: O upload manual tem prioridade sobre a extração automática.</em>'
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