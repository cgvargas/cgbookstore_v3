"""
Script rápido para resetar senha de um usuário.
Uso: python resetar_senha_rapido.py NOME_USUARIO NOVA_SENHA
"""
import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from django.contrib.auth.models import User


def resetar_senha(username, nova_senha):
    try:
        user = User.objects.get(username=username)
        user.set_password(nova_senha)
        user.save()

        print("=" * 60)
        print("SENHA RESETADA COM SUCESSO!")
        print("=" * 60)
        print(f"\nUsuario: {username}")
        print(f"Nova senha: {nova_senha}")
        print(f"Usuario ativo: {user.is_active}")
        print(f"\nAgora voce pode fazer login em:")
        print("http://127.0.0.1:8000/accounts/login/")
        print("=" * 60)

    except User.DoesNotExist:
        print(f"\n[ERRO] Usuario '{username}' nao encontrado!")
        print("\nUsuarios disponiveis:")
        for u in User.objects.all():
            print(f"  - {u.username}")


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Uso: python resetar_senha_rapido.py USUARIO SENHA")
        print("\nExemplo:")
        print("  python resetar_senha_rapido.py cgvargas 123456")
        print("\nUsuarios disponiveis:")
        for u in User.objects.all():
            print(f"  - {u.username}")
    else:
        username = sys.argv[1]
        senha = sys.argv[2]
        resetar_senha(username, senha)
