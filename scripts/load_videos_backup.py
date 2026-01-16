"""
Script para carregar vídeos do backup.
"""
import os
import json
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from core.models import Video
from django.core.cache import cache

print("🎬 Carregando vídeos do backup...")

# Carregar backup
with open('backup_supabase_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

videos_data = [d for d in data if d['model'] == 'core.video']
print(f"   Vídeos no backup: {len(videos_data)}")

if videos_data:
    print(f"   Campos disponíveis: {list(videos_data[0]['fields'].keys())}")

video_created = 0
video_updated = 0

for v in videos_data:
    pk = v.get('pk')
    f = v['fields']
    
    try:
        existing = Video.objects.filter(pk=pk).first()
        
        if existing:
            video_updated += 1
            continue
            
        # Criar vídeo com campos corretos
        Video.objects.create(
            pk=pk,
            title=f.get('title', ''),
            slug=f.get('slug', ''),
            description=f.get('description', ''),
            platform=f.get('platform', 'youtube'),
            video_url=f.get('video_url', ''),
            video_file=f.get('video_file', ''),
            embed_code=f.get('embed_code', ''),
            video_type=f.get('video_type', 'other'),
            thumbnail_url=f.get('thumbnail_url', ''),
            duration=f.get('duration', ''),
            views_count=f.get('views_count', 0) or 0,
            featured=f.get('featured', False),
            active=f.get('active', True),
        )
        video_created += 1
        print(f"   ✓ {f.get('title', 'Video')[:50]}")
        
    except Exception as e:
        print(f"   ❌ Erro video {pk}: {str(e)[:60]}")

print(f"\n📊 Resultado:")
print(f"   ✓ Criados: {video_created}")
print(f"   ○ Existentes: {video_updated}")
print(f"   Total no banco: {Video.objects.count()}")

cache.clear()
print("\n✅ Concluído!")
