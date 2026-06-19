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
except Exception as e:
    print(f"Erro ao conectar: {e}")
    exit(1)

titles = ["Devoradores de Estrelas", "Verity", "Brandon Sanderson"]

# Get columns
cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'news_article'")
cols = [r[0] for r in cursor.fetchall()]

# Select articles where title contains any of our titles
for t in titles:
    print(f"=== BUSCANDO ARTIGOS COM O TITULO CONTENDO '{t}' ===")
    cursor.execute(f"SELECT {', '.join(cols)} FROM public.news_article WHERE title ILIKE %s", (f"%{t}%",))
    rows = cursor.fetchall()
    print(f"Encontrados: {len(rows)}")
    for row in rows:
        for col_name, val in zip(cols, row):
            # Print only non-null or relevant fields
            if val is not None and col_name != 'content':
                print(f"  {col_name}: {repr(val)}")
            elif col_name == 'content':
                # Print first 200 chars and search for any image/media/iframe tags
                print(f"  content (len={len(val or '')}): {repr((val or '')[:200])}...")
                # Find all img, iframe, source tags or src attributes
                srcs = [m for m in psycopg.sql.SQL(" ").join([]).as_string(conn) if False] # placeholder
                import re
                src_finds = re.findall(r'src=["\']([^"\']+)["\']', val or '')
                if src_finds:
                    print(f"    Embedded sources (src): {src_finds}")
        print("-" * 50)

cursor.close()
conn.close()
