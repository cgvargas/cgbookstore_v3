"""
Script de teste para os endpoints de view do Assistente Administrativo IA.
Valida o comportamento das rotas AJAX no Django.
"""

import os
import sys
import django
from django.test import Client
from django.contrib.auth import get_user_model

# Configurar Django
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Adicionar diretório raiz do projeto ao sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()
from django.conf import settings
if 'testserver' not in settings.ALLOWED_HOSTS:
    settings.ALLOWED_HOSTS.append('testserver')
from core.models import Author, Category


def test_admin_ai_views():
    print("=" * 70)
    print("TESTANDO ENDPOINTS AJAX DO ASSISTENTE IA")
    print("=" * 70)

    User = get_user_model()
    admin_user = User.objects.filter(is_superuser=True).first()
    
    if not admin_user:
        print("❌ Erro: Nenhum superusuário cadastrado no banco para rodar o teste.")
        return

    # Garantir que o usuário admin tenha is_staff=True e is_active=True
    admin_user.is_staff = True
    admin_user.is_active = True
    admin_user.save()

    client = Client()
    # Simular login completo usando a senha que acabamos de resetar
    login_success = client.login(username=admin_user.username, password='admin123456')
    print(f"✅ Usuário '{admin_user.username}' logado com sucesso? {login_success}")
    print(f"   Atributos: is_staff={admin_user.is_staff}, is_active={admin_user.is_active}, is_superuser={admin_user.is_superuser}")

    # 1. Testar criação rápida de autor
    print("\n🧪 Testando: Criar Autor Rápido...")
    author_name = "Novo Autor Teste IA"
    # Deletar se já existir
    Author.objects.filter(name=author_name).delete()
    
    response = client.post('/api/admin/book/create-author-quick/', {'name': author_name})
    assert response.status_code == 200, f"Status code incorreto: {response.status_code}"
    
    res_data = response.json()
    assert res_data['success'] is True, "Falha na criação rápida de autor"
    assert res_data['name'] == author_name, "Nome retornado divergente"
    author_id = res_data['id']
    print(f"   ✅ Autor criado com sucesso! ID: {author_id}, Nome: {res_data['name']}")

    # Testar se tenta criar de novo (deve retornar existente)
    response_again = client.post('/api/admin/book/create-author-quick/', {'name': author_name})
    res_data_again = response_again.json()
    assert res_data_again['id'] == author_id, "ID divergente ao tentar duplicar"
    print(f"   ✅ Tentativa de duplicação tratada corretamente: {res_data_again['message']}")

    # 2. Testar criação rápida de categoria
    print("\n🧪 Testando: Criar Categoria Rápida...")
    category_name = "Nova Categoria Teste IA"
    # Deletar se já existir
    Category.objects.filter(name=category_name).delete()
    
    response = client.post('/api/admin/book/create-category-quick/', {'name': category_name})
    assert response.status_code == 200, f"Status code incorreto: {response.status_code}"
    
    res_data = response.json()
    assert res_data['success'] is True, "Falha na criação rápida de categoria"
    assert res_data['name'] == category_name, "Nome retornado divergente"
    category_id = res_data['id']
    print(f"   ✅ Categoria criada com sucesso! ID: {category_id}, Nome: {res_data['name']}")

    # Testar se tenta criar de novo (deve retornar existente)
    response_again = client.post('/api/admin/book/create-category-quick/', {'name': category_name})
    res_data_again = response_again.json()
    assert res_data_again['id'] == category_id, "ID divergente ao tentar duplicar"
    print(f"   ✅ Tentativa de duplicação tratada corretamente: {res_data_again['message']}")

    # 3. Testar análise de metadados com texto estruturado (mockando o serviço da IA)
    print("\n🧪 Testando: Endpoint de Análise de Metadados (Mockado)...")
    from unittest.mock import patch
    
    mock_extracted = {
        "title": "O Hobbit",
        "subtitle": "",
        "description": "Uma sinopse teste.",
        "publication_date": "1937-09-21",
        "isbn": "9788595084741",
        "publisher": "HarperCollins",
        "price": 45.0,
        "page_count": 328,
        "language": "pt",
        "available_print": True,
        "available_kindle": False,
        "available_audiobook": False,
        "available_pdf": False,
        "author_name": author_name,
        "category_name": category_name,
        "author_id": author_id,
        "category_id": category_id
    }

    with patch('core.services.ai_book_assistant.AIBookAssistantService.analyze_book_data') as mock_analyze:
        mock_analyze.return_value = mock_extracted
        
        response = client.post('/api/admin/book/analyze-metadata/', {'text': 'Cadastre o hobbit'})
        assert response.status_code == 200, f"Status code incorreto: {response.status_code}"
        
        res_data = response.json()
        assert res_data['success'] is True, "Falha no endpoint de análise"
        assert res_data['data']['title'] == "O Hobbit", "Título extraído divergente"
        assert res_data['data']['author_id'] == author_id, "ID do Autor mapeado divergente"
        assert res_data['data']['category_id'] == category_id, "ID da Categoria mapeada divergente"
        
        print(f"   ✅ Endpoint de análise funcionou corretamente e retornou dados mapeados!")
        print(f"   Dados retornados: {res_data['data']}")

    # Limpeza
    Author.objects.filter(name=author_name).delete()
    Category.objects.filter(name=category_name).delete()
    print("\n🧹 Limpeza de dados de teste concluída.")
    print("=" * 70)


if __name__ == "__main__":
    test_admin_ai_views()
