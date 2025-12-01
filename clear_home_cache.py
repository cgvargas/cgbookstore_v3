#!/usr/bin/env python
"""Script para limpar o cache da home"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from django.core.cache import cache

print("🧹 Limpando cache da home...")
result = cache.delete('home_full_context')

if result:
    print("✅ Cache limpo com sucesso!")
else:
    print("ℹ️  Nenhum cache encontrado (já estava limpo)")

print("\n🔄 Recarregue a página principal para ver o banner!")
