import os
import sys

# Configurar Django settings para carregar variáveis de ambiente
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
import django
django.setup()

from django.conf import settings
import mercadopago

def test_mercadopago_connection():
    token = settings.MERCADOPAGO_ACCESS_TOKEN
    print("=== Teste de Conexao com MercadoPago ===")
    
    if not token:
        print("[ERRO] MERCADOPAGO_ACCESS_TOKEN nao esta configurado no arquivo .env!")
        return False
        
    print(f"Token encontrado: {token[:10]}...{token[-5:] if len(token) > 5 else ''}")
    
    try:
        # Inicializar SDK
        sdk = mercadopago.SDK(token)
        print("[OK] SDK inicializado com sucesso.")
        
        # Criar uma preferência de teste
        print("\nTestando criacao de Preferencia de Checkout...")
        preference_data = {
            "items": [{
                "title": "Teste de Assinatura CGBookStore",
                "quantity": 1,
                "unit_price": 9.90,
                "currency_id": "BRL"
            }],
            "back_urls": {
                "success": "https://cgbookstore.onrender.com/finance/subscription/success/",
                "failure": "https://cgbookstore.onrender.com/finance/subscription/failure/",
                "pending": "https://cgbookstore.onrender.com/finance/subscription/pending/"
            },
            "auto_return": "approved"
        }
        
        pref_response = sdk.preference().create(preference_data)
        if pref_response.get("status") == 201:
            pref = pref_response.get("response", {})
            print("[OK] Preferencia criada com sucesso!")
            print(f"   ID da Preferencia: {pref.get('id')}")
            print(f"   Sandbox Checkout URL: {pref.get('sandbox_init_point')}")
            print(f"   Production Checkout URL: {pref.get('init_point')}")
            return True
        else:
            print(f"[ERRO] Falha ao criar preferencia: {pref_response}")
            return False
            
    except Exception as e:
        print(f"[ERRO] Erro inesperado durante o teste: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_mercadopago_connection()
