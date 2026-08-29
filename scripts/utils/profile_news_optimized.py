import os
import django
import time
from django.test import RequestFactory
from django.urls import reverse

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cgbookstore.settings")
django.setup()

from news.models import Article, Category, Newsletter

def news_home_optimized(request):
    breaking_news = Article.objects.defer('content').filter(
        is_published=True,
        is_breaking=True
    ).order_by('-published_at').first()

    featured_main = Article.objects.defer('content').filter(
        is_published=True,
        is_featured=True,
        priority=5
    ).order_by('-published_at').first()

    featured_secondary = Article.objects.defer('content').filter(
        is_published=True,
        is_featured=True,
        priority__in=[3, 4]
    ).order_by('-published_at')[:3]

    sidebar_highlights = Article.objects.defer('content').filter(
        is_published=True,
        is_featured=True
    ).order_by('-priority', '-published_at')[:8]

    latest_news = Article.objects.defer('content').filter(
        is_published=True,
        content_type='news'
    ).order_by('-published_at')[:6]

    interviews = Article.objects.defer('content').filter(
        is_published=True,
        content_type='interview'
    ).order_by('-published_at')[:3]

    events = Article.objects.defer('content').filter(
        is_published=True,
        content_type='event',
        event_date__isnull=False
    ).order_by('event_date')[:4]

    guides = Article.objects.defer('content').filter(
        is_published=True,
        content_type__in=['guide', 'article']
    ).order_by('-published_at')[:4]

    tip_of_week = Article.objects.defer('content').filter(
        is_published=True,
        content_type='tip'
    ).order_by('-published_at').first()

    categories = Category.objects.filter(is_active=True).order_by('order', 'name')
    
    # Just to simulate the evaluation
    for q in [featured_secondary, sidebar_highlights, latest_news, interviews, events, guides, categories]:
        list(q)
        
    return True

def profile_news():
    print("Iniciando profile da view OTIMIZADA...")
    factory = RequestFactory()
    request = factory.get('/noticias/')
    
    from django.contrib.auth.models import AnonymousUser
    request.user = AnonymousUser()
    request.session = {}
    
    start = time.time()
    news_home_optimized(request)
        
    end = time.time()
    print(f"Tempo total OTIMIZADA: {end - start:.4f} segundos")

if __name__ == '__main__':
    profile_news()
