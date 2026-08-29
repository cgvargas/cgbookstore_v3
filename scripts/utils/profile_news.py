import os
import django
import time
from django.test import RequestFactory
from django.urls import reverse

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cgbookstore.settings")
django.setup()

from news.views import news_home

def profile_news():
    print("Iniciando profile da view news_home...")
    factory = RequestFactory()
    request = factory.get('/noticias/')
    
    # Mocking user context for the request
    from django.contrib.auth.models import AnonymousUser
    request.user = AnonymousUser()
    request.session = {}
    
    start = time.time()
    response = news_home(request)
    
    # Force render to evaluate all lazy querysets
    if hasattr(response, 'render'):
        response.render()
        
    end = time.time()
    print(f"Tempo total: {end - start:.4f} segundos")
    print(f"Status: {response.status_code}")
    print(f"Tamanho gerado: {len(response.content)} bytes")

if __name__ == '__main__':
    profile_news()
