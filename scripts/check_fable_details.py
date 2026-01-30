import os
import sys
sys.path.insert(0, r'c:\ProjectDjango\cgbookstore_v3')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')

import django
django.setup()

from core.models import Video

v = Video.objects.filter(title__icontains='fable').first()
if v:
    print(f"Title: {v.title}")
    print(f"Platform: {v.platform}")
    print(f"Video File: {v.video_file}")
    if v.video_file:
        print(f"Video File URL: {v.video_file.url}")
else:
    print("Video not found")
