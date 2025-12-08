# coding: utf-8
"""
Verificar videos do YouTube Shorts
"""

from core.models import Video

print("\n" + "=" * 70)
print("VERIFICAR YOUTUBE SHORTS")
print("=" * 70)

shorts = Video.objects.filter(video_url__contains='/shorts/')
print(f"\nTotal de Shorts encontrados: {shorts.count()}")

for v in shorts[:5]:
    print(f"\n{v.title}")
    print(f"  URL: {v.video_url}")
    print(f"  Embed Code: {v.embed_code}")
    print(f"  Embed URL: {v.get_embed_url()}")

print("\n" + "=" * 70)
