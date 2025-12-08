"""
Teste para verificar se a correção de alucinação do chatbot está funcionando.
"""
import os
import sys
import django

# Configurar encoding para UTF-8
if sys.platform == 'win32':
    os.system('')  # Habilitar ANSI escape codes no Windows
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from chatbot_literario.gemini_service import get_chatbot_service

def test_chatbot_no_hallucination():
    """
    Testa se o chatbot agora responde corretamente quando não sabe a resposta.
    """
    print("=" * 80)
    print("TESTE: Verificacao de Alucinacao do Chatbot")
    print("=" * 80)
    print()

    # Obter serviço do chatbot (GROQ configurado no .env)
    chatbot = get_chatbot_service()

    print(f"[OK] Provedor de IA: {chatbot.__class__.__name__}")
    print(f"[OK] Modelo: {chatbot.model_name}")
    print()

    # Teste 1: Pergunta sobre livro que provavelmente não está no banco
    test_message = "Quem escreveu o livro Quarta Asa?"

    print(f"[>>] PERGUNTA DE TESTE:")
    print(f"     '{test_message}'")
    print()
    print("[...] Aguardando resposta da IA...")
    print()

    try:
        response = chatbot.get_response(test_message, conversation_history=None)

        print("=" * 80)
        print("[<<] RESPOSTA DO CHATBOT:")
        print("=" * 80)
        print(response)
        print()

        # Verificar se a resposta contém indicadores de honestidade
        honesty_indicators = [
            "não encontrei",
            "nao encontrei",
            "não tenho",
            "nao tenho",
            "não sei",
            "nao sei",
            "não tenho certeza",
            "nao tenho certeza",
            "banco de dados",
            "lupa",
            "buscar"
        ]

        response_lower = response.lower()
        found_indicators = [ind for ind in honesty_indicators if ind in response_lower]

        # Verificar se NÃO está alucinando (inventando autores)
        wrong_authors = ["fernando sabino", "clarice lispector", "guimaraes rosa"]
        is_hallucinating = any(author in response_lower for author in wrong_authors)

        print("=" * 80)
        print("[ANALISE] ANALISE DA RESPOSTA:")
        print("=" * 80)

        if found_indicators and not is_hallucinating:
            print("[SUCESSO] Chatbot admitiu nao ter a informacao!")
            print(f"          Indicadores encontrados: {', '.join(found_indicators)}")
            print()
            print("[OK] A correcao funcionou! O chatbot agora:")
            print("     - Admite quando nao sabe")
            print("     - Nao inventa informacoes")
            print("     - Sugere usar a busca")
        elif is_hallucinating:
            print("[FALHA] Chatbot ainda esta alucinando!")
            print("        Detectado: Menciona autores incorretos")
        else:
            print("[ATENCAO] Resposta ambigua")
            print("          A resposta nao contem indicadores claros de honestidade")
            print("          mas tambem nao esta claramente alucinando.")

        print()

    except Exception as e:
        print(f"[ERRO] Erro ao testar chatbot: {e}")
        import traceback
        traceback.print_exc()

    print("=" * 80)
    print("FIM DO TESTE")
    print("=" * 80)

if __name__ == '__main__':
    test_chatbot_no_hallucination()
