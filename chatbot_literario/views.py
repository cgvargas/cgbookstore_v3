"""
Views para o Chatbot Literário.
Inclui views para interface web e API REST.
"""
import time
import logging
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import ChatSession, ChatMessage, ConversationContext
from .serializers import (
    ChatSessionSerializer,
    ChatSessionListSerializer,
    SendMessageSerializer,
    ChatResponseSerializer,
    ConversationContextSerializer
)
from .gemini_service import get_chatbot_service

logger = logging.getLogger(__name__)


class ChatbotView(LoginRequiredMixin, TemplateView):
    """
    View para a interface do chatbot.
    Renderiza o template 'chatbot_literario/chat.html'.
    """
    template_name = 'chatbot_literario/chat.html'
    login_url = '/accounts/login/'


# ==================== API REST ====================


class SendMessageAPIView(APIView):
    """
    API para enviar mensagem ao chatbot e receber resposta.

    POST /api/chatbot/send/
    Body: {
        "message": "sua mensagem aqui",
        "session_id": 123  // opcional, cria nova sessão se não fornecido
    }

    Response: {
        "session_id": 123,
        "user_message": {...},
        "bot_message": {...},
        "session_title": "..."
    }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Processa mensagem do usuário e retorna resposta do chatbot."""
        # Validar dados de entrada
        serializer = SendMessageSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'error': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        user_message_text = serializer.validated_data['message']
        session_id = serializer.validated_data.get('session_id')

        try:
            # 1. Obter ou criar sessão
            if session_id:
                try:
                    session = ChatSession.objects.get(id=session_id, user=request.user)
                except ChatSession.DoesNotExist:
                    return Response(
                        {'error': 'Sessão não encontrada ou não pertence ao usuário'},
                        status=status.HTTP_404_NOT_FOUND
                    )
            else:
                # Criar nova sessão
                session = ChatSession.objects.create(user=request.user)

            # 2. Salvar mensagem do usuário
            user_message = ChatMessage.objects.create(
                session=session,
                role='user',
                content=user_message_text
            )

            # 3. Obter histórico da conversa (últimas 10 mensagens)
            previous_messages = session.messages.exclude(id=user_message.id).order_by('created_at')[:10]
            conversation_history = []

            # Obter nome do usuário (first_name ou username)
            user_name = request.user.first_name or request.user.username

            # Adicionar histórico de mensagens anteriores
            for msg in previous_messages:
                conversation_history.append({
                    "role": msg.role if msg.role == "user" else "model",
                    "parts": [msg.content]
                })

            # 4. Obter resposta do chatbot
            chatbot_service = get_chatbot_service()

            # Adicionar contexto do usuário à mensagem
            message_with_context = f"[Usuário: {user_name}] {user_message_text}"

            start_time = time.time()
            bot_response_text = chatbot_service.get_response(
                message=message_with_context,
                conversation_history=conversation_history
            )
            response_time = time.time() - start_time

            # 5. Salvar resposta do chatbot
            bot_message = ChatMessage.objects.create(
                session=session,
                role='assistant',
                content=bot_response_text,
                response_time=response_time
            )

            # 6. Gerar título da sessão se for a primeira mensagem do usuário
            if not session.title:
                session.generate_title()

            # 7. Preparar resposta
            response_data = {
                'session_id': session.id,
                'user_message': {
                    'id': user_message.id,
                    'role': user_message.role,
                    'content': user_message.content,
                    'created_at': user_message.created_at,
                },
                'bot_message': {
                    'id': bot_message.id,
                    'role': bot_message.role,
                    'content': bot_message.content,
                    'created_at': bot_message.created_at,
                    'response_time': bot_message.response_time,
                },
                'session_title': session.title
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {e}", exc_info=True)
            return Response(
                {'error': f'Erro ao processar mensagem: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ChatSessionListAPIView(APIView):
    """
    API para listar sessões de chat do usuário.

    GET /api/chatbot/sessions/

    Response: [
        {
            "id": 1,
            "title": "...",
            "is_active": true,
            "created_at": "...",
            "messages_count": 5,
            "last_message_time": "..."
        },
        ...
    ]
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Retorna todas as sessões do usuário."""
        sessions = ChatSession.objects.filter(user=request.user).order_by('-updated_at')
        serializer = ChatSessionListSerializer(sessions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ChatSessionDetailAPIView(APIView):
    """
    API para obter detalhes de uma sessão específica (incluindo mensagens).

    GET /api/chatbot/sessions/<id>/

    Response: {
        "id": 1,
        "title": "...",
        "is_active": true,
        "messages": [...]
    }
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, session_id):
        """Retorna detalhes de uma sessão específica."""
        try:
            session = ChatSession.objects.get(id=session_id, user=request.user)
            serializer = ChatSessionSerializer(session)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ChatSession.DoesNotExist:
            return Response(
                {'error': 'Sessão não encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )


class ClearSessionAPIView(APIView):
    """
    API para limpar/encerrar uma sessão de chat.

    POST /api/chatbot/sessions/<id>/clear/

    Response: {
        "message": "Sessão encerrada com sucesso"
    }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, session_id):
        """Encerra uma sessão de chat."""
        try:
            session = ChatSession.objects.get(id=session_id, user=request.user)
            session.is_active = False
            session.save()
            return Response(
                {'message': 'Sessão encerrada com sucesso'},
                status=status.HTTP_200_OK
            )
        except ChatSession.DoesNotExist:
            return Response(
                {'error': 'Sessão não encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )


class NewSessionAPIView(APIView):
    """
    API para criar uma nova sessão de chat.

    POST /api/chatbot/sessions/new/

    Response: {
        "session_id": 123,
        "message": "Nova sessão criada com sucesso"
    }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Cria uma nova sessão de chat."""
        try:
            session = ChatSession.objects.create(user=request.user)
            return Response(
                {
                    'session_id': session.id,
                    'message': 'Nova sessão criada com sucesso'
                },
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            logger.error(f"Erro ao criar nova sessão: {e}", exc_info=True)
            return Response(
                {'error': f'Erro ao criar sessão: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ConversationContextAPIView(APIView):
    """
    API para obter o contexto de conversa do usuário.

    GET /api/chatbot/context/

    Response: {
        "favorite_genres": [...],
        "favorite_authors": [...],
        "reading_preferences": {...},
        "interests": [...]
    }
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Retorna o contexto de conversa do usuário."""
        try:
            context, created = ConversationContext.objects.get_or_create(user=request.user)
            serializer = ConversationContextSerializer(context)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Erro ao obter contexto: {e}", exc_info=True)
            return Response(
                {'error': f'Erro ao obter contexto: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
