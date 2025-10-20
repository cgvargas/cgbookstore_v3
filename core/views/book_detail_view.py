"""
View de Detalhes do Livro.
Exibe informações completas de um livro específico.
"""
from django.views.generic import DetailView
from core.models import Book


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
            # Buscar prateleiras do profile (inclui vazias)
            profile = self.request.user.profile
            context['custom_shelves'] = profile.get_custom_shelves()

            # ⚡ NOVO: Adicionar progresso de leitura se estiver lendo este livro
            from accounts.models import ReadingProgress, BookShelf

            # Verificar se livro está na prateleira "Lendo"
            is_reading = BookShelf.objects.filter(
                user=self.request.user,
                book=book,
                shelf_type='reading'
            ).exists()

            # Se está lendo, buscar o progresso
            if is_reading:
                reading_progress = ReadingProgress.objects.filter(
                    user=self.request.user,
                    book=book,
                    is_abandoned=False,
                    finished_at__isnull=True
                ).select_related('book').first()

                context['reading_progress'] = reading_progress

        return context
