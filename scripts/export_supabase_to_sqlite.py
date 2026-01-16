"""
Script para exportar dados do Supabase (PostgreSQL) e importar no SQLite local.

Uso:
1. Descomente DATABASE_URL no .env (para conectar ao Supabase)
2. Execute: python scripts/export_supabase_to_sqlite.py --export
3. Comente DATABASE_URL no .env (para usar SQLite)
4. Execute: python scripts/export_supabase_to_sqlite.py --import
"""
import os
import sys
import json
import argparse
from pathlib import Path

# Adicionar o diretório do projeto ao path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')

import django
django.setup()

from django.core.management import call_command
from django.conf import settings

BACKUP_FILE = BASE_DIR / 'backup_supabase_data.json'

# Apps e models para excluir do backup (dados do sistema, não de negócio)
EXCLUDE_MODELS = [
    'contenttypes.contenttype',
    'auth.permission',
    'sessions.session',
    'admin.logentry',
]


def export_data():
    """Exporta dados do Supabase para arquivo JSON."""
    db_engine = settings.DATABASES['default'].get('ENGINE', '')
    
    if 'sqlite' in db_engine:
        print("❌ ERRO: Você está conectado ao SQLite!")
        print("📝 Descomente a linha DATABASE_URL no .env e tente novamente.")
        return False
    
    print("=" * 60)
    print("📤 EXPORTANDO DADOS DO SUPABASE")
    print("=" * 60)
    print(f"🔗 Conectado a: {settings.DATABASES['default'].get('HOST', 'N/A')}")
    print(f"💾 Arquivo de saída: {BACKUP_FILE}")
    print()
    
    try:
        # Construir argumentos de exclusão
        exclude_args = []
        for model in EXCLUDE_MODELS:
            exclude_args.extend(['--exclude', model])
        
        print("⏳ Exportando dados (isso pode demorar alguns minutos)...")
        
        with open(BACKUP_FILE, 'w', encoding='utf-8') as f:
            call_command(
                'dumpdata',
                '--natural-foreign',
                '--natural-primary',
                '--indent', '2',
                *exclude_args,
                stdout=f
            )
        
        file_size = BACKUP_FILE.stat().st_size / (1024 * 1024)  # MB
        print(f"✅ Exportação concluída! Arquivo: {file_size:.2f} MB")
        print()
        print("=" * 60)
        print("📋 PRÓXIMOS PASSOS:")
        print("=" * 60)
        print("1. Comente a linha DATABASE_URL no .env (adicione # no início)")
        print("2. Execute: python scripts/export_supabase_to_sqlite.py --import")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"❌ Erro na exportação: {e}")
        return False


def import_data():
    """Importa dados do arquivo JSON para o SQLite local."""
    db_engine = settings.DATABASES['default'].get('ENGINE', '')
    
    if 'postgresql' in db_engine:
        print("❌ ERRO: Você ainda está conectado ao PostgreSQL!")
        print("📝 Comente a linha DATABASE_URL no .env e tente novamente.")
        return False
    
    if not BACKUP_FILE.exists():
        print(f"❌ ERRO: Arquivo de backup não encontrado: {BACKUP_FILE}")
        print("📝 Execute primeiro: python scripts/export_supabase_to_sqlite.py --export")
        return False
    
    print("=" * 60)
    print("📥 IMPORTANDO DADOS PARA O SQLITE")
    print("=" * 60)
    print(f"📂 Arquivo de entrada: {BACKUP_FILE}")
    print()
    
    try:
        file_size = BACKUP_FILE.stat().st_size / (1024 * 1024)  # MB
        print(f"⏳ Importando {file_size:.2f} MB de dados...")
        
        call_command('loaddata', str(BACKUP_FILE), verbosity=1)
        
        print()
        print("✅ Importação concluída com sucesso!")
        print()
        print("=" * 60)
        print("🎉 PRONTO! Seus dados estão no SQLite local.")
        print("   Agora você pode usar o sistema normalmente com alta velocidade!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"❌ Erro na importação: {e}")
        print()
        print("💡 DICA: Se houver erro de integridade, tente:")
        print("   1. Deletar o arquivo db.sqlite3")
        print("   2. Executar: python manage.py migrate")
        print("   3. Tentar novamente: python scripts/export_supabase_to_sqlite.py --import")
        return False


def main():
    parser = argparse.ArgumentParser(description='Exportar/Importar dados entre Supabase e SQLite')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--export', action='store_true', help='Exportar dados do Supabase para JSON')
    group.add_argument('--import', dest='import_data', action='store_true', help='Importar dados do JSON para SQLite')
    
    args = parser.parse_args()
    
    if args.export:
        success = export_data()
    elif args.import_data:
        success = import_data()
    else:
        parser.print_help()
        success = False
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
