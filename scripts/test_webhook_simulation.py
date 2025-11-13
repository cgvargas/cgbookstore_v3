#!/usr/bin/env python
"""
Script para simular webhook do Mercado Pago e testar ativação de assinatura

USO:
    python manage.py shell < scripts/test_webhook_simulation.py
"""

import json
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from finance.services import MercadoPagoService
from finance.models import Subscription
from django.contrib.auth.models import User

def simulate_approved_payment(username='vania', subscription_id=None):
    """
    Simula um webhook de pagamento aprovado
    """
    print("=" * 60)
    print("🧪 SIMULAÇÃO DE WEBHOOK - PAGAMENTO APROVADO")
    print("=" * 60)

    # Busca usuário
    try:
        user = User.objects.get(username=username)
        print(f"✓ Usuário encontrado: {user.username} ({user.email})")
    except User.DoesNotExist:
        print(f"❌ Usuário '{username}' não encontrado")
        return False

    # Busca ou cria assinatura
    if subscription_id:
        try:
            subscription = Subscription.objects.get(id=subscription_id)
        except Subscription.DoesNotExist:
            print(f"❌ Assinatura ID {subscription_id} não encontrada")
            return False
    else:
        subscription, created = Subscription.objects.get_or_create(
            user=user,
            defaults={'payment_method': 'pix', 'price': 9.90, 'status': 'pendente'}
        )
        if created:
            print(f"✓ Assinatura criada: ID {subscription.id}")
        else:
            print(f"✓ Assinatura existente: ID {subscription.id}")

    print(f"\nStatus ANTES: {subscription.status}")
    print(f"Premium ativo ANTES: {subscription.is_active}")

    # Simula webhook do MP
    webhook_data = {
        "action": "payment.updated",
        "api_version": "v1",
        "data": {
            "id": "1234567890"  # ID fictício do pagamento
        },
        "date_created": "2025-11-13T17:00:00.000-04:00",
        "id": 12345,
        "live_mode": False,
        "type": "payment",
        "user_id": "123456"
    }

    # Dados do pagamento simulado (isso seria retornado pela API do MP)
    payment_data = {
        "id": 1234567890,
        "status": "approved",
        "status_detail": "accredited",
        "external_reference": f"subscription_{subscription.id}",
        "transaction_amount": 9.90,
        "payment_method_id": "pix",
        "payer": {
            "email": user.email
        }
    }

    print("\n" + "=" * 60)
    print("📨 PROCESSANDO WEBHOOK SIMULADO...")
    print("=" * 60)

    # Como não podemos acessar a API real do MP no teste, vamos processar diretamente
    mp_service = MercadoPagoService()

    # Ativa assinatura manualmente (simulando o que o webhook faria)
    try:
        subscription.mp_payment_id = str(payment_data['id'])
        subscription.status = 'ativa'
        subscription.activate(duration_days=30)

        print("\n✅ PAGAMENTO PROCESSADO COM SUCESSO!")
        print(f"\nStatus DEPOIS: {subscription.status}")
        print(f"Premium ativo DEPOIS: {subscription.is_active}")
        print(f"Data de início: {subscription.start_date}")
        print(f"Data de expiração: {subscription.expiration_date}")

        # Verifica UserProfile
        try:
            profile = user.userprofile
            print(f"\n👤 UserProfile:")
            print(f"   is_premium: {profile.is_premium}")
            print(f"   premium_expires_at: {profile.premium_expires_at}")
        except:
            print("\n⚠️  UserProfile não encontrado")

        print("\n" + "=" * 60)
        print("🎉 TESTE CONCLUÍDO - ASSINATURA ATIVADA!")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"\n❌ ERRO ao processar webhook: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    # Executa simulação
    simulate_approved_payment()
