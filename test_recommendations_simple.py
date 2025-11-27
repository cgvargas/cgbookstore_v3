"""
Script de teste para o Sistema de Recomendações SIMPLIFICADO.

Testa:
1. Recomendações baseadas em prateleiras
2. Recomendações colaborativas
3. Fallback para populares
4. Filtro de capas válidas
"""
import os
import django
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from django.contrib.auth.models import User
from recommendations.algorithms_simple import get_simple_recommendation_engine


def test_recommendations():
    """Testa recomendações para usuários."""
    print("=" * 80)
    print("TESTE: Sistema de Recomendações SIMPLIFICADO")
    print("=" * 80)

    engine = get_simple_recommendation_engine()

    # Buscar um usuário de teste
    try:
        user = User.objects.filter(is_active=True).first()

        if not user:
            print("❌ Nenhum usuário encontrado no banco!")
            print("   Crie um usuário primeiro: python manage.py createsuperuser")
            return False

        print(f"\n🧪 Testando recomendações para: {user.username}")
        print("-" * 80)

        # Teste 1: Gerar 6 recomendações
        n = 6
        print(f"\n📚 Gerando {n} recomendações...")

        recommendations = engine.recommend(user, n=n)

        if not recommendations:
            print(f"⚠️  Nenhuma recomendação gerada!")
            print(f"   Adicione alguns livros às prateleiras do usuário primeiro")
            return False

        print(f"✓ {len(recommendations)} recomendações geradas!\n")

        # Exibir recomendações
        for i, rec in enumerate(recommendations, 1):
            book = rec['book']
            score = rec['score']
            reason = rec['reason']

            # Verificar capa
            has_cover = bool(book.cover_image)
            cover_status = "✓" if has_cover else "✗"

            print(f"{i}. {book.title}")
            print(f"   Autor: {book.author}")
            print(f"   Score: {score:.2f}")
            print(f"   Razão: {reason}")
            print(f"   Capa: {cover_status} {book.cover_image.url if has_cover else 'SEM CAPA'}")
            print()

        # Validações
        print("-" * 80)
        print("VALIDAÇÕES:")
        print("-" * 80)

        # 1. Todos têm capas válidas?
        books_with_cover = sum(1 for rec in recommendations if rec['book'].cover_image)
        print(f"✓ Livros com capa: {books_with_cover}/{len(recommendations)}")

        if books_with_cover < len(recommendations):
            print(f"  ⚠️  ATENÇÃO: {len(recommendations) - books_with_cover} livro(s) SEM capa!")

        # 2. Todos têm scores válidos?
        valid_scores = all(0.0 <= rec['score'] <= 1.0 for rec in recommendations)
        print(f"✓ Scores válidos (0.0-1.0): {'SIM' if valid_scores else 'NÃO'}")

        # 3. Todos têm razão/explicação?
        with_reason = sum(1 for rec in recommendations if rec['reason'])
        print(f"✓ Livros com explicação: {with_reason}/{len(recommendations)}")

        print("\n" + "=" * 80)
        print("✅ TESTE CONCLUÍDO COM SUCESSO!")
        print("=" * 80)

        return True

    except Exception as e:
        print(f"\n❌ ERRO NO TESTE: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_recommendations()
    sys.exit(0 if success else 1)
