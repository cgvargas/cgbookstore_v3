# Script para exportar dados com encoding UTF-8
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from django.core.management import call_command

# Força encoding UTF-8
sys.stdout.reconfigure(encoding='utf-8')

print("Iniciando export do banco de dados...")

try:
    with open('backup_cgbookstore.json', 'w', encoding='utf-8') as f:
        call_command(
            'dumpdata',
            '--exclude=auth.permission',
            '--exclude=contenttypes', 
            '--exclude=admin.logentry',
            '--indent=2',
            stdout=f
        )
    print("✅ Export concluído com sucesso!")
    print(f"Arquivo: backup_cgbookstore.json")
except Exception as e:
    print(f"❌ Erro: {e}")
