"""
Script para criar o Universo Literário de Tolkien no banco de dados.
Execute com: python manage.py shell < scripts/create_tolkien_universe.py
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from core.models import LiteraryUniverse, Author

# Buscar autor Tolkien
try:
    tolkien = Author.objects.get(name__icontains='tolkien')
    print(f"✅ Autor encontrado: {tolkien.name} (ID: {tolkien.id})")
except Author.DoesNotExist:
    print("❌ Autor Tolkien não encontrado!")
    exit(1)

# Criar universo literário
universe, created = LiteraryUniverse.objects.get_or_create(
    slug='tolkien',
    defaults={
        'title': 'Mundo de Tolkien',
        'author': tolkien,
        'is_active': True,
        'show_in_menu': True,
        'display_order': 1,
        'theme_color_primary': '#f4d03f',
        'theme_color_secondary': '#c9a227',
        'hero_icon': 'fa-ring',
        'page_title': 'Mundo de Tolkien',
        'page_subtitle': 'Explore o Mundo de',
        'page_description': 'Mergulhe no universo fantástico criado por J.R.R. Tolkien. Descubra a Terra-média, seus habitantes, línguas e a mitologia que inspirou gerações de leitores e escritores.',
        'meta_title': 'Mundo de Tolkien - CGBookStore',
        'meta_description': 'Explore o universo literário de J.R.R. Tolkien. Livros, história e curiosidades sobre a Terra-média.',
    }
)

if created:
    print(f"✅ Universo criado: {universe.title} (ID: {universe.id})")
else:
    print(f"ℹ️ Universo já existe: {universe.title} (ID: {universe.id})")

print(f"\n🔗 Acesse no admin: /admin/core/literaryuniverse/{universe.id}/change/")
print(f"🌐 Página pública: /universo/{universe.slug}/")
