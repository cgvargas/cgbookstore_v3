"""
Script para verificar qual banco de dados está sendo usado pelo sistema.
"""
import os
import sys
import django

# Configurar encoding UTF-8
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from django.conf import settings
from django.db import connection
from datetime import datetime

print("=" * 80)
print("RELATORIO DE CONFIGURACAO DO BANCO DE DADOS")
print("=" * 80)
print(f"\nData/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")

# 1. Configuração no settings.py
print("1. CONFIGURACAO NO SETTINGS.PY")
print("-" * 80)
db_config = settings.DATABASES['default']
print(f"Engine: {db_config.get('ENGINE')}")
print(f"Name: {db_config.get('NAME')}")
print(f"User: {db_config.get('USER')}")
print(f"Host: {db_config.get('HOST')}")
print(f"Port: {db_config.get('PORT')}")
print(f"Connection Max Age: {db_config.get('CONN_MAX_AGE')} segundos")

# 2. Variáveis de ambiente
print("\n2. VARIAVEIS DE AMBIENTE")
print("-" * 80)
database_url = os.getenv('DATABASE_URL', 'NÃO CONFIGURADA')
supabase_url = os.getenv('SUPABASE_URL', 'NÃO CONFIGURADA')
redis_url = os.getenv('REDIS_URL', 'NÃO CONFIGURADA')

print(f"DATABASE_URL: {database_url[:80]}..." if len(database_url) > 80 else f"DATABASE_URL: {database_url}")
print(f"SUPABASE_URL: {supabase_url}")
print(f"REDIS_URL: {redis_url[:80]}..." if len(redis_url) > 80 else f"REDIS_URL: {redis_url}")

# 3. Análise do DATABASE_URL
print("\n3. ANALISE DO BANCO DE DADOS ATIVO")
print("-" * 80)
if 'render.com' in database_url:
    print("*** ATENCAO: Usando banco Render (cgbookstore-db)")
    print("    Este banco tem data de validade: INICIO DE DEZEMBRO 2024")
    print("    *** URGENTE: Migrar para Supabase antes da expiracao!")
    db_type = "RENDER (TEMPORARIO)"
elif 'supabase.co' in database_url:
    print("OK: Usando banco Supabase (permanente)")
    db_type = "SUPABASE (PERMANENTE)"
elif 'sqlite' in database_url.lower():
    print("Usando SQLite local (desenvolvimento)")
    db_type = "SQLITE (LOCAL)"
else:
    print("Tipo de banco desconhecido")
    db_type = "DESCONHECIDO"

# 4. Testar conexão
print("\n4. TESTE DE CONEXAO")
print("-" * 80)
try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"OK: Conexao bem-sucedida!")
        print(f"Versao do PostgreSQL: {version}")

        # Verificar host da conexão
        cursor.execute("SELECT inet_server_addr();")
        try:
            server_addr = cursor.fetchone()[0]
            print(f"Endereco do servidor: {server_addr}")
        except:
            print("Endereco do servidor: (nao disponivel)")

        # Contar tabelas
        cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_schema = 'public';
        """)
        table_count = cursor.fetchone()[0]
        print(f"Numero de tabelas: {table_count}")

except Exception as e:
    print(f"ERRO ao conectar: {str(e)}")

# 5. Cache/Redis
print("\n5. CONFIGURACAO DE CACHE (REDIS)")
print("-" * 80)
cache_config = settings.CACHES['default']
print(f"Backend: {cache_config.get('BACKEND')}")
print(f"Location: {cache_config.get('LOCATION')}")
print(f"Timeout padrão: {cache_config.get('TIMEOUT')} segundos")

# 6. Supabase Storage
print("\n6. SUPABASE STORAGE")
print("-" * 80)
if supabase_url != 'NAO CONFIGURADA':
    print(f"OK: Supabase configurado: {supabase_url}")
    print("Storage usado para: Avatares, Banners, Capas de Livros, etc.")
else:
    print("ERRO: Supabase nao configurado")

# 7. Recomendações
print("\n7. RECOMENDACOES E ACOES NECESSARIAS")
print("-" * 80)
if db_type == "RENDER (TEMPORARIO)":
    print("*** ACAO URGENTE NECESSARIA:")
    print("   1. Fazer backup completo do banco Render")
    print("   2. Criar banco PostgreSQL no Supabase")
    print("   3. Migrar dados do Render para Supabase")
    print("   4. Atualizar DATABASE_URL para apontar para Supabase")
    print("   5. Atualizar variaveis de ambiente no Render.com")
    print("\n   PRAZO: Antes do inicio de dezembro 2024")
elif db_type == "SUPABASE (PERMANENTE)":
    print("OK: Tudo certo! Banco de dados permanente em uso.")
    print("   Continue usando o Supabase normalmente.")
else:
    print("AVISO: Verifique a configuracao do banco de dados.")

print("\n" + "=" * 80)
print("FIM DO RELATORIO")
print("=" * 80)
