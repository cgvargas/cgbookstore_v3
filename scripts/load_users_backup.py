"""
Script para carregar usuários e prateleiras do backup.
"""
import os
import json
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import BookShelf
from core.models import Book
from django.core.cache import cache

print("👥 Carregando usuários do backup...")

# Carregar dados
with open('backup_supabase_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Carregar usuários
users_data = [d for d in data if d['model'] == 'auth.user']
print(f"   Usuários no backup: {len(users_data)}")

user_map = {}  # username -> user
created = 0

for u in users_data:
    f = u['fields']
    pk = u.get('pk')  # May not exist in this format
    
    user, was_created = User.objects.get_or_create(
        username=f['username'],
        defaults={
            'email': f.get('email', ''),
            'is_staff': f.get('is_staff', False),
            'is_superuser': f.get('is_superuser', False),
            'first_name': f.get('first_name', ''),
            'last_name': f.get('last_name', ''),
        }
    )
    user_map[f['username']] = user  # Map by username instead
    if was_created:
        created += 1

print(f"   ✓ Criados: {created}")

# Carregar prateleiras
print("\n🗄️ Carregando prateleiras do backup...")
shelves_data = [d for d in data if d['model'] == 'accounts.bookshelf']
print(f"   Prateleiras no backup: {len(shelves_data)}")

shelf_created = 0
shelf_skipped = 0
shelf_errors = 0

for s in shelves_data:
    try:
        f = s['fields']
        
        # O campo user pode ser um array com username, ex: ['claud']
        user_field = f.get('user')
        if isinstance(user_field, list) and user_field:
            username = user_field[0]
            user = user_map.get(username)
            if not user:
                user = User.objects.filter(username=username).first()
        else:
            user = User.objects.filter(pk=user_field).first()
        
        # Buscar livro
        book = Book.objects.filter(pk=f.get('book')).first()
        
        if not user or not book:
            shelf_skipped += 1
            continue
        
        # Criar prateleira se não existir
        shelf, was_created = BookShelf.objects.get_or_create(
            user=user,
            book=book,
            shelf_type=f.get('shelf_type', 'to_read'),
            defaults={
                'notes': f.get('notes', ''),
                'is_public': f.get('is_public', False),
            }
        )
        
        if was_created:
            shelf_created += 1
            
    except Exception as e:
        shelf_errors += 1
        print(f"   ❌ Erro: {str(e)[:50]}")

print(f"\n📊 Resultado:")
print(f"   ✓ Prateleiras criadas: {shelf_created}")
print(f"   ○ Puladas: {shelf_skipped}")
print(f"   ✗ Erros: {shelf_errors}")

# Estatísticas finais
cache.clear()
print(f"\n📈 Banco de dados final:")
print(f"   Usuários: {User.objects.count()}")
print(f"   Livros: {Book.objects.count()}")
print(f"   Prateleiras: {BookShelf.objects.count()}")

# Mostrar prateleiras por usuário
print(f"\n📖 Prateleiras por usuário:")
for user in User.objects.all()[:5]:
    count = BookShelf.objects.filter(user=user).count()
    if count > 0:
        print(f"   {user.username}: {count} livros")

print("\n✅ Carregamento concluído!")
