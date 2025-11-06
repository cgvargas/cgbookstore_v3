"""
Script para resetar conexões do banco de dados
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from django.db import connection

# Fix encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def reset_connections():
    """Fecha todas as conexões ativas"""

    print("=" * 70)
    print("RESETANDO CONEXÕES DO BANCO DE DADOS")
    print("=" * 70)
    print()

    try:
        # Fecha a conexão atual
        connection.close()
        print("✅ Conexão fechada com sucesso!")

        # Força limpeza de cursores
        from django.db import reset_queries
        reset_queries()
        print("✅ Queries resetadas!")

    except Exception as e:
        print(f"❌ Erro: {e}")

    print("\n💡 Agora tente acessar o admin novamente.")
    print()

if __name__ == '__main__':
    reset_connections()
