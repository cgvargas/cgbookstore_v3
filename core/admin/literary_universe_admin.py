# core/admin/literary_universe_admin.py
"""
Admin para Universos Literários.
Configuração completa com inlines para conteúdo e banners.
"""

from django.contrib import admin
from django.utils.html import format_html
from core.models import LiteraryUniverse, UniverseContentItem, UniverseBanner


class UniverseContentItemInline(admin.TabularInline):
    """Inline para itens de conteúdo (games, adaptações, etc.)."""
    model = UniverseContentItem
    extra = 0
    fields = ['content_type', 'title', 'url', 'thumbnail', 'display_order', 'is_active']
    ordering = ['content_type', 'display_order']


class UniverseBannerInline(admin.TabularInline):
    """Inline para banners promocionais."""
    model = UniverseBanner
    extra = 0
    fields = ['title', 'position', 'size', 'image', 'is_active', 'display_order']
    ordering = ['position', 'display_order']


@admin.register(LiteraryUniverse)
class LiteraryUniverseAdmin(admin.ModelAdmin):
    """Admin completo para Universos Literários."""
    
    list_display = [
        'title', 
        'author', 
        'is_active', 
        'show_in_menu',
        'display_order',
        'color_preview',
        'view_link',
    ]
    
    list_filter = ['is_active', 'show_in_menu']
    list_editable = ['is_active', 'show_in_menu', 'display_order']
    search_fields = ['title', 'author__name']
    prepopulated_fields = {'slug': ('title',)}
    autocomplete_fields = ['author', 'videos']
    filter_horizontal = ['articles']  # Usa widget filtrado para artigos
    
    inlines = [UniverseContentItemInline, UniverseBannerInline]
    
    fieldsets = (
        ('Identificação', {
            'fields': ('title', 'slug', 'author', 'is_active', 'show_in_menu', 'display_order')
        }),
        ('Visual / Tema', {
            'fields': (
                'hero_banner_image', 
                ('hero_banner_position_horizontal', 'hero_banner_position_vertical'),
                'hero_banner_overlay_opacity',
                'hero_icon', 
                ('theme_color_primary', 'theme_color_secondary')
            ),
        }),
        ('Layout - Livros', {
            'fields': (
                ('books_card_style', 'books_container_style'),
            ),
            'classes': ('collapse',),
        }),
        ('Layout - Artigos', {
            'fields': (
                ('articles_card_style', 'articles_container_style'),
            ),
            'classes': ('collapse',),
        }),
        ('Layout - Vídeos', {
            'fields': (
                ('videos_card_style', 'videos_container_style'),
            ),
            'classes': ('collapse',),
        }),
        ('Layout - Conteúdo Adicional', {
            'fields': (
                ('content_card_style', 'content_container_style'),
            ),
            'classes': ('collapse',),
        }),
        ('Textos da Página', {
            'fields': ('page_subtitle', 'page_title', 'page_description')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',),
        }),
        ('Conteúdo Associado', {
            'fields': ('videos', 'articles'),
            'description': 'Selecione vídeos e artigos para exibir neste universo (além da busca automática).'
        }),
    )
    
    def color_preview(self, obj):
        """Exibe preview das cores do tema."""
        return format_html(
            '<span style="display: inline-block; width: 20px; height: 20px; '
            'background: {}; border-radius: 3px; margin-right: 5px;"></span>'
            '<span style="display: inline-block; width: 20px; height: 20px; '
            'background: {}; border-radius: 3px;"></span>',
            obj.theme_color_primary,
            obj.theme_color_secondary
        )
    color_preview.short_description = 'Cores'
    
    def view_link(self, obj):
        """Link para visualizar a página."""
        if obj.is_active:
            return format_html(
                '<a href="/universo/{}/" target="_blank" class="button">'
                '<i class="fas fa-external-link-alt"></i> Ver</a>',
                obj.slug
            )
        return '-'
    view_link.short_description = 'Visualizar'


@admin.register(UniverseContentItem)
class UniverseContentItemAdmin(admin.ModelAdmin):
    """Admin standalone para itens de conteúdo."""
    list_display = ['title', 'universe', 'content_type', 'is_active', 'display_order']
    list_filter = ['universe', 'content_type', 'is_active']
    search_fields = ['title', 'description']
    list_editable = ['is_active', 'display_order']
    autocomplete_fields = ['universe']


@admin.register(UniverseBanner)
class UniverseBannerAdmin(admin.ModelAdmin):
    """Admin standalone para banners."""
    list_display = [
        'title', 
        'universe', 
        'position', 
        'size', 
        'is_active',
        'banner_preview',
        'visibility_status',
    ]
    list_filter = ['universe', 'position', 'size', 'is_active']
    search_fields = ['title', 'alt_text']
    list_editable = ['is_active']
    autocomplete_fields = ['universe']
    
    fieldsets = (
        ('Básico', {
            'fields': ('universe', 'title', 'is_active')
        }),
        ('Imagens', {
            'fields': ('image', 'image_mobile', 'alt_text')
        }),
        ('Posicionamento', {
            'fields': ('position', 'size', 'display_order')
        }),
        ('Link', {
            'fields': ('link_url', 'link_target')
        }),
        ('Agendamento', {
            'fields': ('start_date', 'end_date'),
            'classes': ('collapse',),
        }),
    )
    
    def banner_preview(self, obj):
        """Preview do banner."""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 100px; max-height: 50px; border-radius: 4px;">',
                obj.image.url
            )
        return '-'
    banner_preview.short_description = 'Preview'
    
    def visibility_status(self, obj):
        """Status de visibilidade baseado em datas."""
        if obj.is_visible():
            return format_html('<span style="color: green;">✓ Visível</span>')
        return format_html('<span style="color: red;">✗ Oculto</span>')
    visibility_status.short_description = 'Status'
