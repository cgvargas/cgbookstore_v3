"""
Script para testar credenciais do Mercado Pago
"""
import os
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# Configura Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
import django
django.setup()

from django.conf import settings
import mercadopago

def test_credentials():
    print("=" * 60)
    print("TESTE DE CREDENCIAIS DO MERCADO PAGO")
    print("=" * 60)

    # Verifica se as credenciais estão configuradas
    access_token = settings.MERCADOPAGO_ACCESS_TOKEN
    public_key = settings.MERCADOPAGO_PUBLIC_KEY

    print(f"\n1. Verificando configurações:")
    print(f"   ACCESS_TOKEN: {access_token[:20]}... (primeiros 20 caracteres)")
    print(f"   PUBLIC_KEY: {public_key[:20]}... (primeiros 20 caracteres)")

    # Verifica se são credenciais de teste ou produção
    if access_token.startswith('TEST-'):
        print(f"\n   ✓ Usando credenciais de TESTE (correto para desenvolvimento)")
    elif access_token.startswith('APP_USR-'):
        print(f"\n   ⚠ Usando credenciais de PRODUÇÃO")
        print(f"     AVISO: Para desenvolvimento, use credenciais de TESTE!")
        print(f"     Credenciais de produção exigem aprovação e configurações adicionais.")
    else:
        print(f"\n   ✗ Formato de credencial desconhecido!")
        return False

    # Testa a conexão
    print(f"\n2. Testando conexão com API do Mercado Pago...")
    try:
        sdk = mercadopago.SDK(access_token)

        # Tenta criar uma preferência de teste
        preference_data = {
            "items": [{
                "title": "Teste de Conexão",
                "description": "Teste",
                "quantity": 1,
                "unit_price": 10.00,
                "currency_id": "BRL"
            }],
            "external_reference": "test_123"
        }

        response = sdk.preference().create(preference_data)

        print(f"   Status da resposta: {response['status']}")

        if response['status'] == 201:
            print(f"\n   ✓ SUCESSO! Credenciais válidas e funcionando!")
            print(f"   Preference ID criado: {response['response']['id']}")
            return True
        elif response['status'] == 403:
            print(f"\n   ✗ ERRO 403 - UNAUTHORIZED")
            print(f"\n   Possíveis causas:")
            print(f"   1. Credenciais de produção sem aprovação")
            print(f"   2. Aplicação não ativada no painel")
            print(f"   3. Permissões insuficientes")
            print(f"\n   SOLUÇÃO: Use credenciais de TESTE para desenvolvimento")
            print(f"   Acesse: https://www.mercadopago.com.br/developers/panel/app")
            print(f"   Vá em 'Credenciais' > 'Credenciais de teste'")
            return False
        else:
            print(f"\n   ✗ Erro inesperado: {response}")
            return False

    except Exception as e:
        print(f"\n   ✗ ERRO: {str(e)}")
        return False

if __name__ == '__main__':
    success = test_credentials()

    print("\n" + "=" * 60)
    if success:
        print("STATUS: Tudo OK! Você pode usar o módulo finance.")
    else:
        print("STATUS: Há problemas com as credenciais.")
        print("\nPróximos passos:")
        print("1. Obtenha credenciais de TESTE em:")
        print("   https://www.mercadopago.com.br/developers/panel/app")
        print("2. Cole no arquivo .env")
        print("3. Reinicie o servidor Django")
    print("=" * 60)
