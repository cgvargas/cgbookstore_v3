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
    path('termos-autor/', views.author_terms, name='author_terms'),
    path('dashboard/', views.author_dashboard, name='author_dashboard'),

    # Gerenciamento de livros (autor)
    path('livro/novo/', views.manage_book, name='create_book'),
    path('livro/<int:book_id>/editar/', views.manage_book, name='manage_book'),
    path('livro/<int:book_id>/deletar/', views.delete_book, name='delete_book'),

    # Gerenciamento de capítulos (autor)
    path('livro/<int:book_id>/capitulos/', views.manage_chapters, name='manage_chapters'),
    path('livro/<int:book_id>/capitulo/novo/', views.edit_chapter, name='edit_chapter'),
    path('livro/<int:book_id>/capitulo/<int:chapter_id>/editar/', views.edit_chapter, name='edit_chapter'),
    path('api/capitulo/<int:chapter_id>/deletar/', views.delete_chapter, name='delete_chapter'),

    # Interações
    path('api/seguir/<int:book_id>/', views.follow_book, name='follow_book'),
    path('api/curtir/<int:book_id>/', views.like_book, name='like_book'),
    path('api/avaliar/<int:book_id>/', views.submit_review, name='submit_review'),
    path('api/review/<int:review_id>/util/', views.mark_review_helpful, name='mark_review_helpful'),

    # Editoras
    path('editora/cadastro/', views.become_publisher, name='become_publisher'),
    path('editora/aguardando/', views.publisher_pending, name='publisher_pending'),
    path('editora/dashboard/', views.publisher_dashboard, name='publisher_dashboard'),
    path('editora/livro/<int:book_id>/', views.publisher_book_detail, name='publisher_book_detail'),
    path('api/interesse/<int:book_id>/', views.express_interest, name='express_interest'),
]
