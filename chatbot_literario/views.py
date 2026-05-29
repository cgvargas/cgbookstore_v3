"""
Views para o Chatbot Literário e Chat de Suporte.
Inclui views para interface web e API REST.
"""
import time
import logging
from django.conf import settings
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
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

            # 2b. [MONITORAMENTO] Analisar conduta da mensagem de forma assíncrona
            try:
                from monitoring.detector import SuspiciousActivityDetector
                from monitoring.tasks import dispatch_whatsapp_alert
                detector = SuspiciousActivityDetector()
                ip_address = (
                    request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip()
                    or request.META.get('REMOTE_ADDR')
                )
                suspicious = detector.analyze_message(
                    user_message=user_message,
                    session=session,
                    user=request.user,
                    ip_address=ip_address,
                )
                if suspicious and suspicious.severity in ('medium', 'high', 'critical'):
                    dispatch_whatsapp_alert(activity_id=suspicious.pk)
            except Exception as monitor_err:
                logger.warning(f"⚠️ Erro no monitoramento de conduta (não crítico): {monitor_err}")

            # 3. Obter histórico da conversa (últimas 10 mensagens mais recentes)
            previous_messages = list(session.messages.exclude(id=user_message.id).order_by('-created_at')[:10])
            previous_messages.reverse()  # Ordenar cronologicamente
            conversation_history = []

            # Obter nome do usuário (first_name ou username)
            user_name = request.user.first_name or request.user.username

            # 4. Obter resposta do chatbot
            chatbot_service = get_chatbot_service()

            # Detectar qual provedor está sendo usado
            from django.conf import settings
            ai_provider = getattr(settings, 'AI_PROVIDER', 'gemini').lower()

            # Adicionar histórico de mensagens anteriores no formato correto
            for msg in previous_messages:
                # Usar conteúdo corrigido se a mensagem foi corrigida pelo administrador
                content_to_send = msg.corrected_content if msg.has_correction and msg.corrected_content else msg.content

                if ai_provider == 'groq':
                    # Formato OpenAI/Groq
                    conversation_history.append({
                        "role": msg.role if msg.role == "user" else "assistant",
                        "content": content_to_send
                    })
                else:
                    # Formato Gemini
                    conversation_history.append({
                        "role": msg.role if msg.role == "user" else "model",
                        "parts": [content_to_send]
                    })

            # Adicionar contexto do usuário APENAS na primeira mensagem (quando não há histórico)
            if not conversation_history:
                # Primeira mensagem: incluir nome para saudação personalizada
                message_with_context = f"[Usuário: {user_name}] {user_message_text}"
            else:
                # Mensagens seguintes: enviar apenas o texto, sem contexto de nome
                message_with_context = user_message_text

            start_time = time.time()
            
            # Tentar com o provedor principal (Gemini por padrão)
            try:
                bot_response_text = chatbot_service.get_response(
                    message=message_with_context,
                    conversation_history=conversation_history
                )
            except Exception as primary_error:
                error_str = str(primary_error).lower()
                # Se for erro de quota do Gemini, fazer fallback para Groq
                if ai_provider == 'gemini' and ('quota' in error_str or '429' in error_str or 'exceeded' in error_str):
                    logger.warning(f"⚠️ Quota Gemini excedida, fazendo fallback para Groq...")
                    try:
                        from .groq_service import get_groq_chatbot_service
                        groq_service = get_groq_chatbot_service()

                        # Converter histórico para formato Groq (OpenAI)
                        groq_history = []
                        for msg in previous_messages:
                            groq_history.append({
                                "role": msg.role if msg.role == "user" else "assistant",
                                "content": msg.content
                            })

                        bot_response_text = groq_service.get_response(
                            message=message_with_context,
                            conversation_history=groq_history
                        )
                        logger.info("✅ Fallback para Groq bem-sucedido!")
                    except Exception as fallback_error:
                        logger.error(f"❌ Fallback para Groq também falhou: {fallback_error}")
                        # [MONITORAMENTO] Registrar falha total da IA
                        try:
                            from monitoring.models import AIResponseAlert
                            from monitoring.tasks import dispatch_whatsapp_alert
                            alert = AIResponseAlert.objects.create(
                                session=session,
                                user=request.user,
                                alert_type='api_error',
                                severity='critical',
                                provider='gemini',
                                error_message=f"Gemini quota + Groq fallback falhou: {fallback_error}",
                                ai_response_preview='',
                            )
                            dispatch_whatsapp_alert(ai_alert_id=alert.pk)
                        except Exception as m_err:
                            logger.warning(f"Erro ao registrar alerta de IA: {m_err}")
                        raise fallback_error
                else:
                    # [MONITORAMENTO] Registrar erro genérico da IA
                    try:
                        from monitoring.models import AIResponseAlert
                        from monitoring.tasks import dispatch_whatsapp_alert
                        alert_type = 'quota_exceeded' if ('quota' in error_str or '429' in error_str) else 'api_error'
                        alert = AIResponseAlert.objects.create(
                            session=session,
                            user=request.user,
                            alert_type=alert_type,
                            severity='high',
                            provider=ai_provider,
                            error_message=str(primary_error)[:500],
                            ai_response_preview='',
                        )
                        dispatch_whatsapp_alert(ai_alert_id=alert.pk)
                    except Exception as m_err:
                        logger.warning(f"Erro ao registrar alerta de IA: {m_err}")
                    # Não é erro de quota ou não é Gemini, propagar erro
                    raise primary_error
            
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


class ReportAIResponseAPIView(APIView):
    """
    Endpoint para o usuário reportar uma resposta inadequada da IA.

    POST /chatbot/api/report-response/
    Body: {
        "message_id": 123,
        "complaint": "A IA informou dados errados sobre..."
    }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Registra a reclamação e dispara alerta WhatsApp."""
        message_id = request.data.get('message_id')
        complaint_text = request.data.get('complaint', '').strip()

        if not message_id:
            return Response({'error': 'message_id é obrigatório'}, status=status.HTTP_400_BAD_REQUEST)

        if not complaint_text:
            return Response({'error': 'complaint não pode ser vazio'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Buscar a mensagem — deve pertencer ao usuário autenticado
            bot_message = ChatMessage.objects.get(
                pk=message_id,
                role='assistant',
                session__user=request.user,
            )
        except ChatMessage.DoesNotExist:
            return Response({'error': 'Mensagem não encontrada'}, status=status.HTTP_404_NOT_FOUND)

            from monitoring.models import AIResponseAlert
            from monitoring.tasks import dispatch_whatsapp_alert
            from django.conf import settings as django_settings

            ai_provider = getattr(django_settings, 'AI_PROVIDER', 'unknown')

            alert = AIResponseAlert.objects.create(
                session=bot_message.session,
                message=bot_message,
                user=request.user,
                alert_type='user_complaint',
                severity='medium',
                provider=ai_provider,
                user_complaint_text=complaint_text[:1000],
                ai_response_preview=bot_message.content[:500],
            )

            # Marcar feedback na mensagem
            bot_message.user_feedback = 'incorrect'
            bot_message.save(update_fields=['user_feedback'])

            # Disparar alerta WhatsApp assíncrono
            dispatch_whatsapp_alert(ai_alert_id=alert.pk)

            logger.info(f"✅ Reclamação registrada: AIResponseAlert #{alert.pk} | Usuário: {request.user.username}")

            return Response(
                {'message': 'Reclamação registrada com sucesso. Obrigado pelo feedback!'},
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            logger.error(f"Erro ao registrar reclamação: {e}", exc_info=True)
            return Response(
                {'error': 'Erro ao registrar reclamação'},
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


# ====================================================================================
# CHAT DE SUPORTE
# ====================================================================================


class SupportChatView(TemplateView):
    """
    View para a página de chat de suporte.
    Disponível para todos (logados e anônimos).
    Renderiza o template 'chatbot_literario/support_chat.html'.
    """
    template_name = 'chatbot_literario/support_chat.html'


class SupportSendMessageAPIView(APIView):
    """
    API para enviar mensagem ao chat de suporte e receber resposta.
    Suporta usuários autenticados e visitantes anônimos.

    POST /chatbot/api/suporte/send/
    Body: {
        "message": "sua dúvida aqui",
        "session_id": 123  // opcional
    }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """Processa mensagem do usuário e retorna resposta do assistente de suporte."""
        serializer = SendMessageSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'error': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        user_message_text = serializer.validated_data['message']
        session_id = serializer.validated_data.get('session_id')

        # Garantir que a sessão Django existe (necessário para usuários anônimos)
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key

        try:
            # 1. Obter ou criar sessão de suporte
            if session_id:
                # Verificar propriedade da sessão (por usuário ou por session_key)
                if request.user.is_authenticated:
                    qs = ChatSession.objects.filter(
                        id=session_id, user=request.user, chat_type='suporte'
                    )
                else:
                    qs = ChatSession.objects.filter(
                        id=session_id, session_key=session_key, chat_type='suporte'
                    )
                try:
                    session = qs.get()
                except ChatSession.DoesNotExist:
                    return Response(
                        {'error': 'Sessão não encontrada'},
                        status=status.HTTP_404_NOT_FOUND
                    )
            else:
                # Criar nova sessão de suporte
                session = ChatSession.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    session_key=None if request.user.is_authenticated else session_key,
                    chat_type='suporte'
                )

            # 2. Salvar mensagem do usuário
            user_message = ChatMessage.objects.create(
                session=session,
                role='user',
                content=user_message_text
            )

            try:
                from monitoring.detector import SuspiciousActivityDetector
                from monitoring.tasks import dispatch_whatsapp_alert
                detector = SuspiciousActivityDetector()
                ip_address = (
                    request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip()
                    or request.META.get('REMOTE_ADDR')
                )
                suspicious = detector.analyze_message(
                    user_message=user_message,
                    session=session,
                    user=request.user if request.user.is_authenticated else None,
                    ip_address=ip_address,
                )
                if suspicious and suspicious.severity in ('medium', 'high', 'critical'):
                    dispatch_whatsapp_alert(activity_id=suspicious.pk)
            except Exception as monitor_err:
                logger.warning(f"⚠️ Erro no monitoramento de suporte (não crítico): {monitor_err}")

            # 3. Obter histórico da conversa (últimas 10 mensagens)
            previous_messages = list(
                session.messages.exclude(id=user_message.id).order_by('-created_at')[:10]
            )
            previous_messages.reverse()

            # 4. Preparar nome do usuário para personalização
            if request.user.is_authenticated:
                user_name = request.user.first_name or request.user.username
            else:
                user_name = 'Visitante'

            # 5. Montar histórico para a AI
            ai_provider = getattr(settings, 'AI_PROVIDER', 'gemini').lower()
            conversation_history = []
            for msg in previous_messages:
                content = msg.corrected_content if msg.has_correction and msg.corrected_content else msg.content
                if ai_provider == 'groq':
                    conversation_history.append({
                        'role': msg.role if msg.role == 'user' else 'assistant',
                        'content': content
                    })
                else:
                    conversation_history.append({
                        'role': msg.role if msg.role == 'user' else 'model',
                        'parts': [content]
                    })

            # Adicionar contexto de nome apenas na primeira mensagem
            if not conversation_history:
                message_with_context = f"[Usuário: {user_name}] {user_message_text}"
            else:
                message_with_context = user_message_text

            # 6. Obter resposta do assistente de suporte
            from .support_service import get_support_chatbot_service

            start_time = time.time()
            support_service = get_support_chatbot_service()
            bot_response_text = support_service.get_response(
                message=message_with_context,
                conversation_history=conversation_history
            )
            response_time = time.time() - start_time

            # 7. Salvar resposta
            bot_message = ChatMessage.objects.create(
                session=session,
                role='assistant',
                content=bot_response_text,
                response_time=response_time
            )

            # 8. Gerar título da sessão
            if not session.title:
                session.generate_title()

            return Response({
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
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Erro ao processar mensagem de suporte: {e}", exc_info=True)
            return Response(
                {'error': f'Erro ao processar mensagem: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SupportSessionListAPIView(APIView):
    """
    API para listar sessões de suporte do usuário.
    Suporta usuários logados e anônimos.

    GET /chatbot/api/suporte/sessions/
    """
    permission_classes = [AllowAny]

    def get(self, request):
        """Retorna sessões de suporte do usuário ou da sessão anônima."""
        if request.user.is_authenticated:
            sessions = ChatSession.objects.filter(
                user=request.user, chat_type='suporte'
            ).order_by('-updated_at')
        else:
            session_key = request.session.session_key
            if not session_key:
                return Response([], status=status.HTTP_200_OK)
            sessions = ChatSession.objects.filter(
                session_key=session_key, chat_type='suporte'
            ).order_by('-updated_at')

        serializer = ChatSessionListSerializer(sessions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SupportSessionDetailAPIView(APIView):
    """
    API para obter detalhes de uma sessão de suporte específica.

    GET /chatbot/api/suporte/sessions/<id>/
    """
    permission_classes = [AllowAny]

    def get(self, request, session_id):
        """Retorna detalhes de uma sessão de suporte."""
        if request.user.is_authenticated:
            qs = ChatSession.objects.filter(id=session_id, user=request.user, chat_type='suporte')
        else:
            session_key = request.session.session_key
            qs = ChatSession.objects.filter(id=session_id, session_key=session_key, chat_type='suporte')

        try:
            session = qs.get()
            serializer = ChatSessionSerializer(session)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ChatSession.DoesNotExist:
            return Response({'error': 'Sessão não encontrada'}, status=status.HTTP_404_NOT_FOUND)
