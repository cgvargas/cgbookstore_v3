"""
URLs para o app New Authors
"""
from django.urls import path
from . import views

app_name = 'new_authors'

urlpatterns = [
    # Páginas públicas
    path('', views.books_list, name='books_list'),
    path('livro/<slug:slug>/', views.book_detail, name='book_detail'),
    path('livro/<slug:book_slug>/capitulo/<int:chapter_number>/', views.chapter_read, name='chapter_read'),
    path('autor/<str:username>/', views.author_profile, name='author_profile'),

    # Busca e filtros
    path('buscar/', views.search_books, name='search_books'),
    path('em-alta/', views.trending_books, name='trending_books'),

    # Área do autor
    path('tornar-se-autor/', views.become_author, name='become_author'),
    path('dashboard/', views.author_dashboard, name='author_dashboard'),

    # Interações
    path('api/seguir/<int:book_id>/', views.follow_book, name='follow_book'),
    path('api/avaliar/<int:book_id>/', views.submit_review, name='submit_review'),
    path('api/review/<int:review_id>/util/', views.mark_review_helpful, name='mark_review_helpful'),

    # Editoras
    path('editora/dashboard/', views.publisher_dashboard, name='publisher_dashboard'),
    path('api/interesse/<int:book_id>/', views.express_interest, name='express_interest'),
]
