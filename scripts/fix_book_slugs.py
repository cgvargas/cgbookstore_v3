"""
Script para corrigir slugs com caracteres acentuados nos livros.
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from django.utils.text import slugify
from core.models import Book

print("🔧 Corrigindo slugs de livros...")

fixed = 0
for book in Book.objects.all():
    # Gerar slug ASCII-only
    new_slug = slugify(book.title, allow_unicode=False)
    
    # Se o slug mudou, verificar se já existe
    if new_slug != book.slug:
        # Garantir unicidade
        base_slug = new_slug
        counter = 1
        while Book.objects.filter(slug=new_slug).exclude(pk=book.pk).exists():
            new_slug = f"{base_slug}-{counter}"
            counter += 1
        
        print(f"   {book.slug} -> {new_slug}")
        book.slug = new_slug
        book.save(update_fields=['slug'])
        fixed += 1

print(f"\n✓ Fixed: {fixed} slugs")
