# coding: utf-8
"""
Script de teste para demonstrar o sistema de thumbnails de video
Execute: python manage.py shell < scripts/testing/test_video_thumbnails.py
"""

from core.models import Video

print("\n" + "=" * 70)
print("TESTE DO SISTEMA DE THUMBNAILS DE VIDEO")
print("=" * 70)

# Limpar videos de teste anteriores
Video.objects.filter(title__startswith='[TESTE]').delete()

# Teste 1: Video do YouTube (thumbnail automatica)
print("\n1. Criando video do YouTube (thumbnail automatica)...")
youtube_video = Video.objects.create(
    title="[TESTE] Book Trailer - YouTube",
    platform="youtube",
    video_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    video_type="trailer",
    description="Video de teste do YouTube com thumbnail automatica"
)
print(f"   - ID: {youtube_video.id}")
print(f"   - Plataforma: {youtube_video.get_platform_display()}")
print(f"   - Embed Code: {youtube_video.embed_code}")
print(f"   - Thumbnail URL: {youtube_video.thumbnail_url}")
print(f"   - Thumbnail Final: {youtube_video.get_thumbnail()}")

# Teste 2: Video do Instagram (sem thumbnail ainda)
print("\n2. Criando video do Instagram (sem thumbnail customizada)...")
instagram_video = Video.objects.create(
    title="[TESTE] Resenha - Instagram",
    platform="instagram",
    video_url="https://www.instagram.com/reel/ABC123/",
    video_type="review",
    description="Video de teste do Instagram - requer upload de thumbnail"
)
print(f"   - ID: {instagram_video.id}")
print(f"   - Plataforma: {instagram_video.get_platform_display()}")
print(f"   - Thumbnail URL: {instagram_video.thumbnail_url or 'Nenhuma'}")
print(f"   - Thumbnail Image: {instagram_video.thumbnail_image or 'Nenhuma'}")
print(f"   - Thumbnail Final: {instagram_video.get_thumbnail() or 'NAO DISPONIVEL'}")

# Teste 3: Video do Vimeo (sem thumbnail ainda)
print("\n3. Criando video do Vimeo (sem thumbnail customizada)...")
vimeo_video = Video.objects.create(
    title="[TESTE] Entrevista - Vimeo",
    platform="vimeo",
    video_url="https://vimeo.com/123456789",
    video_type="interview",
    embed_code="123456789",
    description="Video de teste do Vimeo - requer upload de thumbnail"
)
print(f"   - ID: {vimeo_video.id}")
print(f"   - Plataforma: {vimeo_video.get_platform_display()}")
print(f"   - Embed Code: {vimeo_video.embed_code}")
print(f"   - Thumbnail Final: {vimeo_video.get_thumbnail() or 'NAO DISPONIVEL'}")

# Teste 4: Video do TikTok
print("\n4. Criando video do TikTok (sem thumbnail customizada)...")
tiktok_video = Video.objects.create(
    title="[TESTE] Book Review - TikTok",
    platform="tiktok",
    video_url="https://www.tiktok.com/@user/video/123456789",
    video_type="review",
    description="Video de teste do TikTok - requer upload de thumbnail"
)
print(f"   - ID: {tiktok_video.id}")
print(f"   - Plataforma: {tiktok_video.get_platform_display()}")
print(f"   - Thumbnail Final: {tiktok_video.get_thumbnail() or 'NAO DISPONIVEL'}")

print("\n" + "=" * 70)
print("RESUMO DOS TESTES")
print("=" * 70)

all_test_videos = Video.objects.filter(title__startswith='[TESTE]')
print(f"\nTotal de videos de teste criados: {all_test_videos.count()}")

for video in all_test_videos:
    thumbnail_status = "OK" if video.get_thumbnail() else "FALTA THUMBNAIL"
    thumbnail_source = ""
    if video.thumbnail_image:
        thumbnail_source = "(Upload Customizado)"
    elif video.thumbnail_url:
        thumbnail_source = "(YouTube Auto)"

    print(f"\n- {video.title}")
    print(f"  Plataforma: {video.get_platform_display()}")
    print(f"  Status: {thumbnail_status} {thumbnail_source}")
    print(f"  URL: {video.video_url}")

print("\n" + "=" * 70)
print("PROXIMOS PASSOS")
print("=" * 70)
print("\n1. Acesse o admin: /admin/core/video/")
print("2. Localize os videos [TESTE] criados")
print("3. Para Instagram, Vimeo e TikTok:")
print("   - Clique em 'Editar'")
print("   - Na secao 'Thumbnail', faca upload de uma imagem")
print("   - Salve e veja o preview")
print("\n4. Na listagem, voce vera:")
print("   - YouTube: thumbnail automatica")
print("   - Outros: '-' ate fazer upload")

print("\n" + "=" * 70)
