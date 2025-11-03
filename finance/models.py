"""
Modelos do módulo financeiro - CGBookStore v3
Gerencia assinaturas premium, produtos, pedidos e transações
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal


class Subscription(models.Model):
    """
    Modelo de assinatura premium (R$ 9,90/mês)
    """
    STATUS_CHOICES = [
        ('ativa', 'Ativa'),
        ('pendente', 'Pendente'),
        ('cancelada', 'Cancelada'),
        ('expirada', 'Expirada'),
    ]

    PAYMENT_METHODS = [
        ('pix', 'PIX'),
        ('credit_card', 'Cartão de Crédito'),
        ('boleto', 'Boleto Bancário'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='subscription',
        verbose_name='Usuário'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pendente',
        verbose_name='Status'
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS,
        verbose_name='Método de Pagamento'
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('9.90'),
        verbose_name='Valor Mensal'
    )
    start_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Data de Início'
    )
    expiration_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Data de Expiração'
    )
    next_billing_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Próxima Cobrança'
    )

    # Integração Mercado Pago
    mp_subscription_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name='ID Assinatura MP'
    )
    mp_payment_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name='ID Pagamento MP'
    )
    mp_preference_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name='ID Preferência MP'
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')

    class Meta:
        verbose_name = 'Assinatura'
        verbose_name_plural = 'Assinaturas'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.status}"

    def is_active(self):
        """Verifica se a assinatura está ativa e não expirou"""
        if self.status != 'ativa':
            return False
        if self.expiration_date and self.expiration_date < timezone.now():
            return False
        return True

    def activate(self, duration_days=30, is_free_campaign=False):
        """
        Ativa a assinatura por um período específico

        Args:
            duration_days (int): Duração em dias (padrão: 30)
            is_free_campaign (bool): Se é uma campanha gratuita (não cobra)
        """
        self.status = 'ativa'
        self.start_date = timezone.now()
        self.expiration_date = timezone.now() + timedelta(days=duration_days)

        # Se não for campanha gratuita, define próxima cobrança
        if not is_free_campaign:
            self.next_billing_date = self.expiration_date
        else:
            self.next_billing_date = None  # Campanhas gratuitas não têm cobrança

        self.save()

    def cancel(self):
        """Cancela a assinatura"""
        self.status = 'cancelada'
        self.save()

    def renew(self):
        """Renova a assinatura por mais 30 dias"""
        if self.expiration_date:
            self.expiration_date += timedelta(days=30)
        else:
            self.expiration_date = timezone.now() + timedelta(days=30)
        self.next_billing_date = self.expiration_date
        self.status = 'ativa'
        self.save()


class Product(models.Model):
    """Modelo de produto (livros físicos e digitais)"""
    PRODUCT_TYPES = [
        ('physical', 'Livro Físico'),
        ('digital', 'Livro Digital (eBook)'),
        ('both', 'Físico + Digital'),
    ]

    name = models.CharField(max_length=255, verbose_name='Nome do Produto')
    description = models.TextField(verbose_name='Descrição')
    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPES, default='physical', verbose_name='Tipo de Produto')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Preço')
    stock = models.IntegerField(default=0, verbose_name='Estoque')
    isbn = models.CharField(max_length=13, null=True, blank=True, verbose_name='ISBN')
    author = models.CharField(max_length=255, verbose_name='Autor')
    publisher = models.CharField(max_length=255, null=True, blank=True, verbose_name='Editora')
    cover_image = models.URLField(null=True, blank=True, verbose_name='Imagem da Capa')
    digital_file = models.URLField(null=True, blank=True, verbose_name='Arquivo Digital (URL Supabase)')
    is_active = models.BooleanField(default=True, verbose_name='Ativo')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')

    class Meta:
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - R$ {self.price}"

    def has_stock(self):
        if self.product_type == 'digital':
            return True
        return self.stock > 0


class Order(models.Model):
    """Modelo de pedido (carrinho de compras)"""
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('approved', 'Aprovado'),
        ('processing', 'Processando'),
        ('shipped', 'Enviado'),
        ('delivered', 'Entregue'),
        ('cancelled', 'Cancelado'),
        ('refunded', 'Reembolsado'),
    ]

    PAYMENT_METHODS = [
        ('pix', 'PIX'),
        ('credit_card', 'Cartão de Crédito'),
        ('boleto', 'Boleto Bancário'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', verbose_name='Usuário')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Status')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, verbose_name='Método de Pagamento')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Valor Total')
    shipping_address = models.TextField(verbose_name='Endereço de Entrega')
    shipping_city = models.CharField(max_length=100, verbose_name='Cidade')
    shipping_state = models.CharField(max_length=2, verbose_name='Estado')
    shipping_zipcode = models.CharField(max_length=9, verbose_name='CEP')
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name='Custo de Envio')
    mp_payment_id = models.CharField(max_length=255, null=True, blank=True, verbose_name='ID Pagamento MP')
    mp_preference_id = models.CharField(max_length=255, null=True, blank=True, verbose_name='ID Preferência MP')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')
    paid_at = models.DateTimeField(null=True, blank=True, verbose_name='Pago em')

    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['-created_at']

    def __str__(self):
        return f"Pedido #{self.id} - {self.user.username} - R$ {self.total_amount}"

    def calculate_total(self):
        items_total = sum(item.subtotal() for item in self.items.all())
        self.total_amount = items_total + self.shipping_cost
        self.save()
        return self.total_amount


class OrderItem(models.Model):
    """Item individual de um pedido"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='Pedido')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name='Produto')
    quantity = models.IntegerField(default=1, verbose_name='Quantidade')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Preço Unitário')

    class Meta:
        verbose_name = 'Item do Pedido'
        verbose_name_plural = 'Itens do Pedido'

    def __str__(self):
        return f"{self.product.name} x{self.quantity}"

    def subtotal(self):
        return self.quantity * self.unit_price


class TransactionLog(models.Model):
    """Registro de transações e webhooks do Mercado Pago"""
    TRANSACTION_TYPES = [
        ('subscription', 'Assinatura'),
        ('order', 'Pedido'),
        ('refund', 'Reembolso'),
        ('webhook', 'Webhook'),
    ]

    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES, verbose_name='Tipo de Transação')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions', verbose_name='Usuário')
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions', verbose_name='Assinatura')
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions', verbose_name='Pedido')
    mp_payment_id = models.CharField(max_length=255, null=True, blank=True, verbose_name='ID Pagamento MP')
    mp_status = models.CharField(max_length=50, null=True, blank=True, verbose_name='Status MP')
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Valor')
    payment_method = models.CharField(max_length=50, null=True, blank=True, verbose_name='Método de Pagamento')
    raw_data = models.JSONField(null=True, blank=True, verbose_name='Dados Brutos')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')

    class Meta:
        verbose_name = 'Log de Transação'
        verbose_name_plural = 'Logs de Transações'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.transaction_type} - {self.mp_payment_id} - {self.created_at}"


class Campaign(models.Model):
    """
    Modelo de campanha de marketing para concessão de Premium gratuito
    """
    DURATION_CHOICES = [
        (7, '7 dias'),
        (15, '15 dias'),
        (30, '30 dias'),
    ]

    TARGET_TYPES = [
        ('individual', 'Usuário Individual'),
        ('group', 'Grupo de Usuários'),
        ('new_users', 'Novos Usuários'),
        ('birthdays', 'Aniversariantes do Mês'),
        ('custom', 'Critério Personalizado'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Rascunho'),
        ('active', 'Ativa'),
        ('paused', 'Pausada'),
        ('completed', 'Concluída'),
        ('cancelled', 'Cancelada'),
    ]

    # Identificação
    name = models.CharField(
        max_length=200,
        verbose_name='Nome da Campanha',
        help_text='Nome descritivo para a campanha'
    )
    description = models.TextField(
        verbose_name='Descrição',
        help_text='Detalhes sobre o objetivo e público-alvo da campanha'
    )

    # Configuração
    duration_days = models.IntegerField(
        choices=DURATION_CHOICES,
        default=7,
        verbose_name='Duração do Premium Gratuito',
        help_text='Quantos dias de Premium gratuito serão concedidos'
    )

    # Critérios de seleção
    target_type = models.CharField(
        max_length=20,
        choices=TARGET_TYPES,
        default='custom',
        verbose_name='Tipo de Público-Alvo',
        help_text='Como os usuários serão selecionados'
    )

    criteria = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Critérios de Seleção',
        help_text='Filtros e condições para selecionar usuários (formato JSON)'
    )

    # Período da campanha
    start_date = models.DateTimeField(
        verbose_name='Data de Início',
        help_text='Quando a campanha começa a vigorar'
    )
    end_date = models.DateTimeField(
        verbose_name='Data de Término',
        help_text='Quando a campanha termina'
    )

    # Status e controle
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name='Status da Campanha'
    )

    auto_grant = models.BooleanField(
        default=True,
        verbose_name='Concessão Automática',
        help_text='Se marcado, o Premium será concedido automaticamente aos usuários elegíveis'
    )

    max_grants = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='Limite de Concessões',
        help_text='Número máximo de usuários que podem receber (deixe em branco para ilimitado)'
    )

    # Estatísticas
    total_granted = models.IntegerField(
        default=0,
        verbose_name='Total Concedido',
        help_text='Quantos usuários já receberam Premium nesta campanha'
    )

    total_eligible = models.IntegerField(
        default=0,
        verbose_name='Total Elegível',
        help_text='Quantos usuários são elegíveis segundo os critérios'
    )

    # Auditoria
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='campaigns_created',
        verbose_name='Criado por'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')

    class Meta:
        verbose_name = 'Campanha de Marketing'
        verbose_name_plural = 'Campanhas de Marketing'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"

    def is_active_now(self):
        """Verifica se a campanha está ativa no momento"""
        now = timezone.now()
        return (
            self.status == 'active' and
            self.start_date <= now <= self.end_date
        )

    def can_grant_more(self):
        """Verifica se ainda pode conceder mais Premiums"""
        if self.max_grants is None:
            return True
        return self.total_granted < self.max_grants

    def get_remaining_grants(self):
        """Retorna quantas concessões ainda podem ser feitas"""
        if self.max_grants is None:
            return float('inf')
        return max(0, self.max_grants - self.total_granted)


class CampaignGrant(models.Model):
    """
    Registro de concessão de Premium gratuito através de campanha
    """
    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE,
        related_name='grants',
        verbose_name='Campanha'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='campaign_grants',
        verbose_name='Usuário'
    )
    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.CASCADE,
        related_name='campaign_grants',
        verbose_name='Assinatura'
    )

    # Controle de concessão
    granted_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Concedido em'
    )
    expires_at = models.DateTimeField(
        verbose_name='Expira em'
    )
    revoked_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Revogado em'
    )

    # Status
    is_active = models.BooleanField(
        default=True,
        verbose_name='Ativo',
        help_text='Se o Premium concedido ainda está ativo'
    )

    was_notified = models.BooleanField(
        default=False,
        verbose_name='Usuário Notificado',
        help_text='Se o usuário foi notificado por email sobre a concessão'
    )

    # Metadados
    reason = models.TextField(
        blank=True,
        verbose_name='Motivo/Observações',
        help_text='Motivo específico da concessão ou observações do administrador'
    )

    class Meta:
        verbose_name = 'Concessão de Campanha'
        verbose_name_plural = 'Concessões de Campanhas'
        ordering = ['-granted_at']
        unique_together = [['campaign', 'user']]  # Um usuário só pode receber uma vez por campanha

    def __str__(self):
        return f"{self.campaign.name} → {self.user.username}"

    def is_expired(self):
        """Verifica se a concessão já expirou"""
        return self.expires_at < timezone.now()

    def revoke(self):
        """Revoga a concessão de Premium"""
        self.is_active = False
        self.revoked_at = timezone.now()
        self.save()

        # Atualiza a assinatura para cancelada
        if self.subscription:
            self.subscription.cancel()
