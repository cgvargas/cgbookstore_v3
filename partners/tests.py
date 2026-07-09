from django.test import TestCase, override_settings
from unittest.mock import patch
from django.utils.text import slugify
from django.urls import reverse
from core.models import Book, Author, Category
from partners.models import AffiliatePartner, AffiliatePartnerClick
from partners.services.affiliate_service import AffiliateService
import datetime


class AffiliatePartnerModelTest(TestCase):
    """
    Testes unitários para o modelo AffiliatePartner.
    """

    def test_slug_auto_generation(self):
        """
        Garante que o slug é gerado automaticamente a partir do nome.
        """
        partner = AffiliatePartner.objects.create(nome="Amazon Brasil", tracking_id="amazon-20")
        self.assertEqual(partner.slug, "amazon-brasil")

    def test_slug_uniqueness_resolution(self):
        """
        Garante que slugs duplicados são resolvidos adicionando um sufixo numérico.
        """
        partner1 = AffiliatePartner.objects.create(nome="Mercado Livre")
        partner2 = AffiliatePartner.objects.create(nome="Mercado Livre")
        
        self.assertEqual(partner1.slug, "mercado-livre")
        self.assertEqual(partner2.slug, "mercado-livre-1")

    def test_ordering_and_str(self):
        """
        Testa a representação em string e a ordenação por prioridade.
        """
        partner_low = AffiliatePartner.objects.create(nome="Parceiro B", prioridade=1)
        partner_high = AffiliatePartner.objects.create(nome="Parceiro A", prioridade=10)
        
        self.assertEqual(str(partner_low), "Parceiro B")
        
        partners = list(AffiliatePartner.objects.all())
        self.assertEqual(partners[0], partner_high)
        self.assertEqual(partners[1], partner_low)


class AffiliateServiceTest(TestCase):
    """
    Testes unitários para a camada de serviço AffiliateService.
    """

    def setUp(self):
        self.author = Author.objects.create(name="Fiodor Dostoievski")
        self.category = Category.objects.create(name="Clássicos")
        self.book = Book.objects.create(
            title="Crime e Castigo",
            author=self.author,
            category=self.category,
            publication_date=datetime.date(1866, 1, 1),
            purchase_partner_name="Amazon",
            purchase_partner_url="https://www.amazon.com.br/Crime-Castigo-Fiodor-Dostoievski/dp/8573266416"
        )
        self.partner_amazon = AffiliatePartner.objects.create(
            nome="Amazon",
            tracking_id="cgbookstore-20",
            cor_botao="btn-warning",
            icone="fab fa-amazon"
        )

    def test_get_partner_for_book(self):
        """
        Testa a resolução do parceiro comercial do livro por nome e slug.
        """
        resolved_partner = AffiliateService.get_partner_for_book(self.book)
        self.assertEqual(resolved_partner, self.partner_amazon)

        # Teste com parceiro inativo
        self.partner_amazon.ativo = False
        self.partner_amazon.save()
        
        resolved_partner_inactive = AffiliateService.get_partner_for_book(self.book)
        self.assertIsNone(resolved_partner_inactive)

    def test_generate_link_amazon_without_params(self):
        """
        Testa se o link da Amazon recebe o tracking_id como tag.
        """
        url = "https://www.amazon.com.br/dp/8573266416"
        final_url = AffiliateService.generate_link(self.partner_amazon, self.book, url)
        self.assertIn("tag=cgbookstore-20", final_url)

    def test_generate_link_amazon_with_existing_params(self):
        """
        Testa se o link da Amazon com parâmetros existentes preserva os parâmetros e insere/substitui a tag.
        """
        url = "https://www.amazon.com.br/dp/8573266416?ref_=ast_author_dp&language=pt_BR"
        final_url = AffiliateService.generate_link(self.partner_amazon, self.book, url)
        self.assertIn("tag=cgbookstore-20", final_url)
        self.assertIn("ref_=ast_author_dp", final_url)
        self.assertIn("language=pt_BR", final_url)

        # Teste de substituição de tag existente
        url_with_tag = "https://www.amazon.com.br/dp/8573266416?tag=oldtag-20&ref_=dp"
        final_url_replaced = AffiliateService.generate_link(self.partner_amazon, self.book, url_with_tag)
        self.assertIn("tag=cgbookstore-20", final_url_replaced)
        self.assertNotIn("tag=oldtag-20", final_url_replaced)

    def test_get_link_for_book_with_partner(self):
        """
        Testa a integração geral do link de afiliados para o livro.
        """
        final_url = AffiliateService.get_link_for_book(self.book)
        self.assertIn("tag=cgbookstore-20", final_url)

    def test_get_link_for_book_without_partner_fallback(self):
        """
        Testa se faz o fallback seguro caso o parceiro não exista ou esteja inativo.
        """
        self.book.purchase_partner_name = "Estante Virtual"
        self.book.save()

        final_url = AffiliateService.get_link_for_book(self.book)
        self.assertEqual(final_url, self.book.purchase_partner_url)


class BookModelPropertiesTest(TestCase):
    """
    Testes de integração das propriedades do parceiro comercial injetadas no modelo Book.
    """

    def setUp(self):
        self.author = Author.objects.create(name="J.R.R. Tolkien")
        self.category = Category.objects.create(name="Fantasia")
        self.book = Book.objects.create(
            title="O Senhor dos Anéis",
            author=self.author,
            category=self.category,
            publication_date=datetime.date(1954, 7, 29),
            purchase_partner_name="Amazon",
            purchase_partner_url="https://www.amazon.com.br/dp/8595086354"
        )
        self.partner_amazon = AffiliatePartner.objects.create(
            nome="Amazon",
            tracking_id="cgbookstore-20",
            cor_botao="btn-warning",
            icone="fab fa-amazon"
        )

    def test_book_properties_with_active_partner(self):
        """
        Verifica se as propriedades do livro refletem as configurações do parceiro ativo.
        """
        self.assertEqual(self.book.affiliate_partner, self.partner_amazon)
        self.assertIn(f"/partners/redirect/book/{self.book.id}/partner/{self.partner_amazon.id}/", self.book.affiliate_url)
        self.assertEqual(self.book.affiliate_button_class, "btn-warning")
        self.assertEqual(self.book.affiliate_icon_class, "fab fa-amazon")
        self.assertEqual(self.book.affiliate_display_name, "Amazon")

    def test_book_properties_fallback_without_partner(self):
        """
        Verifica o fallback das propriedades do livro caso o parceiro comercial não esteja cadastrado.
        """
        self.book.purchase_partner_name = "Saraiva"
        self.book.save()

        self.assertIsNone(self.book.affiliate_partner)
        self.assertIn(f"/partners/redirect/book/{self.book.id}/", self.book.affiliate_url)
        self.assertNotIn("/partner/", self.book.affiliate_url)
        self.assertEqual(self.book.affiliate_button_class, "btn-success")
        self.assertEqual(self.book.affiliate_icon_class, "fas fa-shopping-cart")
        self.assertEqual(self.book.affiliate_display_name, "Saraiva")


class AffiliateClickTrackingTest(TestCase):
    """
    Testes de integração para rastreamento de cliques, User-Agent parser e segurança contra duplicidade.
    """

    def setUp(self):
        self.author = Author.objects.create(name="Arthur Conan Doyle")
        self.category = Category.objects.create(name="Mistério")
        self.book = Book.objects.create(
            title="Sherlock Holmes",
            author=self.author,
            category=self.category,
            publication_date=datetime.date(1887, 11, 1),
            purchase_partner_name="Amazon",
            purchase_partner_url="https://www.amazon.com.br/dp/8537813583"
        )
        self.partner = AffiliatePartner.objects.create(
            nome="Amazon",
            tracking_id="cgbookstore-20",
            cor_botao="btn-warning",
            icone="fab fa-amazon"
        )

    def test_click_tracking_view_redirects_and_logs(self):
        """
        Verifica se a view de redirecionamento registra o clique com metadados corretos.
        """
        url = reverse('partners:redirect_to_partner', kwargs={'book_id': self.book.id, 'partner_id': self.partner.id})
        
        # User-Agent de Desktop Windows Chrome
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        
        response = self.client.get(
            url, 
            HTTP_USER_AGENT=user_agent,
            HTTP_REFERER="https://www.google.com",
            HTTP_ACCEPT_LANGUAGE="pt-BR,pt;q=0.9"
        )
        
        # Deve redirecionar para a URL final com a tag do parceiro
        self.assertEqual(response.status_code, 302)
        self.assertIn("https://www.amazon.com.br/dp/8537813583", response.url)
        self.assertIn("tag=cgbookstore-20", response.url)
        
        # Deve ter criado 1 registro no banco de dados
        self.assertEqual(AffiliatePartnerClick.objects.count(), 1)
        click = AffiliatePartnerClick.objects.first()
        self.assertEqual(click.book, self.book)
        self.assertEqual(click.partner, self.partner)
        self.assertEqual(click.browser, "Chrome")
        self.assertEqual(click.os, "Windows")
        self.assertEqual(click.device, "Desktop")
        self.assertEqual(click.referer, "https://www.google.com")
        self.assertEqual(click.language, "pt-BR,pt;q=0.9")

    def test_click_tracking_ua_parsing_mobile(self):
        """
        Verifica a detecção de dispositivos móveis no parser.
        """
        url = reverse('partners:redirect_to_partner', kwargs={'book_id': self.book.id, 'partner_id': self.partner.id})
        
        # User-Agent de iPhone Safari
        user_agent = "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1"
        
        response = self.client.get(url, HTTP_USER_AGENT=user_agent)
        
        self.assertEqual(response.status_code, 302)
        click = AffiliatePartnerClick.objects.first()
        self.assertEqual(click.browser, "Safari")
        self.assertEqual(click.os, "iOS")
        self.assertEqual(click.device, "Mobile")

    def test_duplicate_click_prevention(self):
        """
        Garante que cliques consecutivos em curto intervalo de tempo (10s) não gerem múltiplos registros.
        """
        url = reverse('partners:redirect_to_partner', kwargs={'book_id': self.book.id, 'partner_id': self.partner.id})
        
        # Primeiro clique
        response1 = self.client.get(url)
        self.assertEqual(response1.status_code, 302)
        self.assertEqual(AffiliatePartnerClick.objects.count(), 1)
        
        # Segundo clique consecutivo imediato (mesma sessão/anônimo)
        response2 = self.client.get(url)
        self.assertEqual(response2.status_code, 302)
        
        # Apenas 1 clique deve ter sido registrado
        self.assertEqual(AffiliatePartnerClick.objects.count(), 1)


class BookCredibilityPropertiesTest(TestCase):
    """
    Testes unitários para as propriedades de completude e origem de dados do Book.
    """

    def setUp(self):
        self.author = Author.objects.create(name="Oscar Wilde")
        self.category = Category.objects.create(name="Ficção")
        self.book = Book.objects.create(
            title="O Retrato de Dorian Gray",
            author=self.author,
            category=self.category,
            page_count=320,
            isbn="9788567097237",
            publication_date=datetime.date(1890, 6, 20),
            description="Um clássico sobre juventude e arte."
        )

    def test_metadata_completeness_hundred_percent(self):
        self.book.cover_image = "books/dorian.jpg"
        self.book.save()
        self.assertEqual(self.book.metadata_completeness, 100)

    def test_metadata_completeness_partial(self):
        self.assertEqual(self.book.metadata_completeness, 83)  # 5/6 = 83%

    def test_metadata_source_display(self):
        self.assertEqual(self.book.metadata_source_display, "Cadastro Interno")
        self.book.google_books_id = "gbid123"
        self.assertEqual(self.book.metadata_source_display, "Google Books API")


@override_settings(CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}})
class AIReviewServiceTest(TestCase):
    """
    Testes unitários para o serviço AIReviewService (Gemini API Integration).
    """

    def setUp(self):
        self.author = Author.objects.create(name="Machado de Assis")
        self.book = Book.objects.create(title="Dom Casmurro", author=self.author, publication_date=datetime.date(1899, 1, 1))

    @patch('google.generativeai.GenerativeModel')
    @patch('django.conf.settings.GEMINI_API_KEY', 'fake-key')
    def test_generate_review_success(self, mock_model_class):
        mock_response = mock_model_class.return_value.generate_content.return_value
        mock_response.text = """
        {
            "resumo": "Uma obra clássica do realismo brasileiro que investiga o ciúme e a dúvida.",
            "perfil_leitor": "Leitores apaixonados por clássicos e psicologia de personagens.",
            "faixa_etaria": "14+",
            "complexidade": "Média",
            "tempo_leitura": "10 horas",
            "temas_principais": ["Ciúme", "Traição", "Sociedade carioca"],
            "nota_geral": 9.8
        }
        """
        
        from core.services.ai_review_service import AIReviewService
        review = AIReviewService.generate_review(self.book)
        self.assertIsNotNone(review)
        self.assertEqual(review['nota_geral'], 9.8)
        self.assertEqual(review['faixa_etaria'], "14+")
        self.assertIn("Ciúme", review['temas_principais'])


@override_settings(CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}})
class BookRecommendationServiceTest(TestCase):
    """
    Testes para o serviço BookRecommendationService.
    """

    def setUp(self):
        self.author = Author.objects.create(name="George Orwell")
        self.category = Category.objects.create(name="Distopia")
        self.book_base = Book.objects.create(
            title="1984", 
            author=self.author, 
            category=self.category,
            cover_image="covers/1984.jpg",
            publication_date=datetime.date(1949, 6, 8)
        )
        self.book_same_author = Book.objects.create(
            title="A Revolução dos Bichos", 
            author=self.author, 
            category=self.category,
            cover_image="covers/animals.jpg",
            publication_date=datetime.date(1945, 8, 17)
        )
        self.book_same_cat = Book.objects.create(
            title="Fahrenheit 451", 
            author=Author.objects.create(name="Ray Bradbury"), 
            category=self.category,
            cover_image="covers/451.jpg",
            publication_date=datetime.date(1953, 10, 19)
        )

    def test_author_recommendations(self):
        from recommendations.services import BookRecommendationService
        recs = BookRecommendationService.get_author_recommendations(self.book_base)
        self.assertEqual(len(recs), 1)
        self.assertEqual(recs[0], self.book_same_author)

    def test_category_recommendations(self):
        from recommendations.services import BookRecommendationService
        recs = BookRecommendationService.get_category_recommendations(self.book_base)
        self.assertEqual(len(recs), 2)

    def test_collaborative_recommendations(self):
        from accounts.models import BookShelf
        from django.contrib.auth.models import User
        from recommendations.services import BookRecommendationService
        
        user1 = User.objects.create_user(username="user1", password="pw")
        user2 = User.objects.create_user(username="user2", password="pw")
        
        BookShelf.objects.create(user=user1, book=self.book_base, shelf_type='read')
        BookShelf.objects.create(user=user2, book=self.book_base, shelf_type='favorites')
        BookShelf.objects.create(user=user1, book=self.book_same_cat, shelf_type='read')
        
        recs = BookRecommendationService.get_collaborative_recommendations(self.book_base)
        self.assertEqual(len(recs), 1)
        self.assertEqual(recs[0], self.book_same_cat)

    @patch('recommendations.services.recommendation_service.search_books')
    def test_google_books_recommendations_fallback(self, mock_search_books):
        from recommendations.services import BookRecommendationService
        
        mock_search_books.return_value = {
            'items': [
                {
                    'id': 'googleid_999',
                    'volumeInfo': {
                        'title': 'Admirável Mundo Novo',
                        'authors': ['Aldous Huxley'],
                        'description': 'Um clássico distópico futurista.',
                        'imageLinks': {
                            'thumbnail': 'https://example.com/cover.jpg'
                        }
                    }
                }
            ]
        }
        
        recs = BookRecommendationService.get_google_books_recommendations(self.book_base, limit=1)
        self.assertEqual(len(recs), 1)
        temp_book = recs[0]
        self.assertEqual(temp_book.title, "Admirável Mundo Novo")
        self.assertEqual(temp_book.author.name, "Aldous Huxley")
        self.assertEqual(temp_book.cover_url_temp, "https://example.com/cover.jpg")
        self.assertIsNone(temp_book.id)


@override_settings(CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}})
class GamificationIntegrationsTest(TestCase):
    """
    Testes para as integrações de gamificação da Fase 3 (atribuição de XP).
    """

    def setUp(self):
        from django.contrib.auth.models import User
        self.user = User.objects.create_user(username="gameread", email="game@cgb.com", password="password")
        from accounts.models import UserProfile
        self.profile, _ = UserProfile.objects.get_or_create(user=self.user)
        self.profile.total_xp = 100
        self.profile.save()

        self.author = Author.objects.create(name="J.K. Rowling", slug="jk-rowling")
        self.category = Category.objects.create(name="Magia", slug="magia")
        self.book = Book.objects.create(title="Harry Potter", author=self.author, category=self.category, slug="harry-potter", publication_date=datetime.date(1997, 6, 26))

    def test_author_detail_xp_gain(self):
        self.client.login(username="gameread", password="password")
        url = reverse('core:author_detail', kwargs={'slug': self.author.slug})
        
        response1 = self.client.get(url)
        self.assertEqual(response1.status_code, 200)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.total_xp, 105)

        response2 = self.client.get(url)
        self.assertEqual(response2.status_code, 200)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.total_xp, 105)

    def test_category_list_filter_xp_gain(self):
        self.client.login(username="gameread", password="password")
        url = reverse('core:book_list') + f"?category={self.category.slug}"
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.total_xp, 105)

    def test_recommendation_click_xp_gain(self):
        self.client.login(username="gameread", password="password")
        url = reverse('core:book_detail', kwargs={'slug': self.book.slug}) + "?ref=recommendation"
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.total_xp, 105)


class BookRedirectViewRoutingTest(TestCase):
    """
    Testes de integração para a BookRedirectView com foco em slugs numéricos (ex: '1984').
    """

    def setUp(self):
        self.author = Author.objects.create(name="George Orwell")
        self.category = Category.objects.create(name="Distopia")
        self.book_1984 = Book.objects.create(
            title="1984",
            author=self.author,
            category=self.category,
            slug="1984",
            publication_date=datetime.date(1949, 6, 8)
        )

    def test_redirect_view_with_numeric_slug(self):
        # A URL /livros/1984/ deve cair na BookRedirectView, mas renderizar diretamente a página do livro
        url = reverse('core:book_detail_by_id', kwargs={'book_id': 1984})
        response = self.client.get(url)
        # Deve retornar 200 OK (renderizando a página de 1984, não um redirecionamento infinito ou 404)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "1984")

    def test_redirect_view_with_standard_id(self):
        # A URL /livros/<id>/ de um livro com slug de texto (ex: 'Harry Potter' -> slug 'harry-potter') deve redirecionar
        book_hp = Book.objects.create(
            title="Harry Potter",
            author=self.author,
            category=self.category,
            slug="harry-potter",
            publication_date=datetime.date(1997, 6, 26)
        )
        url = reverse('core:book_detail_by_id', kwargs={'book_id': book_hp.id})
        response = self.client.get(url)
        # Deve ser um redirecionamento permanente (301)
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response.url, book_hp.get_absolute_url())


@override_settings(CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}})
class AIFeaturesIntegrationTest(TestCase):
    """
    Suíte de testes de integração para as funcionalidades de IA e Personalização da Fase 4.
    """

    def setUp(self):
        from django.contrib.auth.models import User
        self.user = User.objects.create_user(username="aisocial", email="ai@cgb.com", password="password")
        
        self.author = Author.objects.create(name="Aldous Huxley", slug="aldous-huxley")
        self.category = Category.objects.create(name="Distopia", slug="distopia")
        self.book = Book.objects.create(
            title="Admirável Mundo Novo",
            author=self.author,
            category=self.category,
            slug="admiravel-mundo-novo",
            publication_date=datetime.date(1932, 1, 1),
            cover_image="books/covers/adn.jpg"
        )
        
        from accounts.models import BookShelf
        BookShelf.objects.create(
            user=self.user,
            book=self.book,
            shelf_type="favorites"
        )

    @override_settings(AI_PROVIDER="mock")
    def test_ai_provider_abstraction_and_logging(self):
        from core.services.ai_provider_service import AIProviderFactory
        from monitoring.models import AIUsageLog
        
        provider = AIProviderFactory.get_provider()
        res = provider.generate_json("Gere resumo literário", user=self.user, feature_name="test_feature")
        
        # O mock provider deve retornar chaves esperadas
        self.assertIn("resumo", res)
        self.assertEqual(res["nota_geral"], 9.5)
        
        # Deve ter registrado um log de uso no banco
        logs = AIUsageLog.objects.filter(user=self.user, feature_name="test_feature")
        self.assertTrue(logs.exists())
        self.assertEqual(logs.first().provider, "mock")

    @override_settings(AI_PROVIDER="mock")
    def test_reader_profile_generation_and_learning(self):
        from recommendations.services.reader_profile_service import ReaderProfileService
        from recommendations.models import AIReaderProfile
        
        # 1. Atualizar pesos de perfil baseado na estante
        profile = ReaderProfileService.update_profile_weights(self.user)
        self.assertIn("Distopia", profile.categories_interest)
        self.assertIn("Aldous Huxley", profile.authors_interest)
        self.assertEqual(profile.categories_interest["Distopia"], 1.0)
        
        # 2. Gerar biografia do leitor via IA
        profile = ReaderProfileService.generate_profile_summary_ai(self.user, force=True)
        self.assertTrue(profile.profile_summary)
        self.assertIn("humor", profile.reading_style_ai or {})
        
        # 3. Testar feedback loop (continuous learning)
        ReaderProfileService.adjust_weights_on_feedback(self.user, category_name="Distopia", score_change=-0.2)
        profile.refresh_from_db()
        self.assertEqual(profile.categories_interest["Distopia"], 0.8)

    @override_settings(AI_PROVIDER="mock")
    def test_ai_personalized_recommendations(self):
        from recommendations.services.recommendation_service import BookRecommendationService
        from news.models import Article, Category as NewsCategory
        from core.models import Video
        
        # Criar categoria de notícias e artigo relacionado
        news_cat = NewsCategory.objects.create(name="Distopia", slug="distopia-news")
        Article.objects.create(
            title="Nova adaptação de Huxley",
            content="Detalhes sobre a adaptação.",
            category=news_cat,
            is_published=True
        )
        
        # Criar vídeo de adaptação
        Video.objects.create(
            title="Trailer de Admirável Mundo Novo",
            video_type="adaptation",
            related_book=self.book,
            active=True
        )
        
        recs = BookRecommendationService.get_ai_personalized_recommendations(self.user, limit=2)
        
        # Verificar que a estrutura de resposta está correta
        self.assertIn("books", recs)
        self.assertIn("news", recs)
        self.assertIn("adaptations", recs)
        self.assertTrue(len(recs["adaptations"]) >= 1)

    @override_settings(AI_PROVIDER="mock")
    def test_ai_notifications_targeting(self):
        from core.services.ai_notification_service import AINotificationService
        from recommendations.services.reader_profile_service import ReaderProfileService
        from accounts.models import SystemNotification
        
        # Inicializar os pesos
        ReaderProfileService.update_profile_weights(self.user)
        
        # Testar envio de notificação de novo livro da mesma categoria
        new_book = Book.objects.create(
            title="Fahrenheit 451",
            author=self.author,
            category=self.category,
            slug="fahrenheit-451",
            publication_date=datetime.date(1953, 10, 19)
        )
        
        sent_count = AINotificationService.notify_book_launch(new_book)
        self.assertEqual(sent_count, 1)
        
        # Verificar se a notificação foi de fato criada para o usuário
        user_notifications = SystemNotification.objects.filter(user=self.user, notification_type="book_launch")
        self.assertTrue(user_notifications.exists())
        self.assertIn("Fahrenheit 451", user_notifications.first().message)



