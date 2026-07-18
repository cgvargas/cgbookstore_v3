"""
Testes unitários para utilitários do módulo Product Analytics.

Cobre:
- normalize_page_name
- extract_object_info
- hash_search_query
- detect_device_type / detect_browser_family / detect_os_family
- extract_referer_domain
- is_bot_request
- extract_utm_params
"""
from django.test import TestCase, RequestFactory
from django.contrib.sessions.backends.db import SessionStore

from product_analytics.utils import (
    normalize_page_name,
    extract_object_info,
    hash_search_query,
    detect_device_type,
    detect_browser_family,
    detect_os_family,
    extract_referer_domain,
    is_bot_request,
    extract_utm_params,
    get_session_key,
)


class NormalizePageNameTest(TestCase):
    """Testa a normalização de paths de URL para page_names canônicos."""

    def test_home(self):
        self.assertEqual(normalize_page_name("/"), "home")

    def test_book_detail(self):
        self.assertEqual(normalize_page_name("/livros/tolkien-123/"), "book_detail")
        self.assertEqual(normalize_page_name("/livros/"), "book_detail")

    def test_library(self):
        self.assertEqual(normalize_page_name("/biblioteca/"), "library")
        self.assertEqual(normalize_page_name("/biblioteca"), "library")

    def test_search(self):
        self.assertEqual(normalize_page_name("/busca/"), "search")
        self.assertEqual(normalize_page_name("/busca/?q=tolkien"), "search")

    def test_premium_page(self):
        self.assertEqual(normalize_page_name("/premium/"), "premium_page")

    def test_chatbot(self):
        self.assertEqual(normalize_page_name("/chatbot/"), "chatbot")
        self.assertEqual(normalize_page_name("/assistente/"), "chatbot")

    def test_registration(self):
        self.assertEqual(normalize_page_name("/accounts/signup/"), "registration")

    def test_login(self):
        self.assertEqual(normalize_page_name("/accounts/login/"), "login")

    def test_unknown_returns_other(self):
        self.assertEqual(normalize_page_name("/rota-inexistente/xyz/"), "other")

    def test_strips_query_string(self):
        """Query string não deve afetar a normalização."""
        self.assertEqual(
            normalize_page_name("/livros/abc/?page=2&sort=asc"),
            "book_detail",
        )

    def test_without_trailing_slash(self):
        """Paths sem trailing slash também devem ser reconhecidos."""
        self.assertEqual(normalize_page_name("/chatbot"), "chatbot")


class ExtractObjectInfoTest(TestCase):
    """Testa a extração de tipo e ID de objeto a partir do path."""

    def test_book_with_id_at_end(self):
        obj_type, obj_id = extract_object_info("/livros/o-senhor-dos-aneis-123/")
        self.assertEqual(obj_type, "book")
        self.assertEqual(obj_id, 123)

    def test_book_with_id_only(self):
        obj_type, obj_id = extract_object_info("/livros/42/")
        self.assertEqual(obj_type, "book")
        self.assertEqual(obj_id, 42)

    def test_article(self):
        obj_type, obj_id = extract_object_info("/noticias/tolkien-retorna-999/")
        self.assertEqual(obj_type, "article")
        self.assertEqual(obj_id, 999)

    def test_home_returns_none(self):
        obj_type, obj_id = extract_object_info("/")
        self.assertIsNone(obj_type)
        self.assertIsNone(obj_id)

    def test_ereader(self):
        obj_type, obj_id = extract_object_info("/ereader/77/")
        self.assertEqual(obj_type, "book")
        self.assertEqual(obj_id, 77)


class HashSearchQueryTest(TestCase):
    """Testa o hashing de termos de busca para LGPD."""

    def test_returns_16_hex_chars(self):
        result = hash_search_query("tolkien")
        self.assertEqual(len(result), 16)
        # Deve ser hexadecimal válido
        int(result, 16)

    def test_same_query_same_hash(self):
        self.assertEqual(hash_search_query("tolkien"), hash_search_query("tolkien"))

    def test_case_insensitive(self):
        self.assertEqual(hash_search_query("Tolkien"), hash_search_query("tolkien"))

    def test_different_queries_different_hashes(self):
        self.assertNotEqual(hash_search_query("tolkien"), hash_search_query("shakespeare"))

    def test_empty_returns_empty(self):
        self.assertEqual(hash_search_query(""), "")

    def test_whitespace_normalized(self):
        self.assertEqual(hash_search_query("  tolkien  "), hash_search_query("tolkien"))


class DetectDeviceTypeTest(TestCase):
    """Testa a detecção de tipo de dispositivo."""

    CHROME_DESKTOP = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    IPHONE = (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
    )
    IPAD = (
        "Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
    )
    ANDROID_PHONE = (
        "Mozilla/5.0 (Linux; Android 14; Pixel 8) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.43 Mobile Safari/537.36"
    )

    def test_desktop(self):
        self.assertEqual(detect_device_type(self.CHROME_DESKTOP), "desktop")

    def test_iphone(self):
        self.assertEqual(detect_device_type(self.IPHONE), "mobile")

    def test_ipad_is_tablet(self):
        self.assertEqual(detect_device_type(self.IPAD), "tablet")

    def test_android_phone(self):
        self.assertEqual(detect_device_type(self.ANDROID_PHONE), "mobile")

    def test_empty_ua_returns_unknown(self):
        self.assertEqual(detect_device_type(""), "unknown")


class DetectBrowserFamilyTest(TestCase):
    """Testa a detecção da família do navegador."""

    def test_chrome(self):
        ua = "Mozilla/5.0 ... Chrome/120.0.0.0 Safari/537.36"
        self.assertEqual(detect_browser_family(ua), "Chrome")

    def test_firefox(self):
        ua = "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0"
        self.assertEqual(detect_browser_family(ua), "Firefox")

    def test_edge(self):
        ua = "Mozilla/5.0 ... Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
        self.assertEqual(detect_browser_family(ua), "Edge")

    def test_empty_ua_returns_unknown(self):
        self.assertEqual(detect_browser_family(""), "Unknown")


class DetectOSFamilyTest(TestCase):
    """Testa a detecção do sistema operacional."""

    def test_windows(self):
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ..."
        self.assertEqual(detect_os_family(ua), "Windows")

    def test_android(self):
        ua = "Mozilla/5.0 (Linux; Android 14; ...)"
        self.assertEqual(detect_os_family(ua), "Android")

    def test_ios(self):
        ua = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 ...)"
        self.assertEqual(detect_os_family(ua), "iOS")

    def test_macos(self):
        ua = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) ..."
        self.assertEqual(detect_os_family(ua), "macOS")


class ExtractRefererDomainTest(TestCase):
    """Testa a extração do domínio do referer."""

    def test_google(self):
        self.assertEqual(
            extract_referer_domain("https://www.google.com/search?q=tolkien"),
            "google.com",
        )

    def test_removes_www(self):
        self.assertEqual(
            extract_referer_domain("https://www.example.com/path/to/page"),
            "example.com",
        )

    def test_empty_referer(self):
        self.assertEqual(extract_referer_domain(""), "")

    def test_internal_referer(self):
        self.assertEqual(
            extract_referer_domain("https://cgbookstore.com.br/livros/123/"),
            "cgbookstore.com.br",
        )

    def test_removes_port(self):
        self.assertEqual(
            extract_referer_domain("http://localhost:8000/path/"),
            "localhost",
        )

    def test_no_path_stored(self):
        """Path não deve aparecer no resultado (LGPD: pode conter PII em queries)."""
        result = extract_referer_domain(
            "https://mail.google.com/mail/u/0/?search=tolkien&email=user@test.com"
        )
        self.assertEqual(result, "mail.google.com")
        self.assertNotIn("tolkien", result)
        self.assertNotIn("user", result)


class IsBotRequestTest(TestCase):
    """Testa a detecção de robôs."""

    def test_googlebot(self):
        self.assertTrue(is_bot_request("Googlebot/2.1"))

    def test_bingbot(self):
        self.assertTrue(is_bot_request("bingbot/2.0"))

    def test_normal_user(self):
        ua = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
        )
        self.assertFalse(is_bot_request(ua))

    def test_empty_is_not_bot(self):
        self.assertFalse(is_bot_request(""))

    def test_python_requests(self):
        self.assertTrue(is_bot_request("python-requests/2.31.0"))

    def test_curl(self):
        self.assertTrue(is_bot_request("curl/7.88.0"))


class ExtractUTMParamsTest(TestCase):
    """Testa a extração de parâmetros UTM."""

    def setUp(self):
        self.factory = RequestFactory()

    def _make_request(self, url="/", session_data=None):
        request = self.factory.get(url)
        # Cria sessão fake para o teste
        request.session = {}
        if session_data:
            request.session.update(session_data)
        return request

    def test_extracts_utm_from_url(self):
        request = self._make_request(
            "/?utm_source=google&utm_medium=cpc&utm_campaign=livros"
        )
        utms = extract_utm_params(request)
        self.assertEqual(utms["source"], "google")
        self.assertEqual(utms["medium"], "cpc")
        self.assertEqual(utms["campaign"], "livros")

    def test_empty_without_utm(self):
        request = self._make_request("/")
        utms = extract_utm_params(request)
        self.assertEqual(utms["source"], "")
        self.assertEqual(utms["medium"], "")
        self.assertEqual(utms["campaign"], "")

    def test_truncates_long_values(self):
        long_value = "a" * 200
        request = self._make_request(f"/?utm_source={long_value}")
        utms = extract_utm_params(request)
        self.assertLessEqual(len(utms["source"]), 100)
