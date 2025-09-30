"""
Model Event - Eventos literários (lançamentos, feiras, encontros)
"""
from django.db import models
from django.utils.text import slugify
from django.utils import timezone


class Event(models.Model):
    """
    Model para eventos literários.
    Exemplos: lançamentos de livros, feiras literárias, encontros com autores, palestras.
    """

    EVENT_TYPE_CHOICES = [
        ('launch', 'Lançamento de Livro'),
        ('fair', 'Feira Literária'),
        ('meetup', 'Encontro com Autor'),
        ('workshop', 'Workshop'),
        ('lecture', 'Palestra'),
        ('signing', 'Sessão de Autógrafos'),
        ('reading', 'Clube de Leitura'),
        ('other', 'Outro'),
    ]

    EVENT_STATUS_CHOICES = [
        ('upcoming', 'Próximo'),
        ('ongoing', 'Acontecendo'),
        ('finished', 'Finalizado'),
        ('cancelled', 'Cancelado'),
    ]

    # Informações básicas
    title = models.CharField(
        max_length=200,
        verbose_name="Título",
        help_text="Nome do evento"
    )

    slug = models.SlugField(
        unique=True,
        blank=True,
        verbose_name="Slug"
    )

    description = models.TextField(
        verbose_name="Descrição",
        help_text="Descrição completa do evento"
    )

    short_description = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Descrição Curta",
        help_text="Resumo para o widget (gerado automaticamente se vazio)"
    )

    event_type = models.CharField(
        max_length=20,
        choices=EVENT_TYPE_CHOICES,
        default='other',
        verbose_name="Tipo de Evento"
    )

    # Imagens
    banner_image = models.ImageField(
        upload_to='events/banners/',
        verbose_name="Banner Principal",
        help_text="Imagem grande para página do evento (recomendado: 1200x600px)"
    )

    thumbnail_image = models.ImageField(
        upload_to='events/thumbnails/',
        blank=True,
        verbose_name="Thumbnail",
        help_text="Imagem pequena para cards (recomendado: 400x300px)"
    )

    # Data e Local
    start_date = models.DateTimeField(
        verbose_name="Data/Hora de Início"
    )

    end_date = models.DateTimeField(
        verbose_name="Data/Hora de Término"
    )

    location_name = models.CharField(
        max_length=200,
        verbose_name="Nome do Local",
        help_text="Ex: Livraria Cultura Shopping Iguatemi"
    )

    location_address = models.TextField(
        blank=True,
        verbose_name="Endereço Completo"
    )

    location_city = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Cidade"
    )

    location_state = models.CharField(
        max_length=2,
        blank=True,
        verbose_name="Estado (UF)"
    )

    is_online = models.BooleanField(
        default=False,
        verbose_name="Evento Online",
        help_text="Marque se o evento for online/virtual"
    )

    # Links
    event_url = models.URLField(
        verbose_name="Link do Evento",
        help_text="URL da página oficial do evento"
    )

    registration_url = models.URLField(
        blank=True,
        verbose_name="Link de Inscrição",
        help_text="URL para inscrição/compra de ingressos"
    )

    # Relacionamentos
    related_books = models.ManyToManyField(
        'core.Book',
        blank=True,
        related_name='events',
        verbose_name="Livros Relacionados",
        help_text="Livros que serão lançados ou discutidos no evento"
    )

    related_authors = models.ManyToManyField(
        'core.Author',
        blank=True,
        related_name='events',
        verbose_name="Autores Participantes"
    )

    # Informações adicionais
    capacity = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Capacidade",
        help_text="Número máximo de participantes"
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Preço",
        help_text="Deixe em branco se for gratuito"
    )

    is_free = models.BooleanField(
        default=True,
        verbose_name="Evento Gratuito"
    )

    # Controle de exibição
    featured = models.BooleanField(
        default=False,
        verbose_name="Destaque",
        help_text="Evento será exibido em destaque"
    )

    active = models.BooleanField(
        default=True,
        verbose_name="Ativo",
        help_text="Desmarque para ocultar o evento"
    )

    status = models.CharField(
        max_length=20,
        choices=EVENT_STATUS_CHOICES,
        default='upcoming',
        verbose_name="Status"
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Atualizado em"
    )

    class Meta:
        verbose_name = "Evento"
        verbose_name_plural = "Eventos"
        ordering = ['start_date']

    def save(self, *args, **kwargs):
        """Gera slug e atualiza status automaticamente"""
        if not self.slug:
            self.slug = slugify(self.title)

        # Gerar descrição curta se vazia
        if not self.short_description and self.description:
            self.short_description = self.description[:180] + '...'

        # Atualizar status baseado nas datas
        now = timezone.now()
        if self.end_date < now:
            self.status = 'finished'
        elif self.start_date <= now <= self.end_date:
            self.status = 'ongoing'
        elif self.start_date > now:
            self.status = 'upcoming'

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} - {self.start_date.strftime('%d/%m/%Y')}"

    def is_finished(self):
        """Verifica se o evento já terminou"""
        return timezone.now() > self.end_date

    def is_ongoing(self):
        """Verifica se o evento está acontecendo agora"""
        now = timezone.now()
        return self.start_date <= now <= self.end_date

    def is_upcoming(self):
        """Verifica se o evento ainda vai acontecer"""
        return timezone.now() < self.start_date

    def days_until_event(self):
        """Retorna quantos dias faltam para o evento"""
        if self.is_upcoming():
            delta = self.start_date - timezone.now()
            return delta.days
        return 0

    def get_location_display(self):
        """Retorna localização formatada"""
        if self.is_online:
            return "Evento Online"

        parts = [self.location_name]
        if self.location_city:
            parts.append(self.location_city)
        if self.location_state:
            parts.append(self.location_state)

        return " - ".join(parts)