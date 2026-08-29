import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from core.models import Book

with open("db_check2.txt", "w", encoding="utf-8") as f:
    f.write("Analisando os 10 primeiros livros no banco de dados local:\n")
    f.write("-" * 60 + "\n")
    books = Book.objects.all()[:10]
    for b in books:
        has_author = b.author is not None
        has_pages = b.page_count is not None
        has_isbn = bool(b.isbn)
        has_price = b.price is not None
        
        f.write(f"Livro: {b.title}\n")
        f.write(f"  - Autor: {b.author.name if has_author else 'VAZIO'}\n")
        f.write(f"  - Paginas: {b.page_count if has_pages else 'VAZIO'}\n")
        f.write(f"  - ISBN: {b.isbn if has_isbn else 'VAZIO'}\n")
        f.write(f"  - Preco: {b.price if has_price else 'VAZIO'}\n")
        f.write("-" * 60 + "\n")
