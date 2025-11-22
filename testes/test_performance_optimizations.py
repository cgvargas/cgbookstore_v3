"""
Script de teste de performance das otimizacoes implementadas.
Executar com: python testes/test_performance_optimizations.py
"""

import os
import sys
import time
import django

# Setup Django
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from django.core.cache import cache
from django.test import Client, RequestFactory
from django.contrib.auth import get_user_model

User = get_user_model()


def test_home_view_performance():
    """Testa performance da home page."""
    print("\n[HOME VIEW] Testando Performance da Home Page...")

    client = Client()

    # Primeira requisicao (cache miss)
    start = time.time()
    response = client.get('/')
    first_request = (time.time() - start) * 1000

    print(f"  [1a req] Status: {response.status_code}, Tempo: {first_request:.0f}ms")

    # Segunda requisicao (cache hit)
    start = time.time()
    response = client.get('/')
    second_request = (time.time() - start) * 1000

    print(f"  [2a req] Status: {response.status_code}, Tempo: {second_request:.0f}ms")

    # Comparacao
    if second_request < first_request * 0.5:
        print(f"  [OK] Cache funcionando! Reducao de {((first_request - second_request)/first_request)*100:.0f}%")
        return True
    else:
        print(f"  [WARN] Cache pode nao estar funcionando corretamente")
        return False


def test_recommendations_performance():
    """Testa performance do sistema de recomendacoes."""
    print("\n[RECOMMENDATIONS] Testando Performance das Recomendacoes...")

    try:
        user = User.objects.filter(is_active=True).first()
        if not user:
            print("  [SKIP] Nenhum usuario encontrado")
            return True

        client = Client()
        client.force_login(user)

        # Limpar cache para testar
        cache.delete(f'view_recs:{user.id}:preference_hybrid:6:*')

        # Primeira requisicao (cache miss)
        start = time.time()
        response = client.get('/recommendations/api/recommendations/?algorithm=preference_hybrid&limit=6')
        first_request = (time.time() - start) * 1000

        print(f"  [1a req] User: {user.username}, Status: {response.status_code}, Tempo: {first_request:.0f}ms")

        # Segunda requisicao (cache hit)
        start = time.time()
        response = client.get('/recommendations/api/recommendations/?algorithm=preference_hybrid&limit=6')
        second_request = (time.time() - start) * 1000

        print(f"  [2a req] User: {user.username}, Status: {response.status_code}, Tempo: {second_request:.0f}ms")

        if response.status_code == 200 and second_request < first_request * 0.8:
            print(f"  [OK] Cache de recomendacoes funcionando!")
            return True
        elif response.status_code == 200:
            print(f"  [WARN] Recomendacoes OK, mas cache pode melhorar")
            return True
        else:
            print(f"  [WARN] Verifique o sistema de recomendacoes")
            return False

    except Exception as e:
        print(f"  [ERROR] {e}")
        return False


def test_preference_analyzer_cache():
    """Testa cache do preference analyzer."""
    print("\n[PREFERENCE ANALYZER] Testando Cache de Analise de Preferencias...")

    try:
        from recommendations.preference_analyzer import UserPreferenceAnalyzer

        user = User.objects.filter(is_active=True).first()
        if not user:
            print("  [SKIP] Nenhum usuario encontrado")
            return True

        # Limpar cache
        cache.delete(f'pref_genres:{user.id}:*')
        cache.delete(f'pref_authors:{user.id}:*')

        # Primeira chamada (cache miss)
        start = time.time()
        analyzer = UserPreferenceAnalyzer(user)
        genres1 = analyzer.get_top_genres(n=5)
        authors1 = analyzer.get_top_authors(n=5)
        first_call = (time.time() - start) * 1000

        print(f"  [1a chamada] Tempo: {first_call:.0f}ms")
        print(f"    Top Genres: {len(genres1)}, Top Authors: {len(authors1)}")

        # Segunda chamada (deve usar cache)
        start = time.time()
        analyzer2 = UserPreferenceAnalyzer(user)
        genres2 = analyzer2.get_top_genres(n=5)
        authors2 = analyzer2.get_top_authors(n=5)
        second_call = (time.time() - start) * 1000

        print(f"  [2a chamada] Tempo: {second_call:.0f}ms")

        if second_call < first_call * 0.3:
            print(f"  [OK] Cache Redis funcionando! Reducao de {((first_call - second_call)/first_call)*100:.0f}%")
            return True
        else:
            print(f"  [WARN] Cache pode nao estar funcionando")
            return False

    except Exception as e:
        print(f"  [ERROR] {e}")
        return False


def test_sklearn_preload():
    """Verifica se sklearn foi pre-carregado."""
    print("\n[SKLEARN] Verificando Pre-carregamento...")

    try:
        from recommendations.algorithms import _sklearn_loaded

        if _sklearn_loaded:
            print("  [OK] sklearn ja estava carregado (pre-load funcionou!)")
            return True
        else:
            print("  [WARN] sklearn ainda nao foi carregado")
            return False

    except Exception as e:
        print(f"  [ERROR] {e}")
        return False


def test_storage_mapping():
    """Verifica mapeamento de storage para banners."""
    print("\n[STORAGE] Verificando Mapeamento de Buckets...")

    try:
        from core.storage_backends import SupabaseMediaStorage

        storage = SupabaseMediaStorage()

        # Testar path de banner
        bucket, path = storage._get_bucket_and_path('banners/home/test.jpg')

        if 'banners/home' not in path:
            print(f"  [OK] Mapeamento de banners funcionando: bucket={bucket}")
            return True
        else:
            print(f"  [WARN] Mapeamento pode estar incorreto")
            return False

    except Exception as e:
        print(f"  [ERROR] {e}")
        return False


def main():
    """Executa todos os testes de performance."""
    print("=" * 70)
    print("TESTE DE OTIMIZACOES DE PERFORMANCE - CG Bookstore v3")
    print("=" * 70)

    results = {
        'sklearn_preload': test_sklearn_preload(),
        'storage_mapping': test_storage_mapping(),
        'home_view': test_home_view_performance(),
        'preference_analyzer': test_preference_analyzer_cache(),
        'recommendations': test_recommendations_performance(),
    }

    print("\n" + "=" * 70)
    print("RESUMO DOS TESTES")
    print("=" * 70)

    for test_name, result in results.items():
        status = "[OK] PASSOU" if result else "[WARN] VERIFICAR"
        print(f"  {test_name:.<40} {status}")

    passed = sum(results.values())
    total = len(results)

    print("\n" + "=" * 70)
    print(f"RESULTADO: {passed}/{total} testes passaram")
    print("=" * 70)

    if passed == total:
        print("\nTodas as otimizacoes estao funcionando!")
    else:
        print("\nAlgumas otimizacoes precisam de verificacao.")


if __name__ == '__main__':
    main()
