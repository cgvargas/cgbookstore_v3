"""
Admin para Section e SectionItem - Versão com Dropdown Dinâmico Simples
"""
from django import forms
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.utils.html import format_html
from django.core.exceptions import ValidationError
from core.models import Section, SectionItem, Book, Author, Video


class SectionItemAdminForm(forms.ModelForm):
    """Form customizado com dropdown para selecionar objetos."""

    # Campo dropdown para Book
    book = forms.ModelChoiceField(
        queryset=Book.objects.all().select_related('author', 'category').order_by('title'),
        required=False,
        label="📚 Selecionar Livro",
        help_text="Escolha um livro da lista",
        empty_label="--- Selecione um livro ---"
    )

    # Campo dropdown para Author
    author = forms.ModelChoiceField(
        queryset=Author.objects.all().order_by('name'),
        required=False,
        label="👤 Selecionar Autor",
        help_text="Escolha um autor da lista",
        empty_label="--- Selecione um autor ---"
    )

    # Campo dropdown para Video
    video = forms.ModelChoiceField(
        queryset=Video.objects.all().order_by('title'),
        required=False,
        label="🎬 Selecionar Vídeo",
        help_text="Escolha um vídeo da lista",
        empty_label="--- Selecione um vídeo ---"
    )

    class Meta:
        model = SectionItem
        fields = ['section', 'content_type', 'book', 'author', 'video', 'order', 'active', 'custom_title',
                  'custom_description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Melhorar exibição dos livros no dropdown
        self.fields['book'].label_from_instance = lambda \
            obj: f"{obj.title} - {obj.author.name if obj.author else 'Sem autor'}"

        # Se já existe um objeto, preencher o campo apropriado
        if self.instance and self.instance.pk and self.instance.object_id:
            content_obj = self.instance.content_object
            if isinstance(content_obj, Book):
                self.fields['book'].initial = content_obj
            elif isinstance(content_obj, Author):
                self.fields['author'].initial = content_obj
            elif isinstance(content_obj, Video):
                self.fields['video'].initial = content_obj

    def clean(self):
        cleaned_data = super().clean()
        content_type = cleaned_data.get('content_type')
        book = cleaned_data.get('book')
        author = cleaned_data.get('author')
        video = cleaned_data.get('video')

        # Determinar qual objeto foi selecionado e configurar object_id
        if content_type:
            model_class = content_type.model_class()

            if model_class == Book:
                if book:
                    cleaned_data['object_id'] = book.id
                else:
                    raise ValidationError('Selecione um livro da lista.')
            elif model_class == Author:
                if author:
                    cleaned_data['object_id'] = author.id
                else:
                    raise ValidationError('Selecione um autor da lista.')
            elif model_class == Video:
                if video:
                    cleaned_data['object_id'] = video.id
                else:
                    raise ValidationError('Selecione um vídeo da lista.')

        return cleaned_data

    def save(self, commit=True):
        """Garantir que object_id seja setado antes de salvar."""
        instance = super().save(commit=False)

        # Pegar os dados limpos
        content_type = self.cleaned_data.get('content_type')
        book = self.cleaned_data.get('book')
        author = self.cleaned_data.get('author')
        video = self.cleaned_data.get('video')

        # Setar object_id baseado no tipo selecionado
        if content_type:
            model_class = content_type.model_class()

            if model_class == Book and book:
                instance.object_id = book.id
            elif model_class == Author and author:
                instance.object_id = author.id
            elif model_class == Video and video:
                instance.object_id = video.id

        if commit:
            instance.save()

        return instance


class SectionItemInline(admin.TabularInline):
    """Inline para gerenciar itens dentro de uma seção."""

    model = SectionItem
    form = SectionItemAdminForm
    extra = 1
    fields = ['content_type', 'book', 'author', 'video', 'item_preview', 'order', 'active']
    readonly_fields = ['item_preview']

    def get_queryset(self, request):
        """Retorna queryset otimizado com prefetch de objetos relacionados."""
        from django.contrib.contenttypes.models import ContentType

        qs = super().get_queryset(request)
        qs = qs.select_related('content_type', 'section').order_by('order')

        # Prefetch dos objetos relacionados para evitar N+1 queries
        # Isso carrega Books, Authors e Videos de uma vez
        book_ct = ContentType.objects.get_for_model(Book)
        author_ct = ContentType.objects.get_for_model(Author)
        video_ct = ContentType.objects.get_for_model(Video)

        qs = qs.prefetch_related(
            'content_type',
        )

        return qs

    def item_preview(self, obj):
        """Exibe preview visual do item vinculado."""
        if not obj.pk:
            return format_html('<em style="color: #666;">{}</em>', 'Salve para ver preview')

        content_obj = obj.content_object

        if not content_obj:
            return format_html(
                '<span style="color: red; font-weight: bold;">⚠️ Objeto não encontrado</span>'
            )

        # Preview para Book
        if isinstance(content_obj, Book):
            if content_obj.cover_image:
                return format_html(
                    '<div style="display: flex; align-items: center; gap: 10px;">'
                    '<img src="{}" style="width: 40px; height: 60px; object-fit: cover; border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);" />'
                    '<div>'
                    '<strong style="font-size: 13px;">{}</strong><br/>'
                    '<span style="color: #666; font-size: 11px;">{}</span>'
                    '</div>'
                    '</div>',
                    content_obj.cover_image.url,
                    content_obj.title[:30] + '...' if len(content_obj.title) > 30 else content_obj.title,
                    content_obj.author.name if content_obj.author else 'Sem autor'
                )
            else:
                return format_html(
                    '<div style="display: flex; align-items: center; gap: 10px;">'
                    '<div style="width: 40px; height: 60px; background: #e0e0e0; border-radius: 4px; '
                    'display: flex; align-items: center; justify-content: center; font-size: 20px;">📚</div>'
                    '<strong style="font-size: 13px;">{}</strong>'
                    '</div>',
                    content_obj.title[:30]
                )

        # Preview para Author
        elif isinstance(content_obj, Author):
            if content_obj.photo:
                return format_html(
                    '<div style="display: flex; align-items: center; gap: 10px;">'
                    '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 50%; box-shadow: 0 2px 4px rgba(0,0,0,0.1);" />'
                    '<strong style="font-size: 13px;">{}</strong>'
                    '</div>',
                    content_obj.photo.url,
                    content_obj.name
                )
            else:
                return format_html(
                    '<div style="display: flex; align-items: center; gap: 10px;">'
                    '<div style="width: 50px; height: 50px; background: #e0e0e0; border-radius: 50%; '
                    'display: flex; align-items: center; justify-content: center; font-size: 24px;">👤</div>'
                    '<strong style="font-size: 13px;">{}</strong>'
                    '</div>',
                    content_obj.name
                )

        # Preview para Video
        elif isinstance(content_obj, Video):
            return format_html(
                '<div style="padding: 5px;">'
                '<strong style="font-size: 13px;">🎬 {}</strong><br/>'
                '<span style="color: #666; font-size: 11px;">{}</span>'
                '</div>',
                content_obj.title[:30],
                content_obj.get_platform_display()
            )

        return format_html('<em>{}</em>', str(content_obj))

    item_preview.short_description = 'Preview'


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
        ('Estilo Visual', {
            'classes': ('collapse',),
            'fields': (
                'banner_image',
                'banner_image_preview',
                'background_color',
                'container_opacity',
                'css_class',
                'custom_css'
            ),
            'description': 'Adicione uma imagem de banner para criar seções com imagens de fundo ou banners promocionais. Use CSS customizado para criar estilos únicos.'
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