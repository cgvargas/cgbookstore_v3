"""
Teste do sistema de recomendações potencializado com IA + Google Books.
"""
import os
import sys
import django

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from django.contrib.auth.models import User
from recommendations.models import UserBookInteraction
from recommendations.gemini_ai_enhanced import EnhancedGeminiRecommendationEngine

print("=" * 80)
print("TESTE DO SISTEMA DE RECOMENDAÇÕES POTENCIALIZADO")
print("IA + Google Books API")
print("=" * 80)

# Usuário de teste
user = User.objects.get(username='claud')
print(f"\n✅ Usuário: {user.username}")

# Histórico do usuário
user_history = UserBookInteraction.objects.filter(
    user=user
).select_related('book').order_by('-created_at')

history_data = [{
    'title': interaction.book.title,
    'author': str(interaction.book.author) if interaction.book.author else 'Desconhecido',
    'categories': getattr(interaction.book.category, 'name', '') if hasattr(interaction.book, 'category') else '',
    'interaction_type': interaction.interaction_type
} for interaction in user_history]

print(f"\n📚 Total de interações: {len(history_data)}")
print("\n📖 Livros que o usuário já conhece:")
for i, item in enumerate(history_data[:10], 1):
    print(f"   {i}. {item['title']} ({item['interaction_type']})")

# Testar motor potencializado
engine = EnhancedGeminiRecommendationEngine()

if not engine.is_available():
    print("\n❌ Gemini AI não disponível!")
    sys.exit(1)

print(f"\n🤖 Motor potencializado inicializado")
print(f"   Modelo: {engine.model_name}")

print("\n🔄 Gerando recomendações potencializadas...")
print("   (Isso pode levar 10-15 segundos...)")

try:
    recommendations = engine.generate_enhanced_recommendations(
        user,
        history_data,
        n=6
    )

    print(f"\n✅ {len(recommendations)} recomendações geradas!\n")
    print("=" * 80)

    for i, rec in enumerate(recommendations, 1):
        print(f"\n{i}. {rec['title']}")
        print(f"   Autor: {rec['author']}")
        print(f"   Score: {rec['score']:.0%}")
        print(f"   Cover: {'✅ SIM' if rec.get('cover_image') else '❌ NÃO'}")
        print(f"   Google Books ID: {rec.get('google_books_id', 'N/A')}")
        print(f"   Descrição: {rec.get('description', 'N/A')[:100]}...")
        print(f"   Razão: {rec.get('reason', 'N/A')[:100]}...")
        print(f"   Fonte: {rec.get('source', 'N/A')}")

    print("\n" + "=" * 80)
    print("TESTE CONCLUÍDO!")
    print("=" * 80)

except Exception as e:
    print(f"\n❌ ERRO: {e}")
    import traceback
    traceback.print_exc()
