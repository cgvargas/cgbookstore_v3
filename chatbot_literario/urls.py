from django.urls import path
from . import views

app_name = 'chatbot_literario' # O namespace pode ser diferente, mas 'chatbot' é usado no base.html

urlpatterns = [
    # URL da página do chatbot -> http://localhost:8000/chatbot/
    path('', views.ChatbotView.as_view(), name='chat'),
]