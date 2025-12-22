"""
Admin para Section e SectionItem - Versão Ultra-Leve
Removido: dropdowns customizados, item_preview
Motivo: Formulário anterior levava 240+ segundos para carregar
"""
from django import forms
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.utils.html import format_html
from django.core.exceptions import ValidationError
from core.models import Section, SectionItem, Book, Author, Video


class SectionItemInline(admin.TabularInline):
    """Inline SIMPLIFICADO para gerenciar itens dentro de uma seção.
    
    NOTA: Para adicionar itens, selecione o content_type e digite o object_id.
    Para descobrir o ID de um livro/autor/vídeo, vá na lista correspondente.
    """
    
    model = SectionItem
    extra = 1
    # Campos mínimos - sem dropdowns pesados
    fields = ['content_type', 'object_id', 'order', 'active']
    
    # Sem readonly_fields que causam queries extras
    # Sem form customizado que carrega dropdowns

    def get_queryset(self, request):
        """Queryset otimizado - apenas select_related básico."""
        return super().get_queryset(request).select_related('content_type').order_by('order')


class SectionAdminForm(forms.ModelForm):
    """Form customizado para Section com textarea para CSS."""

    custom_css = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 10,
            'cols': 80,
            'style': 'font-family: monospace; font-size: 13px;',
            'placeholder': '/* Adicione seu CSS customizado aqui */\n\n.my-custom-class {\n    /* seus estilos */\n}'
        }),
        label="CSS Personalizado",
        help_text="CSS customizado para esta seção (será inserido dentro de uma tag &lt;style&gt;)"
    )

    class Meta:
        model = Section
        fields = '__all__'


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    """Administração de Seções da Home."""

    form = SectionAdminForm

    list_display = [
        'title',
        'content_type',
        'layout',
        'banner_preview',
        'card_style',
        'card_hover_effect',
        'active',
        'order',
        'items_count',
        'created_at'
    ]
    list_filter = [
        'content_type',
        'layout',
        'card_style',
        'card_hover_effect',
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
            ),
            'description': 'URLs sugeridas: /livros/ (livros), /autores/ (autores), /videos/ (vídeos), /eventos/ (eventos)'
        }),
        ('Personalização de Cards', {
            'fields': (
                'card_style',
                'card_hover_effect',
                'show_price',
                'show_rating',
                'show_author'
            ),
            'description': 'Configure a aparência e comportamento dos cards desta seção'
        }),
        ('Banner da Seção', {
            'classes': ('collapse',),
            'fields': (
                'banner_image',
                'banner_image_preview',
                'banner_height',
                ('banner_position_vertical', 'banner_position_horizontal'),
            ),
            'description': 'Configure a imagem de banner para a seção'
        }),
        ('Efeitos Visuais do Banner', {
            'classes': ('collapse',),
            'fields': (
                'banner_overlay_opacity',
                ('banner_blur_edges', 'banner_blur_intensity'),
            ),
            'description': (
                'Overlay: Escurecimento sobre a imagem do banner (0.0-1.0, recomendado: 0.4-0.6)<br>'
                'Desfoque: Aplica fade gradual nas bordas superior e inferior (60-120px)'
            )
        }),
        ('Estilo Visual Avançado', {
            'classes': ('collapse',),
            'fields': (
                'background_color',
                'container_opacity',
                'css_class',
                'custom_css'
            ),
            'description': 'Configurações avançadas de estilo. Use CSS customizado para criar estilos únicos.'
        }),
        ('Timestamps', {
            'classes': ('collapse',),
            'fields': (
                'created_at',
                'updated_at'
            )
        })
    )

    readonly_fields = ['created_at', 'updated_at', 'banner_image_preview']

    def banner_preview(self, obj):
        """Exibe preview do banner na lista."""
        if obj.banner_image:
            return format_html(
                '<img src="{}" style="width: 60px; height: 30px; object-fit: cover; border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);" />',
                obj.banner_image.url
            )
        return format_html('<span style="color: #999;">Sem banner</span>')

    banner_preview.short_description = 'Banner'

    def banner_image_preview(self, obj):
        """Exibe preview da imagem de banner no formulário."""
        if obj.banner_image:
            return format_html(
                '<div style="margin-top: 10px;">'
                '<img src="{}" style="max-width: 100%; max-height: 300px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);" />'
                '<p style="margin-top: 8px; color: #666; font-size: 12px;">Preview do banner atual</p>'
                '</div>',
                obj.banner_image.url
            )
        return format_html('<p style="color: #999; font-style: italic;">Nenhuma imagem de banner carregada</p>')

    banner_image_preview.short_description = 'Preview do Banner'

    def items_count(self, obj):
        """Retorna quantidade de itens ativos na seção."""
        count = obj.items.filter(active=True).count()
        total = obj.items.count()

        if count == 0:
            color = 'red'
        elif count < total:
            color = 'orange'
        else:
            color = 'green'

        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span> / {}',
            color, count, total
        )

    items_count.short_description = 'Itens (Ativos/Total)'