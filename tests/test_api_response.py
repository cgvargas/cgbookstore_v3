"""
Testar resposta da API de recomendacoes para debug.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from recommendations.views_simple import get_recommendations_simple
import json

print("="*60)
print("TESTE DE RESPOSTA DA API")
print("="*60)

# Criar request fake
factory = RequestFactory()
user = User.objects.get(username='claud')

# Simular request GET
request = factory.get('/recommendations/api/recommendations/?algorithm=preference_hybrid&limit=6')
request.user = user

# Chamar view
response = get_recommendations_simple(request)

print(f"\nStatus Code: {response.status_code}")
print(f"Content-Type: {response.get('Content-Type', 'N/A')}")

# Parse JSON
data = json.loads(response.content)

print(f"\nAlgorithm: {data.get('algorithm')}")
print(f"Count: {data.get('count')}")
print(f"\nRecommendations:")

for i, rec in enumerate(data.get('recommendations', [])[:3], 1):
    print(f"\n{i}. {rec.get('title', 'N/A')}")
    print(f"   ID: {rec.get('id')}")
    print(f"   Slug: {rec.get('slug')}")
    print(f"   Author: {rec.get('author')}")
    print(f"   Cover: {rec.get('cover_image')}")
    print(f"   Score: {rec.get('score')}")
    print(f"   Source: {rec.get('source')}")

print("\n" + "="*60)
