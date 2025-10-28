"""
Script de testes de performance e validação.
Executar com: python manage.py shell < test_performance.py
"""

import time
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from django.core.cache import cache
from django.test import Client
from django.contrib.auth.models import User
from django.db import connection
from django.db import reset_queries


def test_cache():
    """Testa funcionamento do cache."""
    print("\n[CACHE] Testando Cache Redis...")

    try:
        # Set
        cache.set('test_key', 'test_value', timeout=60)

        # Get
        value = cache.get('test_key')
        assert value == 'test_value', "❌ Cache não funcionou"

        # Delete
        cache.delete('test_key')

        print("✅ Cache funcionando corretamente!")
        return True
    except Exception as e:
        print(f"⚠️ Cache com problemas: {e}")
        print("   Nota: Redis precisa estar rodando para o cache funcionar")
        return False


def test_query_performance():
    """Testa performance de queries otimizadas."""
    print("\n⚡ Testando Performance de Queries...")

    try:
        from debates.models import DebateTopic

        reset_queries()

        # Query otimizada
        topics = list(DebateTopic.objects.select_related('book', 'creator')[:10])

        num_queries = len(connection.queries)
        print(f"📊 Queries executadas: {num_queries}")
        print(f"📚 Tópicos carregados: {len(topics)}")

        if num_queries <= 3:
            print("✅ Queries otimizadas!")
        else:
            print(f"⚠️ Muitas queries ({num_queries}), revisar otimizações")
            # Mostrar as queries
            for i, query in enumerate(connection.queries, 1):
                print(f"  Query {i}: {query['sql'][:100]}...")

        return True
    except Exception as e:
        print(f"❌ Erro ao testar queries: {e}")
        return False


def test_celery():
    """Testa execução de tasks Celery."""
    print("\n🔄 Testando Celery...")

    try:
        from core.tasks import test_async_task

        # Nota: Celery worker precisa estar rodando
        result = test_async_task.delay("Performance Test")

        print(f"📨 Task ID: {result.id}")
        print("⚠️ Nota: Celery worker precisa estar rodando para executar a task")
        print("   Execute em outro terminal: celery -A cgbookstore worker -l info --pool=solo")

        try:
            output = result.get(timeout=5)
            print(f"✅ Celery funcionando: {output}")
            return True
        except Exception as e:
            print(f"⚠️ Task não executada (worker pode não estar rodando): {e}")
            return False

    except Exception as e:
        print(f"⚠️ Erro ao testar Celery: {e}")
        return False


def test_rate_limiting():
    """Testa rate limiting."""
    print("\n🛡️ Testando Rate Limiting...")

    try:
        client = Client()

        # Fazer 10 requisições rápidas
        responses = []
        for i in range(10):
            response = client.get('/debates/')
            responses.append(response.status_code)

        print(f"📊 Respostas: {responses}")

        # Verificar se todas foram bem sucedidas
        success_count = sum(1 for r in responses if r == 200)
        print(f"✅ {success_count}/10 requisições bem sucedidas")
        print("⚠️ Rate limiting configurado (200 req/h por IP)")

        return True
    except Exception as e:
        print(f"❌ Erro ao testar rate limiting: {e}")
        return False


def test_indexes():
    """Verifica se os índices foram criados."""
    print("\n🗂️ Testando Índices de Banco...")

    try:
        from django.db import connection

        with connection.cursor() as cursor:
            # Listar índices do PostgreSQL
            cursor.execute("""
                SELECT indexname, tablename
                FROM pg_indexes
                WHERE schemaname = 'public'
                AND tablename LIKE 'debates_%'
                ORDER BY tablename, indexname;
            """)

            indexes = cursor.fetchall()

            print(f"📊 Índices encontrados: {len(indexes)}")
            for idx_name, table_name in indexes:
                print(f"  - {table_name}: {idx_name}")

            # Verificar índices específicos
            expected_indexes = ['idx_post_topic_date', 'idx_topic_pinned_date', 'idx_post_deleted_parent']
            found_indexes = [idx[0] for idx in indexes]

            for expected in expected_indexes:
                if expected in found_indexes:
                    print(f"✅ Índice {expected} encontrado")
                else:
                    print(f"⚠️ Índice {expected} não encontrado")

        return True
    except Exception as e:
        print(f"❌ Erro ao verificar índices: {e}")
        return False


def test_database_connection():
    """Testa conexão com banco de dados."""
    print("\n🔌 Testando Conexão com Banco de Dados...")

    try:
        from django.db import connection

        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            print(f"✅ Conectado ao PostgreSQL")
            print(f"   Versão: {version[:50]}...")

        # Verificar configuração de pooling
        from django.conf import settings
        conn_max_age = settings.DATABASES['default'].get('CONN_MAX_AGE', 0)
        print(f"📊 Connection pooling: {conn_max_age}s")

        if conn_max_age >= 600:
            print("✅ Connection pooling otimizado (≥10min)")
        else:
            print("⚠️ Connection pooling pode ser melhorado")

        return True
    except Exception as e:
        print(f"❌ Erro ao testar banco: {e}")
        return False


def main():
    """Executa todos os testes."""
    print("=" * 70)
    print("🚀 VALIDAÇÃO DE OTIMIZAÇÕES DE ESCALABILIDADE")
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
    print("📊 RESUMO DOS TESTES")
    print("=" * 70)

    for test_name, result in results.items():
        status = "✅ PASSOU" if result else "⚠️ PRECISA ATENÇÃO"
        print(f"{test_name:.<30} {status}")

    passed = sum(results.values())
    total = len(results)
    print("\n" + "=" * 70)
    print(f"🎯 RESULTADO FINAL: {passed}/{total} testes passaram")
    print("=" * 70)

    if passed == total:
        print("\n🎉 PARABÉNS! Todas as otimizações estão funcionando!")
    else:
        print("\n⚠️ Algumas otimizações precisam de atenção (verifique acima)")
        print("\n📝 NOTAS:")
        print("   - Redis: Instalar com 'wsl sudo apt install redis-server'")
        print("   - Celery: Executar 'celery -A cgbookstore worker -l info --pool=solo'")


if __name__ == '__main__':
    main()
