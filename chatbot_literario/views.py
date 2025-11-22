from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
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
        "message": "status message",
        "details": {
            "api_key_configured": bool,
            "model_name": str,
            "can_initialize": bool,
            "error": str (if any)
        }
    }
    """
    from django.conf import settings

    chat_service = get_chat_service()
    available = chat_service.is_available()

    # Informações detalhadas de diagnóstico
    details = {
        'api_key_configured': bool(settings.GEMINI_API_KEY),
        'model_name': chat_service.model_name,
        'can_initialize': False,
        'error': None
    }

    # Tentar inicializar o modelo para verificar se está tudo OK
    if available:
        try:
            model = chat_service.model
            if model:
                details['can_initialize'] = True
            else:
                details['error'] = 'Modelo não pôde ser inicializado'
        except Exception as e:
            details['error'] = str(e)
            available = False

    return JsonResponse({
        'available': available,
        'message': 'Serviço disponível e operacional' if available else 'Serviço indisponível - verifique configuração da API Key',
        'details': details
    })


class DiagnosticView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """
    Página de diagnóstico do chatbot.
    Mostra informações detalhadas sobre o status da API Gemini.
    ACESSO RESTRITO: Apenas superusuários podem acessar esta página.
    """
    template_name = 'chatbot_literario/diagnostic.html'
    login_url = '/accounts/login/'

    def test_func(self):
        """Verifica se o usuário é superuser."""
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        chat_service = get_chat_service()

        # Informações de configuração
        context['api_key_configured'] = bool(settings.GEMINI_API_KEY)
        if settings.GEMINI_API_KEY:
            key = settings.GEMINI_API_KEY
            context['api_key_masked'] = key[:8] + '*' * (len(key) - 12) + key[-4:] if len(key) > 12 else '*' * len(key)
        else:
            context['api_key_masked'] = 'Não configurada'

        context['model_name'] = chat_service.model_name

        # Status do serviço
        context['service_available'] = chat_service.is_available()

        # Tentar inicializar modelo
        context['model_initialized'] = False
        context['initialization_error'] = None

        if context['service_available']:
            try:
                model = chat_service.model
                context['model_initialized'] = model is not None
                if not model:
                    context['initialization_error'] = 'Modelo retornou None'
            except Exception as e:
                context['initialization_error'] = str(e)

        # Estatísticas de uso
        if self.request.user.is_authenticated:
            total_messages = ChatConversation.objects.filter(user=self.request.user).count()
            user_messages = ChatConversation.objects.filter(user=self.request.user, role='user').count()
            bot_messages = ChatConversation.objects.filter(user=self.request.user, role='assistant').count()

            context['stats'] = {
                'total_messages': total_messages,
                'user_messages': user_messages,
                'bot_messages': bot_messages,
            }
        else:
            context['stats'] = None

        return context
