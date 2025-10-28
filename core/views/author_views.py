from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.db.models import Count, Avg
from core.models import Author


class AuthorListView(ListView):
    """Lista todos os autores"""
    model = Author
    template_name = 'core/author_list.html'
    context_object_name = 'authors'
    paginate_by = 24  # 24 autores por página (grid 4x6)

    def get_queryset(self):
        """Retorna autores ordenados por nome, com contagem de livros"""
        queryset = Author.objects.annotate(
            books_count=Count('books')
        ).order_by('name')

        # Busca por nome
        search = self.request.GET.get('q')
        if search:
            queryset = queryset.filter(name__icontains=search)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        return context


class AuthorDetailView(DetailView):
    """Detalhes de um autor específico"""
    model = Author
    template_name = 'core/author_detail.html'
    context_object_name = 'author'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Buscar livros do autor ordenados por título com contagem de avaliações
        # Nota: average_rating já é um campo do modelo Book
        books = self.object.books.annotate(
            reviews_count=Count('user_reviews')
        ).order_by('title')

        context['books'] = books
        context['books_count'] = books.count()

        return context
