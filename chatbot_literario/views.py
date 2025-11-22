from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json
import logging
import uuid

from .models import ChatConversation
from .gemini_service import get_chat_service

logger = logging.getLogger(__name__)


class ChatbotView(LoginRequiredMixin, TemplateView):
    """
    View para a interface do chatbot literário.
    Requer login para acesso.
    """
    template_name = 'chatbot_literario/chat.html'
    login_url = '/accounts/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Gerar ou recuperar session_id
        session_id = self.request.session.get('chat_session_id')
        if not session_id:
            session_id = str(uuid.uuid4())
            self.request.session['chat_session_id'] = session_id

        context['session_id'] = session_id

        # Verificar se o serviço está disponível
        chat_service = get_chat_service()
        context['service_available'] = chat_service.is_available()

        return context


@require_http_methods(["POST"])
@login_required
def send_message(request):
    """
    API endpoint para enviar mensagem ao chatbot.

    Expects JSON:
    {
        "message": "user message",
        "session_id": "optional session id"
    }

    Returns JSON:
    {
        "success": true/false,
        "response": "bot response",
        "error": "error message if any"
    }
    """
    try:
        # Parse request body
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        session_id = data.get('session_id') or request.session.get('chat_session_id')

        if not user_message:
            return JsonResponse({
                'success': False,
                'response': None,
                'error': 'Mensagem não pode estar vazia'
            }, status=400)

        # Gerar session_id se não existir
        if not session_id:
            session_id = str(uuid.uuid4())
            request.session['chat_session_id'] = session_id

        # Salvar mensagem do usuário
        ChatConversation.objects.create(
            user=request.user,
            role='user',
            message=user_message,
            session_id=session_id
        )

        # Buscar histórico da conversa
        history = ChatConversation.get_user_history(
            user=request.user,
            limit=20,
            session_id=session_id
        )

        # Converter para formato esperado pelo serviço
        conversation_history = [
            {
                'role': msg.role,
                'message': msg.message
            }
            for msg in history
        ]

        # Obter resposta do Gemini
        chat_service = get_chat_service()
        result = chat_service.get_response(
            user_message=user_message,
            conversation_history=conversation_history[:-1]  # Excluir a última (atual)
        )

        if result['success']:
            # Salvar resposta do bot
            ChatConversation.objects.create(
                user=request.user,
                role='assistant',
                message=result['response'],
                session_id=session_id
            )

            return JsonResponse({
                'success': True,
                'response': result['response'],
                'error': None,
                'session_id': session_id
            })
        else:
            return JsonResponse({
                'success': False,
                'response': None,
                'error': result['error']
            }, status=500)

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'response': None,
            'error': 'JSON inválido'
        }, status=400)
    except Exception as e:
        logger.error(f"Erro ao processar mensagem do chat: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'response': None,
            'error': 'Erro interno do servidor'
        }, status=500)


@require_http_methods(["GET"])
@login_required
def get_history(request):
    """
    API endpoint para obter histórico de conversas.

    Query params:
    - session_id: ID da sessão (opcional)
    - limit: Número máximo de mensagens (padrão: 20)

    Returns JSON:
    {
        "success": true,
        "messages": [
            {
                "role": "user"/"assistant",
                "message": "content",
                "created_at": "timestamp"
            }
        ]
    }
    """
    try:
        session_id = request.GET.get('session_id') or request.session.get('chat_session_id')
        limit = int(request.GET.get('limit', 20))

        history = ChatConversation.get_user_history(
            user=request.user,
            limit=limit,
            session_id=session_id
        )

        messages = [
            {
                'role': msg.role,
                'message': msg.message,
                'created_at': msg.created_at.isoformat()
            }
            for msg in history
        ]

        return JsonResponse({
            'success': True,
            'messages': messages,
            'session_id': session_id
        })

    except Exception as e:
        logger.error(f"Erro ao buscar histórico: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'messages': [],
            'error': str(e)
        }, status=500)


@require_http_methods(["POST"])
@login_required
def clear_history(request):
    """
    API endpoint para limpar histórico de conversas.

    POST JSON:
    {
        "session_id": "optional session id"
    }

    Returns JSON:
    {
        "success": true,
        "count": number of messages deleted
    }
    """
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id') or request.session.get('chat_session_id')

        count = ChatConversation.clear_user_history(
            user=request.user,
            session_id=session_id
        )

        # Gerar novo session_id
        new_session_id = str(uuid.uuid4())
        request.session['chat_session_id'] = new_session_id

        return JsonResponse({
            'success': True,
            'count': count,
            'session_id': new_session_id
        })

    except Exception as e:
        logger.error(f"Erro ao limpar histórico: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'count': 0,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
@login_required
def check_service(request):
    """
    API endpoint para verificar se o serviço está disponível.

    Returns JSON:
    {
        "available": true/false,
        "message": "status message"
    }
    """
    chat_service = get_chat_service()
    available = chat_service.is_available()

    return JsonResponse({
        'available': available,
        'message': 'Serviço disponível' if available else 'Serviço indisponível - verifique configuração da API Key'
    })
