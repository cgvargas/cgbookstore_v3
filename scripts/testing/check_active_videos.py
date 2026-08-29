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
    
    # Query video records
    cursor.execute("SELECT title, thumbnail_image, thumbnail_url, video_url, video_file FROM public.core_video")
    videos = cursor.fetchall()
    print(f"Total de videos no banco ativo: {len(videos)}")
    for title, thumb, thumb_url, video_url, video_file in videos:
        safe_title = title.encode('ascii', errors='replace').decode('ascii')
        print(f"  Video: '{safe_title}'")
        print(f"    thumbnail_image: {thumb}")
        print(f"    thumbnail_url: {thumb_url}")
        print(f"    video_url: {video_url}")
        print(f"    video_file: {video_file}\n")
        
    cursor.close()
    conn.close()
except Exception as e:
    print(f"Erro: {e}")
