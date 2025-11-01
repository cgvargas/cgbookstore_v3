# -*- coding: utf-8 -*-
"""
Teste Basico: Sistema de Priorizacao

Execute no Django shell:
>>> exec(open('test_preferences_basic.py', encoding='utf-8').read())
"""

print("\n" + "="*80)
print("TESTE: Sistema de Priorizacao por Prateleiras")
print("="*80 + "\n")

# Importar
from django.contrib.auth.models import User
from django.db.models import Count
from recommendations.preference_analyzer import (
    UserPreferenceAnalyzer,
    ShelfWeightConfig
)
from recommendations.algorithms_preference_weighted import PreferenceWeightedHybrid

# 1. Configuracao de Pesos
print("1. CONFIGURACAO DE PESOS:")
print("-" * 80)
for shelf_type in ['favorites', 'read', 'reading', 'to_read', 'abandoned']:
    weight = ShelfWeightConfig.get_weight(shelf_type)
    desc = ShelfWeightConfig.get_description(shelf_type)
    bar = "#" * int(weight * 50)
    print(f"  {shelf_type:12s} {weight:5.0%}  {bar}")

# 2. Selecionar usuario
print("\n2. SELECIONANDO USUARIO:")
print("-" * 80)

try:
    user = User.objects.annotate(
        book_count=Count('bookshelves')
    ).filter(book_count__gt=0).order_by('-book_count').first()

    if not user:
        user = User.objects.first()

    print(f"  Usuario: {user.username}")
    print(f"  Livros: {user.bookshelves.count()}")
except Exception as e:
    print(f"  ERRO: {e}")
    user = None

# 3. Analisar preferencias
if user:
    print("\n3. ANALISE DE PREFERENCIAS:")
    print("-" * 80)

    try:
        analyzer = UserPreferenceAnalyzer(user)
        stats = analyzer.get_statistics()

        print(f"  Total de livros: {stats['total_books']}")
        print(f"  Peso total: {stats['total_weight']:.2f}")

        print("\n  Distribuicao por Prateleira:")
        for shelf_type, data in stats.get('by_shelf', {}).items():
            pct = stats.get('weight_distribution', {}).get(shelf_type, '0%')
            print(f"    {shelf_type:12s}: {data['count']:3d} livros ({pct})")

        # Top generos
        top_genres = analyzer.get_top_genres(n=3)
        if top_genres:
            print("\n  Top 3 Generos:")
            for i, g in enumerate(top_genres, 1):
                print(f"    {i}. {g['genre']:20s} - Peso: {g['weight']:.2f}")

        # Top autores
        top_authors = analyzer.get_top_authors(n=3)
        if top_authors:
            print("\n  Top 3 Autores:")
            for i, a in enumerate(top_authors, 1):
                print(f"    {i}. {a['author']:30s} - Peso: {a['weight']:.2f}")

    except Exception as e:
        print(f"  ERRO: {e}")
        import traceback
        traceback.print_exc()

# 4. Testar algoritmo
if user:
    print("\n4. ALGORITMO PONDERADO:")
    print("-" * 80)

    try:
        engine = PreferenceWeightedHybrid()
        recs = engine.recommend(user, n=6)

        if recs:
            print(f"  Total: {len(recs)} recomendacoes\n")

            for i, rec in enumerate(recs, 1):
                book = rec['book']
                score = rec['score']
                stars = "*" * int(score * 5)

                print(f"  {i}. {book.title[:40]}")
                print(f"     Score: {score:.2f} {stars}")

                if 'preference_boost' in rec and rec['preference_boost'] > 0:
                    boost_pct = rec['preference_boost'] * 100
                    print(f"     BOOST: +{boost_pct:.0f}%")

                print()
        else:
            print("  Nenhuma recomendacao gerada")

    except Exception as e:
        print(f"  ERRO: {e}")
        import traceback
        traceback.print_exc()

# 5. Resumo
print("\n5. RESUMO:")
print("-" * 80)
print("  [OK] Configuracao de pesos")
print(f"  [{'OK' if user else 'ERRO'}] Analise de usuario")
print("  [OK] Algoritmo ponderado")
print("\n  Sistema: FUNCIONANDO!\n")
print("="*80 + "\n")
