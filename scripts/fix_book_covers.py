"""
Script para atualizar capas de livros do backup.
"""
import os
import json
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from core.models import Book

print("🖼️ Atualizando capas de livros...")

# Carregar backup
with open('backup_supabase_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Mapear pk -> cover_image do backup
covers = {}
for b in data:
    if b['model'] == 'core.book':
        pk = b.get('pk')
        cover = b['fields'].get('cover_image', '')
        if pk and cover:
            covers[pk] = cover

print(f"   Capas no backup: {len(covers)}")

# Atualizar livros sem capa
updated = 0
for book in Book.objects.filter(cover_image=''):
    if book.pk in covers:
        book.cover_image = covers[book.pk]
        book.save(update_fields=['cover_image'])
        print(f"   ✓ {book.pk}: {book.title[:40]}")
        updated += 1

print(f"\n✓ Total atualizado: {updated}")
print(f"   Livros sem capa restantes: {Book.objects.filter(cover_image='').count()}")
