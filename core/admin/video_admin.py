"""
Admin para Video
"""
from django.contrib import admin
from core.models import Video


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    """Administração de Vídeos."""

    list_display = [
        'title',
        'platform',
        'video_type',
        'get_related_books',
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
        'related_books__title',
        'related_author__name'
    ]
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['featured', 'active']
    date_hierarchy = 'created_at'

    filter_horizontal = ('related_books',)
    autocomplete_fields = ['related_author']

    def get_related_books(self, obj):
        return ", ".join([b.title for b in obj.related_books.all()[:3]]) or "-"
    get_related_books.short_description = "Livros Relacionados"

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
                'video_file',
                'embed_code',
                'thumbnail_image',
                'thumbnail_url',
                'duration'
            ),
            'description': 'Para YouTube, Vimeo, Instagram ou TikTok: use URL do Vídeo. Para arquivos locais: selecione "Upload de Arquivo" e envie o arquivo MP4/WebM.'
        }),
        ('Relacionamentos', {
            'fields': (
                'related_books',
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