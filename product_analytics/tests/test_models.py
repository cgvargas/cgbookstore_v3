"""
Testes para models do módulo Product Analytics.

Cobre:
- AnalyticsSession: criação, propriedades, is_active, duration
- ProductEvent: criação, clean(), validação de allowlist
- DailyMetricSnapshot: upsert idempotente, unique_together
"""
from decimal import Decimal
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from product_analytics.models import AnalyticsSession, ProductEvent, DailyMetricSnapshot
from product_analytics.constants import ALLOWED_EVENT_TYPES


class AnalyticsSessionModelTest(TestCase):
    """Testa o model AnalyticsSession."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="leitor_teste",
            password="senha123",
            email="leitor@test.com",
        )

    def _make_session(self, **kwargs):
        defaults = {
            "session_key": "abc12345678901234567890123456789012",
            "started_at": timezone.now(),
            "last_activity_at": timezone.now(),
        }
        defaults.update(kwargs)
        return AnalyticsSession.objects.create(**defaults)

    def test_create_anonymous_session(self):
        session = self._make_session()
        self.assertIsNone(session.user)
        self.assertFalse(session.is_authenticated)
        self.assertIsNotNone(session.pk)

    def test_create_authenticated_session(self):
        session = self._make_session(user=self.user, is_authenticated=True)
        self.assertEqual(session.user, self.user)
        self.assertTrue(session.is_authenticated)

    def test_duration_seconds_no_end(self):
        """Duração calculada com last_activity_at quando sem ended_at."""
        started = timezone.now() - timezone.timedelta(minutes=10)
        session = self._make_session(
            started_at=started,
            last_activity_at=timezone.now(),
        )
        duration = session.duration_seconds
        self.assertIsNotNone(duration)
        # ~600s ± 5s de margem de tempo de test
        self.assertGreaterEqual(duration, 595)
        self.assertLessEqual(duration, 610)

    def test_duration_seconds_with_end(self):
        """Duração calculada com ended_at quando disponível."""
        started = timezone.now() - timezone.timedelta(minutes=20)
        ended = timezone.now() - timezone.timedelta(minutes=5)
        session = self._make_session(
            started_at=started,
            last_activity_at=timezone.now(),
            ended_at=ended,
        )
        # Deve usar ended_at (15 min = 900s) e não last_activity_at
        duration = session.duration_seconds
        self.assertIsNotNone(duration)
        self.assertGreaterEqual(duration, 895)
        self.assertLessEqual(duration, 910)

    def test_duration_minutes_property(self):
        started = timezone.now() - timezone.timedelta(minutes=5)
        session = self._make_session(
            started_at=started,
            last_activity_at=timezone.now(),
        )
        mins = session.duration_minutes
        self.assertIsNotNone(mins)
        self.assertGreaterEqual(mins, 4.9)

    def test_is_active_fresh_session(self):
        """Sessão recém-criada deve ser ativa."""
        session = self._make_session()
        self.assertTrue(session.is_active)

    def test_is_active_ended_session(self):
        """Sessão encerrada não deve ser ativa."""
        session = self._make_session(ended_at=timezone.now())
        self.assertFalse(session.is_active)

    def test_str_representation(self):
        session = self._make_session(user=self.user, is_authenticated=True)
        self.assertIn("leitor_teste", str(session))

    def test_str_anonymous(self):
        session = self._make_session(session_key="aaabbbccc12345678901234567890123456")
        self.assertIn("Anônimo", str(session))


class ProductEventModelTest(TestCase):
    """Testa o model ProductEvent."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="leitor_evento",
            password="senha123",
        )
        self.session = AnalyticsSession.objects.create(
            session_key="xyz12345678901234567890123456789012",
            started_at=timezone.now(),
            last_activity_at=timezone.now(),
        )

    def _make_event(self, **kwargs):
        defaults = {
            "event_type": "page_view",
            "page_name": "home",
            "session": self.session,
        }
        defaults.update(kwargs)
        return ProductEvent.objects.create(**defaults)

    def test_create_page_view_event(self):
        event = self._make_event()
        self.assertEqual(event.event_type, "page_view")
        self.assertEqual(event.page_name, "home")
        self.assertIsNone(event.user)

    def test_create_event_with_user(self):
        event = self._make_event(user=self.user)
        self.assertEqual(event.user, self.user)

    def test_create_event_with_metadata(self):
        event = self._make_event(
            event_type="search_performed",
            page_name="search",
            metadata={"query_term_hash": "abc123", "result_count": 15},
        )
        self.assertEqual(event.metadata["result_count"], 15)

    def test_create_all_allowed_event_types(self):
        """Todos os tipos da allowlist devem ser criados sem erro."""
        for event_type in ALLOWED_EVENT_TYPES:
            event = self._make_event(event_type=event_type)
            self.assertEqual(event.event_type, event_type)

    def test_clean_raises_for_invalid_event_type(self):
        """clean() deve rejeitar event_types fora da allowlist."""
        event = ProductEvent(
            event_type="hacker_payload",
            page_name="home",
            session=self.session,
        )
        with self.assertRaises(ValidationError):
            event.clean()

    def test_clean_raises_for_invalid_object_type(self):
        """clean() deve rejeitar object_types não mapeados."""
        event = ProductEvent(
            event_type="page_view",
            page_name="book_detail",
            object_type="invalid_type",
            session=self.session,
        )
        with self.assertRaises(ValidationError):
            event.clean()

    def test_str_representation(self):
        event = self._make_event(user=self.user)
        self.assertIn("page_view", str(event))
        self.assertIn("home", str(event))
        self.assertIn("leitor_evento", str(event))

    def test_event_without_session(self):
        """Evento sem sessão deve ser permitido (ex: eventos server-side)."""
        event = self._make_event(session=None)
        self.assertIsNone(event.session)

    def test_metadata_default_empty_dict(self):
        event = self._make_event()
        self.assertEqual(event.metadata, {})


class DailyMetricSnapshotModelTest(TestCase):
    """Testa o model DailyMetricSnapshot."""

    def setUp(self):
        from datetime import date
        self.today = date.today()

    def test_upsert_creates_new(self):
        snapshot = DailyMetricSnapshot.upsert(
            date=self.today,
            metric_name="dau",
            value=Decimal("250"),
            source_apps=["product_analytics"],
        )
        self.assertIsNotNone(snapshot.pk)
        self.assertEqual(snapshot.metric_name, "dau")
        self.assertEqual(snapshot.value, Decimal("250"))

    def test_upsert_is_idempotent(self):
        """Chamar upsert duas vezes para a mesma chave deve atualizar, não duplicar."""
        DailyMetricSnapshot.upsert(
            date=self.today,
            metric_name="dau",
            value=Decimal("100"),
        )
        DailyMetricSnapshot.upsert(
            date=self.today,
            metric_name="dau",
            value=Decimal("350"),
        )
        count = DailyMetricSnapshot.objects.filter(
            date=self.today, metric_name="dau"
        ).count()
        snapshot = DailyMetricSnapshot.objects.get(
            date=self.today, metric_name="dau"
        )
        self.assertEqual(count, 1)
        self.assertEqual(snapshot.value, Decimal("350"))

    def test_upsert_with_dimension(self):
        """Dimensões distintas criam linhas distintas."""
        DailyMetricSnapshot.upsert(
            date=self.today,
            metric_name="dau",
            value=Decimal("100"),
            dimension="device_type",
            dimension_value="mobile",
        )
        DailyMetricSnapshot.upsert(
            date=self.today,
            metric_name="dau",
            value=Decimal("150"),
            dimension="device_type",
            dimension_value="desktop",
        )
        count = DailyMetricSnapshot.objects.filter(
            date=self.today, metric_name="dau"
        ).count()
        self.assertEqual(count, 2)

    def test_is_partial_default_false(self):
        snapshot = DailyMetricSnapshot.upsert(
            date=self.today, metric_name="test_metric", value=1
        )
        self.assertFalse(snapshot.is_partial)

    def test_is_partial_can_be_set(self):
        snapshot = DailyMetricSnapshot.upsert(
            date=self.today,
            metric_name="sessions_total",
            value=0,
            is_partial=True,
        )
        self.assertTrue(snapshot.is_partial)

    def test_str_representation(self):
        snapshot = DailyMetricSnapshot.upsert(
            date=self.today, metric_name="dau", value=300
        )
        self.assertIn("dau", str(snapshot))
        self.assertIn("300", str(snapshot))

    def test_str_partial_label(self):
        snapshot = DailyMetricSnapshot.upsert(
            date=self.today, metric_name="page_views_total", value=0, is_partial=True
        )
        self.assertIn("partial", str(snapshot))
