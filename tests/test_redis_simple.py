#!/usr/bin/env python
"""
Teste simples da conexão Django com Redis
"""
import redis

# Teste direto com Redis
print("=" * 60)
print("TESTE DE CONEXÃO COM REDIS")
print("=" * 60)
print()

try:
    # Conectar ao Redis diretamente
    r = redis.Redis(host='127.0.0.1', port=6379, db=1, decode_responses=True)

    # Testar PING
    print("1. Testando PING...")
    pong = r.ping()
    print(f"   [OK] PONG recebido: {pong}")
    print()

    # Testar SET/GET
    print("2. Testando SET/GET...")
    r.set('test_cgbookstore', 'Redis funcionando!', ex=60)
    value = r.get('test_cgbookstore')
    print(f"   [OK] Valor armazenado: {value}")
    print()

    # Limpar teste
    r.delete('test_cgbookstore')
    print("3. Limpeza concluida")
    print()

    print("=" * 60)
    print("[OK] REDIS ESTA FUNCIONANDO PERFEITAMENTE!")
    print("=" * 60)
    print()
    print("Informações do Redis:")
    info = r.info('server')
    print(f"  - Versão: {info['redis_version']}")
    print(f"  - Modo: {info['redis_mode']}")
    print(f"  - Uptime: {info['uptime_in_seconds']} segundos")
    print()
    print("Próximo passo: Configurar o Django para usar este Redis")
    print()

except redis.ConnectionError as e:
    print(f"[ERRO] Nao foi possivel conectar ao Redis")
    print(f"  Detalhes: {e}")
    print()
    print("  Verifique se o Docker esta rodando:")
    print("  1. docker ps | grep cgbookstore_redis")
    print("  2. docker start cgbookstore_redis")
    print()
except Exception as e:
    print(f"[ERRO INESPERADO] {e}")
    print()
