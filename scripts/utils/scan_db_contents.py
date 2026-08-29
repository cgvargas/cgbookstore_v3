import os
import psycopg
import re

try:
    conn = psycopg.connect(
        dbname="postgres",
        user="postgres.xmrnlckrazptjbnmmhjj",
        password="Oa023568910@",
        host="aws-0-us-west-2.pooler.supabase.com",
        port="5432"
    )
    cursor = conn.cursor()
    print("Conexao estabelecida.")
except Exception as e:
    print(f"Erro ao conectar: {e}")
    exit(1)

# Scan news articles content
cursor.execute("SELECT id, title, featured_image, content FROM public.news_article")
articles = cursor.fetchall()

print(f"Buscando referencias a /media/ no conteudo das noticias...")
print("=" * 80)

media_pattern = re.compile(r'(/media/[^\s"\'\)>]+)')

all_found_media = set()

for art_id, title, feat_img, content in articles:
    if not content:
        continue
    found = media_pattern.findall(content)
    if found:
        print(f"Noticia: '{title}' (ID: {art_id})")
        print(f"  Imagem de Destaque: {feat_img}")
        print(f"  Referencias no conteudo:")
        for path in found:
            print(f"    - {path}")
            all_found_media.add(path)
        print()

print("=" * 80)
print(f"Total de paths de midia encontrados no conteudo das noticias: {len(all_found_media)}")
for path in sorted(all_found_media):
    print(f"  {path}")

cursor.close()
conn.close()
