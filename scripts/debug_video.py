import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'cgbookstore.settings'
import django
django.setup()

from core.models import Video

v = Video.objects.get(id=16)
print(f"=== Video ID 16 ===")
print(f"Title: {v.title}")
print(f"Platform: {v.platform}")
print(f"Video URL: {v.video_url}")
print(f"Embed Code (raw): '{v.embed_code}'")
print(f"get_embed_url(): {v.get_embed_url()}")
print()

# Test if embed_code is a valid YouTube ID
if v.embed_code and len(v.embed_code) == 11:
    print(f"✅ Embed code looks like a valid YouTube ID (11 chars)")
else:
    print(f"⚠️ Embed code length is {len(v.embed_code)} (should be 11 for YouTube)")
    
# Verify the video URL format
if 'youtu' in v.video_url:
    print(f"✅ Video URL contains 'youtu' - appears to be YouTube")
else:
    print(f"⚠️ Video URL doesn't look like YouTube: {v.video_url}")
