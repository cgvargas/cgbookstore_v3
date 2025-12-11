from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # Ferramentas administrativas (sem necessidade de Shell)
    path('admin-tools/', include('core.urls_admin_tools', namespace='admin_tools')),

    # Django-allauth URLs (ANTES de accounts/)
    path('accounts/', include('allauth.urls')),

    # Nossas URLs customizadas (profile, etc.)
    path('profile/', include('accounts.urls', namespace='accounts')),

    path('chatbot/', include('chatbot_literario.urls', namespace='chatbot')),
    path('debates/', include('debates.urls')),
    path('recommendations/', include('recommendations.urls', namespace='recommendations')),
    path('finance/', include('finance.urls', namespace='finance')),
    path('novos-autores/', include('new_authors.urls', namespace='new_authors')),
    path('noticias/', include('news.urls', namespace='news')),
    path('ckeditor5/', include('django_ckeditor_5.urls')),
    path('', include('core.urls', namespace='core')),
]

# Servir arquivos de media em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)