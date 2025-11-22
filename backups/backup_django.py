"""
Script para fazer backup completo usando Django dumpdata.
Exporta todos os dados em formato JSON.
"""
import os
import sys
import django
from datetime import datetime
import subprocess
import json

# Configurar encoding UTF-8
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from django.core.management import call_command
from django.apps import apps

print("=" * 80)
print("BACKUP COMPLETO DO BANCO DE DADOS (Django dumpdata)")
print("=" * 80)
print(f"\nData/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")

# Gerar nome do arquivo de backup
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
backup_file = f"backup_render_full_{timestamp}.json"
backup_path = os.path.join(os.getcwd(), backup_file)

print(f"Arquivo de backup: {backup_file}")
print("-" * 80)

# Listar todos os apps e models
print("\nModels que serao exportados:")
print("-" * 80)

apps_to_backup = []
for app_config in apps.get_app_configs():
    if app_config.name in ['core', 'accounts', 'debates', 'recommendations', 'finance', 'chatbot_literario']:
        models = list(app_config.get_models())
        if models:
            print(f"\n{app_config.verbose_name} ({app_config.label}):")
            for model in models:
                print(f"  - {model.__name__}")
            apps_to_backup.append(app_config.label)

print("\n" + "-" * 80)
print("\nIniciando backup...")
print("(Isso pode levar alguns minutos)\n")

try:
    # Fazer backup completo
    with open(backup_path, 'w', encoding='utf-8') as f:
        call_command(
            'dumpdata',
            *apps_to_backup,
            indent=2,
            output=backup_path,
            natural_foreign=True,
            natural_primary=True,
        )

    # Verificar tamanho do arquivo
    file_size = os.path.getsize(backup_path)
    file_size_mb = file_size / (1024 * 1024)

    # Contar registros
    with open(backup_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        record_count = len(data)

    print("\n" + "=" * 80)
    print("BACKUP CONCLUIDO COM SUCESSO!")
    print("=" * 80)
    print(f"\nArquivo: {backup_file}")
    print(f"Tamanho: {file_size_mb:.2f} MB")
    print(f"Registros: {record_count:,}")
    print(f"Localizacao: {backup_path}")

    # Criar backup por app individual (para facilitar troubleshooting)
    print("\n" + "-" * 80)
    print("Criando backups individuais por app...")
    print("-" * 80)

    for app_label in apps_to_backup:
        app_backup_file = f"backup_render_{app_label}_{timestamp}.json"
        app_backup_path = os.path.join(os.getcwd(), app_backup_file)

        with open(app_backup_path, 'w', encoding='utf-8') as f:
            call_command(
                'dumpdata',
                app_label,
                indent=2,
                output=app_backup_path,
                natural_foreign=True,
                natural_primary=True,
            )

        app_size = os.path.getsize(app_backup_path)
        app_size_kb = app_size / 1024

        with open(app_backup_path, 'r', encoding='utf-8') as f:
            app_data = json.load(f)
            app_records = len(app_data)

        print(f"  {app_label}: {app_records} registros ({app_size_kb:.1f} KB)")

    print("\n" + "=" * 80)
    print("ARQUIVOS DE BACKUP CRIADOS:")
    print("=" * 80)
    print(f"\n1. Backup completo: {backup_file}")
    print(f"2. Backups por app: backup_render_<app>_{timestamp}.json")

    print("\n" + "=" * 80)
    print("PROXIMOS PASSOS:")
    print("=" * 80)
    print("1. Guardar estes arquivos em local seguro")
    print("2. Obter DATABASE_URL do banco Supabase")
    print("3. Executar migracao para Supabase")
    print("\nPara migrar, forneca:")
    print("  - Host do banco Supabase")
    print("  - Nome do banco")
    print("  - Usuario")
    print("  - Senha")
    print("  - Porta (geralmente 5432)")
    print("=" * 80)

except Exception as e:
    print("\n" + "=" * 80)
    print("ERRO AO FAZER BACKUP!")
    print("=" * 80)
    print(f"\nErro: {str(e)}")
    import traceback
    print("\nTraceback:")
    print(traceback.format_exc())
    sys.exit(1)
