"""
Script para migrar dados do Render para Supabase.
"""
import os
import sys
import django
from getpass import getpass

# Configurar encoding UTF-8
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

print("=" * 80)
print("MIGRACAO RENDER -> SUPABASE")
print("=" * 80)

# Solicitar senha do Supabase
print("\nPara iniciar a migracao, forneca a senha do banco Supabase:")
supabase_password = getpass("Senha do Supabase: ")

if not supabase_password:
    print("\nERRO: Senha nao fornecida!")
    sys.exit(1)

# Configurar URLs dos bancos
RENDER_URL = os.getenv('DATABASE_URL')  # Banco atual (Render)
SUPABASE_URL = f"postgresql://postgres.uomjbcuowfgcwhsejatn:{supabase_password}@aws-1-sa-east-1.pooler.supabase.com:6543/postgres?pgbouncer=true"
SUPABASE_DIRECT_URL = f"postgresql://postgres.uomjbcuowfgcwhsejatn:{supabase_password}@aws-1-sa-east-1.pooler.supabase.com:5432/postgres"

print("\n" + "=" * 80)
print("ETAPA 1: TESTAR CONEXAO COM SUPABASE")
print("=" * 80)

# Testar conexão com Supabase
import psycopg

try:
    print("\nTestando conexao direta (porta 5432)...")
    conn = psycopg.connect(SUPABASE_DIRECT_URL, connect_timeout=10)
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()[0]
    print(f"OK: Conexao bem-sucedida!")
    print(f"Versao: {version}")

    # Verificar se o banco está vazio ou tem tabelas
    cursor.execute("""
        SELECT COUNT(*)
        FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_type = 'BASE TABLE';
    """)
    table_count = cursor.fetchone()[0]
    print(f"Tabelas existentes no Supabase: {table_count}")

    if table_count > 0:
        print("\n*** ATENCAO: O banco Supabase JA possui tabelas!")
        response = input("Deseja continuar e SOBRESCREVER? (sim/nao): ")
        if response.lower() != 'sim':
            print("Migracao cancelada pelo usuario.")
            sys.exit(0)

    cursor.close()
    conn.close()

except Exception as e:
    print(f"\nERRO ao conectar no Supabase: {str(e)}")
    print("\nVerifique:")
    print("1. A senha esta correta")
    print("2. Seu IP esta na whitelist do Supabase")
    print("3. O banco existe e esta acessivel")
    sys.exit(1)

print("\n" + "=" * 80)
print("ETAPA 2: CONFIGURAR DJANGO PARA USAR SUPABASE")
print("=" * 80)

# Configurar Django para usar Supabase temporariamente
os.environ['DATABASE_URL'] = SUPABASE_DIRECT_URL
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from django.core.management import call_command
from django.db import connection

print("\nTestando Django com Supabase...")
try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1;")
        print("OK: Django conectado ao Supabase!")
except Exception as e:
    print(f"ERRO: {str(e)}")
    sys.exit(1)

print("\n" + "=" * 80)
print("ETAPA 3: EXECUTAR MIGRATIONS NO SUPABASE")
print("=" * 80)

print("\nCriando estrutura do banco (migrations)...")
try:
    call_command('migrate', verbosity=2)
    print("\nOK: Migrations executadas com sucesso!")
except Exception as e:
    print(f"\nERRO nas migrations: {str(e)}")
    sys.exit(1)

print("\n" + "=" * 80)
print("ETAPA 4: COPIAR DADOS DO RENDER PARA SUPABASE")
print("=" * 80)

print("\nEsta etapa requer pg_dump e psql instalados.")
print("Alternativa: Usar Django para copiar dados app por app.")
print("\nEscolha o metodo:")
print("1. Django dumpdata/loaddata (mais lento, funciona sem pg_dump)")
print("2. pg_dump direto (mais rapido, requer PostgreSQL tools)")

method = input("\nMetodo (1 ou 2): ")

if method == "1":
    print("\n" + "-" * 80)
    print("USANDO METODO DJANGO")
    print("-" * 80)

    # Reconectar ao Render para fazer dump
    print("\nReconectando ao banco Render para extrair dados...")
    os.environ['DATABASE_URL'] = RENDER_URL

    # Reconfigurar Django (isso vai reconectar)
    from django.db import connections
    connections['default'].close()

    apps_to_migrate = ['core', 'accounts', 'debates', 'recommendations', 'finance']

    for app_label in apps_to_migrate:
        print(f"\nExportando {app_label}...")
        backup_file = f"temp_backup_{app_label}.json"

        try:
            with open(backup_file, 'w', encoding='utf-8') as f:
                call_command(
                    'dumpdata',
                    app_label,
                    indent=2,
                    output=backup_file,
                    natural_foreign=True,
                    natural_primary=True,
                    verbosity=0
                )
            print(f"  OK: {app_label} exportado")
        except Exception as e:
            print(f"  ERRO ao exportar {app_label}: {str(e)}")
            continue

        # Reconectar ao Supabase para importar
        print(f"  Importando {app_label} para Supabase...")
        os.environ['DATABASE_URL'] = SUPABASE_DIRECT_URL
        connections['default'].close()

        try:
            call_command('loaddata', backup_file, verbosity=0)
            print(f"  OK: {app_label} importado")

            # Remover arquivo temporário
            os.remove(backup_file)
        except Exception as e:
            print(f"  ERRO ao importar {app_label}: {str(e)}")
            print(f"  Arquivo mantido: {backup_file}")

    print("\n" + "=" * 80)
    print("MIGRACAO CONCLUIDA!")
    print("=" * 80)

elif method == "2":
    print("\n" + "-" * 80)
    print("USANDO METODO PG_DUMP")
    print("-" * 80)
    print("\nExecute manualmente:")
    print(f"\npg_dump '{RENDER_URL}' | psql '{SUPABASE_DIRECT_URL}'")
    print("\nOu use PGAdmin/DBeaver para copiar os dados.")

else:
    print("\nOpcao invalida!")
    sys.exit(1)

print("\n" + "=" * 80)
print("PROXIMOS PASSOS:")
print("=" * 80)
print("1. Verificar dados no Supabase")
print("2. Atualizar .env local com nova DATABASE_URL")
print("3. Testar sistema localmente")
print("4. Atualizar variaveis de ambiente no Render.com")
print("5. Deploy e teste em producao")
print("=" * 80)
