from django.urls import path
from core.views import (
    HomeView,
    BookListView,
    BookDetailView,
    SearchView,
    AboutView,
    ContactView,
    LibraryView
)

app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('livros/', BookListView.as_view(), name='book_list'),
    path('livros/<slug:slug>/', BookDetailView.as_view(), name='book_detail'),
    path('buscar/', SearchView.as_view(), name='search'),
    path('sobre/', AboutView.as_view(), name='about'),
    path('contato/', ContactView.as_view(), name='contact'),
    path('biblioteca/', LibraryView.as_view(), name='library'),
]