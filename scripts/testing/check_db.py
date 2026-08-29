import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from core.models import Book

print("Analisando os 10 primeiros livros no banco de dados local:")
print("-" * 60)
books = Book.objects.all()[:10]
for b in books:
    has_author = b.author is not None
    has_pages = b.page_count is not None
    has_isbn = bool(b.isbn)
    has_price = b.price is not None
    
    print(f"Livro: {b.title}")
    print(f"  - Autor: {b.author.name if has_author else 'VAZIO'}")
    print(f"  - Páginas: {b.page_count if has_pages else 'VAZIO'}")
    print(f"  - ISBN: {b.isbn if has_isbn else 'VAZIO'}")
    print(f"  - Preço: {b.price if has_price else 'VAZIO'}")
    print("-" * 60)
