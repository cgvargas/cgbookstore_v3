from django.urls import path
from . import views

app_name = 'debates'

urlpatterns = [
    # Lista e detalhes
    path('', views.debates_list, name='list'),
    path('topico/<slug:slug>/', views.topic_detail, name='topic_detail'),

    # Criar
    path('criar/<int:book_id>/', views.create_topic, name='create_topic'),

    # Posts
    path('post/criar/<slug:topic_slug>/', views.create_post, name='create_post'),
    path('post/votar/<int:post_id>/', views.vote_post, name='vote_post'),
    path('post/deletar/<int:post_id>/', views.delete_post, name='delete_post'),
    path('post/editar/<int:post_id>/', views.edit_post, name='edit_post'),
]