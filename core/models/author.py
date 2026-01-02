"""
Model de Autor.
Representa autores de livros com biografia e foto.
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
        blank=True,
        verbose_name="Slug"
    )

    bio = models.TextField(
        blank=True,
        null=True,
        verbose_name="Biografia"
    )

    photo = models.ImageField(
        upload_to='authors/photos/',
        blank=True,
        null=True,
        verbose_name="Foto",
        help_text="Foto do autor (recomendado: 400x400px)"
    )

    # Redes sociais
    website = models.URLField(
        blank=True,
        verbose_name="Website",
        help_text="Site oficial do autor"
    )

    twitter = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Twitter/X",
        help_text="Nome de usuário (sem @)"
    )

    instagram = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Instagram",
        help_text="Nome de usuário (sem @)"
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
        """Gera slug automaticamente a partir do nome, garantindo unicidade."""
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            # Verificar se o slug já existe (excluindo o próprio objeto se já tem pk)
            while Author.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                counter += 1
                slug = f"{base_slug}-{counter}"
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_books_count(self):
        """Retorna quantidade de livros do autor."""
        return self.books.count()

    get_books_count.short_description = "Livros"