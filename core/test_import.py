from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from unittest.mock import patch
from core.models import Book

class BookImportValidationTests(TestCase):
    """Testes unitários para validar a política de qualidade na importação de livros do Google Books."""

    def setUp(self):
        # Usuário normal e superusuário
        self.user = User.objects.create_user(username='normaluser', password='pass123')
        self.admin = User.objects.create_superuser(username='adminuser', password='pass123')
        
    @patch('core.views.book_search_views.get_book_by_id')
    def test_import_validation_failures_for_normal_user(self, mock_get_book):
        """Valida que usuários normais são barrados ao tentar importar livros com dados incompletos."""
        self.client.login(username='normaluser', password='pass123')
        
        # Cenário 1: Sem capa (thumbnail nulo)
        mock_get_book.return_value = {
            'title': 'Livro Sem Capa',
            'authors': ['Autor'],
            'isbn_13': '9781234567890',
            'description': 'Uma descrição bem longa com mais de oitenta caracteres para passar na validação de tamanho de texto de descrição.',
            'page_count': 100,
            'thumbnail': None
        }
        response = self.client.post(reverse('core:api_import_google', kwargs={'google_book_id': 'id1'}))
        self.assertEqual(response.status_code, 400)
        self.assertIn("imagem de capa", response.json()['message'])
        
        # Cenário 2: Sem autor
        mock_get_book.return_value = {
            'title': 'Livro Sem Autor',
            'authors': [],
            'isbn_13': '9781234567890',
            'description': 'Uma descrição bem longa com mais de oitenta caracteres para passar na validação de tamanho de texto de descrição.',
            'page_count': 100,
            'thumbnail': 'http://image.url'
        }
        response = self.client.post(reverse('core:api_import_google', kwargs={'google_book_id': 'id2'}))
        self.assertEqual(response.status_code, 400)
        self.assertIn("informações de autor", response.json()['message'])

        # Cenário 3: Sem ISBN
        mock_get_book.return_value = {
            'title': 'Livro Sem ISBN',
            'authors': ['Autor'],
            'isbn_13': None,
            'isbn_10': None,
            'description': 'Uma descrição bem longa com mais de oitenta caracteres para passar na validação de tamanho de texto de descrição.',
            'page_count': 100,
            'thumbnail': 'http://image.url'
        }
        response = self.client.post(reverse('core:api_import_google', kwargs={'google_book_id': 'id3'}))
        self.assertEqual(response.status_code, 400)
        self.assertIn("código ISBN", response.json()['message'])

        # Cenário 4: Descrição muito curta
        mock_get_book.return_value = {
            'title': 'Livro Sem Descrição',
            'authors': ['Autor'],
            'isbn_13': '9781234567890',
            'description': 'Curta.',
            'page_count': 100,
            'thumbnail': 'http://image.url'
        }
        response = self.client.post(reverse('core:api_import_google', kwargs={'google_book_id': 'id4'}))
        self.assertEqual(response.status_code, 400)
        self.assertIn("descrição do livro é inexistente ou muito curta", response.json()['message'])

        # Cenário 5: Contagem de páginas inválida
        mock_get_book.return_value = {
            'title': 'Livro Sem Páginas',
            'authors': ['Autor'],
            'isbn_13': '9781234567890',
            'description': 'Uma descrição bem longa com mais de oitenta caracteres para passar na validação de tamanho de texto de descrição.',
            'page_count': 0,
            'thumbnail': 'http://image.url'
        }
        response = self.client.post(reverse('core:api_import_google', kwargs={'google_book_id': 'id5'}))
        self.assertEqual(response.status_code, 400)
        self.assertIn("contagem de páginas", response.json()['message'])

    @patch('core.views.book_search_views.get_book_by_id')
    @patch('core.views.book_search_views.download_cover')
    def test_import_success_grants_xp_for_normal_user(self, mock_download, mock_get_book):
        """Valida que livros com dados completos são importados por usuários comuns e estes ganham +15 XP."""
        self.client.login(username='normaluser', password='pass123')
        mock_download.return_value = 'path/to/cover.jpg'
        
        mock_get_book.return_value = {
            'title': 'Livro Válido Inédito',
            'authors': ['Autor Válido'],
            'isbn_13': '9789999999999',
            'description': 'Uma descrição super longa e detalhada com muitos caracteres para assegurar que passará em qualquer validação de tamanho de texto de descrição.',
            'page_count': 250,
            'thumbnail': 'http://image.url'
        }
        
        initial_xp = self.user.profile.total_xp
        response = self.client.post(reverse('core:api_import_google', kwargs={'google_book_id': 'id_valido'}))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        self.assertEqual(response.json()['xp_earned'], 15)
        
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.total_xp, initial_xp + 15)

    @patch('core.views.book_search_views.get_book_by_id')
    @patch('core.views.book_search_views.download_cover')
    def test_import_bypass_for_superuser(self, mock_download, mock_get_book):
        """Valida que superusuários conseguem importar qualquer livro mesmo que esteja incompleto."""
        self.client.login(username='adminuser', password='pass123')
        mock_download.return_value = None # Ignorar download de capa
        
        # Dados incompletos (sem capa, sem páginas) que seriam rejeitados para usuário comum
        mock_get_book.return_value = {
            'title': 'Livro Incompleto do Admin',
            'authors': ['Autor'],
            'isbn_13': '9788888888888',
            'description': 'Curta.',
            'page_count': 0,
            'thumbnail': None
        }
        
        response = self.client.post(reverse('core:api_import_google', kwargs={'google_book_id': 'id_admin'}))
        # Deve ter sucesso porque é superuser!
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
