"""
Script simples para testar o chatbot literário sem infraestrutura Django.
Uso: python test_chatbot_simple.py
"""
import os
import sys

# Configurar DJANGO_SETTINGS_MODULE
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')

# Adicionar o diretório do projeto ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importar Django e configurar
import django
django.setup()

from chatbot_literario.gemini_service import get_chatbot_service

def main():
    print("=" * 70)
    print("  🤖 TESTE SIMPLES DO CHATBOT LITERÁRIO - NOVA CONFIGURAÇÃO")
    print("=" * 70)

    # Inicializar serviço
    print("\n🔧 Inicializando serviço...")
    try:
        service = get_chatbot_service()
        print("✅ Serviço inicializado")
        print(f"   - Temperature: {service.generation_config['temperature']}")
        print(f"   - Max tokens: {service.generation_config['max_output_tokens']}")
        print(f"   - Prompt simplificado: {len(service.SYSTEM_PROMPT)} caracteres")
    except Exception as e:
        print(f"❌ Erro: {e}")
        return

    # Teste 1: Recomendação (DEVE usar nome e ser conciso)
    print("\n" + "─" * 70)
    print("📨 TESTE 1: Recomendação de livro")
    print("   (Deve: usar nome, 3 títulos específicos, ser conciso)")

    msg1 = "[Usuário: Dbit] Me recomende um livro de ficção científica"
    print(f"👤 Mensagem: {msg1}")

    try:
        resp1 = service.get_response(msg1)
        print(f"\n🤖 Resposta:\n{resp1}\n")

        # Verificações
        if "Dbit" in resp1:
            print("✅ Usa o nome do usuário")
        else:
            print("❌ NÃO usou o nome do usuário!")

        if len(resp1) < 500:
            print("✅ Resposta concisa")
        else:
            print(f"⚠️  Resposta longa ({len(resp1)} caracteres)")
    except Exception as e:
        print(f"❌ Erro: {e}")

    # Teste 2: Onde comprar (NUNCA deve dizer que vende)
    print("\n" + "─" * 70)
    print("📨 TESTE 2: Onde comprar livro")
    print("   (Deve: indicar Amazon, NÃO dizer 'vendemos')")

    msg2 = "[Usuário: Dbit] Onde posso comprar O Silmarillion?"
    print(f"👤 Mensagem: {msg2}")

    try:
        resp2 = service.get_response(msg2)
        print(f"\n🤖 Resposta:\n{resp2}\n")

        # Verificações
        if "vende" in resp2.lower() or "vendemos" in resp2.lower():
            print("❌ ERRO CRÍTICO: Diz que vende livros!")
        else:
            print("✅ NÃO diz que vende livros")

        if "Amazon" in resp2:
            print("✅ Indica Amazon")
        else:
            print("⚠️  Não menciona Amazon")

        if "comunidade" in resp2.lower() or "aplicação" in resp2.lower():
            print("✅ Explica que é comunidade/aplicação")
        else:
            print("⚠️  Não explica modelo de negócio")
    except Exception as e:
        print(f"❌ Erro: {e}")

    # Teste 3: O que é CG.BookStore
    print("\n" + "─" * 70)
    print("📨 TESTE 3: Explicar o que é CG.BookStore")
    print("   (Deve: dizer que é comunidade/app, NÃO e-commerce)")

    msg3 = "[Usuário: Dbit] Vocês vendem livros?"
    print(f"👤 Mensagem: {msg3}")

    try:
        resp3 = service.get_response(msg3)
        print(f"\n🤖 Resposta:\n{resp3}\n")

        # Verificações críticas
        if "sim" in resp3.lower() and "vende" in resp3.lower():
            print("❌ ERRO CRÍTICO: Diz que SIM, vendemos!")
        elif "não" in resp3.lower() and ("vende" in resp3.lower() or "vendemos" in resp3.lower()):
            print("✅ Corretamente diz que NÃO vende")
        else:
            print("⚠️  Resposta ambígua sobre vendas")

        if "comunidade" in resp3.lower():
            print("✅ Menciona comunidade")
        else:
            print("⚠️  Não menciona comunidade")
    except Exception as e:
        print(f"❌ Erro: {e}")

    print("\n" + "=" * 70)
    print("✨ TESTE CONCLUÍDO")
    print("=" * 70)

if __name__ == "__main__":
    main()
