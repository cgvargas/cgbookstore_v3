from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('chatbot/', include('chatbot_literario.urls', namespace='chatbot')),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('debates/', include('debates.urls')),
    path('recommendations/', include('recommendations.urls', namespace='recommendations')),
    path('', include('core.urls', namespace='core')),
]

# Servir arquivos de media em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)