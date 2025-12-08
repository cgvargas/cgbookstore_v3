# coding: utf-8
"""
Script para testar o modal de video
"""

from core.models import Video
from django.template import Template, Context

print("\n" + "=" * 70)
print("TESTE DO MODAL DE VIDEO")
print("=" * 70)

# Testar videos
videos = Video.objects.all()[:5]

for video in videos:
    print(f"\n{video.title}")
    print(f"  Platform: {video.platform}")
    print(f"  Embed Code: {video.embed_code}")
    print(f"  Get Embed URL: {video.get_embed_url()}")

    # Testar template
    t = Template('{{ video.get_embed_url }}')
    rendered = t.render(Context({'video': video}))
    print(f"  Template Rendered: [{rendered}]")
    print(f"  Is 'None' string?: {rendered == 'None'}")
    print(f"  Is empty?: {rendered == ''}")

print("\n" + "=" * 70)
