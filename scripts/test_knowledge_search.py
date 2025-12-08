"""
Testa a busca de conhecimentos
"""
import os
import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'cgbookstore.settings'
django.setup()

from chatbot_literario.knowledge_base_service import get_knowledge_service

kb_service = get_knowledge_service()

# Testes
questions = [
    "Como posso debater sobre um livro com outros usuarios?",
    "Quero saber como inicio um debate com a comunidade sobre um livro",
    "Onde posso encontrar livros de autores novos?",
    "Como avaliar um livro?",
]

print("=" * 70)
print("TESTANDO BUSCA DE CONHECIMENTOS")
print("=" * 70)

for question in questions:
    print(f"\nPergunta: {question}")
    print("-" * 70)

    result = kb_service.search_knowledge(question)

    if result:
        print(f"ENCONTRADO!")
        print(f"Pergunta Original: {result['original_question'][:60]}...")
        print(f"Keywords: {', '.join(result['keywords'][:5])}")
        print(f"Confianca: {result['confidence_score']}")
        print(f"\nResposta Correta:")
        print(result['correct_response'][:200] + "...")
    else:
        print("NAO ENCONTRADO")

print("\n" + "=" * 70)
