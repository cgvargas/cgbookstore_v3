"""
Comando Django para popular dados iniciais no banco de dados.
Uso: python manage.py setup_initial_data
"""

from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from django.contrib.auth import get_user_model
from core.models import Category, Book, Author
from allauth.socialaccount.models import SocialApp
from datetime import date
import os

User = get_user_model()


class Command(BaseCommand):
    help = 'Popula o banco de dados com dados iniciais essenciais'

    def add_arguments(self, parser):
        parser.add_argument(
            '--admin-email',
            type=str,
            default='admin@cgbookstore.com',
            help='Email do usuário administrador (padrão: admin@cgbookstore.com)'
        )
        parser.add_argument(
            '--admin-password',
            type=str,
            default='admin123',
            help='Senha do usuário administrador (padrão: admin123)'
        )
        parser.add_argument(
            '--skip-superuser',
            action='store_true',
            help='Pular criação de superusuário'
        )
        parser.add_argument(
            '--skip-categories',
            action='store_true',
            help='Pular criação de categorias'
        )
        parser.add_argument(
            '--skip-books',
            action='store_true',
            help='Pular criação de livros de exemplo'
        )
        parser.add_argument(
            '--skip-social',
            action='store_true',
            help='Pular configuração de apps sociais'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('🚀 Iniciando configuração de dados iniciais...'))
        self.stdout.write(self.style.SUCCESS('=' * 70))

        # 1. Configurar Site
        self.setup_site()

        # 2. Criar superusuário
        if not options['skip_superuser']:
            self.create_superuser(
                options['admin_email'],
                options['admin_password']
            )

        # 3. Criar categorias
        if not options['skip_categories']:
            self.create_categories()

        # 4. Criar livros de exemplo
        if not options['skip_books']:
            self.create_sample_books()

        # 5. Configurar Social Apps (Google e Facebook)
        if not options['skip_social']:
            self.setup_social_apps()

        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('✅ Configuração concluída com sucesso!'))
        self.stdout.write(self.style.SUCCESS('=' * 70))

    def setup_site(self):
        """Configura o Site para django-allauth."""
        self.stdout.write('📍 Configurando Site...')

        site_domain = os.getenv('SITE_DOMAIN', 'localhost:8000')
        site_name = os.getenv('SITE_NAME', 'CG Bookstore')

        site, created = Site.objects.get_or_create(
            id=1,
            defaults={
                'domain': site_domain,
                'name': site_name
            }
        )

        if not created:
            site.domain = site_domain
            site.name = site_name
            site.save()
            self.stdout.write(self.style.WARNING(f'   ⚠️  Site atualizado: {site_name} ({site_domain})'))
        else:
            self.stdout.write(self.style.SUCCESS(f'   ✅ Site criado: {site_name} ({site_domain})'))

    def create_superuser(self, email, password):
        """Cria um superusuário se não existir."""
        self.stdout.write('👤 Criando superusuário...')

        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.WARNING(f'   ⚠️  Usuário com email {email} já existe'))
            return

        if User.objects.filter(username='admin').exists():
            self.stdout.write(self.style.WARNING('   ⚠️  Usuário admin já existe'))
            return

        user = User.objects.create_superuser(
            username='admin',
            email=email,
            password=password
        )

        self.stdout.write(self.style.SUCCESS(f'   ✅ Superusuário criado:'))
        self.stdout.write(self.style.SUCCESS(f'      Username: admin'))
        self.stdout.write(self.style.SUCCESS(f'      Email: {email}'))
        self.stdout.write(self.style.WARNING(f'      Senha: {password}'))
        self.stdout.write(self.style.WARNING('      ⚠️  ALTERE A SENHA EM PRODUÇÃO!'))

    def create_categories(self):
        """Cria categorias padrão de livros."""
        self.stdout.write('📚 Criando categorias...')

        categories_data = [
            ('Ficção', True),
            ('Romance', True),
            ('Fantasia', True),
            ('Ficção Científica', True),
            ('Terror', False),
            ('Suspense', True),
            ('Aventura', False),
            ('Biografia', False),
            ('História', False),
            ('Tecnologia', True),
            ('Negócios', False),
            ('Autoajuda', True),
            ('Poesia', False),
            ('Infantil', True),
            ('Jovem Adulto', True),
            ('Clássicos', True),
            ('Literatura Brasileira', True),
            ('Literatura Estrangeira', False),
            ('HQ e Mangá', True),
            ('Educação', False),
        ]

        created_count = 0
        for name, featured in categories_data:
            category, created = Category.objects.get_or_create(
                name=name,
                defaults={'featured': featured}
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'   ✅ Categoria criada: {name}'))
            else:
                self.stdout.write(self.style.WARNING(f'   ⚠️  Categoria já existe: {name}'))

        self.stdout.write(self.style.SUCCESS(f'   Total: {created_count} categorias criadas'))

    def create_sample_books(self):
        """Cria livros de exemplo para demonstração."""
        self.stdout.write('📖 Criando livros de exemplo...')

        # Obter categorias
        ficcao = Category.objects.filter(name='Ficção').first()
        tecnologia = Category.objects.filter(name='Tecnologia').first()
        classicos = Category.objects.filter(name='Clássicos').first()

        if not all([ficcao, tecnologia, classicos]):
            self.stdout.write(self.style.ERROR('   ❌ Categorias não encontradas. Execute sem --skip-categories'))
            return

        # Criar autores
        authors_data = [
            {'name': 'George Orwell', 'biography': 'Escritor e jornalista britânico.'},
            {'name': 'Isaac Asimov', 'biography': 'Escritor e bioquímico russo-americano.'},
            {'name': 'Machado de Assis', 'biography': 'Escritor brasileiro, fundador da Academia Brasileira de Letras.'},
        ]

        authors = {}
        for author_data in authors_data:
            author, created = Author.objects.get_or_create(
                name=author_data['name'],
                defaults={'biography': author_data['biography']}
            )
            authors[author_data['name']] = author
            if created:
                self.stdout.write(self.style.SUCCESS(f'   ✅ Autor criado: {author.name}'))

        # Criar livros
        books_data = [
            {
                'title': '1984',
                'author': authors['George Orwell'],
                'category': ficcao,
                'description': 'Romance distópico de George Orwell sobre totalitarismo.',
                'publication_date': date(1949, 6, 8),
                'isbn': '9780451524935',
                'publisher': 'Secker & Warburg',
                'price': 29.90,
                'language': 'pt',
            },
            {
                'title': 'Fundação',
                'author': authors['Isaac Asimov'],
                'category': ficcao,
                'description': 'Primeira obra da série Fundação, sobre psicohistória.',
                'publication_date': date(1951, 5, 1),
                'isbn': '9780553293357',
                'publisher': 'Gnome Press',
                'price': 34.90,
                'language': 'pt',
            },
            {
                'title': 'Dom Casmurro',
                'author': authors['Machado de Assis'],
                'category': classicos,
                'description': 'Romance clássico brasileiro sobre ciúme e traição.',
                'publication_date': date(1899, 1, 1),
                'isbn': '9788544001073',
                'publisher': 'Laemmert',
                'price': 24.90,
                'language': 'pt',
            },
        ]

        created_count = 0
        for book_data in books_data:
            # Usar slug como identificador único
            from django.utils.text import slugify
            slug = slugify(book_data['title'])

            book, created = Book.objects.get_or_create(
                slug=slug,
                defaults=book_data
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'   ✅ Livro criado: {book.title}'))
            else:
                self.stdout.write(self.style.WARNING(f'   ⚠️  Livro já existe: {book.title}'))

        self.stdout.write(self.style.SUCCESS(f'   Total: {created_count} livros criados'))

    def setup_social_apps(self):
        """Configura apps sociais (Google e Facebook) se as credenciais existirem."""
        self.stdout.write('🔐 Configurando apps sociais...')

        google_client_id = os.getenv('GOOGLE_CLIENT_ID', '')
        google_secret = os.getenv('GOOGLE_CLIENT_SECRET', '')
        facebook_app_id = os.getenv('FACEBOOK_APP_ID', '')
        facebook_secret = os.getenv('FACEBOOK_APP_SECRET', '')

        site = Site.objects.get(id=1)
        created_count = 0

        # Google OAuth
        if google_client_id and google_secret:
            google_app, created = SocialApp.objects.get_or_create(
                provider='google',
                defaults={
                    'name': 'Google',
                    'client_id': google_client_id,
                    'secret': google_secret,
                }
            )
            if created:
                google_app.sites.add(site)
                created_count += 1
                self.stdout.write(self.style.SUCCESS('   ✅ Google OAuth configurado'))
            else:
                # Atualizar credenciais se mudaram
                google_app.client_id = google_client_id
                google_app.secret = google_secret
                google_app.save()
                google_app.sites.add(site)
                self.stdout.write(self.style.WARNING('   ⚠️  Google OAuth atualizado'))
        else:
            self.stdout.write(self.style.WARNING('   ⚠️  Credenciais Google não encontradas (GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET)'))

        # Facebook OAuth
        if facebook_app_id and facebook_secret:
            facebook_app, created = SocialApp.objects.get_or_create(
                provider='facebook',
                defaults={
                    'name': 'Facebook',
                    'client_id': facebook_app_id,
                    'secret': facebook_secret,
                }
            )
            if created:
                facebook_app.sites.add(site)
                created_count += 1
                self.stdout.write(self.style.SUCCESS('   ✅ Facebook OAuth configurado'))
            else:
                # Atualizar credenciais se mudaram
                facebook_app.client_id = facebook_app_id
                facebook_app.secret = facebook_secret
                facebook_app.save()
                facebook_app.sites.add(site)
                self.stdout.write(self.style.WARNING('   ⚠️  Facebook OAuth atualizado'))
        else:
            self.stdout.write(self.style.WARNING('   ⚠️  Credenciais Facebook não encontradas (FACEBOOK_APP_ID, FACEBOOK_APP_SECRET)'))

        if created_count == 0 and not (google_client_id or facebook_app_id):
            self.stdout.write(self.style.WARNING('   ⚠️  Nenhuma credencial OAuth configurada'))
