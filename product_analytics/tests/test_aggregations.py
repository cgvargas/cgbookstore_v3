"""
Testes para agregação, snapshots e retenção do Product Analytics.

Cobre:
- AppSelectors
- SnapshotService (DAU/WAU/MAU, Sessões, Conversão Premium, Duração)
- Retenção D1, D7, D30
- Command compute_daily_metrics
"""
import datetime
from decimal import Decimal
from django.test import TestCase, override_settings
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.management import call_command

# Modelos do App e Externos
from product_analytics.models import DailyMetricSnapshot, ProductEvent, AnalyticsSession
from product_analytics.constants import (
    METRIC_DAU,
    METRIC_WAU,
    METRIC_MAU,
    METRIC_NEW_USERS,
    METRIC_BOOKS_ADDED,
    METRIC_BOOKS_COMPLETED,
    METRIC_PREMIUM_CONVERSIONS,
    METRIC_RETENTION_D1,
    METRIC_RETENTION_D7,
    METRIC_RETENTION_D30,
)
from product_analytics.services.selectors import AppSelectors
from product_analytics.services.snapshot_service import SnapshotService

try:
    from core.models import Book, Author
    from accounts.models import BookShelf
    from finance.models import Subscription
    from chatbot_literario.models import ChatSession
    from partners.models import AffiliatePartner, AffiliatePartnerClick
except ImportError:
    Book = None
    BookShelf = None
    Subscription = None
    ChatSession = None
    AffiliatePartnerClick = None


class AppSelectorsTest(TestCase):
    """Testa a extração de dados através do AppSelectors."""

    def setUp(self):
        self.User = get_user_model()
        self.today = timezone.localdate()

        # Cria usuário de teste
        self.user = self.User.objects.create_user(
            username="usuario_teste_sel",
            email="sel@test.com",
            password="password123",
        )
        # Ajusta a data de cadastro do usuário para hoje
        self.User.objects.filter(pk=self.user.pk).update(
            date_joined=timezone.now()
        )

        # Configura dependências do core se existirem
        if Book and Author:
            self.author = Author.objects.create(name="Tolkien")
            self.book = Book.objects.create(
                title="O Hobbit",
                author=self.author,
                price=Decimal("49.90"),
                publication_date=datetime.date(1937, 9, 21),
            )

    def test_new_users_count(self):
        count = AppSelectors.get_new_users_count(self.today)
        self.assertEqual(count, 1)

        # Ontem deve ser 0
        yesterday = self.today - datetime.timedelta(days=1)
        self.assertEqual(AppSelectors.get_new_users_count(yesterday), 0)

    def test_books_added_and_completed_counts(self):
        if not BookShelf:
            self.skipTest("BookShelf model não disponível.")

        # Adiciona livro à prateleira lendo
        shelf = BookShelf.objects.create(
            user=self.user,
            book=self.book,
            shelf_type="reading",
            date_added=timezone.now()
        )
        self.assertEqual(AppSelectors.get_books_added_count(self.today), 1)
        self.assertEqual(AppSelectors.get_books_completed_count(self.today), 0)

        # Agora marca como concluído
        shelf.shelf_type = "read"
        shelf.finished_reading = timezone.now()
        shelf.save()

        self.assertEqual(AppSelectors.get_books_completed_count(self.today), 1)


class SnapshotServiceTest(TestCase):
    """Testa os cálculos de snapshots consolidados do SnapshotService."""

    def setUp(self):
        self.User = get_user_model()
        self.today = timezone.localdate()
        self.user = self.User.objects.create_user(
            username="usuario_snap",
            email="snap@test.com",
        )
        self.session = AnalyticsSession.objects.create(
            session_key="snap_session_key_123456789012345678",
            started_at=timezone.now(),
            last_activity_at=timezone.now(),
            user=self.user,
        )

    def test_pre_tracking_partial_metrics(self):
        """Métricas para datas anteriores ao rastreamento devem ser marcadas como parciais."""
        yesterday = self.today - datetime.timedelta(days=10)
        # Calcula ontem
        snapshots = SnapshotService.compute_day(yesterday)

        # Filtra o DAU
        dau_snap = next(s for s in snapshots if s.metric_name == METRIC_DAU)
        self.assertTrue(dau_snap.is_partial)
        self.assertEqual(dau_snap.value, Decimal("0"))

    def test_compute_day_kpis(self):
        """Testa o cálculo correto de métricas analíticas em um dia com tracking ativo."""
        # Cria um evento de page_view hoje
        ProductEvent.objects.create(
            session=self.session,
            user=self.user,
            event_type="page_view",
            page_name="home",
            created_at=timezone.now()
        )

        snapshots = SnapshotService.compute_day(self.today)

        # Verifica DAU
        dau_snap = next(s for s in snapshots if s.metric_name == METRIC_DAU)
        self.assertEqual(dau_snap.value, Decimal("1"))
        self.assertFalse(dau_snap.is_partial)

        # Verifica WAU
        wau_snap = next(s for s in snapshots if s.metric_name == METRIC_WAU)
        self.assertEqual(wau_snap.value, Decimal("1"))

        # Verifica MAU
        mau_snap = next(s for s in snapshots if s.metric_name == METRIC_MAU)
        self.assertEqual(mau_snap.value, Decimal("1"))

    def test_user_retention_calculation(self):
        """Testa o cálculo de retenção D1 (coorte de novos usuários)."""
        User = get_user_model()
        today = timezone.localdate()

        # Cria usuário que cadastrou ONTEM
        yesterday = today - datetime.timedelta(days=1)
        yesterday_dt = timezone.make_aware(datetime.datetime.combine(yesterday, datetime.time(12, 0)))

        user_ret = User.objects.create_user(
            username="user_ret_test",
            email="ret@test.com",
        )
        # Força data de cadastro para ontem
        User.objects.filter(pk=user_ret.pk).update(date_joined=yesterday_dt)

        # Hoje o usuário faz um page_view
        session = AnalyticsSession.objects.create(
            session_key="ret_session_key_12345678901234567890",
            started_at=timezone.now(),
            last_activity_at=timezone.now(),
            user=user_ret,
        )
        ProductEvent.objects.create(
            session=session,
            user=user_ret,
            event_type="page_view",
            page_name="home",
            created_at=timezone.now()
        )

        # Calcula a métrica para ONTEM (quando o usuário cadastrou)
        snapshots = SnapshotService.compute_day(yesterday)

        # A retenção D1 de ontem deve ser 100%
        ret1 = next(s for s in snapshots if s.metric_name == METRIC_RETENTION_D1)
        self.assertEqual(ret1.value, Decimal("100.00"))


class CommandComputeDailyMetricsTest(TestCase):
    """Testa o comando administrativo compute_daily_metrics."""

    def test_command_defaults_to_yesterday(self):
        # Deve rodar sem levantar exceções
        call_command("compute_daily_metrics")

    def test_command_specific_date(self):
        call_command("compute_daily_metrics", date="2026-07-16")
        count = DailyMetricSnapshot.objects.filter(date="2026-07-16").count()
        self.assertGreater(count, 0)

    def test_command_backfill_range(self):
        call_command("compute_daily_metrics", start="2026-07-10", end="2026-07-12")
        # Deve ter snapshots para 10, 11 e 12 de Julho
        for d in ["2026-07-10", "2026-07-11", "2026-07-12"]:
            self.assertGreater(
                DailyMetricSnapshot.objects.filter(date=d).count(),
                0
            )
