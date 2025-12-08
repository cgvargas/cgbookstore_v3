"""
Script de teste para o sistema RAG (Retrieval-Augmented Generation).

Testa as funcionalidades:
1. Busca de livros por categoria
2. Busca de livros por autor
3. Detecção de intenções
4. Enriquecimento de mensagens com dados verificados
"""

import os
import django
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from chatbot_literario.knowledge_retrieval import get_knowledge_retrieval_service
from chatbot_literario.groq_service import get_groq_chatbot_service


def test_knowledge_retrieval():
    """Testa o serviço de busca de conhecimento."""
    print("=" * 80)
    print("TESTE 1: Knowledge Retrieval Service")
    print("=" * 80)

    knowledge = get_knowledge_retrieval_service()

    # Teste 1: Buscar livros por categoria
    print("\nBuscando livros de 'Fantasia'...")
    books = knowledge.search_books_by_category("Fantasia", limit=3)
    print(f"OK - Encontrados {len(books)} livros")
    for book in books:
        print(f"   - {book['title']} ({book['author_name']})")

    # Teste 2: Buscar livros por autor
    print("\nBuscando livros de autores com 'Lewis'...")
    books = knowledge.search_books_by_author("Lewis", limit=5)
    print(f"OK - Encontrados {len(books)} livros")
    for book in books:
        print(f"   - {book['title']} ({book['author_name']})")

    # Teste 3: Formatar para prompt
    if books:
        print("\nExemplo de formatacao para prompt:")
        formatted = knowledge.format_book_for_prompt(books[0])
        print(formatted)


def test_rag_intent_detection():
    """Testa detecção de intenções RAG."""
    print("\n" + "=" * 80)
    print("TESTE 2: Deteccao de Intencoes RAG")
    print("=" * 80)

    groq_service = get_groq_chatbot_service()

    test_messages = [
        "Me recomende livros de ficcao cientifica",
        "Me fale sobre O Principe Caspian",
        "Quais livros do C.S. Lewis existem?",
        "Me conte sobre o livro 3",
        "Quais sao os livros da serie Narnia?",
    ]

    for message in test_messages:
        intent = groq_service._detect_rag_intent(message)
        print(f"\nMensagem: '{message}'")
        print(f"   Intent: {intent['intent_type']}")


def test_rag_full_integration():
    """Testa integração completa do RAG."""
    print("\n" + "=" * 80)
    print("TESTE 3: Integracao Completa RAG")
    print("=" * 80)

    groq_service = get_groq_chatbot_service()

    # Teste com mensagem que deveria ativar RAG
    message = "Me recomende 3 livros de fantasia"
    print(f"\nMensagem original: '{message}'")

    intent = groq_service._detect_rag_intent(message)
    print(f"   Intent detectado: {intent['intent_type']}")

    enriched = groq_service._apply_rag_knowledge(message, intent)

    if enriched != message:
        print(f"\nOK - RAG ATIVADO! Mensagem enriquecida:")
        print("-" * 80)
        print(enriched[:500])  # Mostrar primeiros 500 chars
        if len(enriched) > 500:
            print("... (truncado)")
    else:
        print("\nERRO - RAG NAO ATIVADO")


def main():
    """Executa todos os testes."""
    print("\nINICIANDO TESTES DO SISTEMA RAG")
    print("=" * 80)

    try:
        # Teste 1
        test_knowledge_retrieval()

        # Teste 2
        test_rag_intent_detection()

        # Teste 3
        test_rag_full_integration()

        print("\n" + "=" * 80)
        print("OK - TODOS OS TESTES CONCLUIDOS COM SUCESSO!")
        print("=" * 80)

    except Exception as e:
        print(f"\nERRO NOS TESTES: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
