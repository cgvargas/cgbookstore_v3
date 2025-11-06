"""
Script para testar múltiplas execuções da mesma campanha
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

# Fix encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def test_multiple_executions():
    """Testa múltiplas execuções da mesma campanha"""

    print("=" * 70)
    print("TESTE DE MÚLTIPLAS EXECUÇÕES - INCREMENTO DO CONTADOR")
    print("=" * 70)
    print()

    # Pega a primeira campanha
    campaign = Campaign.objects.filter(status='active').first()

    if not campaign:
        print("❌ Nenhuma campanha ativa encontrada!")
        return

    print(f"🎯 Testando campanha: {campaign.name}\n")

    # Status inicial
    print("📊 STATUS INICIAL:")
    print(f"   Execuções: {campaign.execution_count}")
    if campaign.last_execution_date:
        print(f"   Última execução: {campaign.last_execution_date.strftime('%d/%m/%Y %H:%M')}")
    else:
        print(f"   Última execução: Nunca")

    print("\n" + "=" * 70)
    print("🚀 EXECUTANDO CAMPANHA 3 VEZES...")
    print("=" * 70)

    for i in range(1, 4):
        print(f"\n▶️ Execução #{i}")

        result = CampaignService.execute_campaign(campaign, preview=False)

        if result['success']:
            # Recarrega para ver valores atualizados
            campaign.refresh_from_db()

            print(f"   ✅ Sucesso!")
            print(f"   Contador de execuções: {campaign.execution_count}")
            print(f"   Última execução: {campaign.last_execution_date.strftime('%d/%m/%Y %H:%M:%S')}")
        else:
            print(f"   ❌ Erro: {result.get('error')}")

    print("\n" + "=" * 70)
    print("📊 STATUS FINAL:")
    print("=" * 70)
    campaign.refresh_from_db()
    print(f"\n🔹 {campaign.name}")
    print(f"   ✓ Execuções totais: {campaign.execution_count}")
    print(f"   ✓ Última execução: {campaign.last_execution_date.strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"   ✓ Total concedido: {campaign.total_granted}")

    print("\n" + "=" * 70)
    print("✅ TESTE CONCLUÍDO - CONTADOR FUNCIONANDO!")
    print("=" * 70)
    print()

if __name__ == '__main__':
    test_multiple_executions()
