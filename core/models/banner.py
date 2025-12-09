"""
Model Banner - Banners promocionais para carrossel da home
"""
from django.db import models
from core.storage_backends import SupabaseMediaStorage


class Banner(models.Model):
    """
    Model para banners promocionais exibidos em carrossel na página inicial.
    Permite ao administrador gerenciar banners com rotação automática.
    """

    # Informações básicas
    title = models.CharField(
        max_length=200,
        verbose_name="Título",
        help_text="Título do banner (para identificação no admin)"
    )

    subtitle = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Subtítulo",
        help_text="Texto secundário exibido no banner (opcional)"
    )

    description = models.TextField(
        blank=True,
        verbose_name="Descrição",
        help_text="Texto descritivo exibido no banner (opcional)"
    )

    # Imagem do banner
    image = models.ImageField(
        upload_to='banners/home/',
        storage=SupabaseMediaStorage(),
        verbose_name="Imagem do Banner",
        help_text="Imagem do banner (recomendado: 1920x600px, máx. 5MB)"
    )

    # Link de ação
    link_url = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="Link de Destino",
        help_text="URL para onde o usuário será direcionado ao clicar. Ex: /novos-autores/ ou https://site.com"
    )

    link_text = models.CharField(
        max_length=50,
        blank=True,
        default="Saiba mais",
        verbose_name="Texto do Botão",
        help_text="Texto exibido no botão de ação"
    )

    open_in_new_tab = models.BooleanField(
        default=False,
        verbose_name="Abrir em Nova Aba",
        help_text="Marque para abrir o link em nova aba"
    )

    # Configurações de exibição
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordem de Exibição",
        help_text="Ordem em que o banner aparece no carrossel (menor = primeiro)"
    )

    active = models.BooleanField(
        default=True,
        verbose_name="Ativo",
        help_text="Desmarque para ocultar este banner"
    )

    height = models.PositiveIntegerField(
        default=700,
        verbose_name="Altura do Banner (px)",
        help_text="Altura do banner em pixels (padrão: 700px, estilo Crunchyroll: 700-900px)"
    )

    # Período de exibição
    start_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Data de Início",
        help_text="Data/hora de início da exibição (deixe vazio para exibir imediatamente)"
    )

    end_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Data de Término",
        help_text="Data/hora de término da exibição (deixe vazio para exibir indefinidamente)"
    )

    # Estatísticas
    views_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Visualizações",
        help_text="Número de vezes que o banner foi exibido"
    )

    clicks_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Cliques",
        help_text="Número de cliques no banner"
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
        verbose_name = "Banner"
        verbose_name_plural = "Banners"
        ordering = ['order', '-created_at']

    def __str__(self):
        status = "✓" if self.active else "✗"
        return f"{status} {self.title} (Ordem: {self.order})"

    def is_visible(self):
        """
        Verifica se o banner deve ser exibido baseado em:
        - Status ativo
        - Data de início (se definida)
        - Data de término (se definida)
        """
        if not self.active:
            return False

        from django.utils import timezone
        now = timezone.now()

        # Verificar data de início
        if self.start_date and now < self.start_date:
            return False

        # Verificar data de término
        if self.end_date and now > self.end_date:
            return False

        return True

    def increment_views(self):
        """Incrementa contador de visualizações"""
        self.views_count += 1
        self.save(update_fields=['views_count'])

    def increment_clicks(self):
        """Incrementa contador de cliques"""
        self.clicks_count += 1
        self.save(update_fields=['clicks_count'])

    def get_ctr(self):
        """Calcula CTR (Click-Through Rate) em porcentagem"""
        if self.views_count == 0:
            return 0
        return round((self.clicks_count / self.views_count) * 100, 2)
