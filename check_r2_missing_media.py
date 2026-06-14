import os
import psycopg
import boto3

# ---------------------------------------------------------------------------
# 1. Carregar Variáveis de Ambiente do .env
# ---------------------------------------------------------------------------
env_vars = {}
with open('.env', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#'):
            parts = line.split('=', 1)
            if len(parts) == 2:
                key = parts[0].strip()
                val = parts[1].strip().strip('"').strip("'")
                env_vars[key] = val

R2_ACCOUNT_ID = env_vars.get('R2_ACCOUNT_ID')
R2_ACCESS_KEY_ID = env_vars.get('R2_ACCESS_KEY_ID')
R2_SECRET_ACCESS_KEY = env_vars.get('R2_SECRET_ACCESS_KEY')
R2_BUCKET_NAME = env_vars.get('R2_BUCKET_NAME', 'cgbookstore-media')

s3 = boto3.client(
    's3',
    endpoint_url=f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com",
    aws_access_key_id=R2_ACCESS_KEY_ID,
    aws_secret_access_key=R2_SECRET_ACCESS_KEY,
)

# ---------------------------------------------------------------------------
# 2. Conectar ao Banco de Dados e Coletar Caminhos
# ---------------------------------------------------------------------------
try:
    conn = psycopg.connect(
        dbname="postgres",
        user="postgres.xmrnlckrazptjbnmmhjj",
        password="Oa023568910@",
        host="aws-0-us-west-2.pooler.supabase.com",
        port="5432"
    )
    cursor = conn.cursor()
    print("Conectado ao banco de dados.")
except Exception as e:
    print(f"Erro ao conectar ao banco: {e}")
    exit(1)

# List of media paths referenced in DB: (source_table, db_path, identifier)
paths_to_check = []

# A. News featured images
cursor.execute("SELECT id, title, featured_image FROM public.news_article WHERE featured_image IS NOT NULL AND featured_image != ''")
for art_id, title, img_path in cursor.fetchall():
    paths_to_check.append(('news_article.featured_image', img_path, f"Article ID {art_id} ({title[:30]})"))

# B. Video thumbnails
cursor.execute("SELECT id, title, thumbnail_image FROM public.core_video WHERE thumbnail_image IS NOT NULL AND thumbnail_image != ''")
for vid_id, title, img_path in cursor.fetchall():
    paths_to_check.append(('core_video.thumbnail_image', img_path, f"Video ID {vid_id} ({title[:30]})"))

# C. Literary universes banners
cursor.execute("""
    SELECT column_name FROM information_schema.columns 
    WHERE table_schema = 'public' AND table_name = 'core_literaryuniverse' 
      AND (column_name LIKE '%image%' OR column_name LIKE '%foto%' OR column_name LIKE '%capa%' OR column_name LIKE '%banner%')
      AND data_type IN ('character varying', 'text')
""")
universe_cols = [r[0] for r in cursor.fetchall()]
for col in universe_cols:
    cursor.execute(f"SELECT id, title, {col} FROM public.core_literaryuniverse WHERE {col} IS NOT NULL AND {col} != ''")
    for u_id, title, img_path in cursor.fetchall():
        paths_to_check.append((f'core_literaryuniverse.{col}', img_path, f"Universe ID {u_id} ({title[:30]})"))

# D. Categories images
cursor.execute("""
    SELECT column_name FROM information_schema.columns 
    WHERE table_schema = 'public' AND table_name = 'core_category' 
      AND (column_name LIKE '%image%' OR column_name LIKE '%foto%' OR column_name LIKE '%capa%')
      AND data_type IN ('character varying', 'text')
""")
category_cols = [r[0] for r in cursor.fetchall()]
for col in category_cols:
    cursor.execute(f"SELECT id, name, {col} FROM public.core_category WHERE {col} IS NOT NULL AND {col} != ''")
    for cat_id, name, img_path in cursor.fetchall():
        paths_to_check.append((f'core_category.{col}', img_path, f"Category ID {cat_id} ({name[:30]})"))

print(f"Total de recursos referenciados para verificar no R2: {len(paths_to_check)}")
print("-" * 80)

missing_in_r2 = []
for idx, (table_col, db_path, ident) in enumerate(paths_to_check, start=1):
    r2_key = db_path.replace('\\', '/')
    exists = False
    try:
        s3.head_object(Bucket=R2_BUCKET_NAME, Key=r2_key)
        exists = True
    except Exception:
        pass
    
    if not exists:
        missing_in_r2.append((table_col, db_path, ident))
        print(f"MISSING: {r2_key} | {table_col} | {ident}")
    else:
        # print(f"OK: {r2_key}")
        pass

print("-" * 80)
print(f"Resumo: Total referenciado no DB: {len(paths_to_check)} | Faltando no R2: {len(missing_in_r2)}")

cursor.close()
conn.close()
