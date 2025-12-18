# scripts/create_featured_author.py
"""Script para criar configuração inicial do autor em destaque (Tolkien)"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from core.models import Author, FeaturedAuthorSettings

def main():
    # Buscar autor Tolkien
    author = Author.objects.filter(name__icontains='tolkien').first()
    
    if not author:
        print("❌ Autor Tolkien não encontrado!")
        return
    
    print(f"✓ Autor encontrado: {author.name}")
    
    # Criar ou atualizar settings
    settings, created = FeaturedAuthorSettings.objects.get_or_create(
        author=author,
        defaults={
            'is_active': True,
            'home_title': 'J.R.R. Tolkien',
            'home_subtitle': 'Explore o Mundo de',
            'home_description': 'Descubra a Terra-média através das obras do mestre da fantasia',
            'home_button_text': 'Explorar Mundo de Tolkien',
            'home_button_icon': 'fa-compass',
            'page_title': 'Explore o Mundo de J.R.R. Tolkien',
            'page_description': 'Mergulhe nas obras do mestre da fantasia que criou a Terra-média e encantou gerações de leitores.',
            'stat_badge_1': 'Épicos',
            'stat_badge_2': 'Lendários',
        }
    )
    
    if created:
        print(f"✓ FeaturedAuthorSettings CRIADO para {author.name}")
    else:
        print(f"✓ FeaturedAuthorSettings já existe para {author.name}")
    
    print(f"  - Ativo: {settings.is_active}")
    print(f"  - Título: {settings.home_title}")
    print(f"  - Botão: {settings.home_button_text}")

if __name__ == '__main__':
    main()
