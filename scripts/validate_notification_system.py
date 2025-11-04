#!/usr/bin/env python
"""
Script de validacao completo do sistema de notificacoes de campanhas.
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import CampaignNotification, NotificationRegistry
from django.urls import resolve, reverse

def validate_registry():
    """Valida o registro no NotificationRegistry."""
    print("=" * 70)
    print("1. VALIDACAO DO NOTIFICATION REGISTRY")
    print("=" * 70)

    registered_types = list(NotificationRegistry.get_all_types())

    if 'campaign' in registered_types:
        print("OK: CampaignNotification registrado")
        info = NotificationRegistry.get('campaign')
        print(f"   Classe: {info['class'].__name__}")
        print(f"   Nome: {info['config'].get('category_name')}")
        print(f"   Icone: {info['config'].get('icon')}")
        print(f"   Cor: {info['config'].get('color')}")
        return True
    else:
        print("ERRO: CampaignNotification NAO registrado")
        print(f"   Tipos registrados: {registered_types}")
        return False

def validate_notifications():
    """Valida notificacoes no banco."""
    print("\n" + "=" * 70)
    print("2. VALIDACAO DE NOTIFICACOES NO BANCO")
    print("=" * 70)

    count = CampaignNotification.objects.count()
    print(f"Total de notificacoes de campanha: {count}")

    if count == 0:
        print("AVISO: Nenhuma notificacao encontrada")
        return False

    # Verificar notificacao mais recente
    latest = CampaignNotification.objects.order_by('-created_at').first()
    print(f"\nNotificacao mais recente:")
    print(f"  ID: {latest.id}")
    print(f"  Usuario: {latest.user.username}")
    print(f"  Campanha: {latest.campaign.name if latest.campaign else 'N/A'}")
    print(f"  Tipo: {latest.notification_type}")
    print(f"  Mensagem: {latest.message[:60]}...")
    print(f"  Action URL: {latest.action_url}")
    print(f"  Action Text: {latest.action_text}")
    print(f"  Lida: {'Sim' if latest.is_read else 'Nao'}")

    # Validar URL de acao
    if latest.action_url:
        try:
            resolve(latest.action_url)
            print(f"  OK: URL '{latest.action_url}' e valida")
        except:
            print(f"  ERRO: URL '{latest.action_url}' NAO existe")
            return False

    return True

def validate_urls():
    """Valida URLs registradas."""
    print("\n" + "=" * 70)
    print("3. VALIDACAO DE URLS")
    print("=" * 70)

    urls_to_test = [
        ('notifications_unified', '/api/notifications/unified/'),
        ('mark_notification_read_unified', '/api/notifications/unified/mark-read/'),
        ('delete_selected_notifications_unified', '/api/notifications/unified/delete-selected/'),
        ('mark_all_notifications_as_read', '/api/notifications/unified/mark-all-read/'),
    ]

    all_ok = True
    for name, expected_path in urls_to_test:
        try:
            url = reverse(f'core:{name}')
            if url == expected_path:
                print(f"OK: {name}")
                print(f"     {url}")
            else:
                print(f"AVISO: {name}")
                print(f"     Esperado: {expected_path}")
                print(f"     Real: {url}")
        except:
            print(f"ERRO: {name} NAO encontrado")
            all_ok = False

    return all_ok

def validate_user_notifications():
    """Valida notificacoes de um usuario especifico."""
    print("\n" + "=" * 70)
    print("4. VALIDACAO DE NOTIFICACOES DO USUARIO")
    print("=" * 70)

    try:
        user = User.objects.get(username='claud')
        print(f"Usuario: {user.username}")

        # Usar NotificationRegistry para buscar TODAS as notificacoes
        all_notifs = NotificationRegistry.get_all_notifications(user, unread_only=False)
        print(f"Total de notificacoes (todas categorias): {len(all_notifs)}")

        # Contar por categoria
        categories = {}
        for notif in all_notifs:
            for cat in NotificationRegistry.get_all_types():
                info = NotificationRegistry.get(cat)
                if isinstance(notif, info['class']):
                    categories[cat] = categories.get(cat, 0) + 1
                    break

        print("\nPor categoria:")
        for cat, count in categories.items():
            print(f"  {cat}: {count}")

        # Verificar notificacoes de campanha
        campaign_notifs = CampaignNotification.objects.filter(user=user)
        print(f"\nNotificacoes de campanha: {campaign_notifs.count()}")

        for notif in campaign_notifs:
            status = "Lida" if notif.is_read else "Nao lida"
            print(f"  - ID {notif.id}: {notif.notification_type} ({status})")

        return True

    except User.DoesNotExist:
        print("ERRO: Usuario 'claud' nao encontrado")
        return False

def main():
    print("\n")
    print("######################################################################")
    print("#                                                                    #")
    print("#          VALIDACAO DO SISTEMA DE NOTIFICACOES DE CAMPANHAS        #")
    print("#                                                                    #")
    print("######################################################################")
    print("\n")

    results = []

    results.append(("Registry", validate_registry()))
    results.append(("Notificacoes", validate_notifications()))
    results.append(("URLs", validate_urls()))
    results.append(("Usuario", validate_user_notifications()))

    # Resumo
    print("\n" + "=" * 70)
    print("RESUMO DA VALIDACAO")
    print("=" * 70)

    for name, result in results:
        status = "OK" if result else "FALHOU"
        print(f"{name:20s} {status}")

    all_passed = all(r[1] for r in results)

    if all_passed:
        print("\n" + "=" * 70)
        print("SUCESSO: Todas as validacoes passaram!")
        print("O sistema de notificacoes de campanhas esta funcionando corretamente.")
        print("=" * 70)
        return 0
    else:
        print("\n" + "=" * 70)
        print("ATENCAO: Algumas validacoes falharam.")
        print("Revise os erros acima.")
        print("=" * 70)
        return 1

if __name__ == '__main__':
    exit(main())
