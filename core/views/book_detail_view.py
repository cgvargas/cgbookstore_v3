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
        book = self.get_object()

        # Livros relacionados da mesma categoria (lógica existente mantida)
        context['related_books'] = Book.objects.filter(
            category=book.category
        ).exclude(id=book.id)[:4]

        # Inicializa o contexto para evitar erros no template
        context['user_is_reading'] = False
        context['reading_progress'] = None
        context['custom_shelves'] = []

        if self.request.user.is_authenticated:
            # Buscar prateleiras personalizadas (lógica existente mantida)
            profile = self.request.user.profile
            context['custom_shelves'] = profile.get_custom_shelves()

            # --- INÍCIO DA MODIFICAÇÃO ---
            # Importa os modelos necessários
            from accounts.models import ReadingProgress, BookShelf

            # Verifica de forma explícita se o livro está na prateleira "Lendo"
            is_reading = BookShelf.objects.filter(
                user=self.request.user,
                book=book,
                shelf_type='reading'
            ).exists()
            context['user_is_reading'] = is_reading

            # Se estiver lendo, busca e adiciona o objeto de progresso
            if is_reading:
                progress = ReadingProgress.objects.filter(
                    user=self.request.user,
                    book=book,
                ).first()  # Simplificado para pegar o progresso existente
                context['reading_progress'] = progress
            # --- FIM DA MODIFICAÇÃO ---

        return context
