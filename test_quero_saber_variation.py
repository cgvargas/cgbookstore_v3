"""
Teste específico para a variação "Quero saber quem escreveu".
"""
import os
import sys
import django

# Configurar encoding para UTF-8
if sys.platform == 'win32':
    os.system('')
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from chatbot_literario.gemini_service import get_chatbot_service


def test_variation():
    """Testa a variação 'Quero saber quem escreveu'."""
    print("=" * 80)
    print("TESTE: Variacao 'Quero saber quem escreveu'")
    print("=" * 80)
    print()

    chatbot = get_chatbot_service()
    print(f"[OK] Provedor: {chatbot.__class__.__name__}")
    print(f"[OK] Modelo: {chatbot.model_name}")
    print()

    # Testar todas as variações
    test_cases = [
        "Quero saber quem escreveu o livro Quarta Asa?",
        "Gostaria de saber quem escreveu Quarta Asa",
        "Quem escreveu Quarta Asa?",  # Original que funciona
    ]

    for i, question in enumerate(test_cases, 1):
        print(f"[TESTE {i}] {question}")
        print()

        try:
            response = chatbot.get_response(question, conversation_history=None)
            print(f"[RESPOSTA] {response}")
            print()

            # Verificar se Rebecca Yarros está na resposta
            if 'rebecca yarros' in response.lower():
                print(f"[SUCESSO] Autor correto detectado! ✅")
            else:
                print(f"[FALHA] Autor não detectado na resposta ❌")

            print("-" * 80)
            print()

        except Exception as e:
            print(f"[ERRO] {e}")
            import traceback
            traceback.print_exc()
            print()

    print("=" * 80)
    print("FIM DOS TESTES")
    print("=" * 80)


if __name__ == '__main__':
    test_variation()
