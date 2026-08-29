import os
import django
import sys

# Redirecionar stdout para UTF-8
sys.stdout = open('verify_url_utf8.txt', 'w', encoding='utf-8')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from ereader.services.gutenberg import GutenbergService

def test_get_book_url(id):
    print(f"--- Testing get_book for ID {id} ---")
    service = GutenbergService()
    try:
        book = service.get_book(id)
        if book:
            print(f"Title: {book['title']}")
            print(f"EPUB URL: {book['epub_url']}")
            
            if "-images.epub" in book['epub_url']:
                print("SUCCESS: Optimized URL selected.")
            elif "epub3" in book['epub_url']:
                print("WARNING: Creating EPUB3 URL (Optimization might have failed or not available).")
            else:
                print(f"INFO: URL format: {book['epub_url']}")
        else:
            print("Book not found.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_get_book_url("55752") # Dom Casmurro
