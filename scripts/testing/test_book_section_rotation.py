"""
scripts/testing/test_book_section_rotation.py

Script de teste para validar a rotação automática de livros em seções da home.
"""
import os
import sys
import django

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from core.models import Book, Section, SectionItem, Category, Author
from core.services.section_service import insert_book_into_section, auto_detect_and_insert_book_section


def run_tests():
    print("\n==================================================")
    print("TESTE DE ROTACAO AUTOMATICA DE SECOES DE LIVROS")
    print("==================================================\n")

    # 1. Obter ou Criar Autor e Categoria de Teste
    author, _ = Author.objects.get_or_create(
        name="Autor Teste Rotacao"
    )
    cat_lancamentos, _ = Category.objects.get_or_create(
        name="Lancamentos Especial",
        defaults={'slug': 'lancamentos-especial'}
    )

    # 2. Criar ou Obter Seção de Teste com max_items=3
    section, created = Section.objects.get_or_create(
        title="Test Lancamentos",
        defaults={
            'content_type': 'books',
            'layout': 'carousel',
            'active': True,
            'max_items': 3,
            'order': 99
        }
    )
    section.max_items = 3
    section.active = True
    section.save()

    # Limpar itens anteriores da seção de teste
    SectionItem.objects.filter(section=section).delete()
    print(f"Secao de Teste configurada: '{section.title}' (max_items={section.max_items})")

    # 3. Criar 4 Livros de Teste
    books = []
    for i in range(1, 5):
        book, _ = Book.objects.get_or_create(
            slug=f"livro-teste-rotacao-{i}",
            defaults={
                'title': f"Livro Teste Rotacao #{i}",
                'author': author,
                'category': cat_lancamentos,
                'publication_date': timezone.now().date(),
                'price': 49.90
            }
        )
        books.append(book)

    print("\n--- PASSO 1: Inserindo Livro #1 ---")
    success, msg = insert_book_into_section(books[0], section)
    print(f"Resultado: {msg}")
    items = SectionItem.objects.filter(section=section, active=True).order_by('order')
    print("Estado atual da secao:")
    for item in items:
        print(f"  Posicao {item.order}: {item.get_display_title()} (id={item.object_id})")

    assert items.count() == 1
    assert items.first().object_id == books[0].id
    assert items.first().order == 0

    print("\n--- PASSO 2: Inserindo Livro #2 ---")
    success, msg = insert_book_into_section(books[1], section)
    print(f"Resultado: {msg}")
    items = SectionItem.objects.filter(section=section, active=True).order_by('order')
    print("Estado atual da secao:")
    for item in items:
        print(f"  Posicao {item.order}: {item.get_display_title()} (id={item.object_id})")

    assert items.count() == 2
    assert items[0].object_id == books[1].id
    assert items[1].object_id == books[0].id

    print("\n--- PASSO 3: Inserindo Livro #3 ---")
    success, msg = insert_book_into_section(books[2], section)
    print(f"Resultado: {msg}")
    items = SectionItem.objects.filter(section=section, active=True).order_by('order')
    print("Estado atual da secao:")
    for item in items:
        print(f"  Posicao {item.order}: {item.get_display_title()} (id={item.object_id})")

    assert items.count() == 3

    print("\n--- PASSO 4: Inserindo Livro #4 (Excedendo max_items=3, deve rotacionar Livro #1) ---")
    success, msg = insert_book_into_section(books[3], section)
    print(f"Resultado: {msg}")
    items = SectionItem.objects.filter(section=section, active=True).order_by('order')
    print("Estado atual da secao:")
    for item in items:
        print(f"  Posicao {item.order}: {item.get_display_title()} (id={item.object_id})")

    # Livro #1 deve ter sido rotacionado (removido) por exceder max_items=3
    assert items.count() == 3
    assert items[0].object_id == books[3].id
    assert items[1].object_id == books[2].id
    assert items[2].object_id == books[1].id
    book_ids_in_section = [it.object_id for it in items]
    assert books[0].id not in book_ids_in_section, "Livro #1 deveria ter sido removido por excesso!"

    print("\n==================================================")
    print("TODOS OS TESTES DE ROTACAO PASSARAM COM SUCESSO!")
    print("==================================================\n")

    # Limpeza do teste
    SectionItem.objects.filter(section=section).delete()
    section.delete()


if __name__ == '__main__':
    run_tests()
