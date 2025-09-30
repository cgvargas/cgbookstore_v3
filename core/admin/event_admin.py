"""
Admin para Event
"""
from django.contrib import admin
from django.utils.html import format_html
from core.models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    """Administração de Eventos Literários."""

    list_display = [
        'title',
        'event_type',
        'banner_preview',
        'start_date',
        'end_date',
        'status_badge',
        'location_display',
        'featured',
        'active'
    ]
    list_filter = [
        'event_type',
        'status',
        'featured',
        'active',
        'is_online',
        'is_free',
        'start_date',
        'created_at'
    ]
    search_fields = [
        'title',
        'description',
        'location_name',
        'location_city',
        'related_books__title',
        'related_authors__name'
    ]
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created_at', 'updated_at', 'status', 'banner_preview']
    list_editable = ['featured', 'active']
    date_hierarchy = 'start_date'

    # Autocomplete
    autocomplete_fields = ['related_books', 'related_authors']
    filter_horizontal = ['related_books', 'related_authors']

    fieldsets = (
        ('Informações Básicas', {
            'fields': (
                'title',
                'slug',
                'description',
                'short_description',
                'event_type'
            )
        }),
        ('Imagens', {
            'fields': (
                'banner_image',
                'thumbnail_image',
                'banner_preview'
            )
        }),
        ('Data e Horário', {
            'fields': (
                'start_date',
                'end_date',
                'status'
            )
        }),
        ('Localização', {
            'fields': (
                'is_online',
                'location_name',
                'location_address',
                'location_city',
                'location_state'
            )
        }),
        ('Links', {
            'fields': (
                'event_url',
                'registration_url'
            )
        }),
        ('Relacionamentos', {
            'fields': (
                'related_books',
                'related_authors'
            )
        }),
        ('Detalhes Adicionais', {
            'classes': ('collapse',),
            'fields': (
                'capacity',
                'is_free',
                'price'
            )
        }),
        ('Controle de Exibição', {
            'fields': (
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

    def banner_preview(self, obj):
        """Preview do banner do evento."""
        if obj.banner_image:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 200px; border-radius: 8px;" />',
                obj.banner_image.url
            )
        return "Sem banner"

    banner_preview.short_description = "Preview"

    def status_badge(self, obj):
        """Badge colorida com o status do evento."""
        colors = {
            'upcoming': '#007bff',
            'ongoing': '#28a745',
            'finished': '#6c757d',
            'cancelled': '#dc3545'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 12px; border-radius: 12px; font-size: 11px; font-weight: bold;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            obj.get_status_display()
        )

    status_badge.short_description = "Status"

    def location_display(self, obj):
        """Exibe localização de forma resumida."""
        return obj.get_location_display()

    location_display.short_description = "Localização"

    actions = ['mark_as_featured', 'mark_as_not_featured', 'activate_events', 'deactivate_events']

    def mark_as_featured(self, request, queryset):
        """Marca eventos como destaque."""
        updated = queryset.update(featured=True)
        self.message_user(request, f'{updated} evento(s) marcado(s) como destaque.')

    mark_as_featured.short_description = "Marcar como Destaque"

    def mark_as_not_featured(self, request, queryset):
        """Remove destaque dos eventos."""
        updated = queryset.update(featured=False)
        self.message_user(request, f'{updated} evento(s) removido(s) do destaque.')

    mark_as_not_featured.short_description = "Remover Destaque"

    def activate_events(self, request, queryset):
        """Ativa eventos."""
        updated = queryset.update(active=True)
        self.message_user(request, f'{updated} evento(s) ativado(s).')

    activate_events.short_description = "Ativar Eventos"

    def deactivate_events(self, request, queryset):
        """Desativa eventos."""
        updated = queryset.update(active=False)
        self.message_user(request, f'{updated} evento(s) desativado(s).')

    deactivate_events.short_description = "Desativar Eventos"