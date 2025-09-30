"""
Admin para Section e SectionItem
"""
from django.contrib import admin
from core.models import Section, SectionItem


class SectionItemInline(admin.TabularInline):
    """Inline para gerenciar itens dentro de uma seção."""

    model = SectionItem
    extra = 1
    fields = ['content_type', 'object_id', 'order', 'active', 'custom_title']
    readonly_fields = []

    def get_queryset(self, request):
        """Retorna queryset ordenado."""
        qs = super().get_queryset(request)
        return qs.order_by('order')


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    """Administração de Seções da Home com inline para itens."""

    list_display = [
        'title',
        'content_type',
        'layout',
        'active',
        'order',
        'items_count',
        'created_at'
    ]
    list_filter = [
        'content_type',
        'layout',
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
            )
        }),
        ('Estilo Visual', {
            'classes': ('collapse',),
            'fields': (
                'background_color',
                'css_class'
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

    readonly_fields = ['created_at', 'updated_at']

    def items_count(self, obj):
        """Retorna quantidade de itens ativos na seção."""
        return obj.items.filter(active=True).count()

    items_count.short_description = 'Itens Ativos'


@admin.register(SectionItem)
class SectionItemAdmin(admin.ModelAdmin):
    """Administração individual de itens de seção (backup, raramente usado)."""

    list_display = [
        'section',
        'content_object',
        'order',
        'active',
        'created_at'
    ]
    list_filter = [
        'section',
        'content_type',
        'active',
        'created_at'
    ]
    search_fields = [
        'section__title',
        'custom_title',
        'custom_description'
    ]
    list_editable = ['order', 'active']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Seção', {
            'fields': ('section',)
        }),
        ('Conteúdo', {
            'fields': (
                'content_type',
                'object_id'
            )
        }),
        ('Customização', {
            'fields': (
                'custom_title',
                'custom_description'
            )
        }),
        ('Controle', {
            'fields': (
                'order',
                'active'
            )
        })
    )