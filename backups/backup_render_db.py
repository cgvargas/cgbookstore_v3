"""
Script para fazer backup completo do banco de dados Render.
Gera um arquivo SQL com todos os dados e estrutura.
"""
import os
import sys
from datetime import datetime
import subprocess

# Configurar encoding UTF-8
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

print("=" * 80)
print("BACKUP DO BANCO DE DADOS RENDER")
print("=" * 80)
print(f"\nData/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")

# Obter DATABASE_URL do .env
database_url = os.getenv('DATABASE_URL')

if not database_url or 'render.com' not in database_url:
    print("ERRO: DATABASE_URL do Render nao encontrada no ambiente!")
    sys.exit(1)

# Gerar nome do arquivo de backup
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
backup_file = f"backup_render_{timestamp}.sql"
backup_path = os.path.join(os.getcwd(), backup_file)

print(f"DATABASE_URL: {database_url[:50]}...")
print(f"Arquivo de backup: {backup_file}")
print("-" * 80)

# Usar pg_dump para fazer backup
print("\nIniciando backup com pg_dump...")
print("(Isso pode levar alguns minutos dependendo do tamanho do banco)\n")

try:
    # Comando pg_dump
    cmd = [
        'pg_dump',
        '--dbname', database_url,
        '--file', backup_path,
        '--format', 'plain',  # Formato SQL legível
        '--verbose',
        '--no-owner',  # Não incluir comandos de proprietário
        '--no-privileges',  # Não incluir comandos de privilégios
    ]

    # Executar pg_dump
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )

    if result.returncode == 0:
        # Verificar tamanho do arquivo
        file_size = os.path.getsize(backup_path)
        file_size_mb = file_size / (1024 * 1024)

        print("\n" + "=" * 80)
        print("BACKUP CONCLUIDO COM SUCESSO!")
        print("=" * 80)
        print(f"\nArquivo: {backup_file}")
        print(f"Tamanho: {file_size_mb:.2f} MB")
        print(f"Localizacao: {backup_path}")

        # Criar também um backup compactado (opcional)
        print("\nCriando backup compactado...")
        import gzip
        import shutil

        backup_gz = backup_path + '.gz'
        with open(backup_path, 'rb') as f_in:
            with gzip.open(backup_gz, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

        gz_size = os.path.getsize(backup_gz)
        gz_size_mb = gz_size / (1024 * 1024)

        print(f"\nBackup compactado: {backup_file}.gz")
        print(f"Tamanho compactado: {gz_size_mb:.2f} MB")

        print("\n" + "=" * 80)
        print("PROXIMOS PASSOS:")
        print("=" * 80)
        print("1. Guardar estes arquivos em local seguro")
        print("2. Obter credenciais do banco Supabase")
        print("3. Executar script de migracao")
        print("=" * 80)

    else:
        print("\n" + "=" * 80)
        print("ERRO AO FAZER BACKUP!")
        print("=" * 80)
        print(f"\nCodigo de erro: {result.returncode}")
        print(f"\nErro: {result.stderr}")

        if "pg_dump" in result.stderr and "not found" in result.stderr.lower():
            print("\n*** SOLUCAO:")
            print("O comando pg_dump nao esta instalado ou nao esta no PATH.")
            print("Instale o PostgreSQL client tools:")
            print("- Windows: https://www.postgresql.org/download/windows/")
            print("- Ou use: winget install PostgreSQL.PostgreSQL")

        sys.exit(1)

except FileNotFoundError:
    print("\n" + "=" * 80)
    print("ERRO: pg_dump nao encontrado!")
    print("=" * 80)
    print("\nO PostgreSQL client tools precisa estar instalado.")
    print("\nInstale com:")
    print("- Windows: https://www.postgresql.org/download/windows/")
    print("- Ou use: winget install PostgreSQL.PostgreSQL")
    print("\nApos instalar, adicione ao PATH:")
    print("C:\\Program Files\\PostgreSQL\\<versao>\\bin")
    sys.exit(1)

except Exception as e:
    print(f"\nERRO inesperado: {str(e)}")
    sys.exit(1)
