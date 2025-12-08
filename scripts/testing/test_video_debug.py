"""
Script de diagnóstico para sistema de vídeos
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from core.models import Video

print("=" * 60)
print("DIAGNÓSTICO DO SISTEMA DE VÍDEOS")
print("=" * 60)

# Buscar vídeos do YouTube
youtube_videos = Video.objects.filter(platform='youtube')
print(f"\n📊 Total de vídeos YouTube: {youtube_videos.count()}")

if youtube_videos.exists():
    print("\n🎬 Testando vídeos do YouTube:")
    print("-" * 60)

    for video in youtube_videos[:3]:
        print(f"\n📹 Vídeo ID {video.id}: {video.title}")
        print(f"   Platform: {video.platform}")
        print(f"   URL: {video.video_url}")
        print(f"   Embed Code: {video.embed_code}")

        # Testar get_embed_url
        embed_url = video.get_embed_url()
        print(f"   Embed URL: {embed_url}")

        # Testar get_thumbnail
        try:
            thumbnail = video.get_thumbnail()
            print(f"   Thumbnail: {thumbnail if thumbnail else 'None'}")
        except AttributeError as e:
            print(f"   ❌ ERRO no get_thumbnail: {e}")
            print(f"   ⚠️ Migration 0017 pode não ter sido aplicada!")

        # Verificar se thumbnail_image existe
        try:
            has_image = hasattr(video, 'thumbnail_image')
            print(f"   Has thumbnail_image field: {has_image}")
            if has_image:
                print(f"   thumbnail_image value: {video.thumbnail_image}")
        except Exception as e:
            print(f"   ❌ ERRO ao verificar thumbnail_image: {e}")

        print(f"   thumbnail_url: {video.thumbnail_url}")

        # Template rendering test
        print(f"\n   🧪 Teste de Template:")
        print(f"      {{{{ video.get_embed_url }}}}: {embed_url}")
        print(f"      {{{{ video.get_embed_url|default:'' }}}}: {embed_url if embed_url else ''}")

        # Verificar se retorna None como string
        if embed_url is None:
            print(f"      ⚠️ get_embed_url() retorna None!")
        elif str(embed_url) == 'None':
            print(f"      ⚠️ get_embed_url() retorna string 'None'!")
        else:
            print(f"      ✅ get_embed_url() OK")

print("\n" + "=" * 60)
print("VERIFICAÇÃO DE MIGRATIONS")
print("=" * 60)

from django.db import connection
cursor = connection.cursor()

# Verificar se migration 0017 foi aplicada
cursor.execute("""
    SELECT name FROM django_migrations
    WHERE app = 'core' AND name LIKE '%video%'
    ORDER BY id DESC
    LIMIT 5
""")

print("\n📝 Migrations recentes de vídeos:")
for row in cursor.fetchall():
    print(f"   - {row[0]}")

# Verificar estrutura da tabela Video
cursor.execute("""
    SELECT column_name, data_type
    FROM information_schema.columns
    WHERE table_name = 'core_video'
    AND column_name LIKE '%thumbnail%'
""")

print("\n📋 Campos de thumbnail na tabela:")
for row in cursor.fetchall():
    print(f"   - {row[0]}: {row[1]}")

print("\n" + "=" * 60)
print("FIM DO DIAGNÓSTICO")
print("=" * 60)
