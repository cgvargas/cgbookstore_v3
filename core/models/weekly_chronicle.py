"""
Modelo para Crônica Semanal
Permite ao superusuário editar conteúdo e imagens sem alterar a estrutura da página.
"""

from django.db import models
from django.utils import timezone
from django.core.validators import FileExtensionValidator


class WeeklyChronicle(models.Model):
    """
    Modelo para armazenar a Crônica Semanal.
    Suporta imagens em múltiplas proporções (1:1, 4:5, 16:9).
    """

    ASPECT_RATIO_CHOICES = [
        ('1:1', 'Quadrado (1:1)'),
        ('4:5', 'Vertical (4:5)'),
        ('16:9', 'Horizontal (16:9)'),
    ]

    # Informações da Edição
    week_start_date = models.DateField(
        'Início da Semana',
        blank=True,
        null=True,
        help_text='Data de início da semana'
    )

    week_end_date = models.DateField(
        'Fim da Semana',
        blank=True,
        null=True,
        help_text='Data de fim da semana'
    )

    volume_number = models.IntegerField(
        'Volume',
        default=1,
        help_text='Número do volume'
    )

    issue_number = models.IntegerField(
        'Edição',
        default=1,
        help_text='Número da edição'
    )

    # Campos de texto - Artigo Principal
    title = models.CharField(
        'Título',
        max_length=200,
        help_text='Título principal da crônica'
    )

    subtitle = models.CharField(
        'Subtítulo',
        max_length=300,
        blank=True,
        help_text='Subtítulo ou chamada (opcional)'
    )

    introduction = models.TextField(
        'Introdução',
        help_text='Texto introdutório da crônica'
    )

    main_content = models.TextField(
        'Conteúdo Principal',
        help_text='Conteúdo principal da crônica'
    )

    conclusion = models.TextField(
        'Conclusão',
        blank=True,
        help_text='Texto de conclusão (opcional)'
    )

    author_name = models.CharField(
        'Autor',
        max_length=100,
        default='Equipe CG.BookStore',
        help_text='Nome do autor da crônica'
    )

    # Citações
    quote = models.TextField(
        'Citação em Destaque',
        blank=True,
        help_text='Citação ou trecho em destaque (opcional)'
    )

    quote_author = models.CharField(
        'Autor da Citação',
        max_length=100,
        blank=True,
        help_text='Autor da citação em destaque (opcional)'
    )

    quote_secondary = models.TextField(
        'Citação Secundária',
        blank=True,
        default='',
        help_text='Segunda citação em destaque (opcional)'
    )

    quote_secondary_author = models.CharField(
        'Autor da Citação Secundária',
        max_length=100,
        blank=True,
        default='',
        help_text='Autor da segunda citação (opcional)'
    )

    # Destaques da Semana (Sidebar)
    highlights_accomplishment = models.CharField(
        'Realização',
        max_length=300,
        blank=True,
        default='',
        help_text='Realização da semana'
    )

    highlights_social = models.CharField(
        'Social',
        max_length=300,
        blank=True,
        default='',
        help_text='Destaque social da semana'
    )

    highlights_health = models.CharField(
        'Saúde',
        max_length=300,
        blank=True,
        default='',
        help_text='Destaque de saúde da semana'
    )

    highlights_learning = models.CharField(
        'Aprendizado',
        max_length=300,
        blank=True,
        default='',
        help_text='Destaque de aprendizado da semana'
    )

    highlights_personal = models.CharField(
        'Pessoal',
        max_length=300,
        blank=True,
        default='',
        help_text='Destaque pessoal da semana'
    )

    # Seções Adicionais
    section_home_title = models.CharField(
        'Título - Casa & Família',
        max_length=200,
        blank=True,
        default='',
        help_text='Título do artigo sobre casa/família'
    )

    section_home_content = models.TextField(
        'Conteúdo - Casa & Família',
        blank=True,
        default='',
        help_text='Conteúdo do artigo sobre casa/família'
    )

    section_health_title = models.CharField(
        'Título - Saúde',
        max_length=200,
        blank=True,
        default='',
        help_text='Título do artigo sobre saúde'
    )

    section_health_content = models.TextField(
        'Conteúdo - Saúde',
        blank=True,
        default='',
        help_text='Conteúdo do artigo sobre saúde'
    )

    section_entertainment_title = models.CharField(
        'Título - Entretenimento',
        max_length=200,
        blank=True,
        default='',
        help_text='Título do artigo sobre entretenimento'
    )

    section_entertainment_content = models.TextField(
        'Conteúdo - Entretenimento',
        blank=True,
        default='',
        help_text='Conteúdo do artigo sobre entretenimento'
    )

    # Campos de imagem
    featured_image = models.ImageField(
        'Imagem Principal',
        upload_to='chronicles/featured/',
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp'])],
        help_text='Imagem principal da crônica'
    )

    featured_image_ratio = models.CharField(
        'Proporção da Imagem Principal',
        max_length=10,
        choices=ASPECT_RATIO_CHOICES,
        default='16:9',
        help_text='Proporção da imagem principal'
    )

    secondary_image = models.ImageField(
        'Imagem Secundária',
        upload_to='chronicles/secondary/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp'])],
        help_text='Imagem secundária (opcional)'
    )

    secondary_image_ratio = models.CharField(
        'Proporção da Imagem Secundária',
        max_length=10,
        choices=ASPECT_RATIO_CHOICES,
        default='1:1',
        help_text='Proporção da imagem secundária'
    )

    gallery_image_1 = models.ImageField(
        'Galeria - Imagem 1',
        upload_to='chronicles/gallery/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp'])],
        help_text='Primeira imagem da galeria (opcional)'
    )

    gallery_image_1_ratio = models.CharField(
        'Proporção - Galeria 1',
        max_length=10,
        choices=ASPECT_RATIO_CHOICES,
        default='4:5',
        help_text='Proporção da primeira imagem da galeria'
    )

    gallery_image_2 = models.ImageField(
        'Galeria - Imagem 2',
        upload_to='chronicles/gallery/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp'])],
        help_text='Segunda imagem da galeria (opcional)'
    )

    gallery_image_2_ratio = models.CharField(
        'Proporção - Galeria 2',
        max_length=10,
        choices=ASPECT_RATIO_CHOICES,
        default='4:5',
        help_text='Proporção da segunda imagem da galeria'
    )

    gallery_image_3 = models.ImageField(
        'Galeria - Imagem 3',
        upload_to='chronicles/gallery/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp'])],
        help_text='Terceira imagem da galeria (opcional)'
    )

    gallery_image_3_ratio = models.CharField(
        'Proporção - Galeria 3',
        max_length=10,
        choices=ASPECT_RATIO_CHOICES,
        default='4:5',
        help_text='Proporção da terceira imagem da galeria'
    )

    # Metadados
    published_date = models.DateTimeField(
        'Data de Publicação',
        default=timezone.now,
        help_text='Data e hora de publicação da crônica'
    )

    is_published = models.BooleanField(
        'Publicado',
        default=True,
        help_text='Marque para publicar a crônica'
    )

    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    # SEO
    meta_description = models.CharField(
        'Meta Descrição',
        max_length=160,
        blank=True,
        help_text='Descrição para SEO (opcional, máx. 160 caracteres)'
    )

    class Meta:
        verbose_name = 'Crônica Semanal'
        verbose_name_plural = 'Crônicas Semanais'
        ordering = ['-published_date']

    def __str__(self):
        return f"{self.title} - {self.published_date.strftime('%d/%m/%Y')}"

    @property
    def get_aspect_ratio_class(self):
        """Retorna a classe CSS apropriada para a proporção da imagem."""
        ratio_classes = {
            '1:1': 'ratio-1x1',
            '4:5': 'ratio-4x5',
            '16:9': 'ratio-16x9',
        }
        return ratio_classes.get(self.featured_image_ratio, 'ratio-16x9')

    @property
    def get_gallery_images(self):
        """Retorna lista de imagens da galeria com suas proporções."""
        gallery = []

        if self.gallery_image_1:
            gallery.append({
                'image': self.gallery_image_1,
                'ratio': self.gallery_image_1_ratio,
            })

        if self.gallery_image_2:
            gallery.append({
                'image': self.gallery_image_2,
                'ratio': self.gallery_image_2_ratio,
            })

        if self.gallery_image_3:
            gallery.append({
                'image': self.gallery_image_3,
                'ratio': self.gallery_image_3_ratio,
            })

        return gallery
