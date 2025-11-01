"""
Script para testar recomendações de IA Premium do Google Books.
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from django.contrib.auth import get_user_model
from recommendations.gemini_ai_enhanced import EnhancedGeminiRecommendationEngine
from recommendations.models import UserBookInteraction

User = get_user_model()

def test_enhanced_recommendations():
    """Testa o sistema de recomendações potencializadas."""

    # Pegar um usuário (ajuste conforme necessário)
    try:
        # Tentar pegar o primeiro usuário com histórico
        user = User.objects.filter(
            book_interactions__isnull=False
        ).distinct().first()

        if not user:
            # Se não houver usuários com histórico, pegar qualquer usuário
            user = User.objects.first()

        if not user:
            print("ERRO: Nenhum usuario encontrado no banco de dados")
            return

        print(f"Testando recomendacoes para usuario: {user.username}")
        print(f"Historico: {UserBookInteraction.objects.filter(user=user).count()} interacoes")
        print("-" * 80)

        # Criar engine
        engine = EnhancedGeminiRecommendationEngine()

        if not engine.is_available():
            print("ERRO: Gemini AI nao esta disponivel. Verifique GEMINI_API_KEY no .env")
            return

        # Obter histórico
        user_history = UserBookInteraction.objects.filter(
            user=user
        ).select_related('book').order_by('-created_at')[:20]

        history_data = [{
            'title': interaction.book.title,
            'author': str(interaction.book.author) if interaction.book.author else 'Desconhecido',
            'categories': getattr(interaction.book.category, 'name', '') if hasattr(interaction.book, 'category') else '',
            'interaction_type': interaction.interaction_type
        } for interaction in user_history]

        print(f"Livros no historico:")
        for h in history_data[:5]:
            print(f"   - {h['title']} ({h['interaction_type']})")
        if len(history_data) > 5:
            print(f"   ... e mais {len(history_data) - 5} livros")
        print("-" * 80)

        # Gerar recomendações
        print("Gerando recomendacoes com IA Premium (Google Books)...")
        recommendations = engine.generate_enhanced_recommendations(
            user,
            history_data,
            n=6
        )

        print("-" * 80)
        print(f"RESULTADO: {len(recommendations)} recomendacoes geradas")
        print("-" * 80)

        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                print(f"\n{i}. {rec['title']}")
                print(f"   Autor: {rec['author']}")
                print(f"   Razao: {rec['reason']}")
                print(f"   Capa: {'OK' if rec.get('cover_image') else 'NAO'}")
                print(f"   Google Books ID: {rec.get('google_books_id', 'N/A')}")
                print(f"   Source: {rec.get('source', 'N/A')}")
        else:
            print("ERRO: Nenhuma recomendacao foi gerada")
            print("\nPossiveis causas:")
            print("1. Gemini AI nao sugeriu livros")
            print("2. Todos os livros sugeridos foram filtrados (sem capa)")
            print("3. Nenhum livro foi encontrado no Google Books")
            print("\nVerifique os logs acima para mais detalhes.")

    except Exception as e:
        print(f"ERRO durante o teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_enhanced_recommendations()
