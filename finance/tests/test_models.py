"""
Testes automatizados para o app Finance.
Cobertura: Subscription, Campaign, Product, Order
"""
from django.test import TestCase
from django.contrib.auth.models import User
from datetime import date, timedelta
from django.utils import timezone
from decimal import Decimal
from finance.models import Subscription, Campaign, Product, Order, OrderItem, TransactionLog


class SubscriptionModelTest(TestCase):
    """Testes para o model Subscription."""

    def setUp(self):
        """Configuração inicial para os testes."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.subscription = Subscription.objects.create(
            user=self.user,
            status='pendente'
        )

    def test_subscription_creation(self):
        """Testa criação de assinatura."""
        self.assertEqual(self.subscription.user, self.user)
        self.assertEqual(self.subscription.status, 'pendente')

    def test_subscription_str(self):
        """Testa representação string da assinatura."""
        self.assertIn(self.user.username, str(self.subscription))

    def test_subscription_is_active_pending(self):
        """Testa is_active com status pendente."""
        self.assertFalse(self.subscription.is_active)

    def test_subscription_activate(self):
        """Testa ativação de assinatura."""
        self.subscription.activate(duration_days=30)
        self.assertEqual(self.subscription.status, 'ativa')
        self.assertIsNotNone(self.subscription.expires_at)
        self.assertTrue(self.subscription.is_active)

    def test_subscription_activate_free_campaign(self):
        """Testa ativação via campanha gratuita."""
        self.subscription.activate(duration_days=15, is_free_campaign=True)
        self.assertEqual(self.subscription.status, 'ativa')
        self.assertTrue(self.subscription.is_active)

    def test_subscription_cancel(self):
        """Testa cancelamento de assinatura."""
        self.subscription.activate()
        self.subscription.cancel()
        self.assertEqual(self.subscription.status, 'cancelada')
        self.assertFalse(self.subscription.is_active)

    def test_subscription_renew(self):
        """Testa renovação de assinatura."""
        self.subscription.activate()
        old_expires = self.subscription.expires_at
        self.subscription.renew()
        self.assertGreater(self.subscription.expires_at, old_expires)

    def test_subscription_expired(self):
        """Testa assinatura expirada."""
        self.subscription.status = 'ativa'
        self.subscription.expires_at = timezone.now() - timedelta(days=1)
        self.subscription.save()
        self.assertFalse(self.subscription.is_active)


class CampaignModelTest(TestCase):
    """Testes para o model Campaign."""

    def setUp(self):
        """Configuração inicial para os testes."""
        self.campaign = Campaign.objects.create(
            name="Black Friday Premium",
            description="Premium grátis por 30 dias",
            premium_duration_days=30,
            start_date=timezone.now() - timedelta(days=1),
            end_date=timezone.now() + timedelta(days=7),
            max_grants=100,
            is_active=True
        )

    def test_campaign_creation(self):
        """Testa criação de campanha."""
        self.assertEqual(self.campaign.name, "Black Friday Premium")
        self.assertEqual(self.campaign.premium_duration_days, 30)

    def test_campaign_str(self):
        """Testa representação string da campanha."""
        self.assertEqual(str(self.campaign), "Black Friday Premium")

    def test_campaign_is_active_now(self):
        """Testa verificação se campanha está ativa agora."""
        self.assertTrue(self.campaign.is_active_now)

    def test_campaign_is_not_active_before_start(self):
        """Testa campanha antes da data de início."""
        self.campaign.start_date = timezone.now() + timedelta(days=1)
        self.campaign.save()
        self.assertFalse(self.campaign.is_active_now)

    def test_campaign_is_not_active_after_end(self):
        """Testa campanha após data de término."""
        self.campaign.end_date = timezone.now() - timedelta(days=1)
        self.campaign.save()
        self.assertFalse(self.campaign.is_active_now)

    def test_campaign_can_grant_more(self):
        """Testa se pode conceder mais prêmios."""
        self.campaign.grants_used = 0
        self.campaign.save()
        self.assertTrue(self.campaign.can_grant_more)

    def test_campaign_cannot_grant_more(self):
        """Testa quando não pode conceder mais prêmios."""
        self.campaign.grants_used = 100
        self.campaign.save()
        self.assertFalse(self.campaign.can_grant_more)

    def test_campaign_remaining_grants(self):
        """Testa contagem de concessões restantes."""
        self.campaign.grants_used = 30
        self.campaign.save()
        self.assertEqual(self.campaign.get_remaining_grants, 70)


class ProductModelTest(TestCase):
    """Testes para o model Product."""

    def setUp(self):
        """Configuração inicial para os testes."""
        self.product = Product.objects.create(
            name="Livro Físico Teste",
            description="Um livro de teste",
            price=Decimal('49.90'),
            product_type='physical',
            stock=10,
            is_active=True
        )

    def test_product_creation(self):
        """Testa criação de produto."""
        self.assertEqual(self.product.name, "Livro Físico Teste")
        self.assertEqual(self.product.price, Decimal('49.90'))

    def test_product_str(self):
        """Testa representação string do produto."""
        self.assertEqual(str(self.product), "Livro Físico Teste")

    def test_product_has_stock(self):
        """Testa verificação de estoque."""
        self.assertTrue(self.product.has_stock)

    def test_product_no_stock(self):
        """Testa produto sem estoque."""
        self.product.stock = 0
        self.product.save()
        self.assertFalse(self.product.has_stock)

    def test_product_types(self):
        """Testa diferentes tipos de produto."""
        types = ['physical', 'digital', 'both']
        for ptype in types:
            product = Product.objects.create(
                name=f"Produto {ptype}",
                price=Decimal('29.90'),
                product_type=ptype
            )
            self.assertEqual(product.product_type, ptype)


class OrderModelTest(TestCase):
    """Testes para os models Order e OrderItem."""

    def setUp(self):
        """Configuração inicial para os testes."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.product = Product.objects.create(
            name="Produto Teste",
            price=Decimal('49.90'),
            product_type='physical'
        )
        self.order = Order.objects.create(
            user=self.user,
            status='pending'
        )

    def test_order_creation(self):
        """Testa criação de pedido."""
        self.assertEqual(self.order.user, self.user)
        self.assertEqual(self.order.status, 'pending')

    def test_order_str(self):
        """Testa representação string do pedido."""
        self.assertIn(str(self.order.id), str(self.order))

    def test_order_item_creation(self):
        """Testa criação de item de pedido."""
        item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=2,
            unit_price=self.product.price
        )
        self.assertEqual(item.quantity, 2)
        self.assertEqual(item.unit_price, Decimal('49.90'))

    def test_order_item_subtotal(self):
        """Testa cálculo de subtotal do item."""
        item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=3,
            unit_price=Decimal('10.00')
        )
        self.assertEqual(item.subtotal, Decimal('30.00'))

    def test_order_calculate_total(self):
        """Testa cálculo de total do pedido."""
        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=2,
            unit_price=Decimal('25.00')
        )
        product2 = Product.objects.create(
            name="Produto 2",
            price=Decimal('15.00'),
            product_type='digital'
        )
        OrderItem.objects.create(
            order=self.order,
            product=product2,
            quantity=1,
            unit_price=Decimal('15.00')
        )
        total = self.order.calculate_total()
        self.assertEqual(total, Decimal('65.00'))

    def test_order_status_choices(self):
        """Testa diferentes status de pedido."""
        statuses = ['pending', 'approved', 'processing', 'shipped', 'delivered', 'cancelled']
        for status in statuses:
            self.order.status = status
            self.order.save()
            self.assertEqual(self.order.status, status)


class TransactionLogModelTest(TestCase):
    """Testes para o model TransactionLog."""

    def setUp(self):
        """Configuração inicial para os testes."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_transaction_log_creation(self):
        """Testa criação de log de transação."""
        log = TransactionLog.objects.create(
            user=self.user,
            transaction_type='subscription',
            amount=Decimal('9.90'),
            status='completed',
            external_id='MP12345'
        )
        self.assertEqual(log.transaction_type, 'subscription')
        self.assertEqual(log.amount, Decimal('9.90'))

    def test_transaction_log_str(self):
        """Testa representação string do log."""
        log = TransactionLog.objects.create(
            user=self.user,
            transaction_type='order',
            amount=Decimal('50.00'),
            status='pending'
        )
        self.assertIn('order', str(log))

    def test_transaction_log_types(self):
        """Testa diferentes tipos de transação."""
        types = ['subscription', 'order', 'refund', 'webhook']
        for ttype in types:
            log = TransactionLog.objects.create(
                user=self.user,
                transaction_type=ttype,
                amount=Decimal('10.00'),
                status='completed'
            )
            self.assertEqual(log.transaction_type, ttype)
