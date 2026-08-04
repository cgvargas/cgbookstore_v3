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
        query = self.request.GET.get('q', '').strip()
        if not query:
            return Book.objects.none()

        basic_q = (
            Q(title__icontains=query) |
            Q(subtitle__icontains=query) |
            Q(author__name__icontains=query) |
            Q(category__name__icontains=query) |
            Q(isbn__icontains=query)
        )

        words = [w for w in query.split() if len(w) > 2]
        if len(words) > 1:
            words_q = Q()
            for w in words:
                words_q &= (
                    Q(title__icontains=w) |
                    Q(subtitle__icontains=w) |
                    Q(author__name__icontains=w) |
                    Q(category__name__icontains=w) |
                    Q(isbn__icontains=w)
                )
            filter_q = basic_q | words_q
        else:
            filter_q = basic_q

        return Book.objects.filter(filter_q).distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        return context