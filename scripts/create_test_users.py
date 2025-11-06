"""
Script para criar usuarios de teste para o sistema de campanhas de marketing
"""
import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from accounts.models import UserProfile

# Fix encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def create_test_users():
    """Cria usuários de teste para diferentes cenários de campanha"""

    print("🚀 Criando usuários de teste...\n")

    # Lista de usuários a criar
    test_users = [
        # Usuários novos (últimos 7 dias)
        {
            'username': 'novo_usuario_1',
            'email': 'novo1@test.com',
            'password': 'test123',
            'first_name': 'Novo',
            'last_name': 'Usuario Um',
            'date_joined': timezone.now() - timedelta(days=2),
            'last_login': timezone.now() - timedelta(days=1),
        },
        {
            'username': 'novo_usuario_2',
            'email': 'novo2@test.com',
            'password': 'test123',
            'first_name': 'Novo',
            'last_name': 'Usuario Dois',
            'date_joined': timezone.now() - timedelta(days=5),
            'last_login': timezone.now() - timedelta(days=2),
        },

        # Usuários inativos (últimos 60+ dias sem login)
        {
            'username': 'inativo_60dias',
            'email': 'inativo60@test.com',
            'password': 'test123',
            'first_name': 'Inativo',
            'last_name': 'Sessenta Dias',
            'date_joined': timezone.now() - timedelta(days=120),
            'last_login': timezone.now() - timedelta(days=65),
        },
        {
            'username': 'inativo_90dias',
            'email': 'inativo90@test.com',
            'password': 'test123',
            'first_name': 'Inativo',
            'last_name': 'Noventa Dias',
            'date_joined': timezone.now() - timedelta(days=200),
            'last_login': timezone.now() - timedelta(days=95),
        },

        # Usuários ativos
        {
            'username': 'usuario_ativo_1',
            'email': 'ativo1@test.com',
            'password': 'test123',
            'first_name': 'Ativo',
            'last_name': 'Usuario Um',
            'date_joined': timezone.now() - timedelta(days=30),
            'last_login': timezone.now() - timedelta(hours=5),
        },
        {
            'username': 'usuario_ativo_2',
            'email': 'ativo2@test.com',
            'password': 'test123',
            'first_name': 'Ativo',
            'last_name': 'Usuario Dois',
            'date_joined': timezone.now() - timedelta(days=45),
            'last_login': timezone.now() - timedelta(hours=12),
        },

        # Usuários para teste de grupo
        {
            'username': 'grupo_teste_1',
            'email': 'grupo1@test.com',
            'password': 'test123',
            'first_name': 'Grupo',
            'last_name': 'Teste Um',
            'date_joined': timezone.now() - timedelta(days=60),
            'last_login': timezone.now() - timedelta(days=10),
        },
        {
            'username': 'grupo_teste_2',
            'email': 'grupo2@test.com',
            'password': 'test123',
            'first_name': 'Grupo',
            'last_name': 'Teste Dois',
            'date_joined': timezone.now() - timedelta(days=70),
            'last_login': timezone.now() - timedelta(days=15),
        },
        {
            'username': 'grupo_teste_3',
            'email': 'grupo3@test.com',
            'password': 'test123',
            'first_name': 'Grupo',
            'last_name': 'Teste Tres',
            'date_joined': timezone.now() - timedelta(days=80),
            'last_login': timezone.now() - timedelta(days=20),
        },

        # Usuário VIP (para testes individuais)
        {
            'username': 'vip_premium',
            'email': 'vip@test.com',
            'password': 'test123',
            'first_name': 'VIP',
            'last_name': 'Premium',
            'date_joined': timezone.now() - timedelta(days=365),
            'last_login': timezone.now() - timedelta(hours=2),
        },
    ]

    created_count = 0
    skipped_count = 0

    for user_data in test_users:
        username = user_data['username']

        # Verifica se usuário já existe
        if User.objects.filter(username=username).exists():
            print(f"⏭️  {username} - Já existe, pulando...")
            skipped_count += 1
            continue

        # Cria o usuário
        user = User.objects.create_user(
            username=user_data['username'],
            email=user_data['email'],
            password=user_data['password'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
        )

        # Atualiza datas
        user.date_joined = user_data['date_joined']
        user.last_login = user_data['last_login']
        user.save()

        # Garante que UserProfile existe
        profile, created = UserProfile.objects.get_or_create(user=user)
        if created:
            profile.save()

        created_count += 1
        print(f"✅ {username} - Criado com sucesso!")

    print(f"\n{'='*60}")
    print(f"📊 RESUMO:")
    print(f"   ✅ Criados: {created_count}")
    print(f"   ⏭️  Pulados: {skipped_count}")
    print(f"   📝 Total: {created_count + skipped_count}")
    print(f"{'='*60}\n")

    # Exibe informações úteis
    print("🔐 CREDENCIAIS DE ACESSO:")
    print("   Senha para todos: test123\n")

    print("📋 CATEGORIAS DE USUÁRIOS:\n")
    print("   🆕 NOVOS (últimos 7 dias):")
    print("      - novo_usuario_1")
    print("      - novo_usuario_2\n")

    print("   😴 INATIVOS (60+ dias):")
    print("      - inativo_60dias")
    print("      - inativo_90dias\n")

    print("   ✅ ATIVOS:")
    print("      - usuario_ativo_1")
    print("      - usuario_ativo_2\n")

    print("   👥 GRUPO DE TESTE:")
    print("      - grupo_teste_1")
    print("      - grupo_teste_2")
    print("      - grupo_teste_3\n")

    print("   💎 VIP:")
    print("      - vip_premium\n")

    print("💡 EXEMPLOS DE CAMPANHAS PARA TESTAR:\n")
    print("1️⃣  Campanha para NOVOS USUÁRIOS:")
    print('   Critérios: {"days_ago": 7}\n')

    print("2️⃣  Campanha para INATIVOS:")
    print('   Critérios: {"inactive_days": 60, "no_active_subscription": true, "limit": 100}\n')

    print("3️⃣  Campanha para GRUPO:")
    print('   Critérios: {"usernames": ["grupo_teste_1", "grupo_teste_2", "grupo_teste_3"]}\n')

    print("4️⃣  Campanha INDIVIDUAL VIP:")
    print('   Critérios: {"username": "vip_premium"}\n')

    print("✨ Usuários criados com sucesso! Pronto para testar campanhas!")

if __name__ == '__main__':
    create_test_users()
