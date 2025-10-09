"""
Comando para configurar o Supabase
Uso: python manage.py setup_supabase
"""

from django.core.management.base import BaseCommand
from django.conf import settings
from supabase import create_client
import sys


class Command(BaseCommand):
    help = 'Configura o Supabase (cria buckets, testa conexão)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('=== Configurando Supabase ===\n'))

        # Verificar configurações
        if not settings.SUPABASE_URL or not settings.SUPABASE_ANON_KEY:
            self.stdout.write(
                self.style.ERROR(
                    'ERRO: SUPABASE_URL e SUPABASE_ANON_KEY devem estar configurados no arquivo .env'
                )
            )
            self.stdout.write('\nPara configurar:')
            self.stdout.write('1. Acesse seu projeto no Supabase')
            self.stdout.write('2. Vá em Settings > API')
            self.stdout.write('3. Copie a URL e Anon Key')
            self.stdout.write('4. Adicione ao arquivo .env')
            sys.exit(1)

        try:
            # Testar conexão
            self.stdout.write('Testando conexão com Supabase...')
            client = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)

            # Criar buckets
            self.stdout.write('\nCriando buckets de storage...')
            from core.utils.supabase_storage import supabase_storage_admin
            supabase_storage_admin.create_buckets()

            # Testar conexão com o banco
            self.stdout.write('\nTestando conexão com o banco de dados...')
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT version();")
                version = cursor.fetchone()
                self.stdout.write(f'PostgreSQL versão: {version[0]}')

            self.stdout.write(
                self.style.SUCCESS('\n✅ Supabase configurado com sucesso!')
            )

            # Instruções finais
            self.stdout.write('\n=== Próximos passos ===')
            self.stdout.write('1. Execute as migrações: python manage.py migrate')
            self.stdout.write('2. Crie um superusuário: python manage.py createsuperuser')
            self.stdout.write('3. Colete arquivos estáticos: python manage.py collectstatic')
            self.stdout.write('4. Execute o servidor: python manage.py runserver')

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'\n❌ Erro ao configurar Supabase: {str(e)}')
            )
            self.stdout.write('\nVerifique:')
            self.stdout.write('1. As credenciais no arquivo .env estão corretas')
            self.stdout.write('2. Seu projeto Supabase está ativo')
            self.stdout.write('3. O banco de dados está acessível')
            sys.exit(1)