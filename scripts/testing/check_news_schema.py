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
    
    # 1. Encontrar todas as tabelas relacionadas a noticias
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' AND (table_name LIKE '%news%' OR table_name LIKE '%post%' OR table_name LIKE '%artigo%' OR table_name LIKE '%article%')
    """)
    tables = [r[0] for r in cursor.fetchall()]
    print("Tabelas de noticias encontradas:")
    for t in tables:
        print(f"  {t}")
        
    for table_name in tables:
        # 2. Obter colunas
        cursor.execute(f"""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_schema = 'public' AND table_name = '{table_name}'
        """)
        print(f"\nColunas de {table_name}:")
        cols = []
        for col in cursor.fetchall():
            print(f"  {col[0]} ({col[1]})")
            cols.append(col[0])
            
        # 3. Query sample records
        # Encontrar quais colunas parecem ser de imagem
        img_cols = [c for c in cols if 'image' in c.lower() or 'capa' in c.lower() or 'foto' in c.lower() or 'img' in c.lower() or 'banner' in c.lower() or 'thumb' in c.lower()]
        print(f"Colunas de imagem detectadas em {table_name}: {img_cols}")
        
        if img_cols:
            select_cols = ['title' if 'title' in cols else 'id'] + img_cols
            cols_str = ', '.join(select_cols)
            cursor.execute(f"SELECT {cols_str} FROM public.{table_name} LIMIT 10")
            print(f"Registros de {table_name}:")
            for row in cursor.fetchall():
                print(f"  {row}")
                
    cursor.close()
    conn.close()
except Exception as e:
    print(f"Erro: {e}")
