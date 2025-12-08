"""
Admin personalizado para Crônica Semanal.
Interface intuitiva para edição de conteúdo e imagens no estilo jornal.
"""

from django.contrib import admin
from django.utils.html import format_html
from core.models import WeeklyChronicle


@admin.register(WeeklyChronicle)
class WeeklyChronicleAdmin(admin.ModelAdmin):
    """
    Admin personalizado para gerenciar a Crônica Semanal no estilo jornal tradicional.
    """

    list_display = [
        'title',
        'author_name',
        'week_period',
        'volume_issue',
        'is_published',
        'preview_link',
        'updated_at',
    ]

    list_filter = [
        'is_published',
        'published_date',
        'volume_number',
        'created_at',
    ]

    search_fields = [
        'title',
        'subtitle',
        'author_name',
        'introduction',
        'main_content',
    ]

    readonly_fields = [
        'created_at',
        'updated_at',
        'preview_featured_image',
        'preview_secondary_image',
        'preview_gallery_images',
    ]

    fieldsets = (
        ('📰 Informações da Edição', {
            'fields': (
                ('volume_number', 'issue_number'),
                ('week_start_date', 'week_end_date'),
                'published_date',
                'is_published',
            ),
            'description': 'Informações sobre volume, edição e período da crônica.'
        }),

        ('📝 Artigo Principal', {
            'fields': (
                'title',
                'subtitle',
                'author_name',
                'introduction',
                'main_content',
                'conclusion',
            ),
            'description': 'Conteúdo principal que aparece no topo da página.'
        }),

        ('🖼️ Imagem do Artigo Principal', {
            'fields': (
                'featured_image',
                'featured_image_ratio',
                'preview_featured_image',
            ),
            'description': 'Imagem que aparece no artigo principal.'
        }),

        ('⭐ Destaques da Semana (Sidebar)', {
            'fields': (
                'highlights_accomplishment',
                'highlights_social',
                'highlights_health',
                'highlights_learning',
                'highlights_personal',
            ),
            'description': 'Box lateral com destaques rápidos da semana.',
            'classes': ('collapse',),
        }),

        ('💬 Citações em Destaque', {
            'fields': (
                'quote',
                'quote_author',
                'quote_secondary',
                'quote_secondary_author',
            ),
            'description': 'Citações que aparecem em boxes especiais.',
            'classes': ('collapse',),
        }),

        ('🏠 Seção: Casa & Família', {
            'fields': (
                'section_home_title',
                'section_home_content',
                'secondary_image',
                'secondary_image_ratio',
                'preview_secondary_image',
            ),
            'description': 'Artigo sobre casa e família (opcional).',
            'classes': ('collapse',),
        }),

        ('💪 Seção: Saúde & Bem-Estar', {
            'fields': (
                'section_health_title',
                'section_health_content',
            ),
            'description': 'Artigo sobre saúde e bem-estar (opcional).',
            'classes': ('collapse',),
        }),

        ('🎭 Seção: Entretenimento & Cultura', {
            'fields': (
                'section_entertainment_title',
                'section_entertainment_content',
            ),
            'description': 'Artigo sobre entretenimento e cultura (opcional).',
            'classes': ('collapse',),
        }),

        ('🎨 Galeria de Imagens', {
            'fields': (
                ('gallery_image_1', 'gallery_image_1_ratio'),
                ('gallery_image_2', 'gallery_image_2_ratio'),
                ('gallery_image_3', 'gallery_image_3_ratio'),
                'preview_gallery_images',
            ),
            'description': 'Imagens adicionais para ilustrar as seções.',
            'classes': ('collapse',),
        }),

        ('🔍 SEO e Metadados', {
            'fields': (
                'meta_description',
                'created_at',
                'updated_at',
            ),
            'description': 'Informações para otimização de busca.',
            'classes': ('collapse',),
        }),
    )

    def week_period(self, obj):
        """Exibe o período da semana."""
        if obj.week_start_date and obj.week_end_date:
            return f"{obj.week_start_date.strftime('%d/%m')} - {obj.week_end_date.strftime('%d/%m/%Y')}"
        return obj.published_date.strftime('%d/%m/%Y')
    week_period.short_description = 'Período'

    def volume_issue(self, obj):
        """Exibe volume e edição."""
        return f"Vol. {obj.volume_number}, Ed. {obj.issue_number}"
    volume_issue.short_description = 'Volume/Edição'

    def preview_link(self, obj):
        """Link para visualizar a crônica no site."""
        if obj.pk:
            return format_html(
                '<a href="/cronica-semanal/" target="_blank" '
                'style="background: #ff6b35; color: white; padding: 5px 10px; '
                'border-radius: 4px; text-decoration: none; display: inline-block;">'
                '👁️ Visualizar</a>'
            )
        return '-'
    preview_link.short_description = 'Preview'

    def preview_featured_image(self, obj):
        """Pré-visualização da imagem principal."""
        if obj.featured_image:
            return format_html(
                '<div style="max-width: 400px;">'
                '<img src="{}" style="width: 100%; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">'
                '<p style="margin-top: 8px; color: #666; font-size: 12px;">Proporção: {}</p>'
                '</div>',
                obj.featured_image.url,
                obj.get_featured_image_ratio_display()
            )
        return format_html('<p style="color: #999;">Nenhuma imagem adicionada</p>')
    preview_featured_image.short_description = 'Preview da Imagem Principal'

    def preview_secondary_image(self, obj):
        """Pré-visualização da imagem secundária."""
        if obj.secondary_image:
            return format_html(
                '<div style="max-width: 400px;">'
                '<img src="{}" style="width: 100%; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">'
                '<p style="margin-top: 8px; color: #666; font-size: 12px;">Proporção: {}</p>'
                '</div>',
                obj.secondary_image.url,
                obj.get_secondary_image_ratio_display()
            )
        return format_html('<p style="color: #999;">Nenhuma imagem adicionada</p>')
    preview_secondary_image.short_description = 'Preview da Imagem Secundária'

    def preview_gallery_images(self, obj):
        """Pré-visualização das imagens da galeria."""
        html = '<div style="display: flex; gap: 15px; flex-wrap: wrap;">'
        gallery = obj.get_gallery_images

        if not gallery:
            return format_html('<p style="color: #999;">Nenhuma imagem na galeria</p>')

        for idx, item in enumerate(gallery, 1):
            html += f'''
                <div style="flex: 0 0 200px;">
                    <img src="{item['image'].url}"
                         style="width: 100%; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                    <p style="margin-top: 8px; color: #666; font-size: 12px; text-align: center;">
                        Imagem {idx} - {item['ratio']}
                    </p>
                </div>
            '''

        html += '</div>'
        return format_html(html)
    preview_gallery_images.short_description = 'Preview da Galeria'

    def save_model(self, request, obj, form, change):
        """Customização ao salvar o modelo."""
        # Se não houver meta description, gera uma a partir da introdução
        if not obj.meta_description and obj.introduction:
            obj.meta_description = obj.introduction[:157] + '...' if len(obj.introduction) > 157 else obj.introduction

        super().save_model(request, obj, form, change)
