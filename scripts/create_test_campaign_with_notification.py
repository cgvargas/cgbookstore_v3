"""
Script para criar campanha de teste com notificações habilitadas
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from django.utils import timezone
from django.contrib.auth.models import User
from finance.models import Campaign
from finance.services import CampaignService
from accounts.models import CampaignNotification
from datetime import timedelta

# Fix encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def create_test_campaign_with_notification():
    """Cria campanha de teste e executa com notificações"""

    print("=" * 70)
    print("CRIANDO CAMPANHA DE TESTE COM NOTIFICAÇÕES")
    print("=" * 70)
    print()

    # Obter usuário admin
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        admin_user = User.objects.filter(is_staff=True).first()

    # Criar nova campanha
    now = timezone.now()

    campaign = Campaign.objects.create(
        name="Teste de Notificações - Premium 7 dias",
        description="Campanha de teste para verificar envio de notificações no sininho",
        duration_days=7,
        target_type='group',
        criteria={
            "usernames": ["usuario_ativo_1", "usuario_ativo_2"]
        },
        start_date=now,
        end_date=now + timedelta(days=365),
        status='active',
        auto_grant=True,
        send_notification=True,  # HABILITADO!
        max_grants=None,
        created_by=admin_user
    )

    print(f"✅ Campanha criada: {campaign.name}")
    print(f"   ID: {campaign.id}")
    print(f"   Enviar notificação: {campaign.send_notification}")
    print(f"   Público-alvo: usuario_ativo_1, usuario_ativo_2")
    print()

    # Contar notificações antes
    notifications_before = CampaignNotification.objects.count()
    print(f"📊 Notificações antes: {notifications_before}")

    # Executar campanha
    print("\n🚀 Executando campanha...")
    result = CampaignService.execute_campaign(campaign, preview=False)

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
                campaign=campaign
            ).order_by('-created_at')

            print(f"\n📬 {recent_notifications.count()} notificação(ões) criada(s):")
            for notif in recent_notifications:
                print(f"\n🔔 Notificação #{notif.id}")
                print(f"   Usuário: {notif.user.username}")
                print(f"   Tipo: {notif.notification_type}")
                print(f"   Mensagem: {notif.message}")
                print(f"   Prioridade: {notif.priority_name}")
                print(f"   Lida: {'Sim ✓' if notif.is_read else 'Não ●'}")
                print(f"   Criada: {notif.created_at.strftime('%d/%m/%Y %H:%M:%S')}")
                print(f"   Ação: {notif.action_text} → {notif.action_url}")

            print("\n" + "=" * 70)
            print("✨ TESTE CONCLUÍDO COM SUCESSO!")
            print("=" * 70)

        else:
            print("\n⚠️ Nenhuma notificação nova criada!")
            if result['granted_count'] == 0:
                print("   Motivo: Nenhum usuário recebeu Premium")
            else:
                print("   Motivo: Notificações podem estar desabilitadas")

    else:
        print(f"❌ Erro ao executar campanha: {result.get('error')}")

    print("\n💡 PARA VISUALIZAR AS NOTIFICAÇÕES:")
    print("   1. Admin: /admin/accounts/campaignnotification/")
    print("   2. Faça login como 'usuario_ativo_1' (senha: test123)")
    print("   3. Clique no sininho de notificações")
    print()

if __name__ == '__main__':
    create_test_campaign_with_notification()
