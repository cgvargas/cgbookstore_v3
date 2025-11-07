"""
Comando Django para verificar a saúde da aplicação.
Uso: python manage.py health_check
"""

from django.core.management.base import BaseCommand
from django.db import connections, DatabaseError
from django.contrib.sites.models import Site
from django.conf import settings
from core.models import Category, Book
from allauth.socialaccount.models import SocialApp
import os


class Command(BaseCommand):
    help = 'Verifica a saúde da aplicação e configurações'

    def __init__(self):
        super().__init__()
        self.errors = []
        self.warnings = []

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('🏥 HEALTH CHECK - CG Bookstore'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write('')

        # 1. Database Connection
        self.check_database()

        # 2. Redis Connection
        self.check_redis()

        # 3. Django Site
        self.check_site()

        # 4. Social Apps
        self.check_social_apps()

        # 5. Categories
        self.check_categories()

        # 6. Books
        self.check_books()

        # 7. Environment Variables
        self.check_environment()

        # 8. Security Settings
        self.check_security()

        # Summary
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.show_summary()
        self.stdout.write(self.style.SUCCESS('=' * 70))

    def check_database(self):
        """Verifica conexão com o banco de dados."""
        self.stdout.write('🗄️  DATABASE CONNECTION')
        try:
            db_conn = connections['default']
            db_conn.cursor()
            self.stdout.write(self.style.SUCCESS('   ✅ Banco de dados conectado'))

            # Info do banco
            db_settings = settings.DATABASES['default']
            engine = db_settings['ENGINE'].split('.')[-1]
            self.stdout.write(f'   Engine: {engine}')

            if 'NAME' in db_settings:
                self.stdout.write(f'   Database: {db_settings["NAME"]}')

        except DatabaseError as e:
            self.stdout.write(self.style.ERROR(f'   ❌ Erro de conexão: {e}'))
            self.errors.append('Database connection failed')

        self.stdout.write('')

    def check_redis(self):
        """Verifica conexão com Redis."""
        self.stdout.write('🔴 REDIS CONNECTION')
        try:
            from django.core.cache import cache
            cache.set('health_check', 'OK', 10)
            result = cache.get('health_check')

            if result == 'OK':
                self.stdout.write(self.style.SUCCESS('   ✅ Redis conectado'))
                cache.delete('health_check')
            else:
                self.stdout.write(self.style.WARNING('   ⚠️  Redis respondeu incorretamente'))
                self.warnings.append('Redis may have issues')

        except Exception as e:
            self.stdout.write(self.style.WARNING(f'   ⚠️  Redis não disponível: {e}'))
            self.warnings.append('Redis not available (non-critical)')

        self.stdout.write('')

    def check_site(self):
        """Verifica configuração do Site."""
        self.stdout.write('🌐 DJANGO SITE')
        try:
            site = Site.objects.get(id=1)
            self.stdout.write(self.style.SUCCESS(f'   ✅ Site configurado: {site.name}'))
            self.stdout.write(f'   Domain: {site.domain}')
        except Site.DoesNotExist:
            self.stdout.write(self.style.ERROR('   ❌ Site não configurado (ID=1)'))
            self.stdout.write(self.style.WARNING('   Execute: python manage.py setup_initial_data'))
            self.errors.append('Django Site not configured')

        self.stdout.write('')

    def check_social_apps(self):
        """Verifica configuração de apps sociais."""
        self.stdout.write('🔐 SOCIAL AUTHENTICATION')

        social_apps = SocialApp.objects.all()

        if social_apps.exists():
            for app in social_apps:
                has_credentials = bool(app.client_id and app.secret)
                if has_credentials:
                    self.stdout.write(self.style.SUCCESS(f'   ✅ {app.name} configurado'))
                else:
                    self.stdout.write(self.style.WARNING(f'   ⚠️  {app.name} sem credenciais completas'))
                    self.warnings.append(f'{app.name} OAuth incomplete')
        else:
            self.stdout.write(self.style.WARNING('   ⚠️  Nenhum app social configurado'))
            self.stdout.write('   Execute: python manage.py setup_initial_data')
            self.warnings.append('No social apps configured')

        self.stdout.write('')

    def check_categories(self):
        """Verifica se existem categorias."""
        self.stdout.write('📚 CATEGORIES')

        count = Category.objects.count()
        featured_count = Category.objects.filter(featured=True).count()

        if count > 0:
            self.stdout.write(self.style.SUCCESS(f'   ✅ {count} categorias cadastradas'))
            self.stdout.write(f'   Destaque: {featured_count} categorias')
        else:
            self.stdout.write(self.style.WARNING('   ⚠️  Nenhuma categoria cadastrada'))
            self.stdout.write('   Execute: python manage.py setup_initial_data')
            self.warnings.append('No categories in database')

        self.stdout.write('')

    def check_books(self):
        """Verifica se existem livros."""
        self.stdout.write('📖 BOOKS')

        count = Book.objects.count()

        if count > 0:
            self.stdout.write(self.style.SUCCESS(f'   ✅ {count} livros cadastrados'))
        else:
            self.stdout.write(self.style.WARNING('   ⚠️  Nenhum livro cadastrado'))
            self.stdout.write('   Execute: python manage.py setup_initial_data')
            self.warnings.append('No books in database')

        self.stdout.write('')

    def check_environment(self):
        """Verifica variáveis de ambiente importantes."""
        self.stdout.write('🔧 ENVIRONMENT VARIABLES')

        important_vars = {
            'SECRET_KEY': 'Chave secreta do Django',
            'DEBUG': 'Modo de debug',
            'ALLOWED_HOSTS': 'Hosts permitidos',
            'DATABASE_URL': 'URL do banco de dados',
            'REDIS_URL': 'URL do Redis',
        }

        optional_vars = {
            'GOOGLE_CLIENT_ID': 'Google OAuth Client ID',
            'GOOGLE_CLIENT_SECRET': 'Google OAuth Secret',
            'GOOGLE_BOOKS_API_KEY': 'Google Books API',
            'GEMINI_API_KEY': 'Google Gemini AI',
            'SUPABASE_URL': 'Supabase URL',
            'SUPABASE_ANON_KEY': 'Supabase Anon Key',
        }

        # Verificar variáveis importantes
        for var, description in important_vars.items():
            value = os.getenv(var)
            if value:
                # Mascarar valores sensíveis
                if 'SECRET' in var or 'KEY' in var:
                    display_value = f'{value[:4]}...{value[-4:]}' if len(value) > 8 else '***'
                else:
                    display_value = value

                self.stdout.write(self.style.SUCCESS(f'   ✅ {var}: {display_value}'))
            else:
                self.stdout.write(self.style.ERROR(f'   ❌ {var} não configurado'))
                self.errors.append(f'{var} not set')

        # Verificar variáveis opcionais
        missing_optional = []
        for var, description in optional_vars.items():
            if not os.getenv(var):
                missing_optional.append(f'{var} ({description})')

        if missing_optional:
            self.stdout.write(self.style.WARNING(f'   ⚠️  Variáveis opcionais não configuradas: {len(missing_optional)}'))
            for var in missing_optional[:3]:  # Mostrar apenas as 3 primeiras
                self.stdout.write(f'      - {var}')

        self.stdout.write('')

    def check_security(self):
        """Verifica configurações de segurança."""
        self.stdout.write('🔒 SECURITY SETTINGS')

        # Debug mode
        if settings.DEBUG:
            self.stdout.write(self.style.ERROR('   ❌ DEBUG está ATIVO em produção!'))
            self.errors.append('DEBUG is True in production')
        else:
            self.stdout.write(self.style.SUCCESS('   ✅ DEBUG desativado'))

        # HTTPS
        if not settings.DEBUG:
            if settings.SECURE_SSL_REDIRECT:
                self.stdout.write(self.style.SUCCESS('   ✅ HTTPS redirect ativo'))
            else:
                self.stdout.write(self.style.WARNING('   ⚠️  HTTPS redirect desativado'))
                self.warnings.append('HTTPS redirect not enabled')

        # Allowed hosts
        if '*' in settings.ALLOWED_HOSTS:
            self.stdout.write(self.style.ERROR('   ❌ ALLOWED_HOSTS permite todos os hosts (*)'))
            self.errors.append('ALLOWED_HOSTS allows all hosts')
        else:
            self.stdout.write(self.style.SUCCESS(f'   ✅ ALLOWED_HOSTS: {", ".join(settings.ALLOWED_HOSTS)}'))

        self.stdout.write('')

    def show_summary(self):
        """Mostra resumo do health check."""
        total_checks = len(self.errors) + len(self.warnings)

        if not self.errors and not self.warnings:
            self.stdout.write(self.style.SUCCESS('✅ TUDO OK! Aplicação saudável.'))
            return

        if self.errors:
            self.stdout.write(self.style.ERROR(f'❌ ERROS CRÍTICOS: {len(self.errors)}'))
            for error in self.errors:
                self.stdout.write(self.style.ERROR(f'   - {error}'))
            self.stdout.write('')

        if self.warnings:
            self.stdout.write(self.style.WARNING(f'⚠️  AVISOS: {len(self.warnings)}'))
            for warning in self.warnings:
                self.stdout.write(self.style.WARNING(f'   - {warning}'))
            self.stdout.write('')

        if self.errors:
            self.stdout.write(self.style.ERROR('🚨 Ação necessária: corrija os erros críticos!'))
        else:
            self.stdout.write(self.style.WARNING('⚠️  Avisos encontrados, mas aplicação funcional'))
