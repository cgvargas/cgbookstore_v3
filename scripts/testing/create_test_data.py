"""
Script para carregar dados mínimos para testar recomendações.
Cria usuários, categorias, autores, livros e prateleiras diretamente.
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Book, Category, Author
from accounts.models import BookShelf
from django.core.cache import cache

print("🧹 Limpando cache...")
cache.clear()

# Criar usuários de teste
print("\n👥 Criando usuários...")
users = {}
for uname in ['cgvargas', 'admin', 'test_user1', 'test_user2']:
    user, created = User.objects.get_or_create(
        username=uname,
        defaults={
            'email': f'{uname}@example.com',
            'is_staff': uname == 'admin',
            'is_superuser': uname == 'admin',
        }
    )
    if created:
        user.set_password('test1234')
        user.save()
    users[uname] = user
    print(f"   {'✓ Criado' if created else '○ Existe'}: {uname}")

# Criar categorias
print("\n📁 Criando categorias...")
categories = {}
for cat_name in ['Ficção Científica', 'Fantasia', 'Romance', 'Terror', 'Suspense', 'Autoajuda']:
    cat, _ = Category.objects.get_or_create(
        name=cat_name,
        defaults={'slug': cat_name.lower().replace(' ', '-')}
    )
    categories[cat_name] = cat

# Criar autores  
print("\n✍️ Criando autores...")
authors = {}
for author_name in ['Isaac Asimov', 'J.R.R. Tolkien', 'Stephen King', 'Agatha Christie', 'Paulo Coelho']:
    author, _ = Author.objects.get_or_create(name=author_name)
    authors[author_name] = author

# Criar livros
print("\n📚 Criando livros...")
books_data = [
    ('Fundação', 'Isaac Asimov', 'Ficção Científica'),
    ('O Senhor dos Anéis', 'J.R.R. Tolkien', 'Fantasia'),
    ('O Hobbit', 'J.R.R. Tolkien', 'Fantasia'),
    ('It: A Coisa', 'Stephen King', 'Terror'),
    ('O Iluminado', 'Stephen King', 'Terror'),
    ('Assassinato no Expresso do Oriente', 'Agatha Christie', 'Suspense'),
    ('O Alquimista', 'Paulo Coelho', 'Autoajuda'),
    ('Duna', 'Isaac Asimov', 'Ficção Científica'),  # Atribuindo a Asimov para teste
    ('Silmarillion', 'J.R.R. Tolkien', 'Fantasia'),
    ('Pet Sematary', 'Stephen King', 'Terror'),
]

books = {}
for title, author_name, cat_name in books_data:
    book, created = Book.objects.get_or_create(
        title=title,
        defaults={
            'author': authors[author_name],
            'category': categories[cat_name],
            'slug': title.lower().replace(' ', '-').replace(':', ''),
            'publication_date': '2020-01-01',
        }
    )
    books[title] = book
    if created:
        print(f"   ✓ {title}")

# Criar prateleiras para cgvargas (usuário principal)
print("\n🗄️ Criando prateleiras para cgvargas...")
cgvargas = users['cgvargas']

shelves_data = [
    ('O Senhor dos Anéis', 'favorites'),  # Tolkien - favorito
    ('O Hobbit', 'favorites'),             # Tolkien - favorito
    ('Fundação', 'read'),                  # Asimov - lido
    ('It: A Coisa', 'reading'),            # King - lendo
    ('O Alquimista', 'to_read'),           # Paulo Coelho - quer ler
]

for title, shelf_type in shelves_data:
    if title in books:
        bs, created = BookShelf.objects.get_or_create(
            user=cgvargas,
            book=books[title],
            shelf_type=shelf_type
        )
        if created:
            print(f"   ✓ {title} -> {shelf_type}")

# Criar prateleiras diferentes para test_user1
print("\n🗄️ Criando prateleiras para test_user1...")
test_user1 = users['test_user1']

for title, shelf_type in [('O Alquimista', 'favorites'), ('Pet Sematary', 'read')]:
    if title in books:
        BookShelf.objects.get_or_create(
            user=test_user1,
            book=books[title],
            shelf_type=shelf_type
        )
        print(f"   ✓ {title} -> {shelf_type}")

# Estatísticas
print("\n📊 Estatísticas:")
print(f"   Usuários: {User.objects.count()}")
print(f"   Categorias: {Category.objects.count()}")
print(f"   Autores: {Author.objects.count()}")
print(f"   Livros: {Book.objects.count()}")
print(f"   Prateleiras totais: {BookShelf.objects.count()}")
print(f"   Prateleiras cgvargas: {BookShelf.objects.filter(user=cgvargas).count()}")

print("\n✅ Dados de teste criados com sucesso!")
