import os
import sys
import django

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from core.models import Video
from django.db.models import Count

def deduplicate_videos():
    print("[INFO] Iniciando analise de videos duplicados no banco de dados...")
    
    # 1. Agrupar por video_url
    url_groups = Video.objects.exclude(video_url='').values('video_url').annotate(c=Count('id')).filter(c__gt=1)
    merged_count = 0
    deleted_count = 0

    for group in url_groups:
        url = group['video_url']
        videos = list(Video.objects.filter(video_url=url).order_by('id'))
        canonical = videos[0]
        duplicates = videos[1:]

        print(f"\n[DUPLICADO POR URL] '{canonical.title}' (ID {canonical.id}) - {len(videos)} copias")
        
        for dup in duplicates:
            books = list(dup.related_books.all())
            if books:
                canonical.related_books.add(*books)
                print(f"   --> Transferidos {len(books)} livro(s) do ID {dup.id} para o ID {canonical.id}")
            dup.delete()
            deleted_count += 1
        merged_count += 1

    # 2. Agrupar por embed_code (se não vazio)
    embed_groups = Video.objects.exclude(embed_code='').values('embed_code').annotate(c=Count('id')).filter(c__gt=1)
    for group in embed_groups:
        code = group['embed_code']
        videos = list(Video.objects.filter(embed_code=code).order_by('id'))
        canonical = videos[0]
        duplicates = videos[1:]

        print(f"\n[DUPLICADO POR EMBED] '{canonical.title}' (ID {canonical.id}) - {len(videos)} copias")
        
        for dup in duplicates:
            books = list(dup.related_books.all())
            if books:
                canonical.related_books.add(*books)
                print(f"   --> Transferidos {len(books)} livro(s) do ID {dup.id} para o ID {canonical.id}")
            dup.delete()
            deleted_count += 1
        merged_count += 1

    # 3. Agrupar por título (case-insensitive)
    all_videos = list(Video.objects.all())
    title_dict = {}
    for v in all_videos:
        key = v.title.strip().lower()
        title_dict.setdefault(key, []).append(v)

    for key, videos in title_dict.items():
        if len(videos) > 1:
            canonical = videos[0]
            duplicates = videos[1:]
            print(f"\n[DUPLICADO POR TITULO] '{canonical.title}' (ID {canonical.id}) - {len(videos)} copias")
            for dup in duplicates:
                books = list(dup.related_books.all())
                if books:
                    canonical.related_books.add(*books)
                    print(f"   --> Transferidos {len(books)} livro(s) do ID {dup.id} para o ID {canonical.id}")
                dup.delete()
                deleted_count += 1
            merged_count += 1

    print(f"\n[SUCESSO] {merged_count} grupo(s) de videos mesclados. {deleted_count} copia(s) removida(s). Total de videos unicos agora: {Video.objects.count()}")

if __name__ == '__main__':
    deduplicate_videos()
