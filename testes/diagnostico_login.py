"""
Script de diagnóstico para problemas de login.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from django.contrib.auth.models import User
from django.conf import settings


def diagnosticar_login():
    print("=" * 60)
    print("DIAGNOSTICO DE LOGIN - CGBookStore v3")
    print("=" * 60)

    # 1. Verificar usuários no banco
    print("\n[1] USUARIOS NO BANCO DE DADOS:")
    users = User.objects.all()
    print(f"   Total de usuarios: {users.count()}")

    if users.exists():
        print("\n   Lista de usuarios:")
        for user in users:
            print(f"   - {user.username} (ativo: {user.is_active}, staff: {user.is_staff})")
    else:
        print("   [AVISO] Nenhum usuario encontrado!")
        print("   Execute: python manage.py createsuperuser")

    # 2. Verificar configurações de autenticação
    print("\n[2] CONFIGURACOES DE AUTENTICACAO:")
    print(f"   LOGIN_URL: {settings.LOGIN_URL}")
    print(f"   LOGIN_REDIRECT_URL: {settings.LOGIN_REDIRECT_URL}")
    print(f"   LOGOUT_REDIRECT_URL: {settings.LOGOUT_REDIRECT_URL}")

    # 3. Verificar middlewares
    print("\n[3] MIDDLEWARES:")
    auth_middleware = 'django.contrib.auth.middleware.AuthenticationMiddleware'
    session_middleware = 'django.contrib.sessions.middleware.SessionMiddleware'

    if auth_middleware in settings.MIDDLEWARE:
        print(f"   ✅ {auth_middleware}")
    else:
        print(f"   ❌ {auth_middleware} - FALTANDO!")

    if session_middleware in settings.MIDDLEWARE:
        print(f"   ✅ {session_middleware}")
    else:
        print(f"   ❌ {session_middleware} - FALTANDO!")

    # 4. Verificar INSTALLED_APPS
    print("\n[4] INSTALLED_APPS:")
    required_apps = [
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
    ]

    for app in required_apps:
        if app in settings.INSTALLED_APPS:
            print(f"   ✅ {app}")
        else:
            print(f"   ❌ {app} - FALTANDO!")

    # 5. Testar login programaticamente
    print("\n[5] TESTE DE AUTENTICACAO:")
    if users.exists():
        user = users.first()
        print(f"   Testando usuario: {user.username}")
        print(f"   Usuario ativo: {user.is_active}")
        print(f"   Tem senha: {user.has_usable_password()}")

        # Tentar autenticar com senha conhecida
        print("\n   [INFO] Para testar login, tente:")
        print(f"   - Usuario: {user.username}")
        print("   - Resetar senha se necessario:")
        print(f"     python manage.py changepassword {user.username}")

    # 6. Verificar SESSION_ENGINE
    print("\n[6] CONFIGURACOES DE SESSAO:")
    print(f"   SESSION_ENGINE: {settings.SESSION_ENGINE}")

    if 'cache' in settings.SESSION_ENGINE:
        print("   [INFO] Sessoes em cache (Redis)")
        print("   Certifique-se que Redis esta rodando!")
        print("   Teste: redis-cli ping (deve retornar PONG)")

    # 7. Sugestões
    print("\n" + "=" * 60)
    print("SUGESTOES DE SOLUCAO")
    print("=" * 60)

    if not users.exists():
        print("\n1. CRIAR USUARIO:")
        print("   python manage.py createsuperuser")
    else:
        print("\n1. RESETAR SENHA DO USUARIO:")
        print(f"   python manage.py changepassword {users.first().username}")

    print("\n2. VERIFICAR REDIS (se usando cache para sessoes):")
    print("   wsl redis-cli ping")
    print("   (Deve retornar: PONG)")

    print("\n3. LIMPAR SESSOES:")
    print("   python manage.py clearsessions")

    print("\n4. TESTAR LOGIN:")
    print("   - Acesse: http://127.0.0.1:8000/accounts/login/")
    print(f"   - Usuario: {users.first().username if users.exists() else 'SEU_USUARIO'}")
    print("   - Senha: (a que voce definir)")

    print("\n5. VERIFICAR CONSOLE DO NAVEGADOR:")
    print("   - Abra DevTools (F12)")
    print("   - Veja erros JavaScript")
    print("   - Verifique Network tab ao fazer login")

    print("\n" + "=" * 60)


if __name__ == '__main__':
    diagnosticar_login()
