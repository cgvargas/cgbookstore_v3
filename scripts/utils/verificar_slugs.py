"""
Script para verificar e corrigir slugs vazios ou None.
"""
import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from core.models import Book
from django.utils.text import slugify

# Verificar livros com slug problemático
books_sem_slug = Book.objects.filter(slug__isnull=True) | Book.objects.filter(slug='')
print(f"Livros com slug vazio ou None: {books_sem_slug.count()}")

if books_sem_slug.exists():
    print("\nLivros problemáticos:")
    for book in books_sem_slug:
        print(f"  ID {book.id}: \"{book.title}\" - slug=\"{book.slug}\"")

    # Corrigir slugs
    print("\nCorrigindo slugs...")
    for book in books_sem_slug:
        if not book.slug:
            new_slug = slugify(book.title)
            book.slug = new_slug
            book.save()
            print(f"  ✅ ID {book.id}: novo slug = \"{new_slug}\"")

    print(f"\n✅ {books_sem_slug.count()} slugs corrigidos!")
else:
    print("✅ Todos os livros têm slug válido!")

# Verificar duplicatas
from django.db.models import Count
duplicates = Book.objects.values('slug').annotate(count=Count('id')).filter(count__gt=1)
if duplicates.exists():
    print(f"\n⚠️  Encontrados {duplicates.count()} slugs duplicados:")
    for dup in duplicates:
        print(f"  - Slug \"{dup['slug']}\": {dup['count']} ocorrências")
else:
    print("\n✅ Nenhum slug duplicado!")
