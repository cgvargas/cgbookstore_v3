"""
Testar conexão com Supabase
"""
import psycopg
import sys

# Configurar encoding UTF-8
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

SUPABASE_PASSWORD = "Oa023568910@"

# URLs de conexão
SUPABASE_DIRECT = f"postgresql://postgres:{SUPABASE_PASSWORD}@db.uomjbcuowfgcwhsejatn.supabase.co:5432/postgres"
SUPABASE_POOLER = f"postgresql://postgres.uomjbcuowfgcwhsejatn:{SUPABASE_PASSWORD}@aws-1-sa-east-1.pooler.supabase.com:6543/postgres?pgbouncer=true"

print("=" * 80)
print("TESTE DE CONEXAO COM SUPABASE")
print("=" * 80)

print("\n1. Testando conexao DIRECT (porta 5432)...")
try:
    conn = psycopg.connect(SUPABASE_DIRECT, connect_timeout=15)
    cursor = conn.cursor()

    cursor.execute("SELECT version();")
    version = cursor.fetchone()[0]
    print(f"   OK: Conectado!")
    print(f"   Versao: {version[:50]}...")

    cursor.execute("""
        SELECT COUNT(*)
        FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_type = 'BASE TABLE';
    """)
    table_count = cursor.fetchone()[0]
    print(f"   Tabelas existentes: {table_count}")

    cursor.close()
    conn.close()

except Exception as e:
    print(f"   ERRO: {str(e)}")
    sys.exit(1)

print("\n2. Testando conexao POOLER (porta 6543)...")
try:
    conn = psycopg.connect(SUPABASE_POOLER, connect_timeout=15)
    cursor = conn.cursor()
    cursor.execute("SELECT 1;")
    print("   OK: Conectado!")
    cursor.close()
    conn.close()
except Exception as e:
    print(f"   AVISO: {str(e)}")
    print("   (Pooler pode ter restricoes, use conexao direta)")

print("\n" + "=" * 80)
print("CONEXAO COM SUPABASE: OK!")
print("=" * 80)
print("\nProximo passo: Executar migrations no Supabase")
