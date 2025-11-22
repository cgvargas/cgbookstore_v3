"""
Fix SectionItem content_type_id references after migration.

The ContentType IDs changed between Supabase and Render databases:
- Books: 9 -> 15 (core.book)
- Authors: 7 -> 14 (core.author)
- Videos: 10 -> 16 (core.video)
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from core.models import SectionItem, Section
from django.contrib.contenttypes.models import ContentType
from core.models import Book, Author, Video

# Get correct ContentType objects
book_ct = ContentType.objects.get_for_model(Book)
author_ct = ContentType.objects.get_for_model(Author)
video_ct = ContentType.objects.get_for_model(Video)

print(f"Correct ContentTypes:")
print(f"  Book: id={book_ct.id} ({book_ct.app_label}.{book_ct.model})")
print(f"  Author: id={author_ct.id} ({author_ct.app_label}.{author_ct.model})")
print(f"  Video: id={video_ct.id} ({video_ct.app_label}.{video_ct.model})")
print()

# Mapping of old content_type_id → new ContentType
# Based on section.content_type field
mappings = {
    9: book_ct,    # Old book CT → New book CT
    7: author_ct,  # Old author CT → New author CT
    10: video_ct,  # Old video CT → New video CT
}

total_fixed = 0

for old_ct_id, new_ct in mappings.items():
    items = SectionItem.objects.filter(content_type_id=old_ct_id)
    count = items.count()

    if count > 0:
        print(f"Fixing {count} items with content_type_id={old_ct_id} -> {new_ct.id} ({new_ct})")

        # Update content_type_id
        items.update(content_type_id=new_ct.id)

        # Verify
        fixed_items = SectionItem.objects.filter(
            content_type_id=new_ct.id,
            object_id__in=items.values_list('object_id', flat=True)
        )

        # Check if content_objects are now valid
        valid_count = 0
        for item in fixed_items[:5]:  # Sample check
            if item.content_object is not None:
                valid_count += 1

        print(f"  OK Updated {count} items")
        print(f"  OK Sample check: {valid_count}/5 items now have valid content_object")
        total_fixed += count
    else:
        print(f"No items with content_type_id={old_ct_id}")
    print()

print(f"\n" + "="*60)
print(f"Total items fixed: {total_fixed}")
print("="*60 + "\n")

# Final verification
print("Verification - Sections and their items:")
sections = Section.objects.filter(active=True).order_by('order')
for section in sections:
    items = section.get_items()
    valid_objects = sum(1 for item in items if item.content_object is not None)
    print(f"  {section.title} ({section.content_type}): {valid_objects}/{items.count()} items with valid objects")

print("\nFix completed!")
