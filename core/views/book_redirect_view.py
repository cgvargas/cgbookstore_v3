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
        """Redireciona para a URL correta do livro."""
        book = get_object_or_404(Book, id=book_id)
        return redirect(book.get_absolute_url(), permanent=True)
