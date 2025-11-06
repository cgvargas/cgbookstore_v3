import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
import django
django.setup()

from django.conf import settings
import mercadopago
import json

print("=" * 80)
print("DEBUG: Testando API do Mercado Pago")
print("=" * 80)

access_token = settings.MERCADOPAGO_ACCESS_TOKEN
print(f"\nAccess Token (primeiros 30 chars): {access_token[:30]}...")

sdk = mercadopago.SDK(access_token)

# Dados minimos para teste
test_data = {
    "items": [{
        "title": "Teste",
        "quantity": 1,
        "unit_price": 10.0,
        "currency_id": "BRL"
    }]
}

print("\nEnviando requisicao para criar preferencia...")
response = sdk.preference().create(test_data)

print(f"\nStatus HTTP: {response.get('status')}")
print(f"\nResposta completa:")
print(json.dumps(response, indent=2, ensure_ascii=False))

if response.get('status') == 403:
    print("\n" + "=" * 80)
    print("ERRO 403 DETECTADO!")
    print("=" * 80)
    print("\nPossiveis causas:")
    print("1. Aplicacao nao ativada no painel do Mercado Pago")
    print("2. Credenciais de producao sendo usadas sem aprovacao")
    print("3. Falta de permissoes na aplicacao")
    print("\nSOLUCAO:")
    print("- Crie uma NOVA aplicacao no painel")
    print("- Certifique-se de selecionar 'Pagamentos online'")
    print("- Use as credenciais de TESTE da nova aplicacao")
    print("=" * 80)
