"""
Script para normalizar as ordens dos itens nas seções de notícias existentes.
Garante que cada item tenha uma order única e sequencial.
Execute com: python fix_news_orders.py
"""
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from core.models import Section, SectionItem
from news.models import Article
from django.core.cache import cache

print("=" * 60)
print("FIX: Normalizando ordens dos itens nas seções de notícias")
print("=" * 60)

news_sections = Section.objects.filter(content_type='news', active=True)
print(f"\nSeções de notícias ativas: {news_sections.count()}")

for section in news_sections:
    items = list(SectionItem.objects.filter(section=section, active=True).order_by('created_at'))
    print(f"\nSeção: \"{section.title}\" | {len(items)} itens")
    
    for i, item in enumerate(items):
        old_order = item.order
        item.order = i
        item.save(update_fields=['order'])
        try:
            art = Article.objects.get(id=item.object_id)
            print(f"  [{i}] order {old_order} -> {i}: {art.title[:60]}")
        except Article.DoesNotExist:
            print(f"  [{i}] order {old_order} -> {i}: [artigo deletado]")

# Invalidar cache da home
cache.delete('home_full_context')
print("\n[OK] Cache da home invalidado.")
print("\n" + "=" * 60)
print("Normalização concluída! Agora as ordens são sequenciais.")
print("O artigo com order=0 é o PRIMEIRO card (mais recente).")
print("=" * 60)
