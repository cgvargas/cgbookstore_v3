"""
Script para adicionar livros de J.R.R. Tolkien que estão faltando no sistema.
Busca via Google Books API e verifica duplicatas pelo título.
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from core.models import Book, Author, Category
from core.utils.google_books_api import search_books, download_cover, parse_google_books_date

def normalize_title(title):
    """Normaliza título para comparação."""
    if not title:
        return ""
    return title.lower().strip()

def get_existing_tolkien_titles():
    """Retorna lista de títulos de Tolkien já no sistema (normalizados)."""
    tolkien_books = Book.objects.filter(author__name__icontains='tolkien')
    return [normalize_title(b.title) for b in tolkien_books]

def get_or_create_tolkien_author():
    """Obtém ou cria o autor J.R.R. Tolkien."""
    author, created = Author.objects.get_or_create(
        name="J.R.R. Tolkien",
        defaults={
            'bio': 'John Ronald Reuel Tolkien foi um escritor, professor universitário e filólogo britânico, conhecido por criar as obras O Hobbit, O Senhor dos Anéis e O Silmarillion.'
        }
    )
    if created:
        print(f"✅ Autor criado: {author.name}")
    return author

def get_fantasy_category():
    """Obtém ou cria a categoria Fantasia."""
    category, created = Category.objects.get_or_create(
        name="Fantasia",
        defaults={'featured': True}
    )
    if created:
        print(f"✅ Categoria criada: {category.name}")
    return category

def add_tolkien_books():
    """Busca e adiciona livros de Tolkien que estão faltando."""
    
    print("=" * 60)
    print("IMPORTADOR DE LIVROS DE J.R.R. TOLKIEN")
    print("=" * 60)
    
    # Obter títulos existentes
    existing_titles = get_existing_tolkien_titles()
    print(f"\n📚 Livros de Tolkien já no sistema: {len(existing_titles)}")
    for title in existing_titles:
        print(f"   • {title}")
    
    # Buscar no Google Books
    print("\n🔍 Buscando no Google Books API...")
    results = search_books(author='J.R.R. Tolkien', max_results=40)
    
    if 'error' in results:
        print(f"❌ Erro na busca: {results['error']}")
        return
    
    books_found = results.get('books', [])
    print(f"📖 Livros encontrados: {len(books_found)}")
    
    # Filtrar livros que já existem
    author = get_or_create_tolkien_author()
    category = get_fantasy_category()
    
    added_books = []
    skipped_books = []
    
    for book_data in books_found:
        title = book_data.get('title', '')
        normalized = normalize_title(title)
        
        # Verificar se já existe
        if normalized in existing_titles or any(normalized in et or et in normalized for et in existing_titles):
            skipped_books.append(title)
            continue
        
        # Verificar se acabamos de adicionar um similar
        if any(normalize_title(ab['title']) == normalized for ab in added_books):
            continue
        
        # Filtrar apenas livros realmente de Tolkien
        authors_list = book_data.get('authors', [])
        is_tolkien = any('tolkien' in a.lower() for a in authors_list)
        if not is_tolkien:
            continue
        
        # Criar o livro
        try:
            pub_date = parse_google_books_date(book_data.get('published_date'))
            
            book = Book(
                title=title,
                subtitle=book_data.get('subtitle', ''),
                author=author,
                category=category,
                description=book_data.get('description', ''),
                publication_date=pub_date,
                isbn=book_data.get('isbn_13') or book_data.get('isbn_10'),
                publisher=book_data.get('publisher', ''),
                google_books_id=book_data.get('google_book_id'),
                page_count=book_data.get('page_count'),
                average_rating=book_data.get('average_rating'),
                ratings_count=book_data.get('ratings_count'),
                preview_link=book_data.get('preview_link'),
                info_link=book_data.get('info_link'),
                language=book_data.get('language', 'pt'),
            )
            book.save()
            
            # Baixar capa
            thumbnail = book_data.get('thumbnail')
            if thumbnail:
                cover_path = download_cover(thumbnail, book.slug)
                if cover_path:
                    book.cover_image = cover_path
                    book.save()
            
            added_books.append({
                'title': title,
                'isbn': book_data.get('isbn_13') or book_data.get('isbn_10') or 'N/A',
                'publisher': book_data.get('publisher', 'N/A'),
                'pages': book_data.get('page_count', 'N/A'),
            })
            
            # Adicionar à lista de existentes para evitar duplicatas
            existing_titles.append(normalized)
            
            print(f"✅ Adicionado: {title}")
            
        except Exception as e:
            print(f"❌ Erro ao adicionar '{title}': {e}")
    
    # Resumo
    print("\n" + "=" * 60)
    print("RESUMO DA IMPORTAÇÃO")
    print("=" * 60)
    
    if added_books:
        print(f"\n✅ LIVROS ADICIONADOS ({len(added_books)}):")
        print("-" * 60)
        for i, book in enumerate(added_books, 1):
            print(f"{i}. {book['title']}")
            print(f"   📄 ISBN: {book['isbn']}")
            print(f"   🏢 Editora: {book['publisher']}")
            print(f"   📖 Páginas: {book['pages']}")
            print()
    else:
        print("\n⚠️ Nenhum livro novo foi adicionado.")
    
    if skipped_books:
        print(f"\n⏭️ LIVROS IGNORADOS (já existem): {len(skipped_books)}")
        for title in skipped_books[:10]:
            print(f"   • {title}")
        if len(skipped_books) > 10:
            print(f"   ... e mais {len(skipped_books) - 10}")
    
    return added_books

if __name__ == '__main__':
    add_tolkien_books()
