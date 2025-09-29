# C:\Users\claud\OneDrive\ProjectsDjango\CGBookStore_v3\core\views\home_view.py

from django.views.generic import TemplateView
from core.models import Book, Category


class HomeView(TemplateView):
    """
    View para a página inicial.
    Exibe os últimos lançamentos e categorias em destaque.
    """
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['latest_books'] = Book.objects.order_by('-publication_date')[:6]
        context['featured_categories'] = Category.objects.filter(featured=True)[:4]
        return context