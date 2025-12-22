"""
Script para verificar dados do usuario claud
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import BookShelf

print("=" * 80)
print("VERIFICACAO DE DADOS DO USUARIO")
print("=" * 80)

# Listar todos os usuarios
users = User.objects.all()
print(f"\nTotal de usuarios cadastrados: {users.count()}")
print("\nUsuarios:")
for u in users[:10]:
    print(f"  ID {u.id}: {u.username} (Email: {u.email})")

# Verificar usuario claud
user_claud = User.objects.filter(username='claud').first()
print(f"\nUsuario 'claud' encontrado: {user_claud is not None}")

if user_claud:
    print(f"  ID: {user_claud.id}")
    print(f"  Email: {user_claud.email}")
    print(f"  Ativo: {user_claud.is_active}")
    print(f"  Staff: {user_claud.is_staff}")

    # Verificar prateleiras
    bookshelves = BookShelf.objects.filter(user=user_claud)
    print(f"\nTotal de livros na biblioteca de claud: {bookshelves.count()}")

    if bookshelves.exists():
        print("\nLivros nas prateleiras:")
        for b in bookshelves[:10]:
            print(f"  - {b.book.title} (Prateleira: {b.shelf})")
    else:
        print("  NENHUM livro encontrado na biblioteca!")

    # Verificar se ha bookshelves em geral
    total_bookshelves = BookShelf.objects.all().count()
    print(f"\nTotal de bookshelves no sistema: {total_bookshelves}")

    if total_bookshelves > 0:
        print("\nExemplos de bookshelves de outros usuarios:")
        for b in BookShelf.objects.all()[:5]:
            print(f"  Usuario: {b.user.username} - Livro: {b.book.title} ({b.shelf})")
else:
    print("\nUsuario 'claud' NAO encontrado!")
    print("Usuarios disponiveis:")
    for u in users:
        print(f"  - {u.username}")

print("\n" + "=" * 80)
