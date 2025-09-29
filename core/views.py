# C:\Users\claud\OneDrive\ProjectsDjango\CGBookStore_v3\core\views.py

from django.shortcuts import render
from django.views.generic import TemplateView, ListView
from .models import Book, Category, Author
from django.db.models import Q

class HomeView(TemplateView):
    """
    View para a página inicial.
    Renderiza o template 'core/home.html'.
    """
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['latest_books'] = Book.objects.order_by('-publication_date')[:6]
        context['featured_categories'] = Category.objects.filter(featured=True)[:4]
        return context

class BookListView(ListView):
    """
    View para listar todos os livros no catálogo.
    Utiliza o model 'Book' e renderiza 'core/book_list.html'.
    """
    model = Book
    template_name = 'core/book_list.html'
    context_object_name = 'books'
    paginate_by = 12 # Adiciona paginação para melhor performance

class SearchView(ListView):
    """
    View para a busca de livros.
    Filtra os livros com base no parâmetro 'q' da URL.
    """
    model = Book
    template_name = 'core/search_results.html'
    context_object_name = 'books'

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            # Busca por título, nome do autor ou nome da categoria
            return Book.objects.filter(
                Q(title__icontains=query) |
                Q(author__name__icontains=query) |
                Q(category__name__icontains=query)
            ).distinct()
        return Book.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Retorna o termo de busca para o template
        context['search_query'] = self.request.GET.get('q', '')
        return context

class ChatbotView(TemplateView):
    """
    View para a interface do chatbot.
    Renderiza o template 'chatbot_literario/chat.html'.
    """
    template_name = 'chatbot_literario/chat.html'
