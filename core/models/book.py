"""
Model de Livro.
Representa livros com suporte completo à integração com Google Books API.
"""

from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from .author import Author
from .category import Category


class Book(models.Model):
    """
    Modelo principal de livro com suporte a dados do Google Books API.

    Campos locais: informações do catálogo próprio da livraria.
    Campos Google Books: sincronização com a API do Google Books.
    """

    # ========== CAMPOS PRINCIPAIS (CATÁLOGO LOCAL) ==========
    title = models.CharField(
        max_length=300,
        verbose_name="Título"
    )
    slug = models.SlugField(
        unique=True,
        blank=True,
        max_length=350
    )
    author = models.ForeignKey(
        Author,
        on_delete=models.SET_NULL,
        related_name='books',
        verbose_name="Autor",
        null=True,
        blank=True
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='books',
        verbose_name="Categoria"
    )
    description = models.TextField(
        verbose_name="Descrição",
        blank=True,
        null=True
    )
    publication_date = models.DateField(
        verbose_name="Data de Publicação"
    )
    isbn = models.CharField(
        max_length=13,
        unique=True,
        null=True,
        blank=True,
        verbose_name="ISBN",
        help_text="ISBN-10 ou ISBN-13 (opcional se importado do Google Books)"
    )
    publisher = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Editora"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Preço Médio",
        null=True,
        blank=True,
        help_text="Valor médio de mercado (informativo)"
    )

    # ========== CAMPOS DE PARCEIRO COMERCIAL ==========
    purchase_partner_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Parceiro Comercial",
        help_text="Nome do parceiro onde o livro pode ser adquirido (ex: Amazon, Saraiva, Cultura)"
    )
    purchase_partner_url = models.URLField(
        max_length=500,
        blank=True,
        verbose_name="Link para Compra",
        help_text="URL completa da página do livro no site do parceiro comercial"
    )

    cover_image = models.ImageField(
        upload_to='books/covers/',
        blank=True,
        null=True,
        verbose_name="Imagem de Capa"
    )

    # ========== CAMPOS DE INTEGRAÇÃO COM GOOGLE BOOKS API ==========
    google_books_id = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True,
        verbose_name="ID Google Books",
        help_text="ID único do volume na API do Google Books"
    )
    subtitle = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        verbose_name="Subtítulo"
    )
    page_count = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Número de Páginas"
    )
    average_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Avaliação Média",
        help_text="De 0.00 a 5.00 (dados do Google Books)"
    )
    ratings_count = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Total de Avaliações",
        help_text="Número de avaliações no Google Books"
    )
    preview_link = models.URLField(
        max_length=500,
        null=True,
        blank=True,
        verbose_name="Link de Preview",
        help_text="Link para visualizar preview no Google Books"
    )
    info_link = models.URLField(
        max_length=500,
        null=True,
        blank=True,
        verbose_name="Link de Informações",
        help_text="Link para página de informações no Google Books"
    )
    language = models.CharField(
        max_length=10,
        default='pt',
        verbose_name="Idioma",
        help_text="Código ISO 639-1 (ex: pt, en, es, fr)"
    )

    # ========== METADADOS ==========
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Atualizado em"
    )

    class Meta:
        verbose_name = "Livro"
        verbose_name_plural = "Livros"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['isbn']),
            models.Index(fields=['google_books_id']),
            models.Index(fields=['created_at']),
        ]

    def save(self, *args, **kwargs):
        """Gera slug automaticamente a partir do título."""
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """Retorna a URL da página de detalhes do livro."""
        return reverse('core:book_detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.title

    # ========== PROPRIEDADES COMPUTADAS ==========
    @property
    def rating_stars(self):
        """Retorna o número de estrelas cheias para exibição (0-5)."""
        if self.average_rating:
            return int(self.average_rating)
        return 0

    @property
    def rating_percentage(self):
        """Retorna a porcentagem da avaliação para renderizar estrelas."""
        if self.average_rating:
            return (self.average_rating / 5) * 100
        return 0

    @property
    def has_google_books_data(self):
        """Verifica se o livro possui dados sincronizados do Google Books."""
        return bool(self.google_books_id)

    @property
    def has_valid_cover(self):
        """
        Verifica se o livro possui uma capa válida (não genérica).
        Retorna True se houver uma imagem de capa carregada.
        """
        return bool(self.cover_image and self.cover_image.name)

    @property
    def cover_image_url(self):
        """
        Retorna a URL da capa com cache-buster baseado no updated_at.
        Isso força o navegador a recarregar a imagem quando ela é atualizada.
        """
        if self.cover_image:
            # Usar timestamp do updated_at como versão
            version = int(self.updated_at.timestamp())
            return f"{self.cover_image.url}?v={version}"
        return None