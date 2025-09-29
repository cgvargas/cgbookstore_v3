# C:\Users\claud\OneDrive\ProjectsDjango\CGBookStore_v3\core\urls.py

from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('livros/', views.BookListView.as_view(), name='book_list'),
    path('buscar/', views.SearchView.as_view(), name='search'),
    path('sobre/', views.AboutView.as_view(), name='about'),
    path('contato/', views.ContactView.as_view(), name='contact'),
    path('biblioteca/', views.LibraryView.as_view(), name='library'),
]