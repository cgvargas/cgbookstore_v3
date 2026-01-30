import os
import sys
sys.path.insert(0, r'c:\ProjectDjango\cgbookstore_v3')
os.environ['DJANGO_SETTINGS_MODULE'] = 'cgbookstore.settings'

import django
django.setup()

from core.models import Section

print("=== Seções de Vídeo ===\n")
sections = Section.objects.filter(active=True, content_type='videos').order_by('order')
for s in sections:
    print(f"📹 {s.title}")
    print(f"   Layout: {s.layout} ({s.get_layout_display()})")
    print(f"   Itens por Linha: {s.items_per_row}")
    print(f"   Items: {s.items.filter(active=True).count()}")
    print()
