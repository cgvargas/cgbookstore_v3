"""
Widgets customizados para o admin de Section
core/admin/widgets.py
"""
from django import forms
from django.contrib.contenttypes.models import ContentType
from core.models import Book, Author, Video


class ContentObjectWidget(forms.Widget):
    """
    Widget customizado que muda dinamicamente baseado no content_type selecionado.
    Exibe um select com os objetos disponíveis ao invés de campo numérico.
    """
    template_name = 'admin/widgets/content_object_widget.html'

    def __init__(self, attrs=None):
        super().__init__(attrs)
        self.choices = []

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)

        # Adicionar choices ao contexto
        context['widget']['choices'] = self.choices

        return context

    def value_from_datadict(self, data, files, name):
        return data.get(name)


class SectionItemForm(forms.ModelForm):
    """
    Form customizado para SectionItem que adiciona campo de seleção dinâmica.
    """

    # Campo auxiliar para seleção visual
    content_object_select = forms.ChoiceField(
        label='Selecionar Item',
        required=False,
        help_text='Selecione o item da lista ou digite o ID manualmente no campo "Id do objeto"'
    )

    class Meta:
        from core.models import SectionItem
        model = SectionItem
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Preparar choices baseado no content_type da seção pai
        instance = kwargs.get('instance')

        if instance and instance.pk:
            # Modo edição
            content_type = instance.content_type
            self._populate_choices(content_type)

            # Pré-selecionar o valor atual
            if instance.object_id:
                self.fields['content_object_select'].initial = instance.object_id

        # Adicionar classe CSS para estilização
        self.fields['object_id'].widget.attrs.update({
            'class': 'vIntegerField',
            'min': '1',
            'placeholder': 'Digite o ID ou selecione acima'
        })

    def _populate_choices(self, content_type):
        """Popula as choices baseado no tipo de conteúdo."""
        choices = [('', '---------')]

        if not content_type:
            self.fields['content_object_select'].choices = choices
            return

        model_class = content_type.model_class()

        if model_class == Book:
            books = Book.objects.filter(slug__isnull=False).exclude(slug='').order_by('title')
            choices.extend([
                (book.id, f'{book.title} - {book.author.name if book.author else "Sem autor"}')
                for book in books[:100]  # Limitar a 100 para performance
            ])

        elif model_class == Author:
            authors = Author.objects.order_by('name')
            choices.extend([
                (author.id, author.name)
                for author in authors[:100]
            ])

        elif model_class == Video:
            videos = Video.objects.order_by('title')
            choices.extend([
                (video.id, f'{video.title} ({video.get_platform_display()})')
                for video in videos[:100]
            ])

        self.fields['content_object_select'].choices = choices

    def clean(self):
        """Validação customizada."""
        cleaned_data = super().clean()

        # Se o select foi usado, sobrescrever object_id
        content_object_select = cleaned_data.get('content_object_select')
        if content_object_select:
            cleaned_data['object_id'] = int(content_object_select)

        object_id = cleaned_data.get('object_id')
        content_type = cleaned_data.get('content_type')

        # Validar object_id
        if object_id is not None:
            if object_id <= 0:
                raise forms.ValidationError({
                    'object_id': 'O ID do objeto deve ser maior que 0.'
                })

            # Validar se o objeto existe
            if content_type:
                model_class = content_type.model_class()
                try:
                    obj = model_class.objects.get(pk=object_id)

                    # Validação específica para Book (verificar slug)
                    if model_class == Book:
                        if not obj.slug or obj.slug == '':
                            raise forms.ValidationError({
                                'object_id': f'O livro "{obj.title}" não possui slug válido. '
                                             f'Edite o livro e salve para gerar o slug automaticamente.'
                            })

                except model_class.DoesNotExist:
                    raise forms.ValidationError({
                        'object_id': f'{content_type.model} com ID {object_id} não encontrado.'
                    })

        return cleaned_data