"""
Model de Autor.
Representa autores de livros com biografia.
"""

from django.db import models
from django.utils.text import slugify


class Author(models.Model):
    """Autor de livros."""

    name = models.CharField(
        max_length=200,
        verbose_name="Nome"
    )
    slug = models.SlugField(
        unique=True,
        blank=True
    )
    bio = models.TextField(
        blank=True,
        null=True,
        verbose_name="Biografia"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em"
    )

    class Meta:
        verbose_name = "Autor"
        verbose_name_plural = "Autores"
        ordering = ['name']

    def save(self, *args, **kwargs):
        """Gera slug automaticamente a partir do nome."""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name