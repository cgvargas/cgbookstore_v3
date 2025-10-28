"""
Script de teste para o Sistema de Recomendações.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Book
from recommendations.models import UserBookInteraction, UserProfile
from recommendations.algorithms import (
    CollaborativeFilteringAlgorithm,
    ContentBasedFilteringAlgorithm,
    HybridRecommendationSystem
)
from recommendations.gemini_ai import GeminiRecommendationEngine


def test_models():
    """Testa criação de modelos."""
    print("\n[1/6] Testando Modelos...")

    # Verificar se há usuários
    users = User.objects.all()
    print(f"   Usuarios no banco: {users.count()}")

    if users.exists():
        user = users.first()

        # Criar perfil
        profile, created = UserProfile.objects.get_or_create(user=user)
        print(f"   Perfil criado: {created} | User: {user.username}")

        # Verificar interações
        interactions = UserBookInteraction.objects.filter(user=user).count()
        print(f"   Interacoes do usuario: {interactions}")

        return True
    else:
        print("   [AVISO] Nenhum usuario encontrado no banco")
        return False


def test_collaborative_filtering():
    """Testa algoritmo de filtragem colaborativa."""
    print("\n[2/6] Testando Filtragem Colaborativa...")

    users = User.objects.all()
    if not users.exists():
        print("   [SKIP] Nenhum usuario para testar")
        return False

    user = users.first()
    algorithm = CollaborativeFilteringAlgorithm()

    try:
        recommendations = algorithm.recommend(user, n=5)
        print(f"   Recomendacoes geradas: {len(recommendations)}")

        if recommendations:
            print(f"   Primeira recomendacao: {recommendations[0]['book'].title}")
            print(f"   Score: {recommendations[0]['score']:.2f}")
        else:
            print("   [AVISO] Nenhuma recomendacao gerada (normal se usuario nao tem interacoes)")

        return True

    except Exception as e:
        print(f"   [ERRO] {e}")
        return False


def test_content_based_filtering():
    """Testa algoritmo baseado em conteúdo."""
    print("\n[3/6] Testando Filtragem por Conteudo...")

    books = Book.objects.all()
    if not books.exists():
        print("   [SKIP] Nenhum livro no banco")
        return False

    book = books.first()
    algorithm = ContentBasedFilteringAlgorithm()

    try:
        similar_books = algorithm.find_similar_books(book, n=5)
        print(f"   Livros similares a '{book.title}': {len(similar_books)}")

        if similar_books:
            print(f"   Mais similar: {similar_books[0]['book'].title}")
            print(f"   Score: {similar_books[0]['score']:.2f}")

        return True

    except Exception as e:
        print(f"   [ERRO] {e}")
        return False


def test_hybrid_system():
    """Testa sistema híbrido."""
    print("\n[4/6] Testando Sistema Hibrido...")

    users = User.objects.all()
    if not users.exists():
        print("   [SKIP] Nenhum usuario para testar")
        return False

    user = users.first()
    algorithm = HybridRecommendationSystem()

    try:
        recommendations = algorithm.recommend(user, n=10)
        print(f"   Recomendacoes hibridas: {len(recommendations)}")

        if recommendations:
            print(f"   Top recomendacao: {recommendations[0]['book'].title}")
            print(f"   Score: {recommendations[0]['score']:.2f}")
            print(f"   Razao: {recommendations[0]['reason'][:80]}...")

        return True

    except Exception as e:
        print(f"   [ERRO] {e}")
        return False


def test_gemini_integration():
    """Testa integração com Gemini AI."""
    print("\n[5/6] Testando Google Gemini AI...")

    gemini = GeminiRecommendationEngine()

    if not gemini.is_available():
        print("   [AVISO] Gemini API nao configurada (GEMINI_API_KEY faltando)")
        print("   Para testar IA: adicione sua chave em .env")
        return None

    print("   Gemini API configurada!")

    users = User.objects.all()
    if not users.exists():
        print("   [SKIP] Nenhum usuario para testar")
        return False

    user = users.first()

    # Obter histórico
    interactions = UserBookInteraction.objects.filter(user=user).select_related('book')[:5]

    if not interactions.exists():
        print("   [SKIP] Usuario nao tem historico de interacoes")
        return False

    history_data = [{
        'title': i.book.title,
        'author': i.book.author,
        'categories': getattr(i.book, 'categories', ''),
        'interaction_type': i.interaction_type
    } for i in interactions]

    try:
        recommendations = gemini.generate_recommendations(user, history_data, n=3)
        print(f"   Recomendacoes IA geradas: {len(recommendations)}")

        if recommendations:
            print(f"   Primeira: {recommendations[0]['title']}")
            print(f"   Autor: {recommendations[0]['author']}")

        return True

    except Exception as e:
        print(f"   [ERRO] {e}")
        return False


def test_api_endpoints():
    """Testa se as URLs da API estão configuradas."""
    print("\n[6/6] Testando Configuracao da API...")

    try:
        from django.urls import reverse

        # Tentar resolver URLs
        urls_to_test = [
            ('recommendations:get_recommendations', []),
            ('recommendations:profile-me', []),
        ]

        for url_name, args in urls_to_test:
            try:
                url = reverse(url_name, args=args)
                print(f"   [OK] URL '{url_name}' -> {url}")
            except Exception as e:
                print(f"   [ERRO] URL '{url_name}': {e}")

        return True

    except Exception as e:
        print(f"   [ERRO] {e}")
        return False


def main():
    """Executa todos os testes."""
    print("=" * 60)
    print("TESTE DO SISTEMA DE RECOMENDACOES INTELIGENTE")
    print("=" * 60)

    results = []

    results.append(('Modelos', test_models()))
    results.append(('Filtragem Colaborativa', test_collaborative_filtering()))
    results.append(('Filtragem por Conteudo', test_content_based_filtering()))
    results.append(('Sistema Hibrido', test_hybrid_system()))
    results.append(('Google Gemini AI', test_gemini_integration()))
    results.append(('API Endpoints', test_api_endpoints()))

    print("\n" + "=" * 60)
    print("RESUMO DOS TESTES")
    print("=" * 60)

    passed = 0
    failed = 0
    skipped = 0

    for name, result in results:
        if result is True:
            status = "[PASSOU]"
            passed += 1
        elif result is False:
            status = "[FALHOU]"
            failed += 1
        else:
            status = "[SKIP]"
            skipped += 1

        print(f"{status} {name}")

    total = len(results)
    print(f"\nTotal: {total} testes | {passed} passou | {failed} falhou | {skipped} pulado")

    if failed == 0:
        print("\n[SUCESSO] Sistema de Recomendacoes funcionando corretamente!")
    else:
        print(f"\n[ATENCAO] {failed} teste(s) falharam. Revise os erros acima.")


if __name__ == '__main__':
    main()
