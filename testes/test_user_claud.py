"""
Script para testar a API de recomendações com o usuário 'claud'.
"""
import os
import sys
import django

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import RequestFactory
from recommendations.views_simple import get_recommendations_simple
import json


def test_user_claud():
    print("=" * 70)
    print("TESTE DA API DE RECOMENDAÇÕES - USUÁRIO 'claud'")
    print("=" * 70)

    # Procurar usuário 'claud'
    try:
        user = User.objects.get(username='claud')
        print(f"\n✅ Usuário encontrado: {user.username}")
        print(f"   Email: {user.email}")
        print(f"   Data de cadastro: {user.date_joined}")
    except User.DoesNotExist:
        print("\n❌ ERRO: Usuário 'claud' não encontrado!")
        print("\nUsuários disponíveis:")
        for u in User.objects.all():
            print(f"   - {u.username}")
        return

    # Verificar interações do usuário com livros
    from recommendations.models import UserBookInteraction
    interactions = UserBookInteraction.objects.filter(user=user)
    print(f"\n📊 Total de interações do usuário: {interactions.count()}")

    if interactions.exists():
        print("\nÚltimas 5 interações:")
        for interaction in interactions.order_by('-created_at')[:5]:
            rating_info = f" - Rating: {interaction.rating}" if interaction.rating else ""
            print(f"   - {interaction.book.title} ({interaction.interaction_type}){rating_info}")

    # Criar request fake
    factory = RequestFactory()
    request = factory.get('/recommendations/api/recommendations/?algorithm=hybrid&limit=6')
    request.user = user

    print(f"\n🔄 Testando endpoint: GET /recommendations/api/recommendations/?algorithm=hybrid&limit=6")
    print(f"   Usuário autenticado: {user.username}")

    # Chamar a view
    try:
        response = get_recommendations_simple(request)

        print(f"\n📊 RESPOSTA DA API:")
        print(f"   Status Code: {response.status_code}")

        if response.status_code == 200:
            data = json.loads(response.content)
            print(f"   ✅ Algoritmo: {data['algorithm']}")
            print(f"   ✅ Total de recomendações: {data['count']}")

            if data['count'] == 0:
                print("\n⚠️  AVISO: Nenhuma recomendação gerada.")
                print("   Isso é NORMAL se o usuário não tem interações com livros.")
                print("\n   Para criar dados de teste, execute:")
                print("   python criar_dados_teste_recomendacoes.py")
            else:
                print("\n📚 RECOMENDAÇÕES:")
                for i, rec in enumerate(data['recommendations'], 1):
                    print(f"\n   {i}. {rec['title']}")
                    print(f"      Autor: {rec['author']}")
                    print(f"      Score: {rec['score']:.2f}")
                    print(f"      Razão: {rec['reason']}")
        else:
            print(f"   ❌ ERRO: Status {response.status_code}")
            data = json.loads(response.content)
            print(f"   Mensagem: {data.get('error', 'Erro desconhecido')}")
            if 'detail' in data:
                print(f"   Detalhes: {data['detail']}")

    except Exception as e:
        print(f"\n❌ ERRO AO CHAMAR A VIEW:")
        print(f"   {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 70)
    print("TESTE CONCLUÍDO")
    print("=" * 70)


if __name__ == '__main__':
    test_user_claud()
