"""
Testes para o AnalyticsMiddleware.

Cobre:
- Rastreamento de páginas válidas
- Exclusão de admin, static, webhooks
- Exclusão de robôs
- Exclusão de AJAX sem flag
- Modo disabled
- Proteção contra falhas (nunca propaga exceção)
"""
from unittest.mock import patch, MagicMock
from django.test import TestCase, RequestFactory, override_settings
from django.contrib.auth.models import User, AnonymousUser
from django.utils import timezone

from product_analytics.middleware import AnalyticsMiddleware
from product_analytics.models import AnalyticsSession, ProductEvent

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

CHROME_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

GOOGLEBOT_UA = "Googlebot/2.1 (+http://www.google.com/bot.html)"


def make_response(status_code=200):
    """Cria uma response mock com status_code."""
    response = MagicMock()
    response.status_code = status_code
    return response


class AnalyticsMiddlewareTest(TestCase):
    """Testa o AnalyticsMiddleware."""

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="middleware_user",
            password="senha123",
        )

    def _make_middleware(self, mode="synchronous"):
        """Cria instância do middleware com get_response mock."""
        response = make_response()
        get_response = MagicMock(return_value=response)
        with override_settings(
            PRODUCT_ANALYTICS={"PROCESSING_MODE": mode, "SESSION_TIMEOUT_MINUTES": 30}
        ):
            mw = AnalyticsMiddleware(get_response)
            mw._mode = mode
        return mw, get_response

    def _make_request(self, path="/", user=None, ua=CHROME_UA, method="GET"):
        if method == "GET":
            request = self.factory.get(path)
        else:
            request = self.factory.post(path)

        request.META["HTTP_USER_AGENT"] = ua
        request.user = user or AnonymousUser()

        # Simula session do Django
        session = MagicMock()
        session.session_key = "mw_test_key_12345678901234567890123"
        session.__contains__ = MagicMock(return_value=False)
        session.get = MagicMock(return_value=None)
        request.session = session

        return request

    # -------------------------------------------------------------------------
    # Rastreamento básico
    # -------------------------------------------------------------------------

    @override_settings(**ANALYTICS_SYNC_SETTINGS)
    def test_tracks_home_page(self):
        mw, _ = self._make_middleware()
        request = self._make_request("/")
        response = make_response(200)

        with patch.object(mw, "_track_page_view") as mock_track:
            mw._should_track = MagicMock(return_value=True)
            mw(request)

    @override_settings(**ANALYTICS_SYNC_SETTINGS)
    def test_should_track_home_get(self):
        """GET na home deve ser rastreado."""
        mw, _ = self._make_middleware()
        request = self._make_request("/")
        response = make_response(200)
        self.assertTrue(mw._should_track(request, response))

    # -------------------------------------------------------------------------
    # Exclusões
    # -------------------------------------------------------------------------

    @override_settings(**ANALYTICS_SYNC_SETTINGS)
    def test_excludes_static(self):
        mw, _ = self._make_middleware()
        request = self._make_request("/static/css/main.css")
        response = make_response(200)
        self.assertFalse(mw._should_track(request, response))

    @override_settings(**ANALYTICS_SYNC_SETTINGS)
    def test_excludes_media(self):
        mw, _ = self._make_middleware()
        request = self._make_request("/media/book.jpg")
        response = make_response(200)
        self.assertFalse(mw._should_track(request, response))

    @override_settings(**ANALYTICS_SYNC_SETTINGS)
    def test_excludes_admin(self):
        mw, _ = self._make_middleware()
        request = self._make_request("/admin/core/book/")
        response = make_response(200)
        self.assertFalse(mw._should_track(request, response))

    @override_settings(**ANALYTICS_SYNC_SETTINGS)
    def test_excludes_webhooks(self):
        mw, _ = self._make_middleware()
        request = self._make_request("/webhooks/mercadopago/")
        response = make_response(200)
        self.assertFalse(mw._should_track(request, response))

    @override_settings(**ANALYTICS_SYNC_SETTINGS)
    def test_excludes_health_check(self):
        mw, _ = self._make_middleware()
        request = self._make_request("/health/")
        response = make_response(200)
        self.assertFalse(mw._should_track(request, response))

    @override_settings(**ANALYTICS_SYNC_SETTINGS)
    def test_excludes_server_error(self):
        """Página com 500 não deve ser rastreada."""
        mw, _ = self._make_middleware()
        request = self._make_request("/")
        response = make_response(500)
        self.assertFalse(mw._should_track(request, response))

    @override_settings(**ANALYTICS_SYNC_SETTINGS)
    def test_excludes_bot(self):
        """Requisição de robô (Googlebot) não deve ser rastreada."""
        mw, _ = self._make_middleware()
        request = self._make_request("/", ua=GOOGLEBOT_UA)
        response = make_response(200)
        self.assertFalse(mw._should_track(request, response))

    @override_settings(**ANALYTICS_SYNC_SETTINGS)
    def test_excludes_ajax_without_flag(self):
        """AJAX sem header X-Track-Analytics não deve ser rastreado."""
        mw, _ = self._make_middleware()
        request = self._make_request("/livros/")
        request.META["HTTP_X_REQUESTED_WITH"] = "XMLHttpRequest"
        response = make_response(200)
        self.assertFalse(mw._should_track(request, response))

    @override_settings(**ANALYTICS_SYNC_SETTINGS)
    def test_excludes_put_method(self):
        mw, _ = self._make_middleware()
        request = self.factory.put("/livros/42/")
        request.META["HTTP_USER_AGENT"] = CHROME_UA
        request.user = AnonymousUser()
        request.session = MagicMock()
        response = make_response(200)
        self.assertFalse(mw._should_track(request, response))

    # -------------------------------------------------------------------------
    # Modo desabilitado
    # -------------------------------------------------------------------------

    @override_settings(**ANALYTICS_DISABLED_SETTINGS)
    def test_disabled_mode_tracks_nothing(self):
        """Modo disabled: nenhum evento deve ser criado."""
        mw, get_response = self._make_middleware(mode="disabled")
        request = self._make_request("/")

        with patch(
            "product_analytics.middleware.AnalyticsMiddleware._track_page_view"
        ) as mock_track:
            mw(request)
            mock_track.assert_not_called()

    # -------------------------------------------------------------------------
    # Tolerância a falhas
    # -------------------------------------------------------------------------

    @override_settings(**ANALYTICS_SYNC_SETTINGS)
    def test_exception_in_tracking_does_not_break_response(self):
        """Erro no rastreamento nunca deve quebrar a resposta HTTP."""
        mw, _ = self._make_middleware()
        request = self._make_request("/")

        with patch.object(
            mw, "_track_page_view", side_effect=Exception("Tracking explodiu")
        ):
            with patch.object(mw, "_should_track", return_value=True):
                # Não deve levantar exceção
                try:
                    mw(request)
                except Exception:
                    self.fail("Middleware propagou exceção do tracking")
