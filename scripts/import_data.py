# Script para importar dados desabilitando constraints
import os
import sys
import django

sys.path.insert(0, os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from django.core.management import call_command
from django.db import connection

print("Desabilitando constraints...")
with connection.cursor() as cursor:
    cursor.execute("SET session_replication_role = 'replica';")

print("Importando dados...")
try:
    call_command('loaddata', 'backup_cgbookstore.json', verbosity=1)
    print("✅ Dados importados com sucesso!")
except Exception as e:
    print(f"❌ Erro: {e}")

print("Reabilitando constraints...")
with connection.cursor() as cursor:
    cursor.execute("SET session_replication_role = 'origin';")

print("Concluído!")
