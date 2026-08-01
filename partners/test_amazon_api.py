"""
Testes unitários e de integração para a API da Amazon Brasil e Agregador de Metadados.
"""

from django.test import TestCase, override_settings
from core.models import Book, Author, Category
from partners.services.amazon_api_service import AmazonAPIService, AmazonProductData
from partners.services.amazon_service import AmazonURLNormalizer
from core.services.book_metadata_aggregator import BookMetadataAggregator
import datetime


class AmazonAPIServiceTest(TestCase):
    """Testes para o cliente desacoplado da API da Amazon Brasil."""

    def test_status_reporting(self):
        """Verifica o relatório de status da integração."""
        status = AmazonAPIService.get_status()
        self.assertIn('mode_display', status)
        self.assertEqual(status['associate_tag'], 'cgbookstore-20')

    @override_settings(AMAZON_API_MOCK_MODE=True, AMAZON_API_ENABLED=False)
    def test_mock_search_by_isbn(self):
        """Garante que a busca por ISBN em modo Mock retorna dados com o esquema correto."""
        isbn = "9788573266412"
        data = AmazonAPIService.search_by_isbn(isbn)
        
        self.assertIsNotNone(data)
        self.assertIsInstance(data, AmazonProductData)
        self.assertEqual(data.source, "amazon_mock")
        self.assertIn("cgbookstore-20", data.affiliate_url)
        self.assertTrue(data.detail_url.startswith("https://www.amazon.com.br/dp/"))

    @override_settings(AMAZON_API_MOCK_MODE=True)
    def test_mock_search_by_asin(self):
        """Garante que a busca por ASIN retorna a URL normalizada."""
        asin = "8573266416"
        data = AmazonAPIService.search_by_asin(asin)
        
        self.assertIsNotNone(data)
        self.assertEqual(data.asin, "8573266416")
        self.assertEqual(data.affiliate_url, "https://www.amazon.com.br/dp/8573266416?tag=cgbookstore-20")

    def test_url_normalization_with_tag(self):
        """Garante que links da Amazon recebem a tag cgbookstore-20."""
        raw_url = "https://www.amazon.com.br/Crime-Castigo-Fiodor-Dostoievski/dp/8573266416"
        normalized = AmazonURLNormalizer.normalize(raw_url, associate_tag="cgbookstore-20")
        self.assertEqual(normalized, "https://www.amazon.com.br/dp/8573266416?tag=cgbookstore-20")


class BookMetadataAggregatorTest(TestCase):
    """Testes para o agregador unificado de metadados."""

    def setUp(self):
        self.author = Author.objects.create(name="Fiodor Dostoievski")
        self.category = Category.objects.create(name="Clássicos")
        self.book = Book.objects.create(
            title="Crime e Castigo",
            author=self.author,
            category=self.category,
            publication_date=datetime.date(1866, 1, 1),
            isbn="9788573266412"
        )

    @override_settings(AMAZON_API_MOCK_MODE=True)
    def test_enrich_book_with_amazon_mock(self):
        """Verifica o enriquecimento de um livro com dados simulados da Amazon."""
        res = BookMetadataAggregator.fetch_and_enrich_book(self.book)
        
        self.assertTrue(res['success'])
        self.assertTrue(res['has_amazon'])
        
        self.book.refresh_from_db()
        self.assertEqual(self.book.purchase_partner_name, "Amazon")
        self.assertIn("cgbookstore-20", self.book.purchase_partner_url)
        self.assertIsNotNone(self.book.price)
        self.assertTrue(self.book.available_kindle)
