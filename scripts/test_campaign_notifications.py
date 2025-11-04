"""
Script para testar o envio de notificações de campanhas
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from django.utils import timezone
from finance.models import Campaign
from finance.services import CampaignService
from accounts.models import CampaignNotification

# Fix encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def test_campaign_notifications():
    """Testa o envio de notificações ao executar campanhas"""

    print("=" * 70)
    print("TESTE DE NOTIFICAÇÕES DE CAMPANHAS")
    print("=" * 70)
    print()

    # Buscar campanhas ativas
    campaigns = Campaign.objects.filter(status='active')

    if campaigns.count() == 0:
        print("❌ Nenhuma campanha ativa encontrada!")
        return

    print(f"✅ Encontradas {campaigns.count()} campanhas ativas\n")

    # Selecionar uma campanha para testar
    test_campaign = campaigns.filter(send_notification=True).first()

    if not test_campaign:
        print("⚠️ Nenhuma campanha com notificações habilitadas!")
        print("Vou habilitar notificações na primeira campanha...\n")
        test_campaign = campaigns.first()
        test_campaign.send_notification = True
        test_campaign.save()
        print(f"✅ Notificações habilitadas para '{test_campaign.name}'\n")

    print(f"🎯 Testando: {test_campaign.name}")
    print(f"   Enviar notificação? {test_campaign.send_notification}")
    print()

    # Contar notificações antes
    notifications_before = CampaignNotification.objects.count()
    print(f"📊 Notificações antes: {notifications_before}")

    # Executar campanha
    print("\n🚀 Executando campanha...")
    result = CampaignService.execute_campaign(test_campaign, preview=False)

    if result['success']:
        print(f"✅ Campanha executada com sucesso!")
        print(f"   Elegíveis: {result['eligible_count']}")
        print(f"   Concedidos: {result['granted_count']}")

        # Contar notificações depois
        notifications_after = CampaignNotification.objects.count()
        new_notifications = notifications_after - notifications_before

        print(f"\n📊 Notificações depois: {notifications_after}")
        print(f"📩 Novas notificações criadas: {new_notifications}")

        if new_notifications > 0:
            print("\n" + "=" * 70)
            print("✅ NOTIFICAÇÕES ENVIADAS COM SUCESSO!")
            print("=" * 70)

            # Listar notificações criadas
            recent_notifications = CampaignNotification.objects.filter(
                campaign=test_campaign
            ).order_by('-created_at')[:5]

            print("\n📬 Últimas notificações:")
            for notif in recent_notifications:
                print(f"\n🔔 Notificação #{notif.id}")
                print(f"   Usuário: {notif.user.username}")
                print(f"   Tipo: {notif.get_notification_type_display()}")
                print(f"   Mensagem: {notif.message}")
                print(f"   Lida: {'Sim' if notif.is_read else 'Não'}")
                print(f"   Criada: {notif.created_at.strftime('%d/%m/%Y %H:%M:%S')}")
        else:
            print("\n⚠️ Nenhuma notificação nova criada!")
            print("   Possível motivo: Usuários já receberam desta campanha")

    else:
        print(f"❌ Erro ao executar campanha: {result.get('error')}")

    print("\n" + "=" * 70)
    print("📊 ESTATÍSTICAS FINAIS")
    print("=" * 70)

    total_notifications = CampaignNotification.objects.count()
    unread_notifications = CampaignNotification.objects.filter(is_read=False).count()

    print(f"\n📬 Total de notificações no sistema: {total_notifications}")
    print(f"📩 Não lidas: {unread_notifications}")
    print(f"✅ Lidas: {total_notifications - unread_notifications}")

    print("\n💡 PRÓXIMOS PASSOS:")
    print("   1. Acesse /admin/accounts/campaignnotification/ para ver as notificações")
    print("   2. Faça login como um usuário que recebeu Premium")
    print("   3. Verifique o sininho de notificações no frontend")
    print()

if __name__ == '__main__':
    test_campaign_notifications()
