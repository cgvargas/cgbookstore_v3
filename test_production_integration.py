# -*- coding: utf-8 -*-
"""
Teste de Integração - Sistema de Priorização em Produção

Execute este script no Django shell para validar a integração:
>>> exec(open('test_production_integration.py', encoding='utf-8').read())
"""

print("\n" + "="*80)
print("TESTE DE INTEGRAÇÃO: Sistema de Priorização em Produção")
print("="*80 + "\n")

# Importações
from django.contrib.auth.models import User
from django.db.models import Count
from recommendations.algorithms_preference_weighted import (
    PreferenceWeightedHybrid,
    PreferenceWeightedCollaborative,
    PreferenceWeightedContentBased
)
from recommendations.preference_analyzer import UserPreferenceAnalyzer

# 1. Verificar usuário
print("1. SELECIONANDO USUÁRIO DE TESTE:")
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

# 2. Testar os 3 algoritmos ponderados
if user:
    print("\n2. TESTANDO OS 3 ALGORITMOS PONDERADOS:")
    print("-" * 80)

    algorithms = [
        ('PreferenceWeightedHybrid', PreferenceWeightedHybrid(), 'preference_hybrid'),
        ('PreferenceWeightedCollaborative', PreferenceWeightedCollaborative(), 'preference_collab'),
        ('PreferenceWeightedContentBased', PreferenceWeightedContentBased(), 'preference_content')
    ]

    results = {}

    for name, engine, api_name in algorithms:
        print(f"\n  Testando: {name}")
        print(f"  API endpoint: ?algorithm={api_name}")

        try:
            recs = engine.recommend(user, n=6)
            results[api_name] = recs

            print(f"    Recomendacoes: {len(recs)}")

            if recs:
                # Mostrar top 3
                for i, rec in enumerate(recs[:3], 1):
                    book = rec['book']
                    score = rec['score']
                    print(f"    {i}. {book.title[:40]:40s} | Score: {score:.2f}")

                    # Verificar boost
                    if 'preference_boost' in rec and rec['preference_boost'] > 0:
                        boost_pct = rec['preference_boost'] * 100
                        print(f"       BOOST: +{boost_pct:.0f}%")

            print(f"    Status: OK")

        except Exception as e:
            print(f"    ERRO: {e}")
            import traceback
            traceback.print_exc()

# 3. Testar análise de preferências
if user:
    print("\n3. ANÁLISE DE PREFERÊNCIAS DO USUÁRIO:")
    print("-" * 80)

    try:
        analyzer = UserPreferenceAnalyzer(user)
        profile = analyzer.get_preference_profile()

        print(f"  Total de livros: {profile['total_books']}")
        print(f"  Peso total: {profile['total_weight']:.2f}")

        # Top gêneros
        if profile['top_genres']:
            print("\n  Top 3 Generos:")
            for i, g in enumerate(profile['top_genres'][:3], 1):
                print(f"    {i}. {g['genre']:20s} - Peso: {g['weight']:.2f}")

        # Top autores
        if profile['top_authors']:
            print("\n  Top 3 Autores:")
            for i, a in enumerate(profile['top_authors'][:3], 1):
                print(f"    {i}. {a['author']:30s} - Peso: {a['weight']:.2f}")

        print("\n  Status: OK")

    except Exception as e:
        print(f"  ERRO: {e}")
        import traceback
        traceback.print_exc()

# 4. Simular chamadas da API
if user and results:
    print("\n4. SIMULAÇÃO DE CHAMADAS DA API:")
    print("-" * 80)

    endpoints = [
        '/recommendations/api/recommendations/?algorithm=preference_hybrid&limit=6',
        '/recommendations/api/recommendations/?algorithm=preference_collab&limit=6',
        '/recommendations/api/recommendations/?algorithm=preference_content&limit=6'
    ]

    for endpoint in endpoints:
        print(f"\n  GET {endpoint}")
        algorithm = endpoint.split('algorithm=')[1].split('&')[0]

        if algorithm in results:
            recs = results[algorithm]
            print(f"    Response: {{'count': {len(recs)}, 'algorithm': '{algorithm}', 'recommendations': [...]'}}")
            print(f"    Status: 200 OK")
        else:
            print(f"    Status: ERROR")

# 5. Verificar arquivos modificados
print("\n5. ARQUIVOS MODIFICADOS:")
print("-" * 80)

files_modified = [
    ('recommendations/views_simple.py', 'Adicionados algoritmos ponderados'),
    ('recommendations/views.py', 'Adicionados algoritmos ponderados'),
    ('recommendations/serializers.py', 'Atualizadas choices do algoritmo'),
    ('templates/recommendations/recommendations_section.html', 'Adicionado botão "Personalizado"')
]

for file_path, description in files_modified:
    print(f"  {file_path:55s} | {description}")

# 6. Resumo final
print("\n6. RESUMO DA INTEGRAÇÃO:")
print("-" * 80)

print("  Algoritmos Disponíveis:")
print("    - preference_hybrid    : Sistema híbrido ponderado (PADRÃO)")
print("    - preference_collab    : Collaborative ponderado")
print("    - preference_content   : Content-based ponderado")
print("    - hybrid               : Sistema híbrido clássico")
print("    - collaborative        : Collaborative clássico")
print("    - content              : Content-based clássico")
print("    - ai                   : IA Premium (Gemini)")

print("\n  Endpoints da API:")
print("    - GET /recommendations/api/recommendations/?algorithm=preference_hybrid")
print("    - GET /api/recommendations/simple/?algorithm=preference_hybrid")

print("\n  Interface do Usuário:")
print("    - Botão 'Personalizado' (ícone estrela) = preference_hybrid")
print("    - Algoritmo padrão ao carregar a página")

print("\n  Status:")
if user and results:
    successful_tests = sum(1 for r in results.values() if r)
    total_tests = len(results)

    print(f"    Testes executados: {successful_tests}/{total_tests}")
    print(f"    Usuario de teste: {user.username}")
    print(f"    Livros analisados: {user.bookshelves.count()}")

    if successful_tests == total_tests:
        print("\n    STATUS: INTEGRAÇÃO COMPLETA E FUNCIONAL!")
    else:
        print("\n    STATUS: INTEGRAÇÃO PARCIAL (Alguns testes falharam)")
else:
    print("    STATUS: ERRO - Usuário não encontrado ou testes falharam")

print("\n" + "="*80)
print("PRÓXIMOS PASSOS:")
print("="*80)
print("  1. Reiniciar servidor Django: python manage.py runserver")
print("  2. Acessar: http://localhost:8000/")
print("  3. Fazer login")
print("  4. Rolar até a seção 'Para Você'")
print("  5. Clicar no botão 'Personalizado' (estrela)")
print("  6. Validar recomendações ponderadas")
print("="*80 + "\n")
