#!/usr/bin/env python
"""
Script para testar a API unificada de notificações.
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import RequestFactory
from core.views.reading_progress_views import get_all_notifications_unified
import json

def test_api():
    print("=" * 70)
    print("TESTE DA API UNIFICADA DE NOTIFICACOES")
    print("=" * 70)
    print()

    # Obter usuário claud
    try:
        user = User.objects.get(username='claud')
        print(f"Usuario: {user.username}")
        print()
    except User.DoesNotExist:
        print("Usuario 'claud' nao encontrado")
        return

    # Criar request fake
    factory = RequestFactory()
    request = factory.get('/api/notifications/unified/?page=1&unread_only=false&category=all')
    request.user = user

    # Chamar a view
    response = get_all_notifications_unified(request)

    # Parse do JSON
    data = json.loads(response.content)

    print("Resposta da API:")
    print(f"  Success: {data.get('success')}")
    print(f"  Total de notificacoes: {len(data.get('notifications', []))}")
    print(f"  Unread count: {data.get('unread_count')}")
    print()

    print("Category counts:")
    for cat, counts in data.get('category_counts', {}).items():
        print(f"  {cat}: {counts['unread']}/{counts['total']} (nao lidas/total)")
    print()

    print("Notificacoes:")
    for notif in data.get('notifications', []):
        print(f"  ID: {notif['id']}")
        print(f"  Categoria: {notif['category']}")
        print(f"  Tipo: {notif['type']}")
        print(f"  Mensagem: {notif['message'][:60]}...")
        print(f"  Lida: {'Sim' if notif['is_read'] else 'Nao'}")
        print(f"  Tempo: {notif['formatted_time']}")
        print()

if __name__ == '__main__':
    test_api()
