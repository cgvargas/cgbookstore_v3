"""
Debug da extração de título da pergunta do usuário.
Simula exatamente o que acontece no groq_service.py
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

from core.models import Book


def extract_title(message):
    """Simula a lógica de extração do groq_service.py"""
    query_words = [
        'gostaria de saber quem escreveu o livro',
        'gostaria de saber quem escreveu',
        'quero saber quem escreveu o livro',
        'quero saber quem escreveu',
        'quem é o autor do livro',
        'quem é o autor de',
        'quem é o autor do',
        'quem é o autor',
        'quem escreveu o livro',
        'quem escreveu',
        'autor do livro',
        'autor de',
        'autor do',
        'escrito por',
        'o livro',
        'livro'
    ]

    book_title = message.lower()

    print(f"Mensagem original: '{message}'")
    print(f"Mensagem lower: '{book_title}'")
    print()

    # Remover palavras de query
    for query_word in query_words:
        if query_word in book_title:
            old_title = book_title
            book_title = book_title.replace(query_word, '', 1)
            print(f"Removeu '{query_word}': '{old_title}' -> '{book_title}'")
            break

    # Limpar pontuação
    book_title = book_title.replace('?', '').replace('!', '').replace('.', '').replace(',', '').replace(';', '').replace(':', '').strip()
    print(f"Após remover pontuação: '{book_title}'")
    print()

    # Remover artigos, preposições e conjunções
    articles = ['e o ', 'e a ', 'e os ', 'e as ', 'o ', 'a ', 'os ', 'as ', 'um ', 'uma ', 'de ', 'da ', 'do ']
    for article in articles:
        if book_title.startswith(article):
            old_title = book_title
            book_title = book_title[len(article):].strip()
            print(f"Removeu artigo '{article}': '{old_title}' -> '{book_title}'")

    # Remover palavra "livro" sozinha no início
    if book_title.startswith('livro '):
        old_title = book_title
        book_title = book_title[6:].strip()
        print(f"Removeu 'livro ' no início: '{old_title}' -> '{book_title}'")

    print(f"Título final extraído: '{book_title}'")
    print()

    return book_title


def test_extraction():
    """Testa a extração com as perguntas reais do usuário"""
    print("=" * 80)
    print("DEBUG: Extração de Título")
    print("=" * 80)
    print()

    test_cases = [
        "Quero saber quem escreveu o livro Quarta Asa?",
        "E o livro Quarta Asa, quem escreveu?",
        "Quem escreveu Quarta Asa?",
    ]

    for question in test_cases:
        print("-" * 80)
        extracted = extract_title(question)

        # Tentar buscar no banco
        print(f"Tentando buscar no banco com título: '{extracted}'")

        # Busca exata (case-insensitive)
        exact_match = Book.objects.filter(title__iexact=extracted).first()
        if exact_match:
            print(f"✅ BUSCA EXATA encontrou: '{exact_match.title}'")
        else:
            print(f"❌ BUSCA EXATA não encontrou")

        # Busca parcial
        partial_matches = Book.objects.filter(title__icontains=extracted)[:3]
        if partial_matches:
            print(f"✅ BUSCA PARCIAL encontrou {len(partial_matches)} resultado(s):")
            for book in partial_matches:
                print(f"   - '{book.title}'")
        else:
            print(f"❌ BUSCA PARCIAL não encontrou")

        print()

    print("=" * 80)
    print("Verificando se 'Quarta Asa' existe no banco:")
    print("=" * 80)
    quarta_asa = Book.objects.filter(title__icontains='quarta asa').first()
    if quarta_asa:
        print(f"✅ Livro encontrado:")
        print(f"   ID: {quarta_asa.id}")
        print(f"   Título: '{quarta_asa.title}'")
        print(f"   Autor: {quarta_asa.author.name if quarta_asa.author else 'N/A'}")
    else:
        print("❌ Livro não encontrado")


if __name__ == '__main__':
    test_extraction()
