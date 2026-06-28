"""
Script de teste unitário e de integração para o AIBookAssistantService.
Valida o comportamento com dados mockados e permite teste real se a API Key estiver configurada.
"""

import os
import sys
import django
from unittest.mock import MagicMock, patch

# Configurar Django
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Adicionar diretório raiz do projeto ao sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from core.services.ai_book_assistant import AIBookAssistantService
from core.models import Author, Category


def test_ai_assistant_mocked():
    """Valida o serviço usando dados mockados."""
    print("🧪 Rodando teste com API do Gemini mockada...")

    # Mock da resposta do Gemini
    mock_response_json = """
    {
      "title": "O Senhor dos Anéis: A Sociedade do Anel",
      "subtitle": "Parte I da trilogia O Senhor dos Anéis",
      "description": "Uma jornada fantástica pela Terra-média para destruir o Um Anel.",
      "publication_date": "1954-07-29",
      "isbn": "978-8533619081",
      "publisher": "Martins Fontes",
      "price": 59.90,
      "page_count": 424,
      "language": "pt",
      "available_print": true,
      "available_kindle": true,
      "available_audiobook": false,
      "available_pdf": false,
      "author_name": "J. R. R. Tolkien",
      "category_name": "Fantasia"
    }
    """

    # Criar autor e categoria de teste para verificar o mapeamento automático
    author, _ = Author.objects.get_or_create(
        name="J. R. R. Tolkien",
        defaults={"slug": "j-r-r-tolkien", "bio": "Escritor britânico."}
    )
    category, _ = Category.objects.get_or_create(
        name="Fantasia",
        defaults={"slug": "fantasia"}
    )

    # Patch do GenerativeModel
    with patch('google.generativeai.GenerativeModel') as MockModelClass:
        mock_model_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.text = mock_response_json
        mock_model_instance.generate_content.return_value = mock_response
        MockModelClass.return_value = mock_model_instance

        # Inicializa o serviço
        service = AIBookAssistantService()
        
        # Sobrescreve o modelo para garantir que a API real não seja chamada
        service.model = mock_model_instance

        # Executa análise
        result = service.analyze_book_data(text_content="Dados quaisquer de teste")

        # Asserts
        assert result['title'] == "O Senhor dos Anéis: A Sociedade do Anel", "Título incorreto"
        assert result['isbn'] == "978-8533619081", "ISBN incorreto"
        assert result['author_id'] == author.id, "ID do Autor não mapeado corretamente"
        assert result['category_id'] == category.id, "ID da Categoria não mapeado corretamente"
        assert result['available_print'] is True, "Formato físico incorreto"
        
        print("✅ Teste mockado concluído com SUCESSO!")
        print(f"   Título extraído: {result['title']}")
        print(f"   Autor mapeado: {result['author_name']} (ID: {result['author_id']})")
        print(f"   Categoria mapeada: {result['category_name']} (ID: {result['category_id']})")


def test_ai_assistant_live():
    """Valida o serviço fazendo chamada real se a chave de API estiver configurada."""
    service = AIBookAssistantService()
    if not service.is_available():
        print("\n⚠️ Teste live pulado: GEMINI_API_KEY não configurada no .env")
        return

    print("\n🧪 Rodando teste de integração real com a API do Gemini...")
    text_input = (
        "Cadastre para mim o livro O Hobbit do autor J. R. R. Tolkien da editora HarperCollins. "
        "O livro tem 328 páginas, foi lançado em 1937-09-21, ISBN 978-8595084741. "
        "É um livro físico de Fantasia que custa em média R$ 45,00."
    )

    try:
        result = service.analyze_book_data(text_content=text_input)
        print("✅ Chamada real à API do Gemini concluída com SUCESSO!")
        print(f"   JSON retornado: {result}")
    except Exception as e:
        print(f"   ❌ Falha no teste real com a API do Gemini: {e}")


if __name__ == "__main__":
    print("=" * 70)
    print("INICIANDO TESTES DO AI BOOK ASSISTANT")
    print("=" * 70)
    
    # 1. Teste mockado
    test_ai_assistant_mocked()
    
    # 2. Teste live (se aplicável)
    test_ai_assistant_live()
    
    print("=" * 70)
