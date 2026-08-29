import psycopg

try:
    conn = psycopg.connect(
        dbname="postgres",
        user="postgres.xmrnlckrazptjbnmmhjj",
        password="Oa023568910@",
        host="aws-0-us-west-2.pooler.supabase.com",
        port="5432"
    )
    cursor = conn.cursor()
    
    # Query all public tables
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name
    """)
    print("Todas as tabelas do banco de dados ativo:")
    for row in cursor.fetchall():
        print(f"  {row[0]}")
        
    cursor.close()
    conn.close()
except Exception as e:
    print(f"Erro: {e}")
