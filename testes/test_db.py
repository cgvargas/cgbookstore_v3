# test_db.py

import psycopg2
import os


def test_connection():
    """
    Função para testar a conexão com o banco de dados Supabase.
    """
    conn = None
    try:
        # Tenta estabelecer a conexão usando o endereço e credenciais corrigidas
        conn = psycopg2.connect(
            dbname="postgres",
            user="postgres.uomjbcuowfgcwhsejatn",
            password="Oa023568910@",
            host="aws-1-sa-east-1.pooler.supabase.com",
            port="5432"
        )
        print("Conexão com o banco de dados Supabase estabelecida com sucesso! 🎉")

        # Executa uma consulta simples para verificar o acesso
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()
        print(f"Versão do PostgreSQL: {db_version[0]}")

    except psycopg2.OperationalError as e:
        # Se a conexão falhar, exibe a mensagem de erro detalhada
        print(f"Erro de conexão com o banco de dados: {e}")
        print("Verifique se o seu firewall ou rede estão permitindo a conexão.")

    finally:
        # Garante que a conexão seja fechada, mesmo se ocorrer um erro
        if conn:
            conn.close()
            print("Conexão com o banco de dados fechada.")


if __name__ == "__main__":
    test_connection()