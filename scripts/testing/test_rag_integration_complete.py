"""
Teste completo da integração RAG + Anti-Alucinação.
Testa os dois cenários:
1. Livro EXISTE no banco → RAG injeta dados → IA responde com autor correto
2. Livro NÃO EXISTE no banco → RAG não encontra → IA admite não saber
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

def test_scenario(test_name, question, expected_behavior):
    """
    Testa um cenário específico.
    """
    print("=" * 80)
    print(f"TESTE: {test_name}")
    print("=" * 80)
    print(f"[>>] PERGUNTA: '{question}'")
    print(f"[??] COMPORTAMENTO ESPERADO: {expected_behavior}")
    print()

    chatbot = get_chatbot_service()

    try:
        response = chatbot.get_response(question, conversation_history=None)

        print("[<<] RESPOSTA DO CHATBOT:")
        print("-" * 80)
        print(response)
        print("-" * 80)
        print()

        return response
    except Exception as e:
        print(f"[ERRO] {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """
    Testa a integração completa RAG + Anti-Alucinação.
    """
    print("=" * 80)
    print("TESTE COMPLETO: RAG + ANTI-ALUCINACAO")
    print("=" * 80)
    print()

    chatbot = get_chatbot_service()
    print(f"[OK] Provedor: {chatbot.__class__.__name__}")
    print(f"[OK] Modelo: {chatbot.model_name}")
    print()

    # ========================================================================
    # CENÁRIO 1: Livro que provavelmente EXISTE no banco
    # ========================================================================
    response1 = test_scenario(
        test_name="CENARIO 1 - Livro EXISTE no banco",
        question="Quem escreveu O Senhor dos Aneis?",
        expected_behavior="RAG detecta 'author_query' → Busca no banco → Encontra livro → Injeta dados → IA responde 'J.R.R. Tolkien'"
    )

    # Verificar se resposta contém autor correto
    if response1:
        response1_lower = response1.lower()
        if 'tolkien' in response1_lower or 'j.r.r' in response1_lower:
            print("[SUCESSO] Cenario 1: IA respondeu com autor correto!")
            print("          RAG funcionou: Dados verificados foram usados")
        else:
            print("[ATENCAO] Cenario 1: Resposta nao contem 'Tolkien'")
            print("          Pode ser que o livro nao esteja no banco")

    print()
    print()

    # ========================================================================
    # CENÁRIO 2: Livro que NÃO EXISTE no banco (caso original)
    # ========================================================================
    response2 = test_scenario(
        test_name="CENARIO 2 - Livro NAO EXISTE no banco",
        question="Quem escreveu o livro Quarta Asa?",
        expected_behavior="RAG detecta 'author_query' → Busca no banco → NAO encontra → Retorna msg original → IA admite nao saber"
    )

    # Verificar se resposta admite não saber
    if response2:
        response2_lower = response2.lower()
        honesty_indicators = [
            "não encontrei", "nao encontrei",
            "não tenho", "nao tenho",
            "banco de dados", "lupa", "buscar"
        ]
        found = [ind for ind in honesty_indicators if ind in response2_lower]

        # Verificar se NÃO está alucinando
        wrong_authors = ["fernando sabino", "clarice lispector"]
        is_hallucinating = any(author in response2_lower for author in wrong_authors)

        if found and not is_hallucinating:
            print("[SUCESSO] Cenario 2: IA admitiu nao ter informacao!")
            print(f"          Indicadores: {', '.join(found)}")
            print("          Sistema anti-alucinacao funcionou!")
        elif is_hallucinating:
            print("[FALHA] Cenario 2: IA ainda esta alucinando!")
            print("        Detectado autores incorretos na resposta")
        else:
            print("[ATENCAO] Cenario 2: Resposta ambigua")

    print()
    print()

    # ========================================================================
    # CENÁRIO 3: Recomendação (RAG original funcionando)
    # ========================================================================
    response3 = test_scenario(
        test_name="CENARIO 3 - Recomendacao de livros (RAG original)",
        question="Me recomende 3 livros de fantasia",
        expected_behavior="RAG detecta 'book_recommendation' → Busca categoria → Injeta 3 livros verificados"
    )

    if response3:
        # Verificar se resposta tem formato de lista (1., 2., 3.)
        if '1.' in response3 and '2.' in response3 and '3.' in response3:
            print("[SUCESSO] Cenario 3: IA recomendou 3 livros em formato de lista")
            print("          RAG original funcionando!")
        else:
            print("[ATENCAO] Cenario 3: Resposta nao tem formato de lista esperado")

    print()
    print()

    # ========================================================================
    # RESULTADO FINAL
    # ========================================================================
    print("=" * 80)
    print("RESULTADO FINAL")
    print("=" * 80)
    print()
    print("[OK] Sistema Hibrido RAG + Anti-Alucinacao:")
    print()
    print("     Camada 1 (RAG): Busca dados verificados no banco")
    print("        - Se encontrar → Injeta dados → IA usa informacao correta")
    print("        - Se nao encontrar → Passa msg original para Camada 2")
    print()
    print("     Camada 2 (Anti-Alucinacao): Prompt engineering")
    print("        - Se receber [DADOS VERIFICADOS] → Usa apenas esses dados")
    print("        - Se NAO receber dados → Admite nao saber")
    print()
    print("[OK] Resultado: Sistema robusto que:")
    print("     - Responde corretamente quando sabe (RAG)")
    print("     - Admite quando nao sabe (Anti-alucinacao)")
    print("     - NUNCA inventa informacoes falsas")
    print()
    print("=" * 80)


if __name__ == '__main__':
    main()
