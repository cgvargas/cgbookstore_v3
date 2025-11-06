"""
Script para atualizar datas de campanhas expiradas
"""
import os
import sys
import django
from datetime import timedelta

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from django.utils import timezone
from finance.models import Campaign

def update_campaign_dates():
    """Atualiza datas de campanhas para o período atual"""

    now = timezone.now()
    print(f"Data atual: {now.strftime('%d/%m/%Y %H:%M')}\n")

    # Buscar campanhas expiradas
    expired_campaigns = Campaign.objects.filter(end_date__lt=now)

    if expired_campaigns.count() == 0:
        print("Nenhuma campanha expirada encontrada!")
        return

    print(f"Encontradas {expired_campaigns.count()} campanhas expiradas:\n")

    for campaign in expired_campaigns:
        print(f"  {campaign.name}")
        print(f"    Status: {campaign.status}")
        print(f"    Período antigo: {campaign.start_date.strftime('%d/%m/%Y')} até {campaign.end_date.strftime('%d/%m/%Y')}")

        # Atualizar datas
        campaign.start_date = now
        campaign.end_date = now + timedelta(days=365)
        campaign.save()

        print(f"    Período novo: {campaign.start_date.strftime('%d/%m/%Y')} até {campaign.end_date.strftime('%d/%m/%Y')}")
        print(f"    Ativa agora? {campaign.is_active_now()}\n")

    print(f"Total: {expired_campaigns.count()} campanhas atualizadas!")

if __name__ == '__main__':
    update_campaign_dates()
