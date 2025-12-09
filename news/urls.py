from django.urls import path
from . import views

app_name = 'news'

urlpatterns = [
    # Página principal do jornal
    path('', views.news_home, name='home'),

    # Artigos
    path('artigo/<slug:slug>/', views.article_detail, name='article_detail'),

    # Filtros por categoria
    path('categoria/<slug:slug>/', views.category_articles, name='category_articles'),

    # Filtros por tag
    path('tag/<slug:slug>/', views.tag_articles, name='tag_articles'),

    # Filtros por tipo de conteúdo
    path('tipo/<str:content_type>/', views.content_type_articles, name='content_type_articles'),

    # Busca
    path('busca/', views.search_articles, name='search'),

    # Quizzes
    path('quiz/<slug:slug>/', views.quiz_detail, name='quiz_detail'),
    path('quiz/<slug:slug>/enviar/', views.submit_quiz, name='submit_quiz'),

    # Newsletter
    path('newsletter/inscrever/', views.subscribe_newsletter, name='subscribe_newsletter'),
]
