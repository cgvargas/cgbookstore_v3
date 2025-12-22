"""
Verificar dados existentes no Supabase
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

django.setup()

from django.db import connection
from django.apps import apps

print("=" * 80)
print("VERIFICACAO DE DADOS NO SUPABASE")
print("=" * 80)

# Models principais para verificar
models_to_check = [
    ('core', 'Book'),
    ('core', 'Author'),
    ('core', 'Category'),
    ('core', 'Banner'),
    ('core', 'Section'),
    ('accounts', 'UserProfile'),
    ('accounts', 'BookShelf'),
    ('debates', 'DebateTopic'),
    ('finance', 'Subscription'),
]

print("\nContagem de registros por model:")
print("-" * 80)

total_records = 0

for app_label, model_name in models_to_check:
    try:
        model = apps.get_model(app_label, model_name)
        count = model.objects.count()
        total_records += count
        status = "OK" if count > 0 else "VAZIO"
        print(f"{app_label}.{model_name:20s}: {count:6d} registros [{status}]")
    except Exception as e:
        print(f"{app_label}.{model_name:20s}: ERRO - {str(e)[:40]}")

print("-" * 80)
print(f"TOTAL DE REGISTROS: {total_records}")

if total_records > 0:
    print("\n*** O banco Supabase JA POSSUI DADOS!")
    print("Opcoes:")
    print("1. Usar este banco (ja esta pronto)")
    print("2. Limpar e migrar do Render")
    print("3. Comparar dados Render x Supabase")
else:
    print("\n*** Banco Supabase esta vazio (apenas estrutura)")
    print("Necessario migrar dados do Render")

print("=" * 80)
