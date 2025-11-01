# -*- coding: utf-8 -*-
"""
Limpar Cache de Recomendações

Execute no Django shell para limpar o cache:
>>> exec(open('clear_recommendations_cache.py', encoding='utf-8').read())
"""

print("\n" + "="*80)
print("LIMPANDO CACHE DE RECOMENDAÇÕES")
print("="*80 + "\n")

from django.core.cache import cache
from django.contrib.auth.models import User

# Limpar TODOS os caches de recomendações
print("1. Limpando cache geral...")

# Padrões de cache a limpar
cache_patterns = [
    'pref_hybrid_rec:*',
    'pref_collab:*',
    'hybrid_rec:*',
    'collab_filter:*',
    'gemini_rec:*'
]

# Django cache não tem delete_pattern nativo, então vamos limpar por usuário
users = User.objects.all()

cleared_count = 0

for user in users:
    # Cache keys específicos do sistema ponderado
    keys_to_clear = [
        f'pref_hybrid_rec:{user.id}:6',
        f'pref_hybrid_rec:{user.id}:10',
        f'pref_collab:similar_users:{user.id}',
        f'hybrid_rec:{user.id}:6',
        f'hybrid_rec:{user.id}:10',
        f'collab_filter:similar_users:{user.id}',
        f'gemini_rec:{user.id}:6',
        f'gemini_rec:{user.id}:10',
    ]

    for key in keys_to_clear:
        if cache.delete(key):
            cleared_count += 1
            print(f"  ✓ Cleared: {key}")

print(f"\n2. Total de caches limpos: {cleared_count}")

# Opção alternativa: limpar TODO o cache
print("\n3. Limpando TODO o cache do Django...")
cache.clear()
print("  ✓ Cache completamente limpo!")

print("\n" + "="*80)
print("✅ CACHE LIMPO COM SUCESSO!")
print("="*80)
print("\nPRÓXIMOS PASSOS:")
print("  1. Reiniciar o servidor Django")
print("  2. Fazer logout e login novamente")
print("  3. Acessar a página de recomendações")
print("  4. O sistema irá gerar recomendações NOVAS (sem cache)")
print("="*80 + "\n")
