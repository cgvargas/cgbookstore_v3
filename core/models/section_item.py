"""
Model SectionItem - Itens dentro de cada seção
"""
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class SectionItem(models.Model):
    """
    Model para itens dentro de uma seção.
    Usa GenericForeignKey para permitir diferentes tipos de conteúdo.
    """

    # Relacionamento com Section
    section = models.ForeignKey(
        'core.Section',
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name="Seção"
    )

    # GenericForeignKey para conteúdo flexível (Book, Author, Video)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        limit_choices_to={
            'model__in': ('book', 'author', 'video', 'article')
        },
        verbose_name="Tipo de Conteúdo"
    )

    object_id = models.PositiveIntegerField(
        verbose_name="ID do Objeto"
    )

    content_object = GenericForeignKey(
        'content_type',
        'object_id'
    )

    # Controle
    active = models.BooleanField(
        default=True,
        verbose_name="Ativo"
    )

    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordem",
        help_text="Ordem de exibição dentro da seção"
    )

    # Campos opcionais para customização
    custom_title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Título Customizado",
        help_text="Se preenchido, sobrescreve o título original"
    )

    custom_description = models.TextField(
        blank=True,
        verbose_name="Descrição Customizada"
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em"
    )

    class Meta:
        verbose_name = "Item da Seção"
        verbose_name_plural = "Itens das Seções"
        ordering = ['order', '-created_at']
        unique_together = ['section', 'content_type', 'object_id']

    def __str__(self):
        return f"{self.section.title} - {self.get_content_object()}"

    def get_content_object(self):
        """
        Retorna o objeto de conteúdo, usando cache pré-carregado se disponível.
        Evita queries N+1 quando usado com HomeView otimizada.
        """
        # Usar objeto pré-carregado se disponível (setado pela HomeView)
        if hasattr(self, '_prefetched_content_object'):
            return self._prefetched_content_object
        # Fallback para GenericForeignKey padrão
        return self.content_object

    def get_display_title(self):
        """Retorna título customizado ou título original"""
        if self.custom_title:
            return self.custom_title

        obj = self.get_content_object()
        if hasattr(obj, 'title'):
            return obj.title
        elif hasattr(obj, 'name'):
            return obj.name
        return str(obj) if obj else ''

    def get_display_description(self):
        """Retorna descrição customizada ou descrição original"""
        if self.custom_description:
            return self.custom_description

        obj = self.get_content_object()
        if hasattr(obj, 'description'):
            return obj.description
        elif hasattr(obj, 'bio'):
            return obj.bio
        return ""