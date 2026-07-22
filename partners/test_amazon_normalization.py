"""
Testes automatizados para a normalização de links da Amazon Brasil e do Management Command normalize_amazon_links.
"""

from io import StringIO
from django.test import TestCase, override_settings
from django.core.management import call_command
from django.core.exceptions import ValidationError
from django.utils import timezone

from core.models import Book, Author, Category
from partners.models import AffiliatePartner
from partners.services.amazon_service import AmazonURLNormalizer
from partners.services.affiliate_service import AffiliateService
from core.admin.book_admin import BookAdminForm


@override_settings(AMAZON_ASSOCIATE_TAG='cgbookstore-20')
class AmazonURLNormalizerTestCase(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Fantasia", slug="fantasia")
        self.author = Author.objects.create(name="J.R.R. Tolkien", slug="j-r-r-tolkien")
        self.book = Book.objects.create(
            title="Roverando",
            author=self.author,
            category=self.category,
            publication_date=timezone.now().date(),
            purchase_partner_name="Amazon",
            purchase_partner_url="https://www.amazon.com.br/Roverando-J-R-R-Tolkien/dp/6555110937/ref=tmm_hrd_swatch_0?_encoding=UTF8&qid=1784745534&sr=8-1"
        )

    def test_normalize_long_amazon_url(self):
        url = "https://www.amazon.com.br/Roverando-J-R-R-Tolkien/dp/6555110937/ref=tmm_hrd_swatch_0?_encoding=UTF8&qid=1784745534&sr=8-1"
        expected = "https://www.amazon.com.br/dp/6555110937?tag=cgbookstore-20"
        self.assertEqual(AmazonURLNormalizer.normalize(url), expected)

    def test_normalize_short_dp_url(self):
        url = "https://www.amazon.com.br/dp/6555110937"
        expected = "https://www.amazon.com.br/dp/6555110937?tag=cgbookstore-20"
        self.assertEqual(AmazonURLNormalizer.normalize(url), expected)

    def test_normalize_gp_product_url(self):
        url = "https://www.amazon.com.br/gp/product/6555110937"
        expected = "https://www.amazon.com.br/dp/6555110937?tag=cgbookstore-20"
        self.assertEqual(AmazonURLNormalizer.normalize(url), expected)

    def test_normalize_url_with_correct_tag(self):
        url = "https://www.amazon.com.br/dp/6555110937?tag=cgbookstore-20"
        expected = "https://www.amazon.com.br/dp/6555110937?tag=cgbookstore-20"
        self.assertEqual(AmazonURLNormalizer.normalize(url), expected)

    def test_normalize_url_with_other_affiliate_tag(self):
        url = "https://www.amazon.com.br/dp/6555110937?tag=outratag-20&ref_=dp"
        expected = "https://www.amazon.com.br/dp/6555110937?tag=cgbookstore-20"
        self.assertEqual(AmazonURLNormalizer.normalize(url), expected)

    def test_normalize_url_without_query_params(self):
        url = "https://amazon.com.br/dp/6555110937"
        expected = "https://www.amazon.com.br/dp/6555110937?tag=cgbookstore-20"
        self.assertEqual(AmazonURLNormalizer.normalize(url), expected)

    def test_invalid_malformed_url(self):
        with self.assertRaises(ValueError):
            AmazonURLNormalizer.normalize("http://not-a-valid-url-format")

    def test_url_without_asin(self):
        with self.assertRaises(ValueError):
            AmazonURLNormalizer.normalize("https://www.amazon.com.br/b?node=123456")

    def test_url_of_other_domain(self):
        with self.assertRaises(ValueError):
            AmazonURLNormalizer.normalize("https://www.amazon.com/dp/6555110937")
        with self.assertRaises(ValueError):
            AmazonURLNormalizer.normalize("https://www.google.com/dp/6555110937")

    def test_non_amazon_partner_link_unaffected(self):
        url_estante = "https://www.estantevirtual.com.br/livro/o-hobbit"
        self.assertFalse(AmazonURLNormalizer.is_amazon_url(url_estante))

    def test_idempotency(self):
        url = "https://www.amazon.com.br/Roverando-J-R-R-Tolkien/dp/6555110937/ref=sr_1_1"
        res1 = AmazonURLNormalizer.normalize(url)
        res2 = AmazonURLNormalizer.normalize(res1)
        res3 = AmazonURLNormalizer.normalize(res2)
        res4 = AmazonURLNormalizer.normalize(res3)
        res5 = AmazonURLNormalizer.normalize(res4)
        self.assertEqual(res1, res5)
        self.assertEqual(res1, "https://www.amazon.com.br/dp/6555110937?tag=cgbookstore-20")

    def test_admin_form_validation_and_normalization(self):
        form_data = {
            'title': 'Livro Teste Admin',
            'publication_date': '2026-01-01',
            'category': self.category.pk,
            'language': 'pt',
            'purchase_partner_name': 'Amazon',
            'purchase_partner_url': 'https://www.amazon.com.br/Livro-Teste/dp/8573266416/ref=ast_author_dp'
        }
        form = BookAdminForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(
            form.cleaned_data['purchase_partner_url'],
            'https://www.amazon.com.br/dp/8573266416?tag=cgbookstore-20'
        )

    def test_admin_form_invalid_amazon_url_raises_error(self):
        form_data = {
            'title': 'Livro Teste Admin',
            'publication_date': '2026-01-01',
            'category': self.category.pk,
            'language': 'pt',
            'purchase_partner_name': 'Amazon',
            'purchase_partner_url': 'https://www.amazon.com.br/b?node=99999'
        }
        form = BookAdminForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('purchase_partner_url', form.errors)

    def test_book_detail_template_renders_new_tab_and_sponsored_rel(self):
        response = self.client.get(self.book.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'target="_blank"')
        self.assertContains(response, 'rel="noopener noreferrer sponsored"')



class NormalizeAmazonLinksCommandTestCase(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Fantasia", slug="fantasia")
        self.author = Author.objects.create(name="Author Test", slug="author-test")

        # 1. Livro Amazon com URL longa para atualizar
        self.book1 = Book.objects.create(
            title="Livro Amazon Longo",
            author=self.author,
            category=self.category,
            publication_date=timezone.now().date(),
            purchase_partner_name="Amazon",
            purchase_partner_url="https://www.amazon.com.br/Livro-Longo/dp/6555604344/ref=sr_1_1?dib=123"
        )

        # 2. Livro Amazon já normalizado
        self.book2 = Book.objects.create(
            title="Livro Amazon Já Normalizado",
            author=self.author,
            category=self.category,
            publication_date=timezone.now().date(),
            purchase_partner_name="Amazon",
            purchase_partner_url="https://www.amazon.com.br/dp/8578279581?tag=cgbookstore-20"
        )

        # 3. Livro de outro parceiro (Estante Virtual)
        self.book3 = Book.objects.create(
            title="Livro Estante Virtual",
            author=self.author,
            category=self.category,
            publication_date=timezone.now().date(),
            purchase_partner_name="Estante Virtual",
            purchase_partner_url="https://www.estantevirtual.com.br/livro/123"
        )

    def test_command_dry_run(self):
        out = StringIO()
        call_command('normalize_amazon_links', '--dry-run', stdout=out)
        output = out.getvalue()

        self.assertIn("SIMULACAO (--dry-run)", output)
        self.assertIn("Total de registros da Amazon analisados : 2", output)
        self.assertIn("Registros que serao/foram alterados     : 1", output)

        # Verificar se o banco NÃO foi alterado no dry-run
        self.book1.refresh_from_db()
        self.assertIn("ref=sr_1_1", self.book1.purchase_partner_url)

    def test_command_apply(self):
        out = StringIO()
        call_command('normalize_amazon_links', '--apply', stdout=out)
        output = out.getvalue()

        self.assertIn("EXECUCAO REAL (--apply)", output)
        self.assertIn("Sucesso! 1 registros foram atualizados", output)


        # Verificar se o banco FOI alterado
        self.book1.refresh_from_db()
        self.assertEqual(
            self.book1.purchase_partner_url,
            "https://www.amazon.com.br/dp/6555604344?tag=cgbookstore-20"
        )

        # Verificar se o livro do outro parceiro permaneceu intacto
        self.book3.refresh_from_db()
        self.assertEqual(
            self.book3.purchase_partner_url,
            "https://www.estantevirtual.com.br/livro/123"
        )
