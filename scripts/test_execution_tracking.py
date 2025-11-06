"""
Script para testar o rastreamento de execuções de campanhas
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

def test_execution_tracking():
    """Testa o rastreamento de execuções"""

    print("=" * 70)
    print("TESTE DE RASTREAMENTO DE EXECUÇÕES DE CAMPANHAS")
    print("=" * 70)
    print()

    # Listar todas as campanhas ativas
    campaigns = Campaign.objects.filter(status='active')

    if campaigns.count() == 0:
        print("❌ Nenhuma campanha ativa encontrada!")
        return

    print(f"✅ Encontradas {campaigns.count()} campanhas ativas\n")

    # Mostrar status antes da execução
    print("📊 STATUS ANTES DA EXECUÇÃO:")
    print("-" * 70)
    for campaign in campaigns:
        print(f"\n🔹 {campaign.name}")
        print(f"   Status: {campaign.get_status_display()}")
        print(f"   Período: {campaign.start_date.strftime('%d/%m/%Y')} até {campaign.end_date.strftime('%d/%m/%Y')}")
        print(f"   Ativa agora? {campaign.is_active_now()}")
        print(f"   Execuções: {campaign.execution_count}")
        if campaign.last_execution_date:
            print(f"   Última execução: {campaign.last_execution_date.strftime('%d/%m/%Y %H:%M')}")
        else:
            print(f"   Última execução: Nunca")
        print(f"   Total concedido: {campaign.total_granted}")

    print("\n" + "=" * 70)
    print("🚀 EXECUTANDO PRIMEIRA CAMPANHA...")
    print("=" * 70)

    # Pega a primeira campanha para testar
    test_campaign = campaigns.first()
    print(f"\nTestando: {test_campaign.name}")

    # Executa preview primeiro
    print("\n1️⃣ Preview (sem concessões reais):")
    preview_result = CampaignService.execute_campaign(test_campaign, preview=True)
    print(f"   Elegíveis: {preview_result.get('eligible_count', 0)}")

    # Executa de verdade
    print("\n2️⃣ Execução real:")
    execution_result = CampaignService.execute_campaign(test_campaign, preview=False)

    if execution_result['success']:
        print(f"   ✅ Sucesso!")
        print(f"   Elegíveis: {execution_result.get('eligible_count', 0)}")
        print(f"   Concedidos: {execution_result.get('granted_count', 0)}")
        if execution_result.get('errors'):
            print(f"   ⚠️ Erros: {len(execution_result['errors'])}")
            for error in execution_result['errors'][:3]:
                print(f"      - {error}")
    else:
        print(f"   ❌ Erro: {execution_result.get('error')}")

    # Recarrega a campanha para ver valores atualizados
    test_campaign.refresh_from_db()

    print("\n" + "=" * 70)
    print("📊 STATUS APÓS EXECUÇÃO:")
    print("-" * 70)
    print(f"\n🔹 {test_campaign.name}")
    print(f"   Execuções: {test_campaign.execution_count} 🎯")
    if test_campaign.last_execution_date:
        print(f"   Última execução: {test_campaign.last_execution_date.strftime('%d/%m/%Y %H:%M')} ✅")
    print(f"   Total concedido: {test_campaign.total_granted}")

    # Calcular diferença de tempo
    if test_campaign.last_execution_date:
        now = timezone.now()
        diff = now - test_campaign.last_execution_date
        print(f"   Executada há: {diff.seconds} segundos")

    print("\n" + "=" * 70)
    print("✅ TESTE CONCLUÍDO!")
    print("=" * 70)
    print()
    print("💡 PRÓXIMOS PASSOS:")
    print("   1. Acesse o admin Django: /admin/finance/campaign/")
    print("   2. Veja as colunas 'Execuções' e 'Última Execução' com badges visuais")
    print("   3. Execute outras campanhas e veja o contador aumentar")
    print()

if __name__ == '__main__':
    test_execution_tracking()
