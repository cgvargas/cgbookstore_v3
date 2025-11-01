# -*- coding: utf-8 -*-
"""
Debug: Investigar por que livros das prateleiras ainda aparecem

Execute no Django shell:
>>> exec(open('debug_exclusion.py', encoding='utf-8').read())
"""

print("\n" + "="*80)
print("DEBUG: Investigação de Exclusão de Livros")
print("="*80 + "\n")

from django.contrib.auth.models import User
from accounts.models import BookShelf
from recommendations.algorithms_preference_weighted import (
    PreferenceWeightedHybrid,
    get_user_shelf_book_ids
)

# Pegar seu usuário
user = User.objects.first()  # Ajuste se necessário

print(f"1. USUÁRIO: {user.username}")
print("-" * 80)

# Listar TODOS os livros nas prateleiras
shelves = BookShelf.objects.filter(user=user).select_related('book')
print(f"\nTotal de livros nas prateleiras: {shelves.count()}\n")

shelf_books = {}
for shelf in shelves:
    shelf_type = shelf.get_shelf_type_display()
    if shelf_type not in shelf_books:
        shelf_books[shelf_type] = []
    shelf_books[shelf_type].append({
        'id': shelf.book.id,
        'title': shelf.book.title
    })

for shelf_type, books in shelf_books.items():
    print(f"{shelf_type}: {len(books)} livros")
    for book in books:
        print(f"  - ID {book['id']}: {book['title']}")

# Pegar IDs que DEVEM ser excluídos
user_book_ids = get_user_shelf_book_ids(user)
print(f"\n2. IDS QUE DEVEM SER EXCLUÍDOS:")
print("-" * 80)
print(f"Total: {len(user_book_ids)} IDs")
print(f"IDs: {sorted(user_book_ids)}")

# Testar algoritmo
print(f"\n3. TESTANDO ALGORITMO:")
print("-" * 80)

engine = PreferenceWeightedHybrid()
recs = engine.recommend(user, n=6)

print(f"\nRecomendações recebidas: {len(recs)}\n")

# Verificar cada recomendação
violations = []
for i, rec in enumerate(recs, 1):
    book = rec['book']
    book_id = book.id
    is_in_shelf = book_id in user_book_ids

    status = "❌ VIOLAÇÃO" if is_in_shelf else "✅ OK"

    print(f"{i}. {status} - ID {book_id}: {book.title}")

    if is_in_shelf:
        # Encontrar em qual prateleira está
        for shelf in shelves:
            if shelf.book.id == book_id:
                print(f"   → Está em: {shelf.get_shelf_type_display()}")
                violations.append({
                    'id': book_id,
                    'title': book.title,
                    'shelf': shelf.get_shelf_type_display()
                })
                break

# Resumo
print(f"\n4. RESUMO:")
print("-" * 80)

if violations:
    print(f"❌ FALHOU! {len(violations)} livros das prateleiras apareceram:")
    for v in violations:
        print(f"   - {v['title']} (ID {v['id']}) em '{v['shelf']}'")

    print("\n🔍 POSSÍVEIS CAUSAS:")
    print("   1. Cache: get_user_shelf_book_ids() pode estar retornando cache antigo")
    print("   2. Timing: Livros adicionados após o algoritmo ser executado")
    print("   3. Bug no filtro: Verificar código de exclusão")

    print("\n🔧 SOLUÇÃO:")
    print("   1. Limpar cache do Django")
    print("   2. Reiniciar servidor")
    print("   3. Testar novamente")
else:
    print("✅ SUCESSO! Nenhuma violação encontrada")

print("\n" + "="*80 + "\n")
