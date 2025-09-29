# C:\Users\claud\OneDrive\ProjectsDjango\CGBookStore_v3\core\views\search_view.py

from django.views.generic import ListView
from django.db.models import Q
from core.models import Book


class SearchView(ListView):
    """
    View para a busca de livros.
    Filtra livros por título, autor ou categoria baseado no parâmetro 'q'.
    """
    model = Book
    template_name = 'core/search_results.html'
    context_object_name = 'books'

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return Book.objects.filter(
                Q(title__icontains=query) |
                Q(author__name__icontains=query) |
                Q(category__name__icontains=query)
            ).distinct()
        return Book.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        return context