"""
Script para diagnosticar problemas com imagens do Supabase
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from core.models import Book
from django.conf import settings
from core.utils.supabase_storage import supabase_storage_admin

print("=" * 80)
print("DIAGNÓSTICO DE IMAGENS - SUPABASE STORAGE")
print("=" * 80)

# 1. Verificar configuração
print("\n1. CONFIGURAÇÕES:")
print(f"   USE_SUPABASE_STORAGE: {settings.USE_SUPABASE_STORAGE}")
print(f"   SUPABASE_URL: {settings.SUPABASE_URL}")
print(f"   SUPABASE_ANON_KEY: {'OK - Configurada' if settings.SUPABASE_ANON_KEY else 'ERRO - NAO CONFIGURADA'}")

# 2. Testar conexão com Supabase
print("\n2. CONEXÃO COM SUPABASE:")
try:
    # Listar buckets
    print("   Tentando listar buckets...")
    buckets_info = {
        'book-covers': supabase_storage_admin.BOOK_COVERS_BUCKET,
        'author-photos': supabase_storage_admin.AUTHOR_PHOTOS_BUCKET,
        'user-avatars': supabase_storage_admin.USER_AVATARS_BUCKET,
    }
    print(f"   OK - Buckets configurados: {list(buckets_info.keys())}")
except Exception as e:
    print(f"   ERRO ao conectar: {str(e)}")

# 3. Verificar livros no banco de dados
print("\n3. LIVROS NO BANCO DE DADOS:")
books = Book.objects.all()[:10]
print(f"   Total de livros: {Book.objects.count()}")

if books.exists():
    print("\n   Primeiros 10 livros:")
    for book in books:
        print(f"\n   📚 {book.title}")
        print(f"      ID: {book.id}")
        print(f"      Cover Field: {book.cover_image}")

        # Tentar obter URL
        try:
            if book.cover_image:
                url = book.cover_image.url
                print(f"      Cover URL: {url}")
            else:
                print(f"      Cover URL: (Sem imagem)")
        except Exception as e:
            print(f"      Cover URL: ✗ Erro: {str(e)}")
else:
    print("   ✗ Nenhum livro encontrado no banco de dados")

# 4. Testar acesso direto ao Storage
print("\n4. TESTE DE ACESSO AO STORAGE:")
try:
    # Tentar listar arquivos do bucket de capas
    print(f"   Listando arquivos no bucket '{supabase_storage_admin.BOOK_COVERS_BUCKET}'...")
    files = supabase_storage_admin.list_files(supabase_storage_admin.BOOK_COVERS_BUCKET, '')
    print(f"   ✓ Encontrados {len(files)} arquivos/pastas")

    if files:
        print("\n   Primeiros 5 arquivos/pastas:")
        for i, file_info in enumerate(files[:5], 1):
            name = file_info.get('name', 'N/A')
            print(f"      {i}. {name}")

except Exception as e:
    print(f"   ✗ Erro ao listar arquivos: {str(e)}")

# 5. Verificar URLs públicas
print("\n5. TESTE DE URLs PÚBLICAS:")
if books.exists() and books.first().cover_image:
    first_book = books.first()
    try:
        public_url = first_book.cover_image.url
        print(f"   Exemplo de URL gerada:")
        print(f"   {public_url}")
        print(f"   ✓ URL gerada com sucesso")
    except Exception as e:
        print(f"   ✗ Erro ao gerar URL: {str(e)}")

print("\n" + "=" * 80)
print("DIAGNÓSTICO COMPLETO")
print("=" * 80)
