# -*- coding: utf-8 -*-
"""
Teste de Exclusão de Livros das Prateleiras

Valida que livros das prateleiras do usuário NÃO aparecem nas recomendações.

Execute no Django shell:
>>> exec(open('test_shelf_exclusion.py', encoding='utf-8').read())
"""

print("\n" + "="*80)
print("TESTE: Exclusão de Livros das Prateleiras")
print("="*80 + "\n")

# Importações
from django.contrib.auth.models import User
from django.db.models import Count
from accounts.models import BookShelf
from recommendations.algorithms_preference_weighted import (
    PreferenceWeightedHybrid,
    PreferenceWeightedCollaborative,
    PreferenceWeightedContentBased,
    get_user_shelf_book_ids
)

# 1. Selecionar usuário
print("1. SELECIONANDO USUÁRIO:")
print("-" * 80)

try:
    user = User.objects.annotate(
        book_count=Count('bookshelves')
    ).filter(book_count__gt=0).order_by('-book_count').first()

    if not user:
        user = User.objects.first()

    print(f"  Usuario: {user.username}")
    print(f"  Livros na biblioteca: {user.bookshelves.count()}")
except Exception as e:
    print(f"  ERRO: {e}")
    user = None

# 2. Listar livros nas prateleiras
if user:
    print("\n2. LIVROS NAS PRATELEIRAS:")
    print("-" * 80)

    shelves = BookShelf.objects.filter(user=user).select_related('book')
    user_book_ids = get_user_shelf_book_ids(user)

    print(f"  Total: {len(user_book_ids)} livros\n")

    # Agrupar por prateleira
    by_shelf = {}
    for shelf in shelves:
        shelf_type = shelf.get_shelf_type_display()
        if shelf_type not in by_shelf:
            by_shelf[shelf_type] = []
        by_shelf[shelf_type].append(shelf.book.title)

    for shelf_type, books in by_shelf.items():
        print(f"  {shelf_type}: {len(books)} livros")
        for book_title in books[:3]:  # Mostrar apenas 3 primeiros
            print(f"    - {book_title}")
        if len(books) > 3:
            print(f"    ... e mais {len(books) - 3}")

# 3. Testar algoritmos
if user:
    print("\n3. TESTANDO ALGORITMOS:")
    print("-" * 80)

    algorithms = [
        ('PreferenceWeightedHybrid', PreferenceWeightedHybrid()),
        ('PreferenceWeightedCollaborative', PreferenceWeightedCollaborative()),
        ('PreferenceWeightedContentBased', PreferenceWeightedContentBased())
    ]

    all_passed = True

    for name, engine in algorithms:
        print(f"\n  Testando: {name}")

        try:
            recs = engine.recommend(user, n=6)

            # Verificar se alguma recomendação está nas prateleiras
            violations = []
            for rec in recs:
                if rec['book'].id in user_book_ids:
                    violations.append(rec['book'].title)

            if violations:
                print(f"    ❌ FALHOU! {len(violations)} livros das prateleiras apareceram:")
                for title in violations:
                    print(f"       - {title}")
                all_passed = False
            else:
                print(f"    ✅ PASSOU! {len(recs)} recomendações, nenhuma das prateleiras")

                # Mostrar top 3
                for i, rec in enumerate(recs[:3], 1):
                    print(f"       {i}. {rec['book'].title[:40]}")

        except Exception as e:
            print(f"    ❌ ERRO: {e}")
            all_passed = False
            import traceback
            traceback.print_exc()

# 4. Resumo final
print("\n4. RESUMO:")
print("-" * 80)

if user and all_passed:
    print("  ✅ TODOS OS TESTES PASSARAM!")
    print(f"  ✅ {len(user_book_ids)} livros das prateleiras foram corretamente excluídos")
    print("  ✅ Nenhuma recomendação duplicada encontrada")
elif user and not all_passed:
    print("  ❌ ALGUNS TESTES FALHARAM!")
    print("  ❌ Livros das prateleiras aparecem nas recomendações")
    print("  ⚠  Verifique o código de filtro")
else:
    print("  ❌ ERRO - Usuário não encontrado")

print("\n" + "="*80)
print("PRÓXIMOS PASSOS:")
print("="*80)

if all_passed:
    print("  1. Sistema está funcionando corretamente")
    print("  2. Testar na interface web")
    print("  3. Validar com outros usuários")
else:
    print("  1. Revisar código de filtro")
    print("  2. Verificar função get_user_shelf_book_ids()")
    print("  3. Re-executar teste")

print("="*80 + "\n")
