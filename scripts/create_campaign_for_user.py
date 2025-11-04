"""
Script para criar e executar campanha para um usuário específico
Uso: python scripts/create_campaign_for_user.py <username> [dias]
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

def create_campaign_for_user(username, duration_days=30):
    """
    Cria e executa campanha para um usuário específico

    Args:
        username: Nome do usuário
        duration_days: Dias de Premium (padrão: 30)
    """

    print("=" * 70)
    print("CRIAR E EXECUTAR CAMPANHA PARA USUÁRIO")
    print("=" * 70)
    print()

    # Verificar se usuário existe
    try:
        user = User.objects.get(username=username)
        print(f"✅ Usuário encontrado: {username}")
        print(f"   Email: {user.email}")
        print(f"   Nome: {user.get_full_name() or 'Não informado'}")
        print()
    except User.DoesNotExist:
        print(f"❌ ERRO: Usuário '{username}' não existe!")
        print()
        print("💡 Usuários disponíveis:")
        users = User.objects.all()[:10]
        for u in users:
            print(f"   - {u.username}")
        return

    # Verificar se já tem campanha ativa
    from finance.models import CampaignGrant
    active_grants = CampaignGrant.objects.filter(
        user=user,
        is_active=True,
        expires_at__gte=timezone.now()
    )

    if active_grants.exists():
        print("⚠️ ATENÇÃO: Usuário já possui Premium ativo via campanha!")
        for grant in active_grants:
            print(f"   Campanha: {grant.campaign.name}")
            print(f"   Expira em: {grant.expires_at.strftime('%d/%m/%Y')}")
        print()
        response = input("Deseja criar uma nova campanha mesmo assim? (s/N): ")
        if response.lower() != 's':
            print("❌ Operação cancelada.")
            return

    # Obter usuário admin
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        admin_user = User.objects.filter(is_staff=True).first()

    # Criar campanha
    now = timezone.now()
    campaign_name = f"Premium para {username} - {duration_days} dias"

    print(f"🎯 Criando campanha: {campaign_name}")
    print()

    campaign = Campaign.objects.create(
        name=campaign_name,
        description=f"Campanha especial concedendo {duration_days} dias de Premium gratuito para {username}",
        duration_days=duration_days,
        target_type='individual',
        criteria={"username": username},
        start_date=now,
        end_date=now + timedelta(days=365),
        status='active',
        auto_grant=True,
        send_notification=True,  # ✅ NOTIFICAÇÃO HABILITADA!
        max_grants=1,
        created_by=admin_user
    )

    print(f"✅ Campanha criada!")
    print(f"   ID: {campaign.id}")
    print(f"   Nome: {campaign.name}")
    print(f"   Duração: {campaign.duration_days} dias")
    print(f"   Notificação: {'✓ Habilitada' if campaign.send_notification else '✗ Desabilitada'}")
    print()

    # Executar campanha
    print("🚀 Executando campanha...")
    result = CampaignService.execute_campaign(campaign, preview=False)

    if result['success']:
        print(f"✅ Campanha executada com sucesso!")
        print(f"   Elegíveis: {result['eligible_count']}")
        print(f"   Concedidos: {result['granted_count']}")

        if result['granted_count'] > 0:
            # Buscar concessão
            grant = CampaignGrant.objects.filter(
                campaign=campaign,
                user=user
            ).first()

            if grant:
                print()
                print("📋 DETALHES DA CONCESSÃO:")
                print(f"   Usuário: {grant.user.username}")
                print(f"   Concedido em: {grant.granted_at.strftime('%d/%m/%Y %H:%M')}")
                print(f"   Expira em: {grant.expires_at.strftime('%d/%m/%Y %H:%M')}")
                print(f"   Status: {'✓ Ativo' if grant.is_active else '✗ Inativo'}")

            # Buscar notificação
            notification = CampaignNotification.objects.filter(
                campaign=campaign,
                user=user
            ).first()

            if notification:
                print()
                print("🔔 NOTIFICAÇÃO ENVIADA:")
                print(f"   Tipo: {notification.notification_type}")
                print(f"   Mensagem: {notification.message}")
                print(f"   Prioridade: {notification.priority_name}")
                print(f"   Lida: {'Sim ✓' if notification.is_read else 'Não ●'}")
                print(f"   Criada: {notification.created_at.strftime('%d/%m/%Y %H:%M:%S')}")
            else:
                print()
                print("⚠️ Nenhuma notificação criada (send_notification pode estar desabilitado)")

        else:
            print()
            print("⚠️ Nenhum Premium concedido!")
            if result.get('errors'):
                print("   Erros:")
                for error in result['errors']:
                    print(f"   - {error}")

    else:
        print(f"❌ Erro ao executar campanha: {result.get('error')}")
        return

    print()
    print("=" * 70)
    print("✨ CAMPANHA CRIADA E EXECUTADA COM SUCESSO!")
    print("=" * 70)
    print()
    print("💡 PRÓXIMOS PASSOS:")
    print(f"   1. Faça login como '{username}' no site")
    print("   2. Clique no sininho (bell icon) no header")
    print("   3. Veja a notificação de Premium concedido!")
    print()
    print("📊 ACESSO RÁPIDO ADMIN:")
    print(f"   Campanha: /admin/finance/campaign/{campaign.id}/change/")
    print("   Concessões: /admin/finance/campaigngrant/")
    print("   Notificações: /admin/accounts/campaignnotification/")
    print()

def main():
    """Função principal"""

    if len(sys.argv) < 2:
        print("=" * 70)
        print("USO DO SCRIPT")
        print("=" * 70)
        print()
        print("Sintaxe:")
        print("  python scripts/create_campaign_for_user.py <username> [dias]")
        print()
        print("Exemplos:")
        print("  python scripts/create_campaign_for_user.py claud")
        print("  python scripts/create_campaign_for_user.py claud 30")
        print("  python scripts/create_campaign_for_user.py joao 7")
        print()
        print("Parâmetros:")
        print("  <username>  Nome do usuário (obrigatório)")
        print("  [dias]      Dias de Premium (opcional, padrão: 30)")
        print()
        return

    username = sys.argv[1]
    duration_days = int(sys.argv[2]) if len(sys.argv) > 2 else 30

    # Validar duração
    valid_durations = [7, 15, 30]
    if duration_days not in valid_durations:
        print(f"⚠️ ATENÇÃO: {duration_days} dias não é uma opção padrão.")
        print(f"   Opções recomendadas: {valid_durations}")
        print(f"   Continuando com {duration_days} dias...")
        print()

    create_campaign_for_user(username, duration_days)

if __name__ == '__main__':
    main()
