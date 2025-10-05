"""
View de Detalhes do Livro.
Exibe informações completas de um livro específico.
"""

from django.views.generic import DetailView
from core.models import Book
from accounts.models import BookShelf


class BookDetailView(DetailView):
    """
    View para exibir detalhes completos de um livro.

    Acessível via slug em: /livros/<slug>/
    Suporta dados locais e integrados do Google Books API.
    """
    model = Book
    template_name = 'core/book_detail.html'
    context_object_name = 'book'

    def get_context_data(self, **kwargs):
        """Adiciona contexto extra para o template."""
        context = super().get_context_data(**kwargs)

        # Livros relacionados da mesma categoria
        book = self.get_object()
        context['related_books'] = Book.objects.filter(
            category=book.category
        ).exclude(
            id=book.id
        )[:4]

        # Adicionar prateleiras personalizadas se usuário autenticado
        if self.request.user.is_authenticated:
            # Buscar prateleiras personalizadas do usuário
            custom_shelves = BookShelf.objects.filter(
                user=self.request.user,
                shelf_type='custom'
            ).values_list('custom_shelf_name', flat=True).distinct().order_by('custom_shelf_name')

            context['custom_shelves'] = list(custom_shelves)

        return context