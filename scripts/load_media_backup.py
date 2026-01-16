"""
Script para carregar vídeos e atualizar fotos de autores do backup.
"""
import os
import json
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from core.models import Author, Video
from django.core.cache import cache

print("📦 Carregando dados do backup...")

# Carregar backup
with open('backup_supabase_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# ========== AUTORES ==========
print("\n👤 Atualizando autores...")
authors_data = [d for d in data if d['model'] == 'core.author']
print(f"   Autores no backup: {len(authors_data)}")

author_updated = 0
for a in authors_data:
    pk = a.get('pk')
    f = a['fields']
    
    try:
        author = Author.objects.filter(pk=pk).first()
        if not author:
            # Criar autor se não existir
            author = Author.objects.create(
                pk=pk,
                name=f.get('name', ''),
                slug=f.get('slug', ''),
                bio=f.get('bio', ''),
                photo=f.get('photo', ''),
                website=f.get('website', ''),
            )
            author_updated += 1
        else:
            # Atualizar foto se estiver vazia
            if not author.photo and f.get('photo'):
                author.photo = f.get('photo', '')
                author.save(update_fields=['photo'])
                author_updated += 1
    except Exception as e:
        print(f"   ❌ Erro autor {pk}: {str(e)[:40]}")

print(f"   ✓ Autores atualizados: {author_updated}")

# ========== VÍDEOS ==========
print("\n🎬 Carregando vídeos...")
videos_data = [d for d in data if d['model'] == 'core.video']
print(f"   Vídeos no backup: {len(videos_data)}")

video_created = 0
for v in videos_data:
    pk = v.get('pk')
    f = v['fields']
    
    try:
        if not Video.objects.filter(pk=pk).exists():
            Video.objects.create(
                pk=pk,
                title=f.get('title', ''),
                slug=f.get('slug', ''),
                description=f.get('description', ''),
                video_file=f.get('video_file', ''),
                video_url=f.get('video_url', ''),
                thumbnail=f.get('thumbnail', ''),
                is_active=f.get('is_active', True),
            )
            video_created += 1
            print(f"   ✓ {f.get('title', 'Video')[:40]}")
    except Exception as e:
        print(f"   ❌ Erro video {pk}: {str(e)[:40]}")

print(f"   ✓ Vídeos criados: {video_created}")

# Estatísticas
cache.clear()
print(f"\n📊 Estatísticas finais:")
print(f"   Autores: {Author.objects.count()}")
print(f"   Autores com foto: {Author.objects.exclude(photo='').count()}")
print(f"   Vídeos: {Video.objects.count()}")

print("\n✅ Carregamento concluído!")
