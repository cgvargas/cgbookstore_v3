#!/usr/bin/env python
"""Script para limpar o cache da home"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from django.core.cache import cache

print("Limpando cache da home...")
result = cache.delete('home_full_context')

if result:
    print("SUCESSO - Cache limpo!")
else:
    print("INFO - Nenhum cache encontrado (ja estava limpo)")

print("\nRecarregue a pagina principal para ver o banner!")
print("Pressione Ctrl+F5 para forcar atualizacao")
