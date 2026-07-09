from django.db import models
from django.utils.text import slugify
from django.conf import settings
from core.models import Book


class AffiliatePartner(models.Model):
    """
    Representa um parceiro comercial de afiliados (ex: Amazon, Estante Virtual, etc.).
    """
    nome = models.CharField(
        max_length=100,
        verbose_name="Nome"
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        blank=True,
        verbose_name="Slug"
    )
    tracking_id = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="ID de Rastreamento (Tracking ID)",
        help_text="Identificador de afiliado para rastreamento de comissões (ex: cgbookstore-20)"
    )
    url_base = models.URLField(
        max_length=500,
        blank=True,
        verbose_name="URL Base",
        help_text="URL base do parceiro se aplicável para redirecionamento"
    )
    logo = models.ImageField(
        upload_to='partners/logos/',
        blank=True,
        null=True,
        verbose_name="Logo do Parceiro"
    )
    cor_botao = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Cor do Botão",
        help_text="Classe CSS do Bootstrap (ex: btn-warning, btn-success) ou cor hexadecimal (ex: #FF9900)"
    )
    icone = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Ícone",
        help_text="Classe CSS do FontAwesome para o ícone do botão (ex: fab fa-amazon, fas fa-shopping-cart)"
    )
    ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo",
        help_text="Se desmarcado, este parceiro e seus links de afiliado não serão ativados"
    )
    prioridade = models.IntegerField(
        default=0,
        verbose_name="Prioridade",
        help_text="Ordenação de prioridade (valores maiores têm maior preferência)"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Atualizado em"
    )

    class Meta:
        verbose_name = "Parceiro Comercial"
        verbose_name_plural = "Parceiros Comerciais"
        ordering = ['-prioridade', 'nome']

    def save(self, *args, **kwargs):
        """Gera slug automaticamente a partir do nome se não estiver preenchido."""
        if not self.slug:
            base_slug = slugify(self.nome)
            slug = base_slug
            counter = 1
            while AffiliatePartner.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome


class AffiliatePartnerClick(models.Model):
    """
    Registra cada clique realizado nos links/botões de compra dos parceiros comerciais.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Usuário",
        related_name="affiliate_clicks"
    )
    session_key = models.CharField(
        max_length=40,
        blank=True,
        verbose_name="Chave de Sessão",
        help_text="Identifica acessos de usuários anônimos"
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        verbose_name="Livro",
        related_name="affiliate_clicks"
    )
    partner = models.ForeignKey(
        AffiliatePartner,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Parceiro Comercial",
        related_name="affiliate_clicks"
    )
    destination_url = models.URLField(
        max_length=1000,
        verbose_name="URL de Destino"
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="Endereço IP"
    )
    user_agent = models.TextField(
        blank=True,
        verbose_name="User-Agent"
    )
    browser = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Navegador"
    )
    os = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Sistema Operacional"
    )
    device = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Dispositivo"
    )
    referer = models.URLField(
        max_length=1000,
        blank=True,
        null=True,
        verbose_name="Referer"
    )
    language = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Idioma do Navegador"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name="Data/Hora"
    )

    class Meta:
        verbose_name = "Clique em Parceiro"
        verbose_name_plural = "Cliques em Parceiros"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['device']),
            models.Index(fields=['browser']),
            models.Index(fields=['os']),
        ]

    def __str__(self):
        timestamp = self.created_at.strftime('%d/%m/%Y %H:%M') if self.created_at else 'Rascunho'
        partner_name = self.partner.nome if self.partner else 'Direto'
        return f"{self.book.title} ({partner_name}) - {timestamp}"

