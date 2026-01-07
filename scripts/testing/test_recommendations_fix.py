"""
Script de teste para verificar correções do sistema de recomendações.
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from django.contrib.auth.models import User
from django.core.cache import cache
from recommendations.algorithms_simple import SimpleRecommendationEngine
from accounts.models import BookShelf

# Limpar cache
cache.clear()
print("✓ Cache limpo")

# Mostrar SHELF_WEIGHTS corrigidos
engine = SimpleRecommendationEngine()
print(f"\n📋 SHELF_WEIGHTS: {engine.SHELF_WEIGHTS}")

# Testar com diferentes usuários
users = User.objects.all()[:3]

for user in users:
    print(f"\n{'='*50}")
    print(f"👤 Usuário: {user.username}")
    
    # Contar prateleiras por tipo
    shelves = BookShelf.objects.filter(user=user)
    print(f"   Prateleiras: {shelves.count()} livros")
    
    for shelf_type in ['favorites', 'reading', 'read', 'to_read']:
        count = shelves.filter(shelf_type=shelf_type).count()
        if count > 0:
            weight = engine.SHELF_WEIGHTS.get(shelf_type, 1.0)
            print(f"   - {shelf_type}: {count} livros (peso: {weight})")
    
    # Gerar recomendações
    recs = engine.recommend(user, n=3)
    print(f"\n   📚 Recomendações ({len(recs)}):")
    
    for i, rec in enumerate(recs, 1):
        title = rec['book'].title[:40] + "..." if len(rec['book'].title) > 40 else rec['book'].title
        print(f"   {i}. {title} (score: {rec['score']:.2f})")

print("\n✅ Teste concluído!")
