"""
Script de Teste CORRIGIDO: Criar System Notifications
CGBookStore v3

Cria apenas SystemNotifications (não precisa de reading_progress)
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from accounts.models import SystemNotification
from django.contrib.auth import get_user_model

User = get_user_model()


def criar_system_notifications():
    """Cria 4 System Notifications de teste"""
    print("=" * 60)
    print("CRIANDO SYSTEM NOTIFICATIONS DE TESTE")
    print("=" * 60)

    user = User.objects.first()

    if not user:
        print("❌ Nenhum usuário encontrado!")
        return

    print(f"\nCriando notificações para: {user.username}\n")

    # 1. Atualização do Sistema
    sn1 = SystemNotification.objects.create(
        user=user,
        notification_type='system_update',
        message='🎉 Sistema de notificações v3.0 está ativo!',
        priority=1,
        is_read=False
    )
    print(f"✅ [{sn1.id}] System Update - Prioridade Baixa")

    # 2. Lançamento de Livro
    sn2 = SystemNotification.objects.create(
        user=user,
        notification_type='book_launch',
        message='📚 Novo lançamento: "Django Avançado" disponível agora!',
        priority=2,
        is_read=False
    )
    print(f"✅ [{sn2.id}] Book Launch - Prioridade Média")

    # 3. Evento Literário
    sn3 = SystemNotification.objects.create(
        user=user,
        notification_type='literary_event',
        message='🎭 Evento: Encontro de Autores - Amanhã às 19h!',
        priority=3,
        is_read=False
    )
    print(f"✅ [{sn3.id}] Literary Event - Prioridade Alta")

    # 4. Manutenção
    sn4 = SystemNotification.objects.create(
        user=user,
        notification_type='system_update',
        message='🔧 Manutenção programada: Domingo 02h-04h',
        priority=1,
        is_read=False
    )
    print(f"✅ [{sn4.id}] Maintenance - Prioridade Baixa")

    print(f"\n✨ 4 System Notifications criadas com sucesso!")
    print(f"\n🔔 Total de notificações não lidas para {user.username}:")

    # Contar não lidas
    total = SystemNotification.objects.filter(user=user, is_read=False).count()
    print(f"   System Notifications: {total}")


if __name__ == '__main__':
    criar_system_notifications()