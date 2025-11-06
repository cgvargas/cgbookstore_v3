#!/usr/bin/env python
"""
Script de teste para simular Premium expirando e testar notificacoes.

Cria concessoes de Premium que expiram em diferentes períodos (3 dias, 1 dia, hoje)
e depois executa o comando de verificação para testar o envio de notificações.
"""
import os
import sys
import django
from datetime import timedelta

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from finance.models import Campaign, CampaignGrant
from accounts.models import UserProfile


def create_test_user(username, email):
    """Cria usuario de teste se nao existir."""
    user, created = User.objects.get_or_create(
        username=username,
        defaults={'email': email, 'is_active': True}
    )

    if created:
        print(f"Usuario criado: {username}")
        # Criar perfil
        UserProfile.objects.get_or_create(user=user)
    else:
        print(f"Usuario ja existe: {username}")

    return user


def create_test_campaign():
    """Cria campanha de teste."""
    now = timezone.now()
    campaign, created = Campaign.objects.get_or_create(
        name='Teste de Expiracao',
        defaults={
            'description': 'Campanha para testar notificacoes de expiracao',
            'duration_days': 7,
            'target_type': 'custom',
            'status': 'active',
            'max_grants': 100,
            'send_notification': True,
            'start_date': now.date(),
            'end_date': (now + timedelta(days=30)).date(),
        }
    )

    if created:
        print(f"Campanha criada: {campaign.name}")
    else:
        print(f"Campanha ja existe: {campaign.name}")

    return campaign


def create_expiring_grant(user, campaign, days_until_expiration):
    """Cria concessao que expira em N dias."""
    now = timezone.now()
    expires_at = now + timedelta(days=days_until_expiration)

    # Verificar se já existe
    existing = CampaignGrant.objects.filter(
        user=user,
        campaign=campaign,
        is_active=True
    ).first()

    if existing:
        # Atualizar data de expiracao
        existing.expires_at = expires_at
        existing.save()
        print(f"  Concessao atualizada: expira em {days_until_expiration} dia(s)")
        return existing
    else:
        # Criar nova
        grant = CampaignGrant.objects.create(
            user=user,
            campaign=campaign,
            granted_at=now - timedelta(days=campaign.duration_days - days_until_expiration),
            expires_at=expires_at,
            is_active=True,
            was_notified=True,  # Ja foi notificado da concessao inicial
        )
        print(f"  Concessao criada: expira em {days_until_expiration} dia(s)")
        return grant


def main():
    print("=" * 70)
    print("CRIACAO DE DADOS DE TESTE PARA NOTIFICACOES DE EXPIRACAO")
    print("=" * 70)
    print()

    # Criar campanha
    print("1. Criando campanha de teste...")
    campaign = create_test_campaign()
    print()

    # Criar usuarios e concessoes
    print("2. Criando usuarios e concessoes com diferentes datas de expiracao...")
    print()

    # Usuario 1: Expira em 3 dias
    print("Usuario 1: premium_expira_3d")
    user1 = create_test_user('premium_expira_3d', 'expira3d@test.com')
    grant1 = create_expiring_grant(user1, campaign, days_until_expiration=3)

    # Usuario 2: Expira em 1 dia
    print("\nUsuario 2: premium_expira_1d")
    user2 = create_test_user('premium_expira_1d', 'expira1d@test.com')
    grant2 = create_expiring_grant(user2, campaign, days_until_expiration=1)

    # Usuario 3: Expira hoje
    print("\nUsuario 3: premium_expira_hoje")
    user3 = create_test_user('premium_expira_hoje', 'expiraHoje@test.com')
    grant3 = create_expiring_grant(user3, campaign, days_until_expiration=0)

    # Usuario 4: Ja expirou (nao deve notificar)
    print("\nUsuario 4: premium_ja_expirou (nao deve notificar)")
    user4 = create_test_user('premium_ja_expirou', 'jaExpirou@test.com')
    grant4 = create_expiring_grant(user4, campaign, days_until_expiration=-1)

    # Usuario 5: Expira daqui 7 dias (nao deve notificar hoje)
    print("\nUsuario 5: premium_expira_7d (nao deve notificar hoje)")
    user5 = create_test_user('premium_expira_7d', 'expira7d@test.com')
    grant5 = create_expiring_grant(user5, campaign, days_until_expiration=7)

    print()
    print("=" * 70)
    print("RESUMO DOS DADOS CRIADOS")
    print("=" * 70)
    print(f"Campanha: {campaign.name} (ID: {campaign.id})")
    print()
    print("Concessoes criadas:")
    print(f"  1. {user1.username} - Expira em 3 dias  -> DEVE notificar")
    print(f"  2. {user2.username} - Expira em 1 dia   -> DEVE notificar")
    print(f"  3. {user3.username} - Expira hoje       -> DEVE notificar")
    print(f"  4. {user4.username} - Ja expirou        -> NAO deve notificar")
    print(f"  5. {user5.username} - Expira em 7 dias  -> NAO deve notificar")
    print()
    print("=" * 70)
    print("COMO TESTAR")
    print("=" * 70)
    print()
    print("1. Dry-run (simula sem enviar):")
    print("   python manage.py check_expiring_premium --dry-run")
    print()
    print("2. Testar apenas 3 dias:")
    print("   python manage.py check_expiring_premium --dry-run --days 3")
    print()
    print("3. Executar para valer:")
    print("   python manage.py check_expiring_premium")
    print()
    print("4. Ver notificacoes criadas:")
    print("   python scripts/list_notifications.py")
    print()
    print("=" * 70)
    print("PRONTO PARA TESTES!")
    print("=" * 70)


if __name__ == '__main__':
    main()
