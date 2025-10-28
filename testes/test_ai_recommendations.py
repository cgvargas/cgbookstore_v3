"""
Teste completo do algoritmo de recomendações com IA.
"""
import os
import sys
import django

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import RequestFactory
from recommendations.views_simple import get_recommendations_simple
import json

print("=" * 70)
print("TESTE DO ALGORITMO IA PREMIUM")
print("=" * 70)

# Usar o usuário claud
user = User.objects.get(username='claud')
print(f"\n✅ Usuário: {user.username}")

# Criar request fake para algoritmo IA
factory = RequestFactory()
request = factory.get('/recommendations/api/recommendations/?algorithm=ai&limit=6')
request.user = user

print(f"\n🤖 Testando algoritmo: IA Premium (Gemini 2.5 Flash)")
print(f"   Endpoint: /recommendations/api/recommendations/?algorithm=ai&limit=6")

# Chamar a view
try:
    response = get_recommendations_simple(request)

    print(f"\n📊 RESPOSTA:")
    print(f"   Status Code: {response.status_code}")

    data = json.loads(response.content)

    if response.status_code == 200:
        if data.get('count', 0) > 0:
            print(f"   ✅ Total de recomendações: {data['count']}")
            print(f"\n📚 RECOMENDAÇÕES GERADAS POR IA:\n")

            for i, rec in enumerate(data['recommendations'], 1):
                print(f"{i}. {rec['title']}")
                print(f"   Autor: {rec['author']}")
                print(f"   Score: {rec['score']:.0%}")
                print(f"   Razão: {rec['reason']}")
                print()
        else:
            print(f"   ⚠️  Nenhuma recomendação gerada")
            print(f"   Isso pode acontecer se:")
            print(f"   - O usuário não tem histórico suficiente")
            print(f"   - A IA não encontrou livros adequados")
    else:
        print(f"   ❌ ERRO: Status {response.status_code}")
        print(f"   Mensagem: {data.get('error', 'Erro desconhecido')}")
        if 'detail' in data:
            print(f"   Detalhes: {data['detail']}")

except Exception as e:
    print(f"\n❌ ERRO:")
    print(f"   {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
