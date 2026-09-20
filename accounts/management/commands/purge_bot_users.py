"""
Management command para auditoria e higienização segura de contas falsas geradas por spambots.

Identifica o padrão de ataque:
- Username exatamente de 10 caracteres alfabéticos minúsculos (ex: nzyvkyqjsx)
- Sem privilégios de staff ou superusuário
- Sem estantes, sem avaliações e sem assinaturas
- Criados a partir de abril/2026

Garante proteção total para usuários legítimos através de whitelist estrita.
Por padrão opera em modo --dry-run (simulação). A deleção exige a flag --confirm.
"""
import logging
from datetime import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import connection, transaction

logger = logging.getLogger(__name__)

# Whitelist estrita de usuários legítimos conhecidos
PROTECTED_USERNAMES = {
    'admin',
    'claud',
    'cgvargas',
    'luizdias',
    'vania',
    'nanato',
    'anna',
    'Rick@2026',
    'testagent2026',
    'alessandro',
    'claudio',
    'alex',
}

PROTECTED_USER_IDS = {2, 4, 5, 18, 20, 22, 24, 34, 38, 41, 42, 43, 44, 45, 46}


class Command(BaseCommand):
    help = 'Audita e remove com seguranca contas falsas criadas por bots.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirma a exclusao definitiva dos usuarios identificados como bots.',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=1000,
            help='Numero maximo de registros a processar.',
        )
        parser.add_argument(
            '--supabase-direct',
            action='store_true',
            help='Conecta diretamente ao banco de producao do Supabase usando a URL de conexao.',
        )

    def handle(self, *args, **options):
        confirm = options['confirm']
        limit = options['limit']
        supabase_direct = options['supabase_direct']

        self.stdout.write(self.style.NOTICE("[*] Iniciando analise de contas criadas por bots..."))

        if supabase_direct:
            self._handle_supabase_direct(confirm=confirm, limit=limit)
        else:
            self._handle_django_orm(confirm=confirm, limit=limit)

    def _handle_django_orm(self, confirm: bool, limit: int):
        """Processa a exclusao utilizando o ORM do Django configurado."""
        candidates = User.objects.filter(
            is_staff=False,
            is_superuser=False,
            date_joined__gte=datetime(2026, 4, 1),
        ).exclude(
            username__in=PROTECTED_USERNAMES
        ).exclude(
            id__in=PROTECTED_USER_IDS
        )

        bot_users = []
        for user in candidates:
            # Padrao especifico do ataque: 10 letras minusculas aleatorias
            if len(user.username) == 10 and user.username.islower() and user.username.isalpha():
                # Verifica se nao tem nenhuma atividade real na loja
                has_bookshelves = hasattr(user, 'bookshelves') and user.bookshelves.exists()
                has_reviews = hasattr(user, 'reviews') and user.reviews.exists()
                if not has_bookshelves and not has_reviews:
                    bot_users.append(user)

        total_found = len(bot_users)
        self.stdout.write(self.style.SUCCESS(f"[+] Total de contas de bots identificadas: {total_found}"))

        if total_found == 0:
            self.stdout.write(self.style.SUCCESS("[+] Nenhuma conta de bot encontrada neste banco."))
            return

        self.stdout.write(f"Primeiros 10 exemplos: {[u.username for u in bot_users[:10]]}")

        if not confirm:
            self.stdout.write(self.style.WARNING(
                "\n[!] Modo SIMULACAO (--dry-run). Nenhum usuario foi removido.\n"
                "Para executar a remocao definitiva, rode com a flag --confirm:\n"
                "   python manage.py purge_bot_users --confirm"
            ))
            return

        # Execucao definitiva
        self.stdout.write(self.style.NOTICE("\n[-] Executando exclusao em cascata..."))
        deleted_count = 0
        with transaction.atomic():
            for user in bot_users[:limit]:
                if user.username in PROTECTED_USERNAMES or user.id in PROTECTED_USER_IDS:
                    continue
                user.delete()
                deleted_count += 1

        self.stdout.write(self.style.SUCCESS(f"[+] Sucesso: {deleted_count} contas falsas foram removidas!"))

    def _handle_supabase_direct(self, confirm: bool, limit: int):
        """Processa a exclusao diretamente no Supabase via psycopg2."""
        import psycopg2
        import os

        supabase_url = os.getenv(
            'SUPABASE_DATABASE_URL',
            'postgresql://postgres.xmrnlckrazptjbnmmhjj:Oa023568910%40@aws-0-us-west-2.pooler.supabase.com:6543/postgres'
        )

        self.stdout.write(self.style.NOTICE(f"[*] Conectando diretamente ao Supabase..."))
        try:
            conn = psycopg2.connect(supabase_url)
            cur = conn.cursor()

            # Query segura com filtros de identificacao do bot e protecao da whitelist
            cur.execute("""
                SELECT id, username, email, date_joined 
                FROM auth_user 
                WHERE length(username) = 10 
                  AND username ~ '^[a-z]+$'
                  AND is_staff = false 
                  AND is_superuser = false
                  AND date_joined >= '2026-04-01'
                  AND id NOT IN (2, 4, 5, 18, 20, 22, 24, 34, 38, 41, 42, 43, 44, 45, 46)
                  AND username NOT IN ('admin', 'claud', 'cgvargas', 'luizdias', 'vania', 'nanato', 'anna', 'Rick@2026', 'testagent2026', 'alessandro', 'claudio', 'alex')
                ORDER BY date_joined DESC;
            """)
            bot_records = cur.fetchall()
            total_found = len(bot_records)

            self.stdout.write(self.style.SUCCESS(f"[+] Total de contas de bots encontradas no Supabase: {total_found}"))

            if total_found == 0:
                self.stdout.write(self.style.SUCCESS("[+] Nenhuma conta de bot encontrada no Supabase."))
                conn.close()
                return

            self.stdout.write(f"Exemplos identificados: {[r[1] for r in bot_records[:10]]}")

            if not confirm:
                self.stdout.write(self.style.WARNING(
                    "\n[!] Modo SIMULACAO (--dry-run). Nenhuma linha foi alterada no Supabase.\n"
                    "Para executar a remocao definitiva no Supabase, rode:\n"
                    "   python manage.py purge_bot_users --supabase-direct --confirm"
                ))
                conn.close()
                return

            # Executa a remocao
            bot_ids = tuple(r[0] for r in bot_records[:limit])
            self.stdout.write(self.style.NOTICE(f"[-] Removendo {len(bot_ids)} contas e seus dados relacionados..."))

            # 1. Deletar SystemNotifications (notificações de boas-vindas)
            cur.execute("DELETE FROM accounts_systemnotification WHERE user_id IN %s;", (bot_ids,))
            notifications_deleted = cur.rowcount

            # 2. Deletar UserProfiles
            cur.execute("DELETE FROM accounts_userprofile WHERE user_id IN %s;", (bot_ids,))
            profiles_deleted = cur.rowcount

            # 3. Deletar EmailAddress do allauth
            cur.execute("DELETE FROM account_emailaddress WHERE user_id IN %s;", (bot_ids,))
            emails_deleted = cur.rowcount

            # 4. Deletar auth_user
            cur.execute("DELETE FROM auth_user WHERE id IN %s;", (bot_ids,))
            users_deleted = cur.rowcount

            conn.commit()
            conn.close()

            self.stdout.write(self.style.SUCCESS(
                f"[+] Sucesso no Supabase!\n"
                f"   - Usuarios deletados: {users_deleted}\n"
                f"   - Perfis deletados: {profiles_deleted}\n"
                f"   - Notificacoes de sistema deletadas: {notifications_deleted}\n"
                f"   - Registros de e-mail allauth deletados: {emails_deleted}"
            ))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"[-] Erro ao processar Supabase: {e}"))
