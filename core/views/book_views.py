# C:\ProjectDjango\cgbookstore_v3\core\views\book_views.py

from django.views.generic import ListView
from django.db.models import Q
from core.models import Book, Category


class BookListView(ListView):
    """
    View para listar todos os livros no catálogo com filtros avançados.

    Suporta:
    - Filtro por categoria (múltiplas seleções)
    - Filtro por faixa de preço (min/max)
    - Busca por título e autor
    - Ordenação (recentes, antigos, preço, título, avaliação)
    - Paginação (12 livros por página)
    """
    model = Book
    template_name = 'core/book_list.html'
    context_object_name = 'books'
    paginate_by = 12

    def get_queryset(self):
        """
        Retorna queryset filtrado e ordenado conforme parâmetros GET.
        """
        queryset = Book.objects.select_related('author', 'category').all()

        # ========== FILTRO: BUSCA POR TÍTULO/AUTOR ==========
        search_query = self.request.GET.get('q', '').strip()
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(author__name__icontains=search_query)
            )

        # ========== FILTRO: CATEGORIAS (múltiplas) ==========
        categories = self.request.GET.getlist('category')
        if categories:
            queryset = queryset.filter(category__slug__in=categories)

        # ========== FILTRO: FAIXA DE PREÇO ==========
        price_min = self.request.GET.get('price_min', '').strip()
        price_max = self.request.GET.get('price_max', '').strip()

        if price_min:
            try:
                queryset = queryset.filter(price__gte=float(price_min))
            except ValueError:
                pass  # Ignora valores inválidos

        if price_max:
            try:
                queryset = queryset.filter(price__lte=float(price_max))
            except ValueError:
                pass  # Ignora valores inválidos

        # ========== ORDENAÇÃO ==========
        sort_by = self.request.GET.get('sort_by', '-created_at')

        # Mapeamento de opções de ordenação
        sort_options = {
            'newest': '-created_at',  # Mais recentes
            'oldest': 'created_at',  # Mais antigos
            'price_asc': 'price',  # Menor preço
            'price_desc': '-price',  # Maior preço
            'title_asc': 'title',  # A-Z
            'title_desc': '-title',  # Z-A
            'rating': '-average_rating',  # Melhor avaliação
        }

        # Aplica ordenação (padrão: mais recentes)
        queryset = queryset.order_by(sort_options.get(sort_by, '-created_at'))

        return queryset

    def get_context_data(self, **kwargs):
        """
        Adiciona dados extras ao contexto do template.
        """
        context = super().get_context_data(**kwargs)

        # Lista de todas as categorias para o formulário de filtros
        context['all_categories'] = Category.objects.all().order_by('name')

        # Parâmetros atuais (para manter estado do formulário)
        context['current_search'] = self.request.GET.get('q', '')
        context['current_categories'] = self.request.GET.getlist('category')
        context['current_price_min'] = self.request.GET.get('price_min', '')
        context['current_price_max'] = self.request.GET.get('price_max', '')
        context['current_sort'] = self.request.GET.get('sort_by', 'newest')

        # Total de resultados (para exibir contador)
        context['total_results'] = self.get_queryset().count()

        # Verifica se há filtros ativos
        context['has_filters'] = any([
            context['current_search'],
            context['current_categories'],
            context['current_price_min'],
            context['current_price_max'],
            context['current_sort'] != 'newest'
        ])

        return context