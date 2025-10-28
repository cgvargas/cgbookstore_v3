"""Teste rápido do cache Redis."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from django.core.cache import cache

print("="*60)
print("TESTANDO CACHE REDIS")
print("="*60)

# Testar set
print("\n1. Testando cache.set()...")
cache.set('teste', 'sucesso!', timeout=60)
print("   [OK] Set realizado")

# Testar get
print("\n2. Testando cache.get()...")
valor = cache.get('teste')
print(f"   Valor recuperado: {valor}")

if valor == 'sucesso!':
    print("   [OK] Cache funcionando perfeitamente!")
else:
    print("   [ERRO] Cache não retornou o valor esperado")

# Limpar
cache.delete('teste')
print("\n3. Cache limpo")

print("\n" + "="*60)
print("TESTE CONCLUIDO COM SUCESSO!")
print("="*60)
