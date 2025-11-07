"""
Comando Django para migrar dados do Supabase para o banco atual.
Uso: python manage.py migrate_from_supabase
"""

from django.core.management.base import BaseCommand
from django.db import connections
import psycopg2
from psycopg2.extras import RealDictCursor
import os


class Command(BaseCommand):
    help = 'Migra dados do Supabase para o banco de dados atual (Render)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simula a migração sem fazer alterações'
        )
        parser.add_argument(
            '--skip-users',
            action='store_true',
            help='Pular migração de usuários'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('🚀 MIGRAÇÃO DE DADOS: Supabase → Render'))
        self.stdout.write(self.style.SUCCESS('=' * 70))

        dry_run = options['dry_run']
        skip_users = options['skip_users']

        if dry_run:
            self.stdout.write(self.style.WARNING('⚠️  MODO DRY-RUN: Nenhuma alteração será feita'))

        # URL do Supabase
        supabase_url = os.getenv('SUPABASE_DATABASE_URL')

        if not supabase_url:
            # Construir URL do Supabase se não estiver definida
            supabase_url = os.getenv('DATABASE_URL')
            if 'supabase' not in supabase_url:
                self.stdout.write(self.style.ERROR('❌ Erro: DATABASE_URL não é do Supabase'))
                self.stdout.write('Configure SUPABASE_DATABASE_URL com a URL do Supabase')
                return

        # Conectar ao Supabase (origem)
        try:
            self.stdout.write('\n📡 Conectando ao Supabase...')
            source_conn = psycopg2.connect(supabase_url)
            source_cursor = source_conn.cursor(cursor_factory=RealDictCursor)
            self.stdout.write(self.style.SUCCESS('   ✅ Conectado ao Supabase'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ❌ Erro ao conectar: {e}'))
            return

        # Conectar ao banco atual (destino - Render)
        try:
            self.stdout.write('\n📡 Conectando ao banco destino (Render)...')
            dest_conn = connections['default']
            dest_cursor = dest_conn.cursor()
            self.stdout.write(self.style.SUCCESS('   ✅ Conectado ao banco destino'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ❌ Erro ao conectar: {e}'))
            source_conn.close()
            return

        # Listar tabelas para migrar (na ordem correta devido a FK)
        tables_order = [
            # Django core
            'django_content_type',
            'auth_permission',
            'auth_group',
            'auth_group_permissions',

            # Usuários
            'auth_user',
            'auth_user_groups',
            'auth_user_user_permissions',

            # Django admin
            'django_admin_log',

            # Django sessions
            'django_session',

            # Sites
            'django_site',

            # Allauth
            'account_emailaddress',
            'account_emailconfirmation',
            'socialaccount_socialapp',
            'socialaccount_socialapp_sites',
            'socialaccount_socialaccount',
            'socialaccount_socialtoken',

            # Core app
            'core_category',
            'core_author',
            'core_book',
            'core_section',
            'core_banner',
            'core_event',
            'core_video',
            'core_sectionitem',

            # Outros apps
            'chatbot_literario_conversation',
            'chatbot_literario_message',
            'debates_debate',
            'debates_comment',
            'recommendations_userinteraction',
            'recommendations_bookrecommendation',
            'finance_transaction',
            'finance_credittransaction',
        ]

        stats = {
            'migrated': 0,
            'skipped': 0,
            'errors': 0,
        }

        try:
            for table in tables_order:
                self.migrate_table(
                    source_cursor,
                    dest_cursor,
                    table,
                    dry_run,
                    stats,
                    skip=(table.startswith('auth_user') and skip_users)
                )

            if not dry_run:
                dest_conn.commit()
                self.stdout.write(self.style.SUCCESS('\n✅ Commit realizado'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n❌ Erro durante migração: {e}'))
            if not dry_run:
                dest_conn.rollback()
                self.stdout.write(self.style.WARNING('⚠️  Rollback realizado'))
            stats['errors'] += 1

        finally:
            source_cursor.close()
            source_conn.close()
            dest_cursor.close()

        # Resumo
        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(self.style.SUCCESS('📊 RESUMO DA MIGRAÇÃO'))
        self.stdout.write('=' * 70)
        self.stdout.write(f"✅ Tabelas migradas: {stats['migrated']}")
        self.stdout.write(f"⏭️  Tabelas puladas: {stats['skipped']}")
        self.stdout.write(f"❌ Erros: {stats['errors']}")
        self.stdout.write('=' * 70)

        if dry_run:
            self.stdout.write(self.style.WARNING('\n⚠️  MODO DRY-RUN: Nenhuma alteração foi feita'))
        else:
            self.stdout.write(self.style.SUCCESS('\n🎉 Migração concluída!'))

    def migrate_table(self, source_cursor, dest_cursor, table, dry_run, stats, skip=False):
        """Migra uma tabela específica."""

        if skip:
            self.stdout.write(f'\n⏭️  Pulando: {table}')
            stats['skipped'] += 1
            return

        try:
            # Verificar se tabela existe no destino
            dest_cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_name = %s
                )
            """, (table,))

            if not dest_cursor.fetchone()[0]:
                self.stdout.write(f'\n⚠️  Tabela {table} não existe no destino, pulando...')
                stats['skipped'] += 1
                return

            # Contar registros na origem
            source_cursor.execute(f'SELECT COUNT(*) FROM {table}')
            count = source_cursor.fetchone()['count']

            if count == 0:
                self.stdout.write(f'\n⏭️  {table}: Vazia, pulando...')
                stats['skipped'] += 1
                return

            self.stdout.write(f'\n📦 {table}: {count} registros')

            # Buscar dados da origem
            source_cursor.execute(f'SELECT * FROM {table}')
            rows = source_cursor.fetchall()

            if not rows:
                stats['skipped'] += 1
                return

            # Preparar INSERT
            columns = rows[0].keys()
            placeholders = ', '.join(['%s'] * len(columns))
            insert_sql = f"""
                INSERT INTO {table} ({', '.join(columns)})
                VALUES ({placeholders})
                ON CONFLICT DO NOTHING
            """

            if not dry_run:
                # Inserir dados
                for row in rows:
                    values = [row[col] for col in columns]
                    dest_cursor.execute(insert_sql, values)

            self.stdout.write(self.style.SUCCESS(f'   ✅ {count} registros migrados'))
            stats['migrated'] += 1

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ❌ Erro em {table}: {e}'))
            stats['errors'] += 1
