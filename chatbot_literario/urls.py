"""
URLs para o Chatbot Literário.
Inclui rotas para interface web e API REST.
"""
from django.urls import path
from . import views

app_name = 'chatbot_literario'

urlpatterns = [
    # ==================== INTERFACE WEB ====================
    # URL da página do chatbot -> http://localhost:8000/chatbot/
    path('', views.ChatbotView.as_view(), name='chat'),

    # ==================== API REST ====================
    # Enviar mensagem ao chatbot
    path('api/send/', views.SendMessageAPIView.as_view(), name='api_send_message'),

    # Listar todas as sessões do usuário
    path('api/sessions/', views.ChatSessionListAPIView.as_view(), name='api_session_list'),

    # Criar nova sessão
    path('api/sessions/new/', views.NewSessionAPIView.as_view(), name='api_new_session'),

    # Detalhes de uma sessão específica
    path('api/sessions/<int:session_id>/', views.ChatSessionDetailAPIView.as_view(), name='api_session_detail'),

    # Encerrar/limpar sessão
    path('api/sessions/<int:session_id>/clear/', views.ClearSessionAPIView.as_view(), name='api_clear_session'),

    # Contexto de conversa do usuário
    path('api/context/', views.ConversationContextAPIView.as_view(), name='api_conversation_context'),
]