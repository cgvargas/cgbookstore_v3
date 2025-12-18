# core/admin/featured_author_settings_admin.py
"""
Admin para configuração de Autor em Destaque.
Interface amigável para editar seção da home e página dedicada.
"""

from django.contrib import admin
from django.utils.html import format_html
from core.models import FeaturedAuthorSettings


@admin.register(FeaturedAuthorSettings)
class FeaturedAuthorSettingsAdmin(admin.ModelAdmin):
    """Admin para FeaturedAuthorSettings com preview e organização por fieldsets."""
    
    list_display = [
        'author_display',
        'home_title',
        'is_active',
        'banner_preview_small',
        'updated_at',
    ]
    list_filter = ['is_active', 'author']
    list_editable = ['is_active']
    search_fields = ['author__name', 'home_title', 'page_title']
    readonly_fields = ['created_at', 'updated_at', 'banner_preview']
    autocomplete_fields = ['author']
    
    fieldsets = (
        ('Configuração Principal', {
            'fields': ('author', 'is_active'),
            'description': 'Selecione o autor e ative/desative a seção na home.'
        }),
        ('Seção na Home', {
            'fields': (
                'home_subtitle',
                'home_title',
                'home_description',
                'home_banner_image',
                'banner_preview',
                'home_button_text',
                'home_button_icon',
                'stat_badge_1',
                'stat_badge_2',
            ),
            'classes': ('wide',),
            'description': 'Configure como a seção aparece na página inicial.'
        }),
        ('Página Dedicada', {
            'fields': (
                'page_title',
                'page_description',
            ),
            'classes': ('wide',),
            'description': 'Configure o conteúdo da página dedicada ao autor.'
        }),
        ('SEO', {
            'fields': ('page_meta_title', 'page_meta_description'),
            'classes': ('collapse',),
            'description': 'Configurações para otimização em mecanismos de busca.'
        }),
        ('Informações', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    def author_display(self, obj):
        """Exibe nome do autor com foto se disponível"""
        if obj.author.photo:
            return format_html(
                '<img src="{}" style="width:30px;height:30px;border-radius:50%;margin-right:8px;object-fit:cover;">'
                '<strong>{}</strong>',
                obj.author.photo.url,
                obj.author.name
            )
        return format_html('<strong>{}</strong>', obj.author.name)
    author_display.short_description = 'Autor'
    author_display.admin_order_field = 'author__name'
    
    def banner_preview(self, obj):
        """Preview grande do banner"""
        if obj.home_banner_image:
            return format_html(
                '<img src="{}" style="max-width:600px;max-height:200px;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,0.2);">',
                obj.home_banner_image.url
            )
        return format_html(
            '<span style="color:#999;font-style:italic;">Nenhum banner configurado</span>'
        )
    banner_preview.short_description = 'Preview do Banner'
    
    def banner_preview_small(self, obj):
        """Preview pequeno para lista"""
        if obj.home_banner_image:
            return format_html(
                '<img src="{}" style="width:80px;height:30px;object-fit:cover;border-radius:4px;">',
                obj.home_banner_image.url
            )
        return format_html('<span style="color:#ccc;">—</span>')
    banner_preview_small.short_description = 'Banner'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('author')
    
    class Media:
        css = {
            'all': ('admin/css/forms.css',)
        }
