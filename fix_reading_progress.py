"""
Fix missing ReadingProgress for books in 'reading' shelf.

Users who added books to "Lendo" shelf before the fix may not have
ReadingProgress objects. This script creates them.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from accounts.models import BookShelf, ReadingProgress
from django.contrib.auth import get_user_model

User = get_user_model()

print("="*60)
print("FIXING MISSING READING PROGRESS")
print("="*60)

# Get all BookShelf with shelf_type='reading'
reading_shelves = BookShelf.objects.filter(shelf_type='reading').select_related('book', 'user')

print(f"\nFound {reading_shelves.count()} books in 'Lendo' shelf\n")

fixed_count = 0
skipped_count = 0

for shelf in reading_shelves:
    user = shelf.user
    book = shelf.book

    # Check if ReadingProgress already exists
    progress_exists = ReadingProgress.objects.filter(user=user, book=book).exists()

    if progress_exists:
        print(f"SKIP: {user.username} - {book.title} (already has progress)")
        skipped_count += 1
    else:
        # Create ReadingProgress
        progress = ReadingProgress.objects.create(
            user=user,
            book=book,
            total_pages=book.page_count or 1,  # Use 1 as fallback
            current_page=0
        )
        print(f"FIXED: {user.username} - {book.title} (created progress: 0/{progress.total_pages})")
        fixed_count += 1

print("\n" + "="*60)
print(f"SUMMARY:")
print(f"  Created: {fixed_count}")
print(f"  Skipped: {skipped_count}")
print(f"  Total:   {fixed_count + skipped_count}")
print("="*60)
