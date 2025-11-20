"""
Script de diagnóstico de performance do CG Bookstore.
Identifica gargalos e sugere otimizações.
Execute: python scripts/diagnose_performance.py
"""
import os
import sys
import django
import time

# Adicionar diretório raiz do projeto ao PYTHONPATH
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from django.conf import settings
from django.core.cache import cache
from django.db import connection
from core.models import Section, Book, Banner

print("=" * 70)
print("DIAGNÓSTICO DE PERFORMANCE - CG Bookstore v3")
print("=" * 70)

# 1. Verificar DEBUG mode
print("\n🔍 1. CONFIGURAÇÃO DEBUG")
print(f"   DEBUG = {settings.DEBUG}")
if settings.DEBUG:
    print("   ⚠️  ATENÇÃO: DEBUG=True pode causar MUITA lentidão!")
    print("   📝 Solução: No .env, defina DEBUG=False para produção")
else:
    print("   ✅ DEBUG=False (otimizado)")

# 2. Verificar Redis/Cache
print("\n🔍 2. CACHE (REDIS)")
try:
    cache.set('performance_test', 'ok', timeout=10)
    result = cache.get('performance_test')
    if result == 'ok':
        print("   ✅ Redis funcionando corretamente")

        # Testar velocidade
        start = time.time()
        for i in range(100):
            cache.set(f'test_{i}', i, timeout=10)
        elapsed = (time.time() - start) * 1000
        print(f"   ⚡ Velocidade: {elapsed:.2f}ms para 100 operações")

        if elapsed > 100:
            print(f"   ⚠️  Redis lento! Verifique se o servidor está rodando")
    else:
        print("   ❌ Redis não está funcionando corretamente")
except Exception as e:
    print(f"   ❌ Erro no Redis: {e}")
    print("   📝 Solução: Inicie o Redis com 'redis-server'")

# 3. Verificar quantidade de queries
print("\n🔍 3. QUERIES DO BANCO DE DADOS")

# Resetar contador de queries
connection.queries_log.clear()

# Simular carregamento da home
from core.views import home
from django.test import RequestFactory
factory = RequestFactory()
request = factory.get('/')
request.user = None  # Usuário anônimo

start_queries = len(connection.queries)
try:
    # Buscar seções (simula parte da home)
    sections = list(Section.objects.filter(active=True).select_related().prefetch_related('items')[:5])
    end_queries = len(connection.queries)

    queries_count = end_queries - start_queries
    print(f"   Queries para carregar 5 seções: {queries_count}")

    if queries_count > 20:
        print(f"   ⚠️  MUITAS queries! Pode estar com N+1 problem")
        print(f"   📝 Solução: Otimizar com select_related/prefetch_related")
    else:
        print(f"   ✅ Queries otimizadas")
except Exception as e:
    print(f"   ❌ Erro ao testar queries: {e}")

# 4. Verificar tamanho do banco
print("\n🔍 4. TAMANHO DO BANCO DE DADOS")
try:
    books_count = Book.objects.count()
    sections_count = Section.objects.count()
    banners_count = Banner.objects.count()

    print(f"   📚 Livros: {books_count}")
    print(f"   📑 Seções: {sections_count}")
    print(f"   🎨 Banners: {banners_count}")

    if books_count > 10000:
        print(f"   ⚠️  Muitos livros! Considere paginação e lazy loading")
except Exception as e:
    print(f"   ❌ Erro: {e}")

# 5. Verificar middlewares
print("\n🔍 5. MIDDLEWARES")
print(f"   Total de middlewares: {len(settings.MIDDLEWARE)}")
for middleware in settings.MIDDLEWARE:
    print(f"   - {middleware}")

# 6. Verificar configuração de recomendações
print("\n🔍 6. SISTEMA DE RECOMENDAÇÕES")
rec_config = settings.RECOMMENDATIONS_CONFIG
print(f"   Cache Timeout: {rec_config['CACHE_TIMEOUT']}s ({rec_config['CACHE_TIMEOUT']/3600:.1f}h)")
print(f"   Similarity Cache: {rec_config['SIMILARITY_CACHE_TIMEOUT']}s ({rec_config['SIMILARITY_CACHE_TIMEOUT']/3600:.1f}h)")

if rec_config['CACHE_TIMEOUT'] < 3600:
    print(f"   ⚠️  Cache curto pode causar recálculos frequentes")
else:
    print(f"   ✅ Cache configurado adequadamente")

# Resumo
print("\n" + "=" * 70)
print("RESUMO E RECOMENDAÇÕES")
print("=" * 70)

recommendations = []

if settings.DEBUG:
    recommendations.append("🔴 CRÍTICO: Desative DEBUG=False no .env para produção")

print("\n💡 DICAS DE OTIMIZAÇÃO:")
print("   1. Use 'python manage.py runserver --noreload' para desenvolvimento")
print("   2. Mantenha o Redis rodando para cache de recomendações")
print("   3. Limpe cache antigo: python manage.py shell -> cache.clear()")
print("   4. Use Ctrl+Shift+R no navegador para limpar cache do browser")
print("   5. Monitore queries lentas com Django Debug Toolbar (dev only)")

if recommendations:
    print("\n⚠️  AÇÕES NECESSÁRIAS:")
    for rec in recommendations:
        print(f"   {rec}")
else:
    print("\n✅ Sistema configurado adequadamente!")

print("\n" + "=" * 70)
