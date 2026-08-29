import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
import django
django.setup()

from django.conf import settings
from core.storage_backends import CloudflareR2MediaStorage

storage = CloudflareR2MediaStorage()

# Testar URL de uma imagem de livro
test_paths = [
    'books/covers/1984.jpg',
    'authors/photos/stephen-king.jpg',
]

print("=== Teste de URLs geradas pelo Storage Backend ===")
print(f"AWS_S3_CUSTOM_DOMAIN: {settings.AWS_S3_CUSTOM_DOMAIN}")
print(f"AWS_S3_ENDPOINT_URL: {settings.AWS_S3_ENDPOINT_URL}")
print()

for path in test_paths:
    try:
        url = storage.url(path)
        print(f"Path: {path}")
        print(f"URL:  {url}")
        print()
    except Exception as e:
        print(f"ERRO para {path}: {e}")
        print()

# Verificar como os modelos estão salvando as imagens
print("=== Verificando modelos no banco ===")
from core.models import Book
books_with_covers = Book.objects.exclude(cover='').exclude(cover=None)[:5]
print(f"Livros com cover no banco: {books_with_covers.count() if hasattr(books_with_covers, 'count') else 'N/A'}")
for book in books_with_covers:
    print(f"  Livro: {book.title[:40]}")
    print(f"  Cover field: {book.cover}")
    try:
        print(f"  Cover URL: {book.cover.url}")
    except Exception as e:
        print(f"  Cover URL ERRO: {e}")
    print()
