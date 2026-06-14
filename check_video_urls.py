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

cursor.execute("SELECT id, title, video_url, thumbnail_image FROM public.core_video WHERE thumbnail_image LIKE '%Captura%' OR thumbnail_image LIKE '%dbit%'")
videos = cursor.fetchall()

print("VIDEOS COM THUMBNAIL AUSENTE:")
print("=" * 80)
for vid_id, title, url, thumb in videos:
    print(f"ID: {vid_id} | Titulo: {title}")
    print(f"  URL: {url}")
    print(f"  Thumbnail no banco: {thumb}")
    print()

cursor.close()
conn.close()
