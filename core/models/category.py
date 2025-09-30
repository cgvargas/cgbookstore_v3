"""
Model de Categoria de Livros.
Representa categorias como Ficção, Romance, Tecnologia, etc.
"""

from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    """Categoria de livros (Ficção, Romance, Tecnologia, etc.)."""

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nome"
    )
    slug = models.SlugField(
        unique=True,
        blank=True
    )
    featured = models.BooleanField(
        default=False,
        verbose_name="Destaque"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em"
    )

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        ordering = ['name']

    def save(self, *args, **kwargs):
        """Gera slug automaticamente a partir do nome."""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name