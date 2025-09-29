# C:\Users\claud\OneDrive\ProjectsDjango\CGBookStore_v3\core\views\book_views.py

from django.views.generic import ListView
from core.models import Book


class BookListView(ListView):
    """
    View para listar todos os livros no catálogo.
    Utiliza paginação para melhor performance.
    """
    model = Book
    template_name = 'core/book_list.html'
    context_object_name = 'books'
    paginate_by = 12