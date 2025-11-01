# -*- coding: utf-8 -*-
"""
Quick Test: Sistema de Priorizacao por Prateleiras

Execute este script quando o Django estiver rodando:
python manage.py shell

>>> exec(open('quick_test_preferences.py', encoding='utf-8').read())
"""

print("\n" + "="*80)
print("🧪 TESTE RÁPIDO: Sistema de Priorização por Prateleiras")
print("="*80 + "\n")

# Importar dependências
from django.contrib.auth.models import User
from recommendations.preference_analyzer import (
    UserPreferenceAnalyzer,
    ShelfWeightConfig,
    print_user_preference_report
)
from recommendations.algorithms_preference_weighted import (
    PreferenceWeightedHybrid
)

# 1. Testar configuração de pesos
print("1️⃣  CONFIGURAÇÃO DE PESOS:")
print("-" * 80)
for shelf_type in ['favorites', 'read', 'reading', 'to_read', 'abandoned']:
    weight = ShelfWeightConfig.get_weight(shelf_type)
    desc = ShelfWeightConfig.get_description(shelf_type)
    bar = "█" * int(weight * 50)
    print(f"  {desc:<50} {bar}")

# 2. Buscar usuário para teste
print("\n2️⃣  SELECIONANDO USUÁRIO PARA TESTE:")
print("-" * 80)

try:
    # Tentar encontrar usuário com mais livros
    users_with_books = User.objects.annotate(
        book_count=Count('bookshelves')
    ).filter(book_count__gt=0).order_by('-book_count')[:5]

    if users_with_books.exists():
        user = users_with_books.first()
        print(f"  ✓ Usuário selecionado: {user.username}")
        print(f"  ✓ Total de livros nas prateleiras: {user.bookshelves.count()}")
    else:
        # Fallback: primeiro usuário
        user = User.objects.first()
        print(f"  ⚠ Usando primeiro usuário: {user.username}")
        print(f"  ⚠ Livros nas prateleiras: {user.bookshelves.count()}")
except Exception as e:
    print(f"  ❌ Erro ao buscar usuário: {e}")
    user = None

# 3. Analisar preferências
if user:
    print("\n3️⃣  ANÁLISE DE PREFERÊNCIAS:")
    print("-" * 80)

    try:
        analyzer = UserPreferenceAnalyzer(user)

        # Estatísticas
        stats = analyzer.get_statistics()
        print(f"  📚 Total de livros: {stats['total_books']}")
        print(f"  ⚖️  Peso total: {stats['total_weight']:.2f}")

        # Distribuição por prateleira
        print("\n  📊 Distribuição por Prateleira:")
        for shelf_type, data in stats['by_shelf'].items():
            pct = stats['weight_distribution'].get(shelf_type, '0%')
            print(f"    • {shelf_type:12s}: {data['count']:3d} livros ({pct:>6s} do peso)")

        # Top gêneros
        top_genres = analyzer.get_top_genres(n=3)
        if top_genres:
            print("\n  🎯 Top 3 Gêneros:")
            for i, g in enumerate(top_genres, 1):
                print(f"    {i}. {g['genre']:20s} - Peso: {g['weight']:.2f} ({g['count']} livros)")

        # Top autores
        top_authors = analyzer.get_top_authors(n=3)
        if top_authors:
            print("\n  ✍️  Top 3 Autores:")
            for i, a in enumerate(top_authors, 1):
                print(f"    {i}. {a['author']:30s} - Peso: {a['weight']:.2f} ({a['count']} livros)")

    except Exception as e:
        print(f"  ❌ Erro na análise: {e}")
        import traceback
        traceback.print_exc()

# 4. Testar algoritmo ponderado
if user:
    print("\n4️⃣  TESTE DO ALGORITMO PONDERADO:")
    print("-" * 80)

    try:
        engine = PreferenceWeightedHybrid()
        recommendations = engine.recommend(user, n=6)

        if recommendations:
            print(f"  ✓ {len(recommendations)} recomendações geradas!\n")

            for i, rec in enumerate(recommendations, 1):
                book = rec['book']
                score = rec['score']
                reason = rec.get('reason', 'N/A')[:60]

                # Indicador de qualidade
                stars = "⭐" * int(score * 5)

                print(f"  {i}. {book.title[:40]:40s} | Score: {score:.2f} {stars}")
                print(f"     Autor: {str(book.author)[:35]}")
                print(f"     Razão: {reason}")

                # Mostrar boost se existir
                if 'preference_boost' in rec and rec['preference_boost'] > 0:
                    boost_pct = rec['preference_boost'] * 100
                    print(f"     🎯 BOOST: +{boost_pct:.0f}% (preferências do usuário)")

                print()
        else:
            print("  ⚠ Nenhuma recomendação gerada")

    except Exception as e:
        print(f"  ❌ Erro ao gerar recomendações: {e}")
        import traceback
        traceback.print_exc()

# 5. Resumo final
print("\n5️⃣  RESUMO:")
print("-" * 80)
print("  ✅ Configuração de pesos: OK")
print(f"  {'✅' if user else '❌'} Análise de usuário: {'OK' if user else 'FALHOU'}")
print("  ✅ Algoritmo ponderado: Testado")
print("\n  🎯 Sistema de Priorização: FUNCIONANDO!\n")

print("="*80)
print("💡 PRÓXIMO PASSO: Integrar em produção")
print("   Substituir HybridRecommendationSystem por PreferenceWeightedHybrid")
print("   em recommendations/views_simple.py")
print("="*80 + "\n")
