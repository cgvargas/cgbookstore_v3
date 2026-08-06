"""
Admin evoluído para Video (Central de Mídias Externas Corporativa).
Inclui suporte ao ImageRightsRecordInline para thumbnails personalizadas,
filtros de saúde da mídia, selo de canal oficial e ações de verificação.
"""

from django.contrib import admin, messages
from django.utils.html import format_html
from django.utils import timezone

from core.models import Video
from core.admin.image_rights_admin import ImageRightsRecordInline
from core.services.image_rights_service import ImageRightsAuditService
from core.services.youtube_media_service import YouTubeMediaService


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    """Administração da Central de Mídias Externas."""

    inlines = [ImageRightsRecordInline]

    list_display = [
        'id',
        'title',
        'platform',
        'video_type',
        'official_badge',
        'status_badge',
        'views_count',
        'featured',
        'active',
        'created_at',
    ]
    list_filter = [
        'platform',
        'video_type',
        'media_status',
        'is_official_channel',
        'featured',
        'active',
        'created_at',
        'related_universes',
        'related_books',
    ]
    search_fields = [
        'title',
        'short_description',
        'description',
        'channel_name',
        'embed_code',
        'related_books__title',
        'related_author__name',
    ]
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = [
        'created_at',
        'updated_at',
        'last_health_check',
        'health_check_source',
        'health_check_message',
    ]
    list_editable = ['featured', 'active']
    date_hierarchy = 'created_at'

    filter_horizontal = ('related_books', 'related_universes', 'related_articles', 'related_quizzes', 'categories')
    autocomplete_fields = ['related_author', 'official_status_verified_by']

    actions = ['check_selected_media_health', 'mark_official_verified']

    fieldsets = (
        ('📋 Informações Básicas', {
            'fields': (
                'title',
                'slug',
                'video_type',
                'short_description',
                'description',
                'language',
                'duration_td',
                'published_date',
            )
        }),
        ('📺 Provedor de Mídia e Identificadores', {
            'fields': (
                'platform',
                'video_url',
                'embed_code',
                'thumbnail_image',
                'thumbnail_url',
            ),
            'description': 'Informações de incorporação. A thumbnail customizada pode ser auditada no inline de Direitos Autorais abaixo.'
        }),
        ('⭐ Canal e Oficialidade (Auditável)', {
            'fields': (
                'channel_name',
                'channel_id',
                'is_official_channel',
                ('official_status_verified_by', 'official_status_verified_at'),
                'official_status_notes',
            ),
            'description': 'Para marcar o canal como Oficial, informe obrigatoriamente a pessoa responsável e a data da verificação.'
        }),
        ('🩺 Auditoria de Saúde e Disponibilidade', {
            'fields': (
                'media_status',
                'is_embeddable',
                'last_health_check',
                'health_check_source',
                'health_check_message',
                'admin_notes',
            ),
            'classes': ('collapse',)
        }),
        ('🔗 Relacionamentos M2M Flexíveis', {
            'fields': (
                'related_books',
                'related_author',
                'related_universes',
                'related_articles',
                'related_quizzes',
                'categories',
            ),
            'classes': ('collapse',)
        }),
        ('📊 Métricas e Controle', {
            'fields': (
                'views_count',
                'display_order',
                'featured',
                'active',
                'created_at',
                'updated_at',
            )
        }),
    )

    def save_model(self, request, obj, form, change):
        # Preencher automaticamente a verificação de canal oficial se for marcado pelo admin
        if obj.is_official_channel and not obj.official_status_verified_by:
            obj.official_status_verified_by = request.user
            obj.official_status_verified_at = timezone.now()

        super().save_model(request, obj, form, change)
        ImageRightsAuditService.audit_model_admin_save(request, obj)

    def official_badge(self, obj):
        if obj.is_official_channel:
            return format_html('<span style="background:#f39c12; color:#fff; padding:3px 8px; border-radius:10px; font-size:0.75rem; font-weight:600;">⭐ Oficial</span>')
        return format_html('<span style="color:#7f8c8d; font-size:0.75rem;">Terceiros</span>')
    official_badge.short_description = "Oficialidade"

    def status_badge(self, obj):
        colors = {
            'active': '#27ae60',
            'removed': '#c0392b',
            'private': '#8e44ad',
            'embed_blocked': '#e67e22',
            'unavailable': '#7f8c8d',
            'unknown': '#95a5a6',
        }
        color = colors.get(obj.media_status, '#7f8c8d')
        return format_html(
            f'<span style="background:{color}; color:#fff; padding:3px 8px; border-radius:10px; font-size:0.75rem; font-weight:600;">{obj.get_media_status_display()}</span>'
        )
    status_badge.short_description = "Saúde"

    @admin.action(description="🩺 Verificar disponibilidade/saúde das mídias selecionadas")
    def check_selected_media_health(self, request, queryset):
        count = 0
        for video in queryset:
            YouTubeMediaService.check_video_health(video)
            count += 1
        self.message_user(request, f"Saúde de {count} mídia(s) verificada(s) com sucesso.", level=messages.SUCCESS)

    @admin.action(description="⭐ Confirmar e marcar canais selecionados como Oficiais")
    def mark_official_verified(self, request, queryset):
        updated = queryset.update(
            is_official_channel=True,
            official_status_verified_by=request.user,
            official_status_verified_at=timezone.now()
        )
        self.message_user(request, f"{updated} mídia(s) marcada(s) como Canal Oficial Verificado.", level=messages.SUCCESS)