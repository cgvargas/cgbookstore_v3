"""
Testar todos os algoritmos de recomendacao para identificar qual esta falhando.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from django.contrib.auth.models import User
from recommendations.algorithms import (
    CollaborativeFilteringAlgorithm,
    ContentBasedFilteringAlgorithm,
    HybridRecommendationSystem
)
from recommendations.algorithms_preference_weighted import PreferenceWeightedHybrid

print("="*60)
print("TESTE DE ALGORITMOS DE RECOMENDACAO")
print("="*60)

# Buscar usuario
user = User.objects.get(username='claud')
print(f"\nUsuario: {user.username}")

algorithms = [
    ('Preference Hybrid (Personalizado)', PreferenceWeightedHybrid),
    ('Hybrid (Hibrido)', HybridRecommendationSystem),
    ('Collaborative (Similares)', CollaborativeFilteringAlgorithm),
    ('Content-Based (Conteudo)', ContentBasedFilteringAlgorithm),
]

print("\n" + "-"*60)
for name, AlgorithmClass in algorithms:
    print(f"\nTestando: {name}")
    try:
        engine = AlgorithmClass()
        recommendations = engine.recommend(user, n=3)
        print(f"  OK: {len(recommendations)} recomendacoes geradas")
        if recommendations:
            print(f"  Primeiro resultado: {recommendations[0].get('title', 'N/A')}")
    except Exception as e:
        print(f"  ERRO: {type(e).__name__}: {str(e)[:100]}")

print("\n" + "="*60)
print("Teste concluido!")
