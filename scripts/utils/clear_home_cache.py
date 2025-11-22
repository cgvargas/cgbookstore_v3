import os
import sys
import django

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from django.core.cache import cache

result = cache.delete('home_full_context')
print(f"Cache 'home_full_context' deleted: {result}")
