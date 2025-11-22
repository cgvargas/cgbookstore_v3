"""
Cria uma subscription premium ativa para o usuario especificado.
"""
import os
import django
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from finance.models import Subscription

# Usuario para criar subscription
USERNAME = 'claud'

print("="*60)
print("CRIACAO DE SUBSCRIPTION PREMIUM")
print("="*60)

# Buscar usuario
try:
    user = User.objects.get(username=USERNAME)
    print(f"\nUsuario encontrado: {user.username} ({user.email})")
except User.DoesNotExist:
    print(f"\nERRO: Usuario '{USERNAME}' nao encontrado!")
    exit(1)

# Verificar se ja tem subscription
existing_sub = Subscription.objects.filter(user=user).first()
if existing_sub:
    print(f"\nSubscription existente encontrada:")
    print(f"  Status: {existing_sub.status}")
    print(f"  Start: {existing_sub.start_date}")
    print(f"  Expiration: {existing_sub.expiration_date}")

    response = input("\nDeseja atualizar para ativa? (s/n): ")
    if response.lower() != 's':
        print("Operacao cancelada.")
        exit(0)

    # Atualizar subscription existente
    existing_sub.status = 'ativa'
    existing_sub.start_date = timezone.now()
    existing_sub.expiration_date = timezone.now() + timedelta(days=365)  # 1 ano
    existing_sub.next_billing_date = timezone.now() + timedelta(days=30)
    existing_sub.save()

    print("\nSubscription atualizada com sucesso!")
    print(f"  Status: {existing_sub.status}")
    print(f"  Valida ate: {existing_sub.expiration_date.strftime('%d/%m/%Y %H:%M')}")
else:
    # Criar nova subscription
    subscription = Subscription.objects.create(
        user=user,
        status='ativa',
        payment_method='pix',
        price=9.90,
        start_date=timezone.now(),
        expiration_date=timezone.now() + timedelta(days=365),  # 1 ano
        next_billing_date=timezone.now() + timedelta(days=30)
    )

    print("\nSubscription criada com sucesso!")
    print(f"  ID: {subscription.id}")
    print(f"  Status: {subscription.status}")
    print(f"  Valor: R$ {subscription.price}")
    print(f"  Valida ate: {subscription.expiration_date.strftime('%d/%m/%Y %H:%M')}")

print("\n" + "="*60)
print("VERIFICACAO")
print("="*60)

# Verificar acesso ao atributo subscription
user.refresh_from_db()
print(f"\nuser.subscription existe: {hasattr(user, 'subscription')}")
if hasattr(user, 'subscription'):
    print(f"user.subscription.status: {user.subscription.status}")
    print(f"user.subscription.is_active(): {user.subscription.is_active()}")

print("\nPremium ativado! Os anuncios nao devem mais aparecer.")
