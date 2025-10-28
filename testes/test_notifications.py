"""
Script de Teste: Criar Notificações Não Lidas
CGBookStore v3

Objetivo: Criar notificações de teste com is_read=False
para validar o sistema de notificações
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from accounts.models import ReadingNotification, SystemNotification
from django.contrib.auth import get_user_model
from datetime import datetime

User = get_user_model()

def diagnostico():
    """Exibe o estado atual das notificações"""
    print("=" * 60)
    print("DIAGNÓSTICO DE NOTIFICAÇÕES")
    print("=" * 60)

    users = User.objects.all()
    print(f"\nUsuários no sistema: {users.count()}")

    for user in users:
        print(f"\n--- Usuário: {user.username} ---")

        # Reading Notifications
        rn_total = ReadingNotification.objects.filter(user=user).count()
        rn_unread = ReadingNotification.objects.filter(user=user, is_read=False).count()
        rn_read = ReadingNotification.objects.filter(user=user, is_read=True).count()

        print(f"  📚 Reading Notifications:")
        print(f"     Total: {rn_total}")
        print(f"     Não lidas: {rn_unread}")
        print(f"     Lidas: {rn_read}")

        # System Notifications
        sn_total = SystemNotification.objects.filter(user=user).count()
        sn_unread = SystemNotification.objects.filter(user=user, is_read=False).count()
        sn_read = SystemNotification.objects.filter(user=user, is_read=True).count()

        print(f"  🔔 System Notifications:")
        print(f"     Total: {sn_total}")
        print(f"     Não lidas: {sn_unread}")
        print(f"     Lidas: {sn_read}")

        print(f"  ✨ TOTAL NÃO LIDAS: {rn_unread + sn_unread}")

def marcar_todas_como_nao_lidas():
    """Marca todas as notificações existentes como NÃO LIDAS"""
    print("\n" + "=" * 60)
    print("MARCANDO TODAS AS NOTIFICAÇÕES COMO NÃO LIDAS")
    print("=" * 60)

    users = User.objects.all()

    for user in users:
        # Atualizar Reading Notifications
        rn_count = ReadingNotification.objects.filter(user=user, is_read=True).update(is_read=False)
        print(f"\n✅ {user.username}: {rn_count} Reading Notifications marcadas como não lidas")

        # Atualizar System Notifications
        sn_count = SystemNotification.objects.filter(user=user, is_read=True).update(is_read=False)
        print(f"✅ {user.username}: {sn_count} System Notifications marcadas como não lidas")

def criar_notificacoes_teste():
    """Cria notificações de teste NÃO LIDAS"""
    print("\n" + "=" * 60)
    print("CRIANDO NOTIFICAÇÕES DE TESTE")
    print("=" * 60)

    user = User.objects.first()

    if not user:
        print("❌ Nenhum usuário encontrado! Crie um usuário primeiro.")
        return

    print(f"\nCriando notificações para: {user.username}")

    # 1. Reading Notification - Progresso
    rn1 = ReadingNotification.objects.create(
        user=user,
        notification_type='progress',
        message='Você está progredindo! Continue lendo para alcançar sua meta.',
        priority=2,
        is_read=False  # ← IMPORTANTE!
    )
    print(f"✅ Criada: ReadingNotification (progress) - ID: {rn1.id}")

    # 2. Reading Notification - Deadline
    rn2 = ReadingNotification.objects.create(
        user=user,
        notification_type='deadline',
        message='Prazo se aproximando! Você tem 3 dias para terminar o livro.',
        priority=3,
        is_read=False  # ← IMPORTANTE!
    )
    print(f"✅ Criada: ReadingNotification (deadline) - ID: {rn2.id}")

    # 3. System Notification - Atualização
    sn1 = SystemNotification.objects.create(
        user=user,
        notification_type='system_update',
        message='Nova funcionalidade disponível: Sistema de notificações v3.0!',
        priority=1,
        is_read=False  # ← IMPORTANTE!
    )
    print(f"✅ Criada: SystemNotification (update) - ID: {sn1.id}")

    # 4. System Notification - Evento
    sn2 = SystemNotification.objects.create(
        user=user,
        notification_type='book_launch',
        message='Novo lançamento: "O Guia Definitivo de Django" já está disponível!',
        priority=2,
        is_read=False  # ← IMPORTANTE!
    )
    print(f"✅ Criada: SystemNotification (launch) - ID: {sn2.id}")

    print(f"\n✨ Total criado: 4 notificações NÃO LIDAS")

def limpar_todas_notificacoes():
    """Remove TODAS as notificações (use com cuidado!)"""
    print("\n" + "=" * 60)
    print("⚠️  LIMPANDO TODAS AS NOTIFICAÇÕES")
    print("=" * 60)

    rn_count = ReadingNotification.objects.all().count()
    sn_count = SystemNotification.objects.all().count()

    resposta = input(f"\n⚠️  Confirma exclusão de {rn_count + sn_count} notificações? (sim/não): ")

    if resposta.lower() == 'sim':
        ReadingNotification.objects.all().delete()
        SystemNotification.objects.all().delete()
        print("✅ Todas as notificações foram removidas!")
    else:
        print("❌ Operação cancelada.")

def menu():
    """Menu interativo"""
    while True:
        print("\n" + "=" * 60)
        print("MENU DE TESTES - NOTIFICAÇÕES v3.0")
        print("=" * 60)
        print("1. Diagnóstico (ver estado atual)")
        print("2. Marcar todas como NÃO LIDAS")
        print("3. Criar 4 notificações de teste NÃO LIDAS")
        print("4. Limpar todas as notificações")
        print("5. Sair")
        print("=" * 60)

        opcao = input("\nEscolha uma opção: ")

        if opcao == '1':
            diagnostico()
        elif opcao == '2':
            marcar_todas_como_nao_lidas()
            diagnostico()
        elif opcao == '3':
            criar_notificacoes_teste()
            diagnostico()
        elif opcao == '4':
            limpar_todas_notificacoes()
            diagnostico()
        elif opcao == '5':
            print("\n👋 Até logo!")
            break
        else:
            print("\n❌ Opção inválida!")

if __name__ == '__main__':
    # Executar diagnóstico inicial
    diagnostico()

    # Exibir menu
    menu()