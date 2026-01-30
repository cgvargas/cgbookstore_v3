import os
import sys
sys.path.insert(0, r'c:\ProjectDjango\cgbookstore_v3')
os.environ['DJANGO_SETTINGS_MODULE'] = 'cgbookstore.settings'

import django
django.setup()

from core.models import Section

print("=== Seções Ativas ===\n")
sections = Section.objects.filter(active=True).order_by('order')
for s in sections:
    print(f"ID: {s.id}")
    print(f"  Title: {s.title}")
    print(f"  Layout: {s.layout}")
    print(f"  Order: {s.order}")
    print(f"  Items: {s.items.filter(active=True).count()}")
    print()
