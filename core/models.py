# C:\Users\claud\OneDrive\ProjectsDjango\CGBookStore_v3\core\models.py

from django.db import models
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nome")
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    # Para o filtro na HomeView que sugeri anteriormente
    featured = models.BooleanField(default=False, verbose_name="Em destaque?")

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Author(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nome")
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    bio = models.TextField(blank=True, null=True, verbose_name="Biografia")

    class Meta:
        verbose_name = "Autor"
        verbose_name_plural = "Autores"
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Book(models.Model):
    title = models.CharField(max_length=200, verbose_name="Título")
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True, verbose_name="Autor")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, verbose_name="Categoria")
    description = models.TextField(blank=True, null=True, verbose_name="Descrição")
    publication_date = models.DateField(verbose_name="Data de Publicação")
    isbn = models.CharField(max_length=13, unique=True, blank=True, null=True, verbose_name="ISBN")
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Preço")
    cover_image = models.ImageField(upload_to='book-covers/', blank=True, null=True, verbose_name="Capa")

    class Meta:
        verbose_name = "Livro"
        verbose_name_plural = "Livros"
        ordering = ['-publication_date', 'title']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
