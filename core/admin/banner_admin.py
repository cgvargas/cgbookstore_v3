"""
Admin para Banner
"""
from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from core.models import Banner


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    """Administração de Banners da Home."""

    list_display = [
        'title',
        'order',
        'image_preview',
        'status_badge',
        'visibility_period',
        'statistics',
        'active'
    ]
    list_filter = [
        'active',
        'created_at',
        'start_date',
        'end_date'
    ]
    search_fields = [
        'title',
        'subtitle',
        'description'
    ]
    readonly_fields = [
        'created_at',
        'updated_at',
        'views_count',
        'clicks_count',
        'image_preview',
        'ctr_display'
    ]
    list_editable = ['order', 'active']
    list_display_links = ['title']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Informações Básicas', {
            'fields': (
                'title',
                'subtitle',
                'description'
            )
        }),
        ('Mídia (Imagem ou Vídeo)', {
            'fields': (
                'video_file',
                'image',
                'image_preview'
            ),
            'description': 'Se um vídeo for selecionado, ele assume o fundo principal. A imagem entra como fallback automático.'
        }),
        ('Posicionamento da Imagem', {
            'fields': (
                ('image_position_vertical', 'image_position_horizontal'),
            ),
            'description': 'Controle onde a imagem é posicionada dentro do banner'
        }),
        ('Efeitos Visuais', {
            'fields': (
                'overlay_opacity',
                ('blur_edges', 'blur_intensity'),
            ),
            'description': (
                'Overlay: Escurecimento sobre a imagem (0.0-1.0, recomendado: 0.2-0.4)<br>'
                'Desfoque: Aplica fade gradual nas bordas superior e inferior (80-150px)'
            )
        }),
        ('Link de Ação', {
            'fields': (
                'link_url',
                'link_text',
                'open_in_new_tab'
            ),
            'description': 'Configure o link para onde o usuário será direcionado ao clicar no banner'
        }),
        ('Configurações de Exibição', {
            'fields': (
                'order',
                'active',
                'height'
            ),
            'description': 'Controle a ordem, status e altura do banner (estilo Crunchyroll: 700-900px)'
        }),
        ('Período de Exibição', {
            'fields': (
                'start_date',
                'end_date'
            ),
            'description': 'Deixe vazio para exibir imediatamente e indefinidamente'
        }),
        ('Estatísticas', {
            'classes': ('collapse',),
            'fields': (
                'views_count',
                'clicks_count',
                'ctr_display'
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

    def image_preview(self, obj):
        """Preview da mídia do banner."""
        if obj.video_file:
            return format_html(
                '<video src="{}" style="max-height: 100px; max-width: 300px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);" muted autoplay loop></video>',
                obj.video_file.url
            )
        elif obj.image:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 300px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);" />',
                obj.image.url
            )
        return "Sem mídia"

    image_preview.short_description = "Preview"

    def status_badge(self, obj):
        """Badge colorida indicando o status do banner."""
        if not obj.active:
            return format_html(
                '<span style="background-color: #dc3545; color: white; padding: 4px 12px; border-radius: 12px; font-size: 11px; font-weight: bold;">INATIVO</span>'
            )

        if obj.is_visible():
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 4px 12px; border-radius: 12px; font-size: 11px; font-weight: bold;">✓ VISÍVEL</span>'
            )
        else:
            now = timezone.now()
            if obj.start_date and now < obj.start_date:
                return format_html(
                    '<span style="background-color: #ffc107; color: #000; padding: 4px 12px; border-radius: 12px; font-size: 11px; font-weight: bold;">⏳ AGENDADO</span>'
                )
            elif obj.end_date and now > obj.end_date:
                return format_html(
                    '<span style="background-color: #6c757d; color: white; padding: 4px 12px; border-radius: 12px; font-size: 11px; font-weight: bold;">EXPIRADO</span>'
                )

        return format_html(
            '<span style="background-color: #6c757d; color: white; padding: 4px 12px; border-radius: 12px; font-size: 11px; font-weight: bold;">-</span>'
        )

    status_badge.short_description = "Status"

    def visibility_period(self, obj):
        """Exibe o período de visibilidade do banner."""
        if not obj.start_date and not obj.end_date:
            return "Sempre visível"

        parts = []
        if obj.start_date:
            parts.append(f"De: {obj.start_date.strftime('%d/%m/%Y %H:%M')}")
        else:
            parts.append("De: Imediatamente")

        if obj.end_date:
            parts.append(f"Até: {obj.end_date.strftime('%d/%m/%Y %H:%M')}")
        else:
            parts.append("Até: Indefinidamente")

        return format_html('<br>'.join(parts))

    visibility_period.short_description = "Período"

    def statistics(self, obj):
        """Exibe estatísticas do banner."""
        ctr = obj.get_ctr()

        return format_html(
            '<div style="line-height: 1.6;">'
            '<strong>👁️ {}</strong> visualizações<br>'
            '<strong>🖱️ {}</strong> cliques<br>'
            '<strong>📊 {}%</strong> CTR'
            '</div>',
            obj.views_count,
            obj.clicks_count,
            ctr
        )

    statistics.short_description = "Estatísticas"

    def ctr_display(self, obj):
        """Exibe CTR formatado."""
        ctr = obj.get_ctr()
        return f"{ctr}%"

    ctr_display.short_description = "CTR (Click-Through Rate)"

    # Actions
    actions = [
        'activate_banners',
        'deactivate_banners',
        'reset_statistics'
    ]

    def activate_banners(self, request, queryset):
        """Ativa banners selecionados."""
        updated = queryset.update(active=True)
        self.message_user(request, f'{updated} banner(s) ativado(s).')

    activate_banners.short_description = "✓ Ativar Banners"

    def deactivate_banners(self, request, queryset):
        """Desativa banners selecionados."""
        updated = queryset.update(active=False)
        self.message_user(request, f'{updated} banner(s) desativado(s).')

    deactivate_banners.short_description = "✗ Desativar Banners"

    def reset_statistics(self, request, queryset):
        """Reseta estatísticas dos banners selecionados."""
        updated = queryset.update(views_count=0, clicks_count=0)
        self.message_user(request, f'Estatísticas de {updated} banner(s) resetadas.')

    reset_statistics.short_description = "🔄 Resetar Estatísticas"
