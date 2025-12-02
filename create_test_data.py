"""
Script para criar dados de teste para o modulo de Autores Emergentes
"""
import os
import sys
import django

# Configurar encoding para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from django.contrib.auth.models import User
from new_authors.models import (
    EmergingAuthor, AuthorBook, Chapter,
    PublisherProfile, AuthorBookReview
)

def create_test_users():
    """Cria usuarios de teste"""
    print("\n[1] Criando usuarios de teste...")

    # Autor 1
    if not User.objects.filter(username='autor_teste1').exists():
        user1 = User.objects.create_user(
            username='autor_teste1',
            email='autor1@teste.com',
            password='teste123',
            first_name='João',
            last_name='Silva'
        )
        print(f"  ✓ Usuario criado: {user1.username}")
    else:
        user1 = User.objects.get(username='autor_teste1')
        print(f"  - Usuario ja existe: {user1.username}")

    # Autor 2
    if not User.objects.filter(username='autor_teste2').exists():
        user2 = User.objects.create_user(
            username='autor_teste2',
            email='autor2@teste.com',
            password='teste123',
            first_name='Maria',
            last_name='Santos'
        )
        print(f"  ✓ Usuario criado: {user2.username}")
    else:
        user2 = User.objects.get(username='autor_teste2')
        print(f"  - Usuario ja existe: {user2.username}")

    # Editora
    if not User.objects.filter(username='editora_teste').exists():
        user3 = User.objects.create_user(
            username='editora_teste',
            email='editora@teste.com',
            password='teste123',
            first_name='Editora',
            last_name='Exemplo'
        )
        print(f"  ✓ Usuario criado: {user3.username}")
    else:
        user3 = User.objects.get(username='editora_teste')
        print(f"  - Usuario ja existe: {user3.username}")

    return user1, user2, user3

def create_authors(user1, user2):
    """Cria perfis de autores emergentes"""
    print("\n[2] Criando perfis de autores emergentes...")

    author1, created = EmergingAuthor.objects.get_or_create(
        user=user1,
        defaults={
            'bio': 'Escritor apaixonado por fantasia e aventura. Estreando no mundo literario com historias envolventes.',
            'is_verified': True,
            'is_active': True
        }
    )
    print(f"  {'✓ Criado' if created else '- Ja existe'}: {author1}")

    author2, created = EmergingAuthor.objects.get_or_create(
        user=user2,
        defaults={
            'bio': 'Autora de romances contemporaneos. Explorando as emocoes humanas atraves da escrita.',
            'is_verified': True,
            'is_active': True
        }
    )
    print(f"  {'✓ Criado' if created else '- Ja existe'}: {author2}")

    return author1, author2

def create_books(author1, author2):
    """Cria livros de teste"""
    print("\n[3] Criando livros de teste...")

    book1, created = AuthorBook.objects.get_or_create(
        author=author1,
        slug='a-jornada-do-heroi',
        defaults={
            'title': 'A Jornada do Heroi',
            'synopsis': 'Um jovem aventureiro descobre seu destino em um mundo magico repleto de desafios e misterios.',
            'genre': 'fantasy',
            'status': 'published',
            'rating_average': 4.5,
            'rating_count': 10,
            'views_count': 150
        }
    )
    print(f"  {'✓ Criado' if created else '- Ja existe'}: {book1.title}")

    book2, created = AuthorBook.objects.get_or_create(
        author=author1,
        slug='sombras-do-passado',
        defaults={
            'title': 'Sombras do Passado',
            'synopsis': 'Um misterio obscuro assombra a pequena cidade. Apenas a verdade pode libertar seus habitantes.',
            'genre': 'mystery',
            'status': 'published',
            'rating_average': 4.2,
            'rating_count': 8,
            'views_count': 120
        }
    )
    print(f"  {'✓ Criado' if created else '- Ja existe'}: {book2.title}")

    book3, created = AuthorBook.objects.get_or_create(
        author=author2,
        slug='amor-em-paris',
        defaults={
            'title': 'Amor em Paris',
            'synopsis': 'Dois coracoes se encontram na cidade luz. Uma historia de amor, superacao e segundas chances.',
            'genre': 'romance',
            'status': 'published',
            'rating_average': 4.8,
            'rating_count': 15,
            'views_count': 200
        }
    )
    print(f"  {'✓ Criado' if created else '- Ja existe'}: {book3.title}")

    return book1, book2, book3

def create_chapters(book1, book2, book3):
    """Cria capitulos de teste"""
    print("\n[4] Criando capitulos de teste...")

    chapters_data = [
        (book1, 1, 'O Chamado', 'Era uma manha como qualquer outra quando tudo mudou...'),
        (book1, 2, 'A Descoberta', 'O artefato brilhava com uma luz misteriosa...'),
        (book1, 3, 'Primeiros Passos', 'A jornada comecava agora, nao havia volta...'),
        (book2, 1, 'A Chegada', 'A cidade parecia tranquila, mas algo estava errado...'),
        (book2, 2, 'Pistas Obscuras', 'Cada pista levava a mais perguntas...'),
        (book3, 1, 'Encontro Inesperado', 'Seus olhos se encontraram na multidao...'),
        (book3, 2, 'Cafe da Manha', 'O aroma do cafe misturava-se com o perfume dela...'),
    ]

    created_count = 0
    for book, number, title, content in chapters_data:
        chapter, created = Chapter.objects.get_or_create(
            book=book,
            number=number,
            defaults={
                'title': title,
                'content': content + '\n\n' + ('Lorem ipsum dolor sit amet. ' * 50),
                'is_published': True,
                'is_free': True,
                'word_count': 300
            }
        )
        if created:
            created_count += 1

    print(f"  ✓ Criados {created_count} novos capitulos")
    return True

def create_publisher(user3):
    """Cria perfil de editora"""
    print("\n[5] Criando perfil de editora...")

    publisher, created = PublisherProfile.objects.get_or_create(
        user=user3,
        defaults={
            'company_name': 'Editora Exemplo LTDA',
            'description': 'Editora especializada em novos talentos literarios. Buscamos historias unicas e autores promissores.',
            'email': 'contato@editoraexemplo.com',
            'website': 'https://editoraexemplo.com',
            'phone': '(11) 98765-4321',
            'is_verified': True,
            'is_active': True
        }
    )
    print(f"  {'✓ Criado' if created else '- Ja existe'}: {publisher.company_name}")

    return publisher

def main():
    """Executa a criacao de dados de teste"""
    print("=" * 60)
    print("CRIANDO DADOS DE TESTE - AUTORES EMERGENTES")
    print("=" * 60)

    try:
        # Criar usuarios
        user1, user2, user3 = create_test_users()

        # Criar autores
        author1, author2 = create_authors(user1, user2)

        # Criar livros
        book1, book2, book3 = create_books(author1, author2)

        # Criar capitulos
        create_chapters(book1, book2, book3)

        # Criar editora
        publisher = create_publisher(user3)

        print("\n" + "=" * 60)
        print("RESUMO")
        print("=" * 60)
        print(f"Usuarios: {User.objects.count()}")
        print(f"Autores: {EmergingAuthor.objects.count()}")
        print(f"Livros: {AuthorBook.objects.count()}")
        print(f"Capitulos: {Chapter.objects.count()}")
        print(f"Editoras: {PublisherProfile.objects.count()}")

        print("\n[OK] Dados de teste criados com sucesso!")
        print("\nCredenciais de teste:")
        print("  Autor 1: autor_teste1 / teste123")
        print("  Autor 2: autor_teste2 / teste123")
        print("  Editora: editora_teste / teste123")

    except Exception as e:
        print(f"\n[ERRO] Falha ao criar dados: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True

if __name__ == '__main__':
    main()
