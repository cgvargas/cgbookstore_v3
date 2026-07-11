import os
import sys
import django
from unittest.mock import MagicMock, patch

# Configurar encoding para UTF-8
if sys.platform == 'win32':
    os.system('')  # Habilitar ANSI escape codes no Windows
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Adicionar raiz do projeto ao path para localizar cgbookstore
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from chatbot_literario.models import ChatSession
from chatbot_literario.views import SendMessageAPIView
from chatbot_literario.support_service import get_support_chatbot_service

def test_views_fallback():
    print("=" * 80)
    print("TESTE 1: Simulando erro 429 no Groq na View do Chatbot")
    print("=" * 80)

    # 1. Configurar Mock do Groq para lançar exceção 429
    # Criamos a exceção do Groq
    from groq import APIStatusError
    mock_response = MagicMock()
    mock_response.status_code = 429
    
    # Exceção simulada de limite de taxa do Groq
    groq_429_error = APIStatusError(
        message="Rate limit reached for model llama-3.3-70b-versatile. Limit: 6000 TPM.",
        response=mock_response,
        body={"error": {"message": "Rate limit reached for llama-3.3-70b-versatile"}}
    )

    # Mock do Gemini para responder com sucesso
    mock_gemini_response = MagicMock()
    mock_gemini_response.text = "Olá! Eu sou o assistente literário respondendo via Gemini devido ao fallback do Groq!"
    mock_gemini_response.candidates = [MagicMock(finish_reason=1)] # 1 = STOP (sucesso)

    # Criar um usuário de teste e sessão
    user = User.objects.get_or_create(username="testuser", email="test@example.com")[0]
    session = ChatSession.objects.create(user=user, title="Sessão de Teste Fallback")

    from rest_framework.test import APIRequestFactory, force_authenticate
    factory = APIRequestFactory()
    request = factory.post('/api/chatbot/send/', {
        'message': 'Olá, chatbot!',
        'session_id': session.id
    }, format='json')
    force_authenticate(request, user=user)

    # Patch GroqChatbotService.client.chat.completions.create para levantar erro 429
    # E patch do Gemini model generate_content para simular sucesso
    with patch('chatbot_literario.groq_service.GroqChatbotService.client') as mock_groq_client, \
         patch('google.generativeai.GenerativeModel.generate_content') as mock_generate_content, \
         patch('django.conf.settings.AI_PROVIDER', 'groq'), \
         patch('monitoring.tasks.dispatch_whatsapp_alert') as mock_alert_task:
        
        # Fazer a chamada do Groq falhar
        mock_groq_client.chat.completions.create.side_effect = groq_429_error
        # Fazer o Gemini funcionar
        mock_generate_content.return_value = mock_gemini_response

        # Executar a View
        view = SendMessageAPIView.as_view()
        response = view(request)

        print(f"Status Code da View: {response.status_code}")
        print(f"Dados retornados: {response.data}")
        
        # Asserções
        assert response.status_code == 200, "A resposta devia ser 200 OK!"
        assert "Gemini" in response.data['bot_message']['content'], "Deveria ter usado o Gemini como fallback!"
        print("\n✅ Teste 1 (Views) passou com sucesso! Fallback Groq -> Gemini funcionou.")
        print()

def test_support_service_fallback():
    print("=" * 80)
    print("TESTE 2: Simulando erro 429 no Groq no Serviço de Suporte")
    print("=" * 80)

    from groq import APIStatusError
    mock_response = MagicMock()
    mock_response.status_code = 429
    groq_429_error = APIStatusError(
        message="Rate limit reached for model llama-3.3-70b-versatile.",
        response=mock_response,
        body={"error": {"message": "Rate limit reached for llama-3.3-70b-versatile"}}
    )

    mock_gemini_response = MagicMock()
    mock_gemini_response.text = "Olá, estou te ajudando via Gemini suporte."
    mock_gemini_response.candidates = [MagicMock(finish_reason=1)]
    mock_gemini_response.prompt_feedback.block_reason = None

    mock_chat = MagicMock()
    mock_chat.send_message.return_value = mock_gemini_response

    # Instanciar o serviço de suporte
    support_service = get_support_chatbot_service()
    support_service._provider = 'groq'
    support_service._service = None

    with patch('chatbot_literario.groq_service.GroqChatbotService.client') as mock_groq_client, \
         patch('google.generativeai.GenerativeModel.start_chat') as mock_start_chat:

        # Fazer o Groq falhar
        mock_groq_client.chat.completions.create.side_effect = groq_429_error
        # Fazer o Gemini funcionar
        mock_start_chat.return_value = mock_chat

        # Chamar get_response
        response = support_service.get_response("Preciso de ajuda com minha senha")
        print(f"Resposta obtida: {response}")

        assert "Gemini" in response, "O serviço de suporte deveria ter feito fallback para o Gemini!"
        print("\n✅ Teste 2 (Support Service) passou com sucesso! Fallback Groq -> Gemini funcionou no suporte.")
        print()

if __name__ == "__main__":
    try:
        test_views_fallback()
        test_support_service_fallback()
        print("🎉 TODOS OS TESTES PASSARAM COM SUCESSO!")
    except Exception as e:
        print(f"❌ TESTE FALHOU: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
