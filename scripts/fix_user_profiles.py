"""
Script para corrigir UserProfiles e sincronizar com CampaignGrants
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from accounts.models import UserProfile
from finance.models import CampaignGrant

def fix_user_profiles():
    """Corrige UserProfiles e sincroniza com campanhas ativas"""

    print("Corrigindo UserProfiles...")

    # 1. Garantir que todos os usuários tenham UserProfile
    users_without_profile = User.objects.filter(profile__isnull=True)
    created_count = 0

    for user in users_without_profile:
        UserProfile.objects.create(user=user)
        created_count += 1
        print(f"  Criado UserProfile para: {user.username}")

    if created_count == 0:
        print("  Todos os usuarios ja tem UserProfile")
    else:
        print(f"  Total criados: {created_count}")

    print("\nSincronizando com concessoes ativas...")

    # 2. Atualizar UserProfiles baseado em concessões ativas
    active_grants = CampaignGrant.objects.filter(
        is_active=True,
        expires_at__gte=timezone.now()
    )

    updated_count = 0
    for grant in active_grants:
        try:
            profile = grant.user.profile
            profile.is_premium = True
            profile.premium_expires_at = grant.expires_at
            profile.save()
            updated_count += 1
            print(f"  Premium ativado para: {grant.user.username} (expira: {grant.expires_at.strftime('%d/%m/%Y')})")
        except UserProfile.DoesNotExist:
            print(f"  ERRO: UserProfile nao encontrado para {grant.user.username}")

    print(f"\nTotal de usuarios Premium atualizados: {updated_count}")
    print("Concluido!")

if __name__ == '__main__':
    fix_user_profiles()
