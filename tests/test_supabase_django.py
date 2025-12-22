"""
Testar Supabase usando Django
"""
import os
import sys
import django

# Configurar encoding UTF-8
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Configurar DATABASE_URL para Supabase
SUPABASE_URL = "postgresql://postgres:Oa023568910@@db.uomjbcuowfgcwhsejatn.supabase.co:5432/postgres"
os.environ['DATABASE_URL'] = SUPABASE_URL
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')

print("=" * 80)
print("TESTE SUPABASE VIA DJANGO")
print("=" * 80)
print(f"\nDATABASE_URL configurado para Supabase")
print(f"Host: db.uomjbcuowfgcwhsejatn.supabase.co")
print(f"Port: 5432")
print(f"Database: postgres")

django.setup()

from django.db import connection

print("\nTestando conexao...")
try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"\nOK: Conectado ao Supabase!")
        print(f"Versao: {version[:80]}...")

        cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_type = 'BASE TABLE';
        """)
        table_count = cursor.fetchone()[0]
        print(f"Tabelas existentes: {table_count}")

        if table_count == 0:
            print("\nBanco vazio - pronto para receber migrations!")
        else:
            print(f"\nBanco ja possui {table_count} tabelas")

except Exception as e:
    print(f"\nERRO: {str(e)}")
    import traceback
    print("\nTraceback completo:")
    print(traceback.format_exc())
    sys.exit(1)

print("\n" + "=" * 80)
print("CONEXAO OK!")
print("=" * 80)
