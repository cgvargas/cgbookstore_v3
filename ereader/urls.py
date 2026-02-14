from django.urls import path
from . import views
from . import views_export

app_name = 'ereader'

urlpatterns = [
    # Biblioteca
    path('', views.library_view, name='library'),
    path('search/', views.search_books_view, name='search'),
    path('my-library/', views.my_library_view, name='my_library'),
    
    # Leitor
    path('read/<int:book_id>/', views.reader_view, name='read'),
    path('book/<int:book_id>/', views.book_detail_view, name='book_detail'),
    
    # Gerenciamento
    path('book/<int:book_id>/add-to-library/', views.add_to_library, name='add_to_library'),
    path('book/<int:book_id>/remove-from-library/', views.remove_from_library, name='remove_from_library'),
    path('book/<int:book_id>/epub/', views.epub_proxy, name='epub_proxy'),
    
    # Exportação de anotações
    path('export/<int:book_id>/txt/', views_export.export_annotations_txt, name='export_txt'),
    path('export/<int:book_id>/html/', views_export.export_annotations_html, name='export_html'),
    path('export/all/', views_export.export_all_annotations, name='export_all'),
]

