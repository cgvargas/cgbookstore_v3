"""
Testes para services do módulo Product Analytics.

Cobre:
- SessionService: get_or_create, timeout, close_session
- EventService: record, _filter_metadata, _is_valid_event_type, deduplicação
"""
from unittest.mock import patch
from django.test import TestCase, override_settings
from django.utils import timezone
from django.contrib.auth.models import User

from product_analytics.models import AnalyticsSession, ProductEvent
from product_analytics.services.session_service import SessionService
from product_analytics.services.event_service import EventService

ANALYTICS_SYNC_SETTINGS = {
    "PRODUCT_ANALYTICS": {
        "PROCESSING_MODE": "synchronous",
        "SESSION_TIMEOUT_MINUTES": 30,
    }
}

ANALYTICS_DISABLED_SETTINGS = {
    "PRODUCT_ANALYTICS": {
        "PROCESSING_MODE": "disabled",
    }
}


class SessionServiceTest(TestCase):
    """Testa o SessionService."""

    SESSION_KEY = "testkey1234567890123456789012345678"

    def setUp(self):
        self.user = User.objects.create_user(
            username="usuario_sessao",
            password="senha123",
        )

    @override_settings(**ANALYTICS_SYNC_SETTINGS)
    def test_creates_new_session(self):
        session = SessionService.get_or_create(
            session_key=self.SESSION_KEY,
            page_name="home",
        )
        self.assertIsNotNone(session)
        self.assertIsNotNone(session.pk)
        self.assertEqual(session.entry_page, "home")

    @override_settings(**ANALYTICS_SYNC_SETTINGS)
    def test_returns_existing_active_session(self):
        """Mesmo session_key deve retornar a mesma sessão dentro do timeout."""
        session1 = SessionService.get_or_create(
            session_key=self.SESSION_KEY,
            page_name="home",
        )
        session2 = SessionService.get_or_create(
            session_key=self.SESSION_KEY,
            page_name="library",
        )
        self.assertEqual(session1.pk, session2.pk)
        # exit_page deve ser atualizada
        session2.refresh_from_db()
        self.assertEqual(session2.exit_page, "library")

    @override_settings(**ANALYTICS_SYNC_SETTINGS)
    def test_creates_new_session_after_timeout(self):
        """Sessão expirada deve resultar em nova sessão."""
        old_time = timezone.now() - timezone.timedelta(hours=2)
        old_session = AnalyticsSession.objects.create(
            session_key=self.SESSION_KEY,
            started_at=old_time,
            last_activity_at=old_time,
            entry_page="home",
            exit_page="home",
        )
        new_session = SessionService.get_or_create(
            session_key=self.SESSION_KEY,
            page_name="chatbot",
        )
        self.assertNotEqual(old_session.pk, new_session.pk)
        # Sessão antiga deve estar encerrada
        old_session.refresh_from_db()
        self.assertIsNotNone(old_session.ended_at)

    @override_settings(**ANALYTICS_SYNC_SETTINGS)
    def test_associates_user_to_existing_session(self):
        """Usuário que faz login deve ter sessão atualizada com user."""
        session = SessionService.get_or_create(
            session_key=self.SESSION_KEY,
            page_name="home",
        )
        self.assertIsNone(session.user)

        session_updated = SessionService.get_or_create(
            session_key=self.SESSION_KEY,
            user=self.user,
            page_name="library",
        )
        session_updated.refresh_from_db()
        self.assertEqual(session_updated.user, self.user)
        self.assertTrue(session_updated.is_authenticated)

    @override_settings(**ANALYTICS_SYNC_SETTINGS)
    def test_close_session(self):
        SessionService.get_or_create(
            session_key=self.SESSION_KEY,
            page_name="home",
        )
        result = SessionService.close_session(self.SESSION_KEY)
        self.assertTrue(result)
        session = AnalyticsSession.objects.filter(
            session_key=self.SESSION_KEY
        ).first()
        self.assertIsNotNone(session.ended_at)

    @override_settings(**ANALYTICS_SYNC_SETTINGS)
    def test_close_nonexistent_session_returns_false(self):
        result = SessionService.close_session("chave-inexistente-12345678901234567")
        self.assertFalse(result)

    @override_settings(**ANALYTICS_SYNC_SETTINGS)
    def test_extracts_device_info(self):
        session = SessionService.get_or_create(
            session_key=self.SESSION_KEY,
            page_name="home",
            device_type="mobile",
            browser_family="Chrome",
            operating_system="Android",
        )
        self.assertEqual(session.device_type, "mobile")
        self.assertEqual(session.browser_family, "Chrome")
        self.assertEqual(session.operating_system, "Android")

    @override_settings(**ANALYTICS_SYNC_SETTINGS)
    def test_tolerates_db_error_silently(self):
        """Erro de banco deve retornar None sem propagar exceção."""
        with patch(
            "product_analytics.models.AnalyticsSession.objects.filter",
            side_effect=Exception("DB offline"),
        ):
            result = SessionService.get_or_create(
                session_key=self.SESSION_KEY,
                page_name="home",
            )
        self.assertIsNone(result)


class EventServiceTest(TestCase):
    """Testa o EventService."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="usuario_evento",
            password="senha123",
        )
        self.session = AnalyticsSession.objects.create(
            session_key="evt_session_key_1234567890123456789",
            started_at=timezone.now(),
            last_activity_at=timezone.now(),
        )

    @override_settings(**ANALYTICS_SYNC_SETTINGS)
    def test_record_page_view(self):
        result = EventService.record(
            event_type="page_view",
            session=self.session,
            page_name="home",
        )
        self.assertTrue(result)
        self.assertEqual(
            ProductEvent.objects.filter(event_type="page_view").count(), 1
        )

    @override_settings(**ANALYTICS_SYNC_SETTINGS)
    def test_record_deduplicates_page_view(self):
        """Dois page_views consecutivos para a mesma página = apenas 1 evento."""
        EventService.record(
            event_type="page_view",
            session=self.session,
            page_name="home",
        )
        result = EventService.record(
            event_type="page_view",
            session=self.session,
            page_name="home",
        )
        self.assertFalse(result)  # Segundo page_view ignorado
        self.assertEqual(
            ProductEvent.objects.filter(event_type="page_view").count(), 1
        )

    @override_settings(**ANALYTICS_SYNC_SETTINGS)
    def test_no_deduplication_for_different_pages(self):
        """page_view em páginas diferentes devem criar eventos distintos."""
        EventService.record(
            event_type="page_view", session=self.session, page_name="home"
        )
        EventService.record(
            event_type="page_view", session=self.session, page_name="library"
        )
        self.assertEqual(
            ProductEvent.objects.filter(event_type="page_view").count(), 2
        )

    @override_settings(**ANALYTICS_DISABLED_SETTINGS)
    def test_disabled_mode_records_nothing(self):
        result = EventService.record(
            event_type="page_view",
            session=self.session,
            page_name="home",
        )
        self.assertFalse(result)
        self.assertEqual(ProductEvent.objects.count(), 0)

    @override_settings(**ANALYTICS_SYNC_SETTINGS)
    def test_invalid_event_type_rejected(self):
        result = EventService.record(
            event_type="sql_injection",
            session=self.session,
            page_name="home",
        )
        self.assertFalse(result)
        self.assertEqual(ProductEvent.objects.count(), 0)

    @override_settings(**ANALYTICS_SYNC_SETTINGS)
    def test_filters_metadata_keys(self):
        """Apenas chaves da allowlist devem ser persistidas."""
        EventService.record(
            event_type="search_performed",
            session=self.session,
            page_name="search",
            metadata={
                "query_term_hash": "abc123def456789a",  # permitido
                "result_count": 42,                      # permitido
                "user_email": "hacker@evil.com",         # NÃO permitido
                "raw_query": "tolkien password=secret",  # NÃO permitido
            },
        )
        event = ProductEvent.objects.get(event_type="search_performed")
        self.assertIn("query_term_hash", event.metadata)
        self.assertIn("result_count", event.metadata)
        self.assertNotIn("user_email", event.metadata)
        self.assertNotIn("raw_query", event.metadata)

    @override_settings(**ANALYTICS_SYNC_SETTINGS)
    def test_invalid_object_type_cleared(self):
        """object_type inválido deve ser removido silenciosamente."""
        result = EventService.record(
            event_type="page_view",
            session=self.session,
            page_name="book_detail",
            object_type="invalid_type_xyzw",
            object_id=999,
        )
        self.assertTrue(result)
        event = ProductEvent.objects.get(event_type="page_view")
        self.assertEqual(event.object_type, "")
        self.assertIsNone(event.object_id)

    @override_settings(**ANALYTICS_SYNC_SETTINGS)
    def test_tolerates_db_error_silently(self):
        """Erro de banco não deve propagar para a view."""
        with patch(
            "product_analytics.services.event_service.ProductEvent.objects.create",
            side_effect=Exception("DB offline"),
        ):
            result = EventService.record(
                event_type="page_view",
                session=self.session,
                page_name="home",
            )
        # Retorna False sem levantar exceção
        self.assertFalse(result)

    def test_is_valid_event_type(self):
        self.assertTrue(EventService._is_valid_event_type("page_view"))
        self.assertFalse(EventService._is_valid_event_type("invalid"))
        self.assertFalse(EventService._is_valid_event_type(""))

    def test_filter_metadata_removes_disallowed_keys(self):
        result = EventService._filter_metadata({
            "result_count": 10,
            "password": "secret",
            "ip_address": "192.168.1.1",
        })
        self.assertEqual(result, {"result_count": 10})

    def test_filter_metadata_truncates_long_strings(self):
        result = EventService._filter_metadata({
            "query_term_hash": "x" * 600,
        })
        self.assertLessEqual(len(result["query_term_hash"]), 500)

    def test_filter_metadata_ignores_complex_types(self):
        """Listas e dicts aninhados não devem ser armazenados."""
        result = EventService._filter_metadata({
            "result_count": 5,
            "nested_dict": {"a": 1},
            "a_list": [1, 2, 3],
        })
        self.assertIn("result_count", result)
        self.assertNotIn("nested_dict", result)
        self.assertNotIn("a_list", result)
