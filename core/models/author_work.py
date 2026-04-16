"""
Model de Obra do Autor.
Representa as obras publicadas por um autor, exibidas na aba 'Obras Lançadas'
na página de detalhe do autor.
"""

from django.db import models
from .author import Author


class AuthorWork(models.Model):
    """Obra publicada por um autor (tabela de obras lançadas)."""

    author = models.ForeignKey(
        Author,
        on_delete=models.CASCADE,
        related_name='works',
        verbose_name='Autor'
    )

    year = models.CharField(
        max_length=20,
        verbose_name='Ano (BR)',
        help_text='Ex: 2024 ou 2023–2024'
    )

    title = models.CharField(
        max_length=300,
        verbose_name='Título'
    )

    format = models.CharField(
        max_length=100,
        verbose_name='Formato',
        help_text='Ex: Capa comum, E-book, HQ, etc.',
        default='Capa comum'
    )

    publisher = models.CharField(
        max_length=200,
        verbose_name='Editora / Loja',
        help_text='Ex: CG.BookStore / Amazon BR',
        blank=True
    )

    notes = models.TextField(
        blank=True,
        verbose_name='Observações',
        help_text='Informações adicionais sobre esta edição/obra'
    )

    order = models.PositiveIntegerField(
        default=0,
        verbose_name='Ordem',
        help_text='Controla a ordenação na tabela (menor = primeiro)'
    )

    class Meta:
        verbose_name = 'Obra do Autor'
        verbose_name_plural = 'Obras do Autor'
        ordering = ['order', 'year', 'title']

    def __str__(self):
        return f'{self.year} — {self.title}'
