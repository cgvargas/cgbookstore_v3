from django.urls import path
from . import views

app_name = 'chatbot_literario'  # Namespace para URLs

urlpatterns = [
    # Página principal do chatbot
    path('', views.ChatbotView.as_view(), name='chat'),

    # Página de diagnóstico
    path('diagnostic/', views.DiagnosticView.as_view(), name='diagnostic'),

    # API Endpoints
    path('api/send/', views.send_message, name='send_message'),
    path('api/history/', views.get_history, name='get_history'),
    path('api/clear/', views.clear_history, name='clear_history'),
    path('api/check/', views.check_service, name='check_service'),
]
