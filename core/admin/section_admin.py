"""
Admin para Section e SectionItem - Versão Estável
"""
from django.contrib import admin
from django.utils.html import format_html
from django.core.exceptions import ValidationError
from core.models import Section, SectionItem, Book, Author, Video


class SectionItemInline(admin.TabularInline):
    """Inline para gerenciar itens dentro de uma seção."""

    model = SectionItem
    extra = 1
    fields = ['content_type', 'object_id', 'item_preview', 'order', 'active', 'custom_title']
    readonly_fields = ['item_preview']

    def get_queryset(self, request):
        """Retorna queryset ordenado."""
        qs = super().get_queryset(request)
        return qs.order_by('order')

    def item_preview(self, obj):
        """Exibe preview visual do item vinculado."""
        if not obj.pk:
            return format_html('<em style="color: #666;">Salve para ver preview</em>')

        content_obj = obj.content_object

        if not content_obj:
            return format_html(
                '<span style="color: red; font-weight: bold;">⚠️ Objeto não encontrado (ID: {})</span>',
                obj.object_id
            )

        # Preview para Book
        if isinstance(content_obj, Book):
            if content_obj.cover_image:
                return format_html(
                    '<div style="display: flex; align-items: center; gap: 10px;">'
                    '<img src="{}" style="width: 40px; height: 60px; object-fit: cover; border-radius: 4px;" />'
                    '<div>'
                    '<strong>{}</strong><br/>'
                    '<span style="color: #666; font-size: 0.9em;">{}</span><br/>'
                    '<span style="color: #999; font-size: 0.85em;">Slug: {}</span>'
                    '</div>'
                    '</div>',
                    content_obj.cover_image.url,
                    content_obj.title[:40],
                    content_obj.author.name if content_obj.author else 'Sem autor',
                    content_obj.slug or '<span style="color:red;">VAZIO</span>'
                )
            else:
                return format_html(
                    '<div style="display: flex; align-items: center; gap: 10px;">'
                    '<div style="width: 40px; height: 60px; background: #e0e0e0; border-radius: 4px; '
                    'display: flex; align-items: center; justify-content: center; font-size: 20px;">📚</div>'
                    '<div>'
                    '<strong>{}</strong><br/>'
                    '<span style="color: #666; font-size: 0.9em;">{}</span><br/>'
                    '<span style="color: #999; font-size: 0.85em;">Slug: {}</span>'
                    '</div>'
                    '</div>',
                    content_obj.title[:40],
                    content_obj.author.name if content_obj.author else 'Sem autor',
                    content_obj.slug or '<span style="color:red;">VAZIO</span>'
                )

        # Preview para Author
        elif isinstance(content_obj, Author):
            if content_obj.photo:
                return format_html(
                    '<div style="display: flex; align-items: center; gap: 10px;">'
                    '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 50%;" />'
                    '<div>'
                    '<strong>{}</strong><br/>'
                    '<span style="color: #666; font-size: 0.9em;">Autor</span><br/>'
                    '<span style="color: #999; font-size: 0.85em;">Slug: {}</span>'
                    '</div>'
                    '</div>',
                    content_obj.photo.url,
                    content_obj.name,
                    content_obj.slug
                )
            else:
                return format_html(
                    '<div style="display: flex; align-items: center; gap: 10px;">'
                    '<div style="width: 50px; height: 50px; background: #e0e0e0; border-radius: 50%; '
                    'display: flex; align-items: center; justify-content: center; font-size: 24px;">👤</div>'
                    '<div>'
                    '<strong>{}</strong><br/>'
                    '<span style="color: #666; font-size: 0.9em;">Autor</span><br/>'
                    '<span style="color: #999; font-size: 0.85em;">Slug: {}</span>'
                    '</div>'
                    '</div>',
                    content_obj.name,
                    content_obj.slug
                )

        # Preview para Video
        elif isinstance(content_obj, Video):
            if content_obj.thumbnail_url:
                return format_html(
                    '<div style="display: flex; align-items: center; gap: 10px;">'
                    '<img src="{}" style="width: 80px; height: 45px; object-fit: cover; border-radius: 4px;" />'
                    '<div>'
                    '<strong>{}</strong><br/>'
                    '<span style="color: #666; font-size: 0.9em;">{}</span>'
                    '</div>'
                    '</div>',
                    content_obj.thumbnail_url,
                    content_obj.title[:40],
                    content_obj.get_platform_display()
                )
            else:
                return format_html(
                    '<div style="display: flex; align-items: center; gap: 10px;">'
                    '<div style="width: 80px; height: 45px; background: #e0e0e0; border-radius: 4px; '
                    'display: flex; align-items: center; justify-content: center; font-size: 20px;">🎥</div>'
                    '<div>'
                    '<strong>{}</strong><br/>'
                    '<span style="color: #666; font-size: 0.9em;">{}</span>'
                    '</div>'
                    '</div>',
                    content_obj.title[:40],
                    content_obj.get_platform_display()
                )

        return format_html('<em>{}</em>', str(content_obj))

    item_preview.short_description = 'Preview do Item'


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    """Administração de Seções da Home."""

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

    def save_formset(self, request, form, formset, change):
        """Valida os SectionItems antes de salvar."""
        instances = formset.save(commit=False)

        for instance in instances:
            if instance.object_id <= 0:
                raise ValidationError(
                    f'ID do objeto inválido: {instance.object_id}. O ID deve ser maior que 0.'
                )

            try:
                obj = instance.content_object
                if not obj:
                    raise ValidationError(
                        f'Objeto não encontrado: {instance.content_type} com ID {instance.object_id}'
                    )

                if isinstance(obj, Book):
                    if not obj.slug or obj.slug == '':
                        raise ValidationError(
                            f'O livro "{obj.title}" (ID: {obj.id}) não possui slug válido. '
                            f'Edite o livro e salve para gerar o slug automaticamente.'
                        )

            except Exception as e:
                raise ValidationError(f'Erro ao validar item: {str(e)}')

            instance.save()

        formset.save_m2m()


@admin.register(SectionItem)
class SectionItemAdmin(admin.ModelAdmin):
    """Administração individual de itens de seção."""

    list_display = [
        'id',
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

    def save_model(self, request, obj, form, change):
        """Valida antes de salvar."""
        if obj.object_id <= 0:
            raise ValidationError('ID do objeto deve ser maior que 0.')

        content_obj = obj.content_object
        if not content_obj:
            raise ValidationError(
                f'Objeto não encontrado: {obj.content_type} com ID {obj.object_id}'
            )

        super().save_model(request, obj, form, change)