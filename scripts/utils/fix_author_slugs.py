"""
Script para corrigir slugs vazios de autores.
"""
import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from core.models import Author
from django.utils.text import slugify

# Verificar autores com slug problemático
authors_sem_slug = Author.objects.filter(slug__isnull=True) | Author.objects.filter(slug='')
print(f"Autores com slug vazio ou None: {authors_sem_slug.count()}")

if authors_sem_slug.exists():
    print("\nAutores problemáticos:")
    for author in authors_sem_slug:
        print(f"  ID {author.id}: \"{author.name}\" - slug=\"{author.slug}\"")

    # Corrigir slugs
    print("\nCorrigindo slugs...")
    for author in authors_sem_slug:
        if not author.slug:
            new_slug = slugify(author.name)
            author.slug = new_slug
            author.save()
            print(f"  ✅ ID {author.id}: novo slug = \"{new_slug}\"")

    print(f"\n✅ {authors_sem_slug.count()} slugs corrigidos!")
else:
    print("✅ Todos os autores têm slug válido!")

# Verificar duplicatas
from django.db.models import Count
duplicates = Author.objects.values('slug').annotate(count=Count('id')).filter(count__gt=1)
if duplicates.exists():
    print(f"\n⚠️  Encontrados {duplicates.count()} slugs duplicados:")
    for dup in duplicates:
        print(f"  - Slug \"{dup['slug']}\": {dup['count']} ocorrências")
else:
    print("\n✅ Nenhum slug duplicado!")
