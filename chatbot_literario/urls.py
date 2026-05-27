"""
URLs para o Chatbot Literário e Chat de Suporte.
Inclui rotas para interface web e API REST.
"""
from django.urls import path
from . import views

app_name = 'chatbot_literario'

urlpatterns = [
    # ==================== CHATBOT LITERÁRIO (Dbit) ====================
    # URL da página do chatbot -> http://localhost:8000/chatbot/
    path('', views.ChatbotView.as_view(), name='chat'),

    # ==================== API REST - CHATBOT LITERÁRIO ====================
    # Enviar mensagem ao chatbot literário
    path('api/send/', views.SendMessageAPIView.as_view(), name='api_send_message'),

    # Listar todas as sessões literárias do usuário
    path('api/sessions/', views.ChatSessionListAPIView.as_view(), name='api_session_list'),

    # Criar nova sessão literária
    path('api/sessions/new/', views.NewSessionAPIView.as_view(), name='api_new_session'),

    # Detalhes de uma sessão literária específica
    path('api/sessions/<int:session_id>/', views.ChatSessionDetailAPIView.as_view(), name='api_session_detail'),

    # Encerrar/limpar sessão literária
    path('api/sessions/<int:session_id>/clear/', views.ClearSessionAPIView.as_view(), name='api_clear_session'),

    # Contexto de conversa do usuário
    path('api/context/', views.ConversationContextAPIView.as_view(), name='api_conversation_context'),

    # ==================== CHAT DE SUPORTE ====================
    # Página do chat de suporte (disponível para todos — logados e anônimos)
    path('suporte/', views.SupportChatView.as_view(), name='support_chat'),

    # Enviar mensagem ao chat de suporte
    path('api/suporte/send/', views.SupportSendMessageAPIView.as_view(), name='api_support_send'),

    # Listar sessões de suporte do usuário/anônimo
    path('api/suporte/sessions/', views.SupportSessionListAPIView.as_view(), name='api_support_sessions'),

    # Detalhes de uma sessão de suporte específica
    path('api/suporte/sessions/<int:session_id>/', views.SupportSessionDetailAPIView.as_view(), name='api_support_session_detail'),
]