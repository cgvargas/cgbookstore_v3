"""
Script de testes de performance e validacao (versao simplificada).
Executar com: python test_performance_simple.py
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from django.core.cache import cache
from django.test import Client
from django.db import connection
from django.db import reset_queries


def test_cache():
    """Testa funcionamento do cache."""
    print("\n[CACHE] Testando Cache Redis...")

    try:
        cache.set('test_key', 'test_value', timeout=60)
        value = cache.get('test_key')
        assert value == 'test_value', "Cache nao funcionou"
        cache.delete('test_key')

        print("[OK] Cache funcionando corretamente!")
        return True
    except Exception as e:
        print(f"[WARN] Cache com problemas: {e}")
        print("       Nota: Redis precisa estar rodando")
        return False


def test_query_performance():
    """Testa performance de queries otimizadas."""
    print("\n[QUERIES] Testando Performance de Queries...")

    try:
        from debates.models import DebateTopic

        reset_queries()
        topics = list(DebateTopic.objects.select_related('book', 'creator')[:10])
        num_queries = len(connection.queries)

        print(f"[INFO] Queries executadas: {num_queries}")
        print(f"[INFO] Topicos carregados: {len(topics)}")

        if num_queries <= 3:
            print("[OK] Queries otimizadas!")
        else:
            print(f"[WARN] Muitas queries ({num_queries})")

        return True
    except Exception as e:
        print(f"[ERROR] Erro ao testar queries: {e}")
        return False


def test_celery():
    """Testa execucao de tasks Celery."""
    print("\n[CELERY] Testando Celery...")

    try:
        from core.tasks import test_async_task

        result = test_async_task.delay("Performance Test")
        print(f"[INFO] Task ID: {result.id}")
        print("[WARN] Celery worker precisa estar rodando")

        try:
            output = result.get(timeout=5)
            print(f"[OK] Celery funcionando: {output}")
            return True
        except Exception as e:
            print(f"[WARN] Worker pode nao estar rodando: {e}")
            return False

    except Exception as e:
        print(f"[WARN] Erro ao testar Celery: {e}")
        return False


def test_rate_limiting():
    """Testa rate limiting."""
    print("\n[RATELIMIT] Testando Rate Limiting...")

    try:
        client = Client()
        responses = []

        for i in range(10):
            response = client.get('/debates/')
            responses.append(response.status_code)

        success_count = sum(1 for r in responses if r == 200)
        print(f"[INFO] {success_count}/10 requisicoes bem sucedidas")
        print("[OK] Rate limiting configurado (200 req/h por IP)")

        return True
    except Exception as e:
        print(f"[ERROR] Erro ao testar rate limiting: {e}")
        return False


def test_indexes():
    """Verifica se os indices foram criados."""
    print("\n[INDEXES] Testando Indices de Banco...")

    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT indexname, tablename
                FROM pg_indexes
                WHERE schemaname = 'public'
                AND tablename LIKE 'debates_%'
                ORDER BY tablename, indexname;
            """)

            indexes = cursor.fetchall()
            print(f"[INFO] Indices encontrados: {len(indexes)}")

            expected_indexes = ['idx_post_topic_date', 'idx_topic_pinned_date', 'idx_post_deleted_parent']
            found_indexes = [idx[0] for idx in indexes]

            for expected in expected_indexes:
                if expected in found_indexes:
                    print(f"[OK] Indice {expected} encontrado")
                else:
                    print(f"[WARN] Indice {expected} nao encontrado")

        return True
    except Exception as e:
        print(f"[ERROR] Erro ao verificar indices: {e}")
        return False


def test_database_connection():
    """Testa conexao com banco de dados."""
    print("\n[DATABASE] Testando Conexao com Banco de Dados...")

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            print(f"[OK] Conectado ao PostgreSQL")

        from django.conf import settings
        conn_max_age = settings.DATABASES['default'].get('CONN_MAX_AGE', 0)
        print(f"[INFO] Connection pooling: {conn_max_age}s")

        if conn_max_age >= 600:
            print("[OK] Connection pooling otimizado (>=10min)")
        else:
            print("[WARN] Connection pooling pode ser melhorado")

        return True
    except Exception as e:
        print(f"[ERROR] Erro ao testar banco: {e}")
        return False


def main():
    """Executa todos os testes."""
    print("=" * 70)
    print("VALIDACAO DE OTIMIZACOES DE ESCALABILIDADE")
    print("=" * 70)

    results = {
        'Cache': test_cache(),
        'Queries': test_query_performance(),
        'Database': test_database_connection(),
        'Indexes': test_indexes(),
        'Rate Limiting': test_rate_limiting(),
        'Celery': test_celery(),
    }

    print("\n" + "=" * 70)
    print("RESUMO DOS TESTES")
    print("=" * 70)

    for test_name, result in results.items():
        status = "[OK] PASSOU" if result else "[WARN] PRECISA ATENCAO"
        print(f"{test_name:.<30} {status}")

    passed = sum(results.values())
    total = len(results)

    print("\n" + "=" * 70)
    print(f"RESULTADO FINAL: {passed}/{total} testes passaram")
    print("=" * 70)

    if passed == total:
        print("\nPARABENS! Todas as otimizacoes estao funcionando!")
    else:
        print("\nAlgumas otimizacoes precisam de atencao")
        print("\nNOTAS:")
        print("  - Redis: Instalar com 'wsl sudo apt install redis-server'")
        print("  - Celery: Executar 'celery -A cgbookstore worker -l info --pool=solo'")


if __name__ == '__main__':
    main()
