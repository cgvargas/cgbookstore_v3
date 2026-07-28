from django.db import migrations
from django.db.models import Count

def deduplicate_videos_migration(apps, schema_editor):
    Video = apps.get_model('core', 'Video')
    
    # 1. Deduplicate por video_url
    url_groups = Video.objects.exclude(video_url='').values('video_url').annotate(c=Count('id')).filter(c__gt=1)
    for group in url_groups:
        url = group['video_url']
        videos = list(Video.objects.filter(video_url=url).order_by('id'))
        canonical = videos[0]
        duplicates = videos[1:]
        for dup in duplicates:
            books = list(dup.related_books.all())
            if books:
                canonical.related_books.add(*books)
            dup.delete()

    # 2. Deduplicate por embed_code
    embed_groups = Video.objects.exclude(embed_code='').values('embed_code').annotate(c=Count('id')).filter(c__gt=1)
    for group in embed_groups:
        code = group['embed_code']
        videos = list(Video.objects.filter(embed_code=code).order_by('id'))
        canonical = videos[0]
        duplicates = videos[1:]
        for dup in duplicates:
            books = list(dup.related_books.all())
            if books:
                canonical.related_books.add(*books)
            dup.delete()

    # 3. Deduplicate por titulo (case-insensitive)
    all_videos = list(Video.objects.all())
    title_dict = {}
    for v in all_videos:
        key = v.title.strip().lower()
        title_dict.setdefault(key, []).append(v)

    for key, videos in title_dict.items():
        if len(videos) > 1:
            canonical = videos[0]
            duplicates = videos[1:]
            for dup in duplicates:
                books = list(dup.related_books.all())
                if books:
                    canonical.related_books.add(*books)
                dup.delete()

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0049_remove_video_related_book_video_related_books'),
    ]

    operations = [
        migrations.RunPython(deduplicate_videos_migration, reverse_code=migrations.RunPython.noop),
    ]
