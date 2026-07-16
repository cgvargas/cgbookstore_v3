"""Testes unitários da política comercial que não dependem do banco de dados."""

from types import SimpleNamespace
from io import StringIO
from urllib.parse import parse_qs, urlsplit
from unittest.mock import MagicMock, patch

from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import SimpleTestCase, override_settings

from partners.services.affiliate_service import AffiliateService
from partners.services.url_validation_service import URLValidationService


PARTNER_CONFIG = {
    'amazon': {
        'allowed_domains': ['amazon.com.br', 'www.amazon.com.br'],
        'tracking_query_param': 'tag',
    },
    'livraria': {
        'allowed_domains': ['livraria.example'],
        'tracking_query_param': 'affiliate-code',
    },
}


def make_partner(**overrides):
    values = {
        'id': 1,
        'nome': 'Amazon',
        'slug': 'amazon',
        'tracking_id': 'tracking-de-teste',
        'url_base': 'https://www.amazon.com.br',
        'ativo': True,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


@override_settings(
    PARTNER_COMMERCIAL_CONFIG=PARTNER_CONFIG,
    PARTNER_SHORTENER_DOMAINS={'amzn.to', 'bit.ly'},
)
class URLValidationServiceTest(SimpleTestCase):
    def setUp(self):
        self.partner = make_partner()

    def assert_has_issue(self, result, code):
        self.assertTrue(result.has_issue(code), result.issues)

    def test_accepts_https_url_on_exact_allowlist(self):
        result = URLValidationService.validate(
            'https://www.amazon.com.br/dp/123?ref_=catalogo',
            partner=self.partner,
        )
        self.assertTrue(result.is_valid, result.issues)
        self.assertEqual(result.hostname, 'www.amazon.com.br')

    def test_requires_https(self):
        result = URLValidationService.validate('http://www.amazon.com.br/dp/123', self.partner)
        self.assert_has_issue(result, 'https_required')

    def test_rejects_lookalike_and_subdomain_hosts(self):
        for url in (
            'https://amazon.com.br.example.org/dp/123',
            'https://amazon.com.br.evil.test/dp/123',
            'https://www-amazon.com.br/dp/123',
            'https://offers.amazon.com.br/dp/123',
        ):
            with self.subTest(url=url):
                self.assert_has_issue(
                    URLValidationService.validate(url, self.partner),
                    'domain_not_allowed',
                )

    def test_rejects_embedded_credentials(self):
        result = URLValidationService.validate(
            'https://user:secret@www.amazon.com.br/dp/123',
            self.partner,
        )
        self.assert_has_issue(result, 'embedded_credentials')

    def test_rejects_ip_hosts(self):
        for url in ('https://127.0.0.1/path', 'https://[::1]/path'):
            with self.subTest(url=url):
                self.assert_has_issue(
                    URLValidationService.validate(url, self.partner),
                    'ip_host_not_allowed',
                )

    def test_rejects_nonstandard_and_invalid_ports(self):
        self.assert_has_issue(
            URLValidationService.validate('https://www.amazon.com.br:8443/dp/123', self.partner),
            'port_not_allowed',
        )
        self.assert_has_issue(
            URLValidationService.validate('https://www.amazon.com.br:notaport/dp/123', self.partner),
            'invalid_port',
        )

    def test_rejects_control_characters_before_trimming(self):
        result = URLValidationService.validate(
            '\nhttps://www.amazon.com.br/dp/123\r',
            self.partner,
        )
        self.assert_has_issue(result, 'control_characters')

    def test_rejects_percent_encoded_control_characters(self):
        result = URLValidationService.validate(
            'https://www.amazon.com.br/dp/123%0d%0aLocation:evil',
            self.partner,
        )
        self.assert_has_issue(result, 'encoded_control_characters')

    def test_rejects_shortened_links(self):
        result = URLValidationService.validate('https://amzn.to/example', self.partner)
        self.assert_has_issue(result, 'shortened_url')

    def test_normalizes_scheme_host_case_and_trailing_dot(self):
        result = URLValidationService.validate('HTTPS://WWW.AMAZON.COM.BR./dp/123', self.partner)
        self.assertTrue(result.is_valid, result.issues)
        self.assertEqual(result.normalized_url, 'https://www.amazon.com.br/dp/123')

    def test_validate_or_raise_exposes_all_issue_codes(self):
        with self.assertRaises(ValidationError) as context:
            URLValidationService.validate_or_raise('http://127.0.0.1:8080/path', self.partner)
        codes = {error.code for error in context.exception.error_dict['url']}
        self.assertTrue({'https_required', 'ip_host_not_allowed', 'port_not_allowed'} <= codes)


@override_settings(PARTNER_COMMERCIAL_CONFIG=PARTNER_CONFIG)
class AffiliateServiceSecurityTest(SimpleTestCase):
    def test_generation_preserves_existing_params_and_fragment(self):
        partner = make_partner()
        original = 'https://www.amazon.com.br/dp/123?ref_=catalogo&language=pt_BR#details'

        generated = AffiliateService.generate_link(partner, None, original)
        parsed = urlsplit(generated)
        params = parse_qs(parsed.query, keep_blank_values=True)

        self.assertEqual(params['ref_'], ['catalogo'])
        self.assertEqual(params['language'], ['pt_BR'])
        self.assertEqual(params['tag'], ['tracking-de-teste'])
        self.assertEqual(parsed.fragment, 'details')

    def test_generation_replaces_existing_tracking_value(self):
        partner = make_partner()
        generated = AffiliateService.generate_link(
            partner,
            None,
            'https://www.amazon.com.br/dp/123?tag=valor-antigo&ref_=catalogo',
        )
        params = parse_qs(urlsplit(generated).query)
        self.assertEqual(params['tag'], ['tracking-de-teste'])
        self.assertEqual(params['ref_'], ['catalogo'])

    def test_generation_uses_partner_config_without_partner_hardcode(self):
        partner = make_partner(
            nome='Livraria Exemplo',
            slug='livraria',
            tracking_id='codigo-de-teste',
            url_base='https://livraria.example',
        )
        generated = AffiliateService.generate_link(
            partner,
            None,
            'https://livraria.example/livro?campaign=inverno',
        )
        params = parse_qs(urlsplit(generated).query)
        self.assertEqual(params['affiliate-code'], ['codigo-de-teste'])
        self.assertEqual(params['campaign'], ['inverno'])

    def test_generation_without_tracking_preserves_original_url(self):
        partner = make_partner(tracking_id='')
        original = 'https://www.amazon.com.br/dp/123?ref_=catalogo'
        self.assertEqual(AffiliateService.generate_link(partner, None, original), original)

    def test_requested_partner_must_match_legacy_book_partner(self):
        book = SimpleNamespace(
            purchase_partner_name='Amazon',
            purchase_partner_url='https://www.amazon.com.br/dp/123',
        )
        manipulated_partner = make_partner(
            nome='Livraria Exemplo',
            slug='livraria',
            url_base='https://livraria.example',
        )
        resolution = AffiliateService.inspect_link_for_book(book, manipulated_partner)
        self.assertIsNone(resolution.partner)
        self.assertEqual(resolution.generated_url, '')
        self.assertFalse(resolution.partner_matches_book)
        self.assertFalse(resolution.is_ready)

    def test_inactive_partner_is_not_ready(self):
        book = SimpleNamespace(
            purchase_partner_name='Amazon',
            purchase_partner_url='https://www.amazon.com.br/dp/123',
        )
        resolution = AffiliateService.inspect_link_for_book(book, make_partner(ativo=False))
        self.assertEqual(resolution.generated_url, '')
        self.assertFalse(resolution.is_ready)


class AuditPartnerLinksCommandTest(SimpleTestCase):
    def _manager_mocks(self, books):
        partner_manager = MagicMock()
        partner_manager.all.return_value.order_by.return_value = []

        book_queryset = MagicMock()
        book_queryset.order_by.return_value = book_queryset
        book_queryset.iterator.return_value = iter(books)
        book_manager = MagicMock()
        book_manager.only.return_value = book_queryset
        return partner_manager, book_manager

    def test_read_only_command_reports_clean_state(self):
        partner_manager, book_manager = self._manager_mocks([])
        stdout = StringIO()
        with (
            patch('partners.management.commands.audit_partner_links.AffiliatePartner.objects', partner_manager),
            patch('partners.management.commands.audit_partner_links.Book.objects', book_manager),
        ):
            call_command('audit_partner_links', stdout=stdout)

        output = stdout.getvalue()
        self.assertIn('SOMENTE LEITURA', output)
        self.assertIn('Total de ocorrências: 0', output)

    def test_fail_on_findings_raises_command_error(self):
        book = SimpleNamespace(
            id=99,
            title='Livro inconsistente',
            purchase_partner_name='Parceiro ausente',
            purchase_partner_url='',
        )
        partner_manager, book_manager = self._manager_mocks([book])
        with (
            patch('partners.management.commands.audit_partner_links.AffiliatePartner.objects', partner_manager),
            patch('partners.management.commands.audit_partner_links.Book.objects', book_manager),
            self.assertRaises(CommandError),
        ):
            call_command('audit_partner_links', fail_on_findings=True, stdout=StringIO())
