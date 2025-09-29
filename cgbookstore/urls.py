from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('chatbot/', include('chatbot_literario.urls', namespace='chatbot')),

    # Adicione a linha abaixo para as URLs de contas
    path('contas/', include('accounts.urls', namespace='accounts')),

    path('', include('core.urls', namespace='core')),
]