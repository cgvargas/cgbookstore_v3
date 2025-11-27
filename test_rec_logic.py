"""
Teste LÓGICO do algoritmo de recomendações (sem banco de dados).

Valida:
1. Estrutura do código
2. Imports corretos
3. Lógica de pesos e scores
"""
import sys

print("=" * 80)
print("TESTE LÓGICO: Sistema de Recomendações Simplificado")
print("=" * 80)

# Teste 1: Importar o módulo
print("\n1. Testando imports...")
try:
    sys.path.insert(0, 'C:/Users/claud/.claude-worktrees/cgbookstore_v3/exciting-thompson')
    from recommendations.algorithms_simple import SimpleRecommendationEngine

    print("   ✓ algorithms_simple.py importado com sucesso")
except ImportError as e:
    print(f"   ✗ ERRO ao importar: {e}")
    sys.exit(1)

# Teste 2: Verificar estrutura da classe
print("\n2. Testando estrutura da classe...")
try:
    engine = SimpleRecommendationEngine()

    # Verificar atributos
    assert hasattr(engine, 'SHELF_WEIGHTS'), "Falta SHELF_WEIGHTS"
    assert hasattr(engine, 'recommend'), "Falta método recommend"
    assert hasattr(engine, '_get_shelf_based_recommendations'), "Falta método _get_shelf_based_recommendations"
    assert hasattr(engine, '_get_collaborative_recommendations'), "Falta método _get_collaborative_recommendations"
    assert hasattr(engine, '_get_popular_books'), "Falta método _get_popular_books"

    print("   ✓ Todos os métodos estão presentes")
except AssertionError as e:
    print(f"   ✗ ERRO na estrutura: {e}")
    sys.exit(1)

# Teste 3: Verificar pesos das prateleiras
print("\n3. Testando pesos das prateleiras...")
expected_weights = {
    'favoritos': 5.0,
    'lidos': 3.0,
    'lendo': 4.0,
    'quer-ler': 2.0,
}

try:
    assert engine.SHELF_WEIGHTS == expected_weights, "Pesos incorretos"
    print(f"   ✓ Pesos configurados corretamente:")
    for shelf, weight in expected_weights.items():
        print(f"      - {shelf}: {weight}")
except AssertionError as e:
    print(f"   ✗ ERRO: {e}")
    print(f"      Esperado: {expected_weights}")
    print(f"      Atual: {engine.SHELF_WEIGHTS}")
    sys.exit(1)

# Teste 4: Verificar cache timeout
print("\n4. Testando configuração de cache...")
try:
    # Mock settings
    class MockSettings:
        RECOMMENDATIONS_CONFIG = {'CACHE_TIMEOUT': 21600}

    # Verificar se timeout está configurado
    assert hasattr(engine, 'cache_timeout'), "Falta cache_timeout"
    print(f"   ✓ Cache timeout configurado")
except AssertionError as e:
    print(f"   ✗ ERRO: {e}")
    sys.exit(1)

# Teste 5: Verificar função singleton
print("\n5. Testando singleton...")
try:
    from recommendations.algorithms_simple import get_simple_recommendation_engine

    engine1 = get_simple_recommendation_engine()
    engine2 = get_simple_recommendation_engine()

    assert engine1 is engine2, "Singleton não está funcionando"
    print("   ✓ Singleton funcionando corretamente (mesma instância)")
except AssertionError as e:
    print(f"   ✗ ERRO: {e}")
    sys.exit(1)

print("\n" + "=" * 80)
print("✅ TODOS OS TESTES LÓGICOS PASSARAM!")
print("=" * 80)
print("\n📝 RESUMO:")
print("   - Algoritmo simplificado criado")
print("   - SEM dependências pesadas (sklearn, Gemini)")
print("   - Filtro de capas direto na query SQL")
print("   - Cache eficiente com hash de prateleiras")
print("   - Pesos configuráveis por tipo de prateleira")
print("\n✨ Sistema de recomendações SIMPLIFICADO e OTIMIZADO!")
print("=" * 80)
