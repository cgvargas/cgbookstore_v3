"""
Teste final completo para o bug "Quarta Asa".
Testa TODAS as variações que o usuário tentou.
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


def test_quarta_asa():
    """Testa todas as variações de pergunta sobre 'Quarta Asa'."""
    print("=" * 80)
    print("TESTE FINAL - BUG 'Quarta Asa' RESOLVIDO")
    print("=" * 80)
    print()

    chatbot = get_chatbot_service()
    print(f"[OK] Provedor: {chatbot.__class__.__name__}")
    print(f"[OK] Modelo: {chatbot.model_name}")
    print()

    # Todas as variações que falharam antes
    test_cases = [
        {
            "question": "Quem escreveu o livro Quarta Asa?",
            "expected_author": "Rebecca Yarros",
            "description": "Pergunta direta - funcionava"
        },
        {
            "question": "Quero saber quem escreveu o livro Quarta Asa?",
            "expected_author": "Rebecca Yarros",
            "description": "Com 'Quero saber' - falhava antes"
        },
        {
            "question": "E o livro Quarta Asa, quem escreveu?",
            "expected_author": "Rebecca Yarros",
            "description": "Com 'E o livro' e vírgula - FALHAVA na conversa real"
        },
        {
            "question": "Gostaria de saber quem escreveu Quarta Asa",
            "expected_author": "Rebecca Yarros",
            "description": "Com 'Gostaria de saber'"
        },
    ]

    print("=" * 80)
    print("TESTANDO TODAS AS VARIAÇÕES")
    print("=" * 80)
    print()

    success_count = 0
    total_count = len(test_cases)

    for i, test_case in enumerate(test_cases, 1):
        question = test_case['question']
        expected_author = test_case['expected_author']
        description = test_case['description']

        print(f"[TESTE {i}/{total_count}] {description}")
        print(f"[PERGUNTA] {question}")
        print()

        try:
            response = chatbot.get_response(question, conversation_history=None)
            print(f"[RESPOSTA] {response}")
            print()

            # Verificar se o autor está na resposta
            if expected_author.lower() in response.lower():
                print(f"[✅ SUCESSO] Autor '{expected_author}' detectado na resposta!")
                success_count += 1
            else:
                print(f"[❌ FALHA] Autor '{expected_author}' NÃO detectado na resposta!")
                # Verificar se admitiu não saber (fallback correto)
                if 'não encontrei' in response.lower() or 'não tenho certeza' in response.lower():
                    print(f"[⚠️ INFO] IA admitiu não saber (fallback correto)")

        except Exception as e:
            print(f"[❌ ERRO] {e}")
            import traceback
            traceback.print_exc()

        print("-" * 80)
        print()

    # Resultado final
    print("=" * 80)
    print("RESULTADO FINAL")
    print("=" * 80)
    print()
    print(f"✅ Sucessos: {success_count}/{total_count}")
    print(f"❌ Falhas: {total_count - success_count}/{total_count}")
    print()

    if success_count == total_count:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print()
        print("✅ Bug 'Quarta Asa' foi RESOLVIDO com sucesso!")
        print()
        print("Melhorias implementadas:")
        print("  1. Detecção de vírgulas na pontuação")
        print("  2. Remoção de conjunções 'e o', 'e a', etc.")
        print("  3. Remoção de palavra 'livro' isolada")
        print("  4. Extração robusta de títulos com múltiplos casos edge")
    else:
        print("⚠️ Alguns testes ainda estão falhando.")
        print()
        print("Por favor, verifique os logs acima para detalhes.")

    print("=" * 80)


if __name__ == '__main__':
    test_quarta_asa()
