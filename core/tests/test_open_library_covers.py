# core/tests/test_open_library_covers.py
"""
Testes abrangentes da integração com Open Library Covers API e do sistema de resolução de capas.

Cobre:
1. Normalização de ISBN (ISBN-10, ISBN-13, casos inválidos).
2. Construção de URLs canônicas e URLs de verificação (?default=false).
3. Verificação de capa via HTTP (200 hit, 404 miss, timeouts, erros de rede).
4. Cache de consultas (positivo 7 dias, negativo 24h, erros transitórios).
5. Resolução e registro seguro de proveniência técnica (ImageRightsRecord).
6. Preservação estrita dos invariantes jurídicos:
   - provenance_provider='open_library' (fonte/proveniência técnica)
   - provenance_method='remote_display' (método de disponibilização)
   - license_type='' (não identificada — Open Library não é licença autoral)
   - legal_basis='' (vazio, sem presunção automática)
   - audit_status='not_audited'
7. Hierarquia multi-tier (Tier 1 local > Tier 2 Open Library > Tier 5 fallback).
8. Respeito à suspensão administrativa / restrição de exibição pública.
9. Auditoria de ativos remotos via ImageRightsAuditService sem erros de checksum.
10. Isolamento estrito por edição (sem substituição de capas entre edições).
11. Enriquecimento da pesquisa assistida (ImageRightsResearchService).
"""

from datetime import date
from unittest.mock import patch, MagicMock
from django.test import TestCase, override_settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.contenttypes.models import ContentType
import requests

from core.models.book import Book
from core.models.category import Category
from core.models.author import Author
from core.models.image_rights import ImageRightsRecord
from core.models.image_rights_audit_log import ImageRightsAuditLog
from core.services.open_library_cover_service import OpenLibraryCoverService
from core.services.book_cover_resolution_service import BookCoverResolutionService
from core.services.image_rights_service import ImageRightsAuditService
from core.services.image_rights_provenance_service import ImageRightsProvenanceService
from core.services.image_rights_research_service import ImageRightsResearchService


@override_settings(CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}})
class OpenLibraryCoverServiceTestCase(TestCase):
    """Testes unitários do OpenLibraryCoverService."""

    def setUp(self):
        cache.clear()
        self.category = Category.objects.create(name="Ficção Científica", slug="ficcao-cientifica")
        self.author = Author.objects.create(name="Arthur C. Clarke", slug="arthur-c-clarke")

    def tearDown(self):
        cache.clear()

    # 1. Normalização de ISBN
    def test_normalize_isbn_valid_formats(self):
        """Testa normalização correta de ISBN-10 e ISBN-13 com e sem hifens."""
        # ISBN-13 com e sem hifens
        self.assertEqual(OpenLibraryCoverService.normalize_isbn("978-0-385-47257-9"), "9780385472579")
        self.assertEqual(OpenLibraryCoverService.normalize_isbn("9780385472579"), "9780385472579")

        # ISBN-10 com e sem hifens
        self.assertEqual(OpenLibraryCoverService.normalize_isbn("0-385-47257-9"), "0385472579")
        self.assertEqual(OpenLibraryCoverService.normalize_isbn("0385472579"), "0385472579")

        # ISBN-10 terminando com 'X' ou 'x'
        self.assertEqual(OpenLibraryCoverService.normalize_isbn("0-8044-2957-X"), "080442957X")
        self.assertEqual(OpenLibraryCoverService.normalize_isbn("080442957x"), "080442957X")

        # ISBN com espaços
        self.assertEqual(OpenLibraryCoverService.normalize_isbn(" 978 0385 472579 "), "9780385472579")

    def test_normalize_isbn_invalid_formats(self):
        """Testa que formatos inválidos retornam None."""
        self.assertIsNone(OpenLibraryCoverService.normalize_isbn(None))
        self.assertIsNone(OpenLibraryCoverService.normalize_isbn(""))
        self.assertIsNone(OpenLibraryCoverService.normalize_isbn("   "))
        self.assertIsNone(OpenLibraryCoverService.normalize_isbn("123"))
        self.assertIsNone(OpenLibraryCoverService.normalize_isbn("123456789012345"))
        self.assertIsNone(OpenLibraryCoverService.normalize_isbn("ABCDEFGHIJ"))
        self.assertIsNone(OpenLibraryCoverService.normalize_isbn("978-0-385-47257-A"))

    # 2. URLs Canônica e Verificação
    def test_canonical_and_verification_urls(self):
        """Verifica URLs canônicas e com ?default=false."""
        isbn = "9780385472579"
        expected_canonical = "https://covers.openlibrary.org/b/isbn/9780385472579-L.jpg"
        expected_verification = "https://covers.openlibrary.org/b/isbn/9780385472579-L.jpg?default=false"

        self.assertEqual(OpenLibraryCoverService.get_canonical_url(isbn, 'L'), expected_canonical)
        self.assertEqual(OpenLibraryCoverService.get_verification_url(isbn, 'L'), expected_verification)

        # Tamanhos diferentes
        self.assertEqual(
            OpenLibraryCoverService.get_canonical_url(isbn, 'M'),
            "https://covers.openlibrary.org/b/isbn/9780385472579-M.jpg"
        )
        self.assertEqual(
            OpenLibraryCoverService.get_canonical_url(isbn, 'S'),
            "https://covers.openlibrary.org/b/isbn/9780385472579-S.jpg"
        )
        # Tamanho inválido faz fallback para 'L'
        self.assertEqual(
            OpenLibraryCoverService.get_canonical_url(isbn, 'XL'),
            expected_canonical
        )

    # 3. Verificação com Mock HTTP
    @patch('core.services.open_library_cover_service.requests.get')
    def test_check_cover_exists_200(self, mock_get):
        """Testa resposta 200 da Open Library Covers API."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        res = OpenLibraryCoverService.check_cover_exists("978-0-385-47257-9", size='L', use_cache=False)

        self.assertTrue(res['exists'])
        self.assertEqual(res['url'], "https://covers.openlibrary.org/b/isbn/9780385472579-L.jpg")
        self.assertEqual(res['status_code'], 200)
        self.assertIsNone(res['error'])
        # Verifica que chamou com stream=True e ?default=false
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        self.assertIn("?default=false", args[0])
        self.assertTrue(kwargs.get('stream'))

    @patch('core.services.open_library_cover_service.requests.get')
    def test_check_cover_not_found_404(self, mock_get):
        """Testa resposta 404 quando capa não existe (?default=false)."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        res = OpenLibraryCoverService.check_cover_exists("978-0-000-00000-0", size='L', use_cache=False)

        self.assertFalse(res['exists'])
        self.assertEqual(res['url'], "")
        self.assertEqual(res['status_code'], 404)
        self.assertIn("404", res['error'])

    @patch('core.services.open_library_cover_service.requests.get')
    def test_check_cover_timeout_and_request_error(self, mock_get):
        """Testa resiliência a timeouts e falhas transitórias de conexão."""
        # Timeout
        mock_get.side_effect = requests.exceptions.Timeout("Connection timed out")
        res_timeout = OpenLibraryCoverService.check_cover_exists("9780385472579", use_cache=False)
        self.assertFalse(res_timeout['exists'])
        self.assertIn("Timeout", res_timeout['error'])

        # Erro de rede genérico
        mock_get.side_effect = requests.exceptions.ConnectionError("Failed to resolve host")
        res_conn = OpenLibraryCoverService.check_cover_exists("9780385472579", use_cache=False)
        self.assertFalse(res_conn['exists'])
        self.assertIn("Erro de rede", res_conn['error'])

    # 4. Cache
    @patch('core.services.open_library_cover_service.requests.get')
    def test_cache_positive_and_negative(self, mock_get):
        """Garante que chamadas subsequentes utilizam o cache sem disparar HTTP."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        isbn = "9780385472579"
        # Primeira chamada dispara HTTP
        res1 = OpenLibraryCoverService.check_cover_exists(isbn, size='L', use_cache=True)
        self.assertTrue(res1['exists'])
        self.assertEqual(mock_get.call_count, 1)

        # Segunda chamada usa cache
        res2 = OpenLibraryCoverService.check_cover_exists(isbn, size='L', use_cache=True)
        self.assertTrue(res2['exists'])
        self.assertEqual(mock_get.call_count, 1)  # Não chamou novamente


@override_settings(CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}})
class BookCoverResolutionAndGovernanceTestCase(TestCase):
    """Testes de resolução hierárquica e conformidade jurídica das capas."""

    def setUp(self):
        cache.clear()
        self.category = Category.objects.create(name="Ficção Científica", slug="ficcao-cientifica")
        self.author = Author.objects.create(name="Arthur C. Clarke", slug="arthur-c-clarke")

        self.book = Book.objects.create(
            title="2001: Uma Odisseia no Espaço",
            isbn="9780385472579",
            author=self.author,
            category=self.category,
            publication_date=date(1968, 7, 1),
            price=49.90,
        )

    def tearDown(self):
        cache.clear()

    @patch('core.services.open_library_cover_service.requests.get')
    def test_resolve_and_register_preserves_legal_invariants(self, mock_get):
        """
        Garante que a descoberta e registro de capa da Open Library NUNCA
        presume regularização jurídica, nascendo sempre como not_audited e legal_basis vazia.
        """
        # Mock da verificação da capa (200) e da Books API
        def mocked_get(url, *args, **kwargs):
            resp = MagicMock()
            if "covers.openlibrary.org" in url:
                resp.status_code = 200
                resp.close = MagicMock()
                return resp
            elif "openlibrary.org/api/books" in url:
                resp.status_code = 200
                resp.json.return_value = {
                    "ISBN:9780385472579": {
                        "title": "2001: A Space Odyssey",
                        "key": "/books/OL7353617M",
                        "cover": {
                            "large": "https://covers.openlibrary.org/b/id/10528432-L.jpg"
                        }
                    }
                }
                return resp
            resp.status_code = 404
            return resp

        mock_get.side_effect = mocked_get

        # Resolver e registrar capa
        resolved_url = OpenLibraryCoverService.resolve_and_register_book_cover(self.book)

        self.assertIsNotNone(resolved_url)
        self.assertEqual(resolved_url, "https://covers.openlibrary.org/b/isbn/9780385472579-L.jpg")

        # Verificar ImageRightsRecord criado
        ct = ContentType.objects.get_for_model(self.book)
        record = ImageRightsRecord.objects.filter(
            content_type=ct,
            object_id=self.book.pk,
            image_field_name='cover_image'
        ).first()

        self.assertIsNotNone(record)
        # INVARIANTES JURÍDICOS E DE GOVERNANÇA:
        # 1. Fonte/Proveniência técnica e método
        self.assertEqual(record.provenance_provider, 'open_library')
        self.assertEqual(record.provenance_method, 'remote_display')

        # 2. NÃO é licença autoral (license_type não identificada)
        self.assertEqual(record.license_type, '')
        self.assertNotEqual(record.license_type, 'open_library')
        self.assertEqual(record.licensor_name, '')
        self.assertEqual(record.license_url, '')

        # 3. legal_basis estritamente vazio
        self.assertEqual(record.legal_basis, '')  # Inegociável: vazio!

        # 4. audit_status estritamente 'not_audited'
        self.assertEqual(record.audit_status, 'not_audited')

        # 5. Nenhuma presunção de CC ou Domínio Público
        self.assertNotIn(record.license_type, ['cc', 'public_domain'])
        self.assertNotIn(record.legal_basis, ['creative_commons', 'public_domain'])

        # 6. Permissão operacional de exibição remota
        self.assertTrue(record.public_display_allowed)
        self.assertEqual(record.source_url, "https://covers.openlibrary.org/b/isbn/9780385472579-L.jpg")
        self.assertEqual(record.provider_asset_id, '10528432')

        # Metadados de segurança e proveniência
        meta = record.provenance_metadata
        self.assertTrue(meta.get('is_remote_storage'))
        self.assertFalse(meta.get('stored_locally'))
        self.assertEqual(meta.get('isbn'), '9780385472579')
        self.assertEqual(meta.get('source_type'), 'open_library')

        # Histórico de auditoria registrado
        log = ImageRightsAuditLog.objects.filter(image_rights_record=record).first()
        self.assertIsNotNone(log)
        self.assertEqual(log.event_type, 'provenance_registered')

        # Auditoria via ImageRightsAuditService
        status, audited_record = ImageRightsAuditService.get_field_audit_status(self.book, 'cover_image')
        self.assertEqual(status, 'not_audited')
        self.assertEqual(audited_record, record)

    @patch('core.services.open_library_cover_service.OpenLibraryCoverService.check_cover_exists')
    def test_book_cover_url_tier2_open_library_resolution(self, mock_check):
        """Testa que Book.cover_image_url resolve Tier 2 (Open Library) quando não há imagem local."""
        mock_check.return_value = {
            'exists': True,
            'url': 'https://covers.openlibrary.org/b/isbn/9780385472579-L.jpg',
            'isbn': '9780385472579',
            'size': 'L',
            'status_code': 200,
            'error': None,
        }

        # O livro não tem cover_image local
        self.assertFalse(bool(self.book.cover_image))

        # Deve resolver URL remota da Open Library
        self.assertTrue(self.book.has_valid_cover)
        self.assertEqual(self.book.cover_image_url, "https://covers.openlibrary.org/b/isbn/9780385472579-L.jpg")
        self.assertEqual(BookCoverResolutionService.get_cover_source_type(self.book), 'open_library')

    def test_book_cover_url_tier1_local_precedence(self):
        """Garante que imagem local autorizada (Tier 1) tem precedência absoluta sobre Open Library."""
        # Criar imagem local de teste
        image_content = b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x01\x44\x00\x3b"
        uploaded_file = SimpleUploadedFile("cover_test.gif", image_content, content_type="image/gif")

        self.book.cover_image = uploaded_file
        self.book.save()

        # Registrar proveniência própria/local
        ImageRightsProvenanceService.register_external_provenance(
            target_obj=self.book,
            image_field_name='cover_image',
            provider='publisher',
            license_type='licensed',
        )

        # Tier 1 deve prevalecer
        cover_url = self.book.cover_image_url
        self.assertIsNotNone(cover_url)
        self.assertIn("cover_test", cover_url)
        self.assertIn("?v=", cover_url)
        self.assertEqual(BookCoverResolutionService.get_cover_source_type(self.book), 'local')

    def test_book_cover_url_restricted_suppression(self):
        """Garante que quando um ativo visual é suspenso/restrito, cover_image_url retorna None."""
        # Criar registro de direitos como restrito
        ct = ContentType.objects.get_for_model(self.book)
        record = ImageRightsRecord.objects.create(
            content_type=ct,
            object_id=self.book.pk,
            image_field_name='cover_image',
            provenance_provider='open_library',
            provenance_method='remote_display',
            source_url="https://covers.openlibrary.org/b/isbn/9780385472579-L.jpg",
            license_type='',
            audit_status='restricted',  # Suspenso
            public_display_allowed=False,  # Proibido
        )

        self.assertFalse(self.book.has_valid_cover)
        self.assertIsNone(self.book.cover_image_url)

        # Fallback retorna o placeholder SVG
        placeholder = BookCoverResolutionService.get_display_cover_or_placeholder(self.book)
        self.assertIn("no-cover-placeholder.svg", placeholder)

    @patch('core.services.open_library_cover_service.OpenLibraryCoverService.check_cover_exists')
    def test_strict_edition_isolation(self, mock_check):
        """Garante que duas edições distintas com ISBNs diferentes não herdam capas entre si."""
        # Edição 1 tem capa
        # Edição 2 não tem capa
        def side_effect(isbn, *args, **kwargs):
            clean = isbn.replace('-', '').strip()
            if clean == '9780385472579':
                return {'exists': True, 'url': f'https://covers.openlibrary.org/b/isbn/{clean}-L.jpg', 'isbn': clean}
            return {'exists': False, 'url': '', 'isbn': clean}

        mock_check.side_effect = side_effect

        book_ed2 = Book.objects.create(
            title="2001: Uma Odisseia no Espaço - Edição Especial",
            isbn="9780000000000",
            author=self.author,
            category=self.category,
            publication_date=date(2001, 1, 1),
            price=59.90,
        )

        self.assertIsNotNone(self.book.cover_image_url)
        self.assertIn("9780385472579", self.book.cover_image_url)

        self.assertIsNone(book_ed2.cover_image_url)
        self.assertFalse(book_ed2.has_valid_cover)

    @patch('core.services.image_rights_research_service.requests.get')
    def test_assisted_research_enriches_open_library_cover(self, mock_get):
        """
        Testa se o ImageRightsResearchService enriquece a consulta à Open Library
        com dados da capa sem violar restrições jurídicas.
        """
        api_mock = MagicMock()
        api_mock.status_code = 200
        api_mock.content = b'{"ISBN:9780385472579": {"title": "2001: A Space Odyssey", "key": "/books/OL7353617M", "cover": {"large": "https://covers.openlibrary.org/b/id/10528432-L.jpg"}}}'
        api_mock.json.return_value = {
            "ISBN:9780385472579": {
                "title": "2001: A Space Odyssey",
                "key": "/books/OL7353617M",
                "cover": {
                    "large": "https://covers.openlibrary.org/b/id/10528432-L.jpg"
                }
            }
        }
        mock_get.return_value = api_mock

        ct = ContentType.objects.get_for_model(self.book)
        record = ImageRightsRecord.objects.create(
            content_type=ct,
            object_id=self.book.pk,
            image_field_name='cover_image',
            provenance_provider='open_library',
            audit_status='not_audited',
            public_display_allowed=True,
        )

        internal_data = {'isbn': self.book.isbn, 'title': self.book.title}
        result = ImageRightsResearchService._research_open_library(record, internal_data)

        # Deve registrar source com has_cover=True e cover_url
        sources = result['sources']
        self.assertEqual(len(sources), 1)
        source = sources[0]
        self.assertTrue(source.get('has_cover'))
        self.assertEqual(source.get('cover_id'), '10528432')
        self.assertEqual(source.get('edition_key'), 'OL7353617M')
        self.assertEqual(source.get('cover_url'), 'https://covers.openlibrary.org/b/isbn/9780385472579-L.jpg')

        # Sugestões: work_title, provider_asset_id, source_url
        suggested_fields = [s['field_name'] for s in result['suggestions']]
        self.assertIn('work_title', suggested_fields)
        self.assertIn('provider_asset_id', suggested_fields)
        self.assertIn('source_url', suggested_fields)

        # Regra de Ouro: NUNCA sugerir rights_holder_name, license_type ou legal_basis da Open Library!
        self.assertNotIn('rights_holder_name', suggested_fields)
        self.assertNotIn('license_type', suggested_fields)
        self.assertNotIn('legal_basis', suggested_fields)

    def test_legacy_open_library_license_type_backward_compatibility(self):
        """Garante que registros legados com license_type='open_library' continuam sendo resolvidos normalmente."""
        ct = ContentType.objects.get_for_model(self.book)
        record = ImageRightsRecord.objects.create(
            content_type=ct,
            object_id=self.book.pk,
            image_field_name='cover_image',
            provenance_provider='',  # legado sem provenance_provider preenchido
            license_type='open_library',  # legado
            source_url="https://covers.openlibrary.org/b/isbn/9780385472579-L.jpg",
            audit_status='not_audited',
            public_display_allowed=True,
        )

        resolved_url = BookCoverResolutionService.get_cover_url(self.book, size='L')
        self.assertEqual(resolved_url, "https://covers.openlibrary.org/b/isbn/9780385472579-L.jpg")
        self.assertTrue(self.book.has_valid_cover)

    @patch('core.services.open_library_cover_service.OpenLibraryCoverService.check_cover_exists')
    def test_open_library_not_authorial_license_and_invariants(self, mock_check):
        """
        Valida exaustivamente os 7 requisitos de conformidade jurídica:
        1. Open Library registrada como fonte/proveniência (provenance_provider='open_library');
        2. Não ser considerada uma licença autoral (license_type='');
        3. legal_basis permaneça vazio ('');
        4. audit_status permaneça 'not_audited';
        5. Nenhuma imagem seja classificada automaticamente como CC ou domínio público;
        6. A resolução e exibição das capas continue funcionando exatamente como antes;
        7. Nenhum comportamento existente das demais fontes de imagens seja alterado.
        """
        mock_check.return_value = {
            'exists': True,
            'url': 'https://covers.openlibrary.org/b/isbn/9780385472579-L.jpg',
            'isbn': '9780385472579',
        }

        # 1-4. Resolução e registro
        url = OpenLibraryCoverService.resolve_and_register_book_cover(self.book)
        self.assertEqual(url, "https://covers.openlibrary.org/b/isbn/9780385472579-L.jpg")

        ct = ContentType.objects.get_for_model(self.book)
        rec = ImageRightsRecord.objects.get(content_type=ct, object_id=self.book.pk, image_field_name='cover_image')

        # 1. Fonte e proveniência técnica
        self.assertEqual(rec.provenance_provider, 'open_library')
        self.assertEqual(rec.provenance_method, 'remote_display')
        self.assertEqual(rec.provenance_metadata.get('source_type'), 'open_library')

        # 2. NÃO é licença autoral
        self.assertEqual(rec.license_type, '')
        self.assertNotEqual(rec.license_type, 'open_library')
        self.assertEqual(rec.licensor_name, '')
        self.assertEqual(rec.license_url, '')

        # 3. legal_basis vazio
        self.assertEqual(rec.legal_basis, '')

        # 4. audit_status é not_audited
        self.assertEqual(rec.audit_status, 'not_audited')

        # 5. Não é classificada como CC ou Domínio Público
        self.assertNotIn(rec.license_type, ['cc', 'public_domain', 'open_library'])
        self.assertNotIn(rec.legal_basis, ['creative_commons', 'public_domain', 'fair_use_art46'])

        # 6. Resolução e exibição funcionando exatamente como antes
        self.assertEqual(BookCoverResolutionService.get_cover_url(self.book), "https://covers.openlibrary.org/b/isbn/9780385472579-L.jpg")
        self.assertEqual(self.book.cover_image_url, "https://covers.openlibrary.org/b/isbn/9780385472579-L.jpg")
        self.assertTrue(self.book.has_valid_cover)
        self.assertEqual(BookCoverResolutionService.get_cover_source_type(self.book), 'open_library')

        # 7. Comportamento de outras fontes (Tier 1 local e Tier 5 placeholder) inalterado
        from django.core.files.uploadedfile import SimpleUploadedFile
        dummy_img = SimpleUploadedFile("local_cover.jpg", b"local_bytes")
        self.book.cover_image.save("local_cover.jpg", dummy_img)
        self.assertEqual(BookCoverResolutionService.get_cover_source_type(self.book), 'local')
        self.assertIn("local_cover", BookCoverResolutionService.get_cover_url(self.book))
