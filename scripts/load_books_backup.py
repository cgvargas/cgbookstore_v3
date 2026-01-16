"""
Script para carregar apenas os livros do backup.
"""
import os
import json
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from core.models import Book, Category, Author
from django.core.cache import cache

print("📚 Carregando livros do backup...")

# Carregar dados
with open('backup_supabase_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

books = [d for d in data if d['model'] == 'core.book']
print(f"   Livros no backup: {len(books)}")

# Desabilitar signals temporariamente para acelerar
from django.db.models.signals import post_save
from core.models import Book

# Carregar livros
created = 0
updated = 0
errors = 0

for b in books:
    try:
        pk = b['pk']
        f = b['fields']
        
        # Skip if book already exists
        if Book.objects.filter(pk=pk).exists():
            updated += 1
            continue
            
        # Skip if slug already exists
        slug = f.get('slug', '')
        if Book.objects.filter(slug=slug).exists():
            slug = f"{slug}-{pk}"  # Make unique
        
        cat = Category.objects.filter(pk=f.get('category')).first()
        auth = Author.objects.filter(pk=f.get('author')).first()
        
        Book.objects.create(
            pk=pk,
            title=f.get('title', ''),
            slug=slug,
            category=cat,
            author=auth,
            description=f.get('description', ''),
            publication_date=f.get('publication_date') or '2020-01-01',
            cover_image=f.get('cover_image', ''),
            page_count=f.get('page_count'),
        )
        created += 1
            
    except Exception as e:
        errors += 1
        if errors <= 3:
            print(f"   ❌ Erro em {f.get('title', 'unknown')}: {str(e)[:50]}")

print(f"\n📊 Resultado:")
print(f"   ✓ Criados: {created}")
print(f"   ↻ Atualizados: {updated}")
print(f"   ✗ Erros: {errors}")

# Também carregar BookShelves
print("\n🗄️ Carregando prateleiras...")

from accounts.models import BookShelf
from django.contrib.auth.models import User

shelves = [d for d in data if d['model'] == 'accounts.bookshelf']
print(f"   Prateleiras no backup: {len(shelves)}")

shelf_created = 0
shelf_errors = 0

for s in shelves:
    try:
        pk = s['pk']
        f = s['fields']
        
        user = User.objects.filter(pk=f.get('user')).first()
        book = Book.objects.filter(pk=f.get('book')).first()
        
        if user and book:
            obj, was_created = BookShelf.objects.update_or_create(
                pk=pk,
                defaults={
                    'user': user,
                    'book': book,
                    'shelf_type': f.get('shelf_type', 'to_read'),
                    'notes': f.get('notes', ''),
                    'is_public': f.get('is_public', False),
                }
            )
            if was_created:
                shelf_created += 1
    except Exception as e:
        shelf_errors += 1

print(f"   ✓ Prateleiras criadas: {shelf_created}")
print(f"   ✗ Erros: {shelf_errors}")

# Estatísticas finais
cache.clear()
print(f"\n📈 Banco de dados final:")
print(f"   Livros: {Book.objects.count()}")
print(f"   Prateleiras: {BookShelf.objects.count()}")

print("\n✅ Carregamento concluído!")
