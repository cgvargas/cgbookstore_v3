"""
View de Redirecionamento para URLs Antigas de Livros.
Redireciona /book/<id>/ para /livros/<slug>/
"""
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from core.models import Book


class BookRedirectView(View):
    """
    Redireciona URLs antigas com ID para URLs novas com slug.

    URL antiga: /book/83/
    URL nova: /livros/slug-do-livro/

    Útil para manter compatibilidade com notificações antigas
    e links externos.
    """

    def get(self, request, book_id):
        """Redireciona para a URL correta do livro ou renderiza diretamente se o slug for numérico."""
        # 1. Tentar buscar por ID primeiro
        book_by_id = Book.objects.filter(id=book_id).first()
        if book_by_id:
            # Se o slug for um número correspondente ao ID, mostramos diretamente
            # para evitar loops de redirecionamento infinitos.
            if book_by_id.slug and book_by_id.slug.isdigit() and int(book_by_id.slug) == book_by_id.id:
                from core.views.book_detail_view import BookDetailView
                return BookDetailView.as_view()(request, slug=book_by_id.slug)
            
            return redirect(book_by_id.get_absolute_url(), permanent=True)

        # 2. Se não existir o ID, verificar se existe algum livro cujo SLUG seja exatamente o número 'book_id'
        # (caso de livros cujo título/slug é um número, como "1984")
        book_by_slug = Book.objects.filter(slug=str(book_id)).first()
        if book_by_slug:
            # Despachamos diretamente para a BookDetailView sem redirecionar, evitando loop infinito
            from core.views.book_detail_view import BookDetailView
            return BookDetailView.as_view()(request, slug=book_by_slug.slug)

        # 3. Fallback: levanta 404 padrão
        from django.http import Http404
        raise Http404("Nenhum livro encontrado com o ID ou slug fornecido.")

