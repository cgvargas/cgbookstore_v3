#!/usr/bin/env python
"""
Script para testar se CampaignNotification está registrada no NotificationRegistry.
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from accounts.models import NotificationRegistry, CampaignNotification
from django.contrib.auth.models import User

def test_registry():
    print("=" * 70)
    print("TESTE DO NOTIFICATION REGISTRY")
    print("=" * 70)
    print()

    # Listar todos os tipos registrados
    print("📋 Tipos de notificação registrados:")
    for category in NotificationRegistry.get_all_types():
        info = NotificationRegistry.get(category)
        config = info.get('config', {})
        print(f"  - {category}: {info['class'].__name__}")
        print(f"    Nome: {config.get('category_name', 'N/A')}")
        print(f"    Ícone: {config.get('icon', 'N/A')}")
        print(f"    Cor: {config.get('color', 'N/A')}")
        print()

    # Testar busca unificada
    print("=" * 70)
    print("TESTE DE BUSCA UNIFICADA")
    print("=" * 70)
    print()

    # Buscar usuário 'claud' que tem notificação
    try:
        user = User.objects.get(username='claud')
        print(f"✓ Usuário encontrado: {user.username}")
        print()

        # Buscar todas as notificações usando o registry
        all_notifs = NotificationRegistry.get_all_notifications(user, unread_only=False)
        print(f"📬 Total de notificações: {len(all_notifs)}")
        print()

        for notif in all_notifs:
            category = None
            for cat in NotificationRegistry.get_all_types():
                info = NotificationRegistry.get(cat)
                if isinstance(notif, info['class']):
                    category = cat
                    break

            status = "✓" if notif.is_read else "●"
            print(f"  [{status}] Categoria: {category}")
            print(f"      ID: {notif.id}")
            print(f"      Tipo: {notif.notification_type}")
            print(f"      Mensagem: {notif.message[:60]}...")
            print(f"      Criada: {notif.created_at.strftime('%d/%m/%Y %H:%M')}")
            print()

        # Buscar apenas não lidas
        unread_notifs = NotificationRegistry.get_all_notifications(user, unread_only=True)
        print(f"📩 Notificações não lidas: {len(unread_notifs)}")

    except User.DoesNotExist:
        print("✗ Usuário 'claud' não encontrado")
        print("  Testando com primeiro usuário disponível...")
        user = User.objects.first()
        if user:
            print(f"  Usuário: {user.username}")
            all_notifs = NotificationRegistry.get_all_notifications(user)
            print(f"  Total de notificações: {len(all_notifs)}")
        else:
            print("  Nenhum usuário encontrado no banco de dados")

if __name__ == '__main__':
    test_registry()
