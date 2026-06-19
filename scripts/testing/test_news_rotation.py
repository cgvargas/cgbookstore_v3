"""
Script de teste para validar a implementação do signal de rotação de notícias.
Execute com: python test_news_signal.py
"""
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from core.models import Section, SectionItem
from news.models import Article
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save

print("=" * 60)
print("TESTE: Rotação Automática de Notícias")
print("=" * 60)

# 1. Verificar seções de notícias
news_sections = Section.objects.filter(content_type='news', active=True)
print(f"\n[1] Seções de notícias ativas: {news_sections.count()}")
for s in news_sections:
    items = s.items.filter(active=True).order_by('order')
    print(f"\n  Seção: \"{s.title}\"")
    print(f"  max_items={s.max_items} | itens ativos={items.count()}")
    for item in items:
        try:
            art = Article.objects.get(id=item.object_id)
            print(f"    order={item.order}: {art.title[:60]}")
        except Article.DoesNotExist:
            print(f"    order={item.order}: [artigo deletado]")

# 2. Verificar se o signal está registrado
print("\n[2] Verificando signals registrados...")
all_receivers = post_save.receivers
print(f"  Total de receivers do post_save: {len(all_receivers)}")

# Testar importação do signal manualmente
try:
    import news.signals
    print("  [OK] news.signals importado com sucesso")
except Exception as e:
    print(f"  [ERRO] Falha ao importar news.signals: {e}")

# 3. Verificar campo max_items no model Section
print("\n[3] Verificando campo max_items...")
from django.db import connection
cursor = connection.cursor()
cursor.execute("PRAGMA table_info(core_section)")
columns = [row[1] for row in cursor.fetchall()]
if 'max_items' in columns:
    print("  [OK] Campo max_items existe na tabela core_section")
else:
    print("  [ERRO] Campo max_items NÃO encontrado na tabela!")

print("\n" + "=" * 60)
print("Teste concluído!")
