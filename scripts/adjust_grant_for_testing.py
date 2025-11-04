#!/usr/bin/env python
"""Ajusta data de concessao existente para testar notificacoes de expiracao."""
import os, sys, django
from datetime import timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from django.utils import timezone
from finance.models import CampaignGrant

grant = CampaignGrant.objects.filter(user__username='claud').first()
if grant:
    grant.expires_at = timezone.now() + timedelta(days=3)
    grant.save()
    print(f'Grant ID {grant.id} atualizado')
    print(f'Usuario: {grant.user.username}')
    print(f'Campanha: {grant.campaign.name}')
    print(f'Expira em: {grant.expires_at}')
    print(f'Dias restantes: 3')
else:
    print('Nenhuma concessao encontrada para usuario claud')
