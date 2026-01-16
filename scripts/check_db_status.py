"""
Script para verificar estado do banco de dados local.
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Book, Author, Video
from accounts.models import BookShelf

print("=" * 50)
print("📊 BANCO DE DADOS LOCAL - STATUS")
print("=" * 50)

print(f"\n👥 Usuários: {User.objects.count()}")

print(f"\n📚 Livros: {Book.objects.count()}")
print(f"   - Com capa: {Book.objects.exclude(cover_image='').count()}")
print(f"   - Sem capa: {Book.objects.filter(cover_image='').count()}")

print(f"\n✍️ Autores: {Author.objects.count()}")
print(f"   - Com foto: {Author.objects.exclude(photo='').count()}")
print(f"   - Sem foto: {Author.objects.filter(photo='').count()}")

print(f"\n🎬 Vídeos: {Video.objects.count()}")

print(f"\n🗄️ Prateleiras: {BookShelf.objects.count()}")

# Mostrar usuários com mais prateleiras
print("\n📖 Top usuários com livros:")
for user in User.objects.all()[:5]:
    count = BookShelf.objects.filter(user=user).count()
    if count > 0:
        print(f"   - {user.username}: {count} livros")

print("\n" + "=" * 50)
print("✅ Verificação concluída!")
