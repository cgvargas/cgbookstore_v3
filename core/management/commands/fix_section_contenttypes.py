"""
Django management command to fix SectionItem content_type_id references.

Usage:
    python manage.py fix_section_contenttypes

This fixes ContentType IDs that changed during migration from Supabase to Render.
"""
from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from core.models import SectionItem, Section, Book, Author, Video


class Command(BaseCommand):
    help = 'Fix SectionItem content_type_id references after migration'

    def handle(self, *args, **options):
        self.stdout.write("=" * 60)
        self.stdout.write("FIXING SECTIONITEM CONTENT_TYPE IDS")
        self.stdout.write("=" * 60)

        # Get correct ContentType objects
        book_ct = ContentType.objects.get_for_model(Book)
        author_ct = ContentType.objects.get_for_model(Author)
        video_ct = ContentType.objects.get_for_model(Video)

        self.stdout.write(f"\nCorrect ContentTypes:")
        self.stdout.write(f"  Book: id={book_ct.id} ({book_ct.app_label}.{book_ct.model})")
        self.stdout.write(f"  Author: id={author_ct.id} ({author_ct.app_label}.{author_ct.model})")
        self.stdout.write(f"  Video: id={video_ct.id} ({video_ct.app_label}.{video_ct.model})")
        self.stdout.write("")

        # Mapping: old_ct_id -> new ContentType
        # These are the old IDs from Supabase that need to be updated
        mappings = {
            9: book_ct,    # Old book CT -> New book CT
            7: author_ct,  # Old author CT -> New author CT
            10: video_ct,  # Old video CT -> New video CT
        }

        total_fixed = 0

        for old_ct_id, new_ct in mappings.items():
            items = SectionItem.objects.filter(content_type_id=old_ct_id)
            count = items.count()

            if count > 0:
                self.stdout.write(
                    f"Fixing {count} items with content_type_id={old_ct_id} -> {new_ct.id} ({new_ct})"
                )

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

                self.stdout.write(self.style.SUCCESS(f"  OK Updated {count} items"))
                self.stdout.write(
                    self.style.SUCCESS(
                        f"  OK Sample check: {valid_count}/5 items now have valid content_object"
                    )
                )
                total_fixed += count
            else:
                self.stdout.write(f"No items with content_type_id={old_ct_id}")

            self.stdout.write("")

        self.stdout.write("=" * 60)
        self.stdout.write(self.style.SUCCESS(f"Total items fixed: {total_fixed}"))
        self.stdout.write("=" * 60)
        self.stdout.write("")

        # Final verification
        self.stdout.write("Verification - Sections and their items:")
        sections = Section.objects.filter(active=True).order_by('order')

        all_valid = True
        for section in sections:
            items = section.get_items()
            valid_objects = sum(1 for item in items if item.content_object is not None)
            total_items = items.count()

            status = self.style.SUCCESS('OK') if valid_objects == total_items else self.style.ERROR('FAIL')
            self.stdout.write(
                f"  [{status}] {section.title} ({section.content_type}): "
                f"{valid_objects}/{total_items} items with valid objects"
            )

            if valid_objects != total_items:
                all_valid = False

        self.stdout.write("")

        if all_valid and total_fixed > 0:
            self.stdout.write(self.style.SUCCESS("Fix completed successfully!"))
        elif total_fixed == 0:
            self.stdout.write(self.style.WARNING("No items needed fixing. All ContentTypes are correct."))
        else:
            self.stdout.write(self.style.ERROR("Some items still have issues. Check logs above."))
