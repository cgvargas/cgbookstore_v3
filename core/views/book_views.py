# C:\ProjectDjango\cgbookstore_v3\core\views\book_views.py

from django.views.generic import ListView
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from core.models import Book, Category, Section, SectionItem


class BookListView(ListView):
    """
    View para listar todos os livros no catálogo com filtros avançados.

    Suporta:
    - Filtro por prateleira/seção (shelf) — livros alocados em seções da home
    - Filtro por categoria (múltiplas seleções)
    - Filtro por autor (slug)
    - Filtro por faixa de preço (min/max)
    - Busca por título e autor
    - Ordenação (recentes, antigos, preço, título, avaliação, mais vendidos)
    - Paginação (12 livros por página)
    """
    model = Book
    template_name = 'core/book_list.html'
    context_object_name = 'books'
    paginate_by = 12

    # Mapeamento de nomes de prateleiras para facilitar busca
    SHELF_ALIASES = {
        'lancamentos': ['lançamentos', 'lancamentos', 'lançamento', 'lancamento', 'novidades', 'new releases'],
        'mais-vendidos': ['mais vendidos', 'mais-vendidos', 'bestsellers', 'best sellers', 'populares'],
        'destaques': ['destaques', 'destaque', 'featured', 'em destaque'],
        'pre-venda': ['pré-venda', 'pre-venda', 'pré venda', 'pre venda'],
    }

    def _get_shelf_book_ids(self, shelf_slug):
        """
        Retorna IDs de livros que pertencem a uma determinada prateleira/seção.
        Busca por slug exato ou por aliases conhecidos.
        """
        # Obter ContentType de Book
        book_ct = ContentType.objects.get_for_model(Book)

        # Tentar buscar seção por ID primeiro
        section = None
        if shelf_slug.isdigit():
            section = Section.objects.filter(id=int(shelf_slug), active=True).first()

        # Se não encontrou por ID, buscar por título (aliases)
        if not section:
            # Verificar aliases conhecidos
            search_terms = [shelf_slug]
            for alias_key, alias_list in self.SHELF_ALIASES.items():
                if shelf_slug.lower() in [alias_key] + alias_list:
                    search_terms = alias_list + [alias_key]
                    break

            # Buscar seção cujo título contenha algum dos termos
            for term in search_terms:
                section = Section.objects.filter(
                    active=True,
                    title__icontains=term
                ).first()
                if section:
                    break

        if not section:
            return None, None

        # Buscar IDs dos livros nessa seção
        book_ids = list(SectionItem.objects.filter(
            section=section,
            content_type=book_ct,
            active=True
        ).values_list('object_id', flat=True))

        return book_ids, section

    def get_queryset(self):
        """
        Retorna queryset filtrado e ordenado conforme parâmetros GET.
        """
        queryset = Book.objects.select_related('author', 'category').all()

        # ========== FILTRO: PRATELEIRA/SEÇÃO (shelf) ==========
        shelf = self.request.GET.get('shelf', '').strip()
        if shelf:
            book_ids, section = self._get_shelf_book_ids(shelf)
            if book_ids is not None:
                queryset = queryset.filter(id__in=book_ids)
                # Guardar seção para uso no contexto
                self._current_section = section
            else:
                # Prateleira não encontrada, retornar vazio
                queryset = queryset.none()

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

        # ========== FILTRO: AUTOR (por slug) ==========
        author_slug = self.request.GET.get('author', '').strip()
        if author_slug:
            queryset = queryset.filter(author__slug=author_slug)

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
            'popular': '-average_rating',  # Populares / Mais vendidos (por rating)
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
        context['current_shelf'] = self.request.GET.get('shelf', '')
        context['current_author'] = self.request.GET.get('author', '')

        # Nome da prateleira ativa (para exibir no cabeçalho)
        shelf_section = getattr(self, '_current_section', None)
        if shelf_section:
            context['shelf_title'] = shelf_section.title
            context['shelf_section'] = shelf_section
        elif context['current_shelf']:
            # Mapear slugs para nomes legíveis
            shelf_names = {
                'lancamentos': 'Lançamentos',
                'mais-vendidos': 'Mais Vendidos',
                'destaques': 'Destaques',
                'pre-venda': 'Pré-Venda',
            }
            context['shelf_title'] = shelf_names.get(
                context['current_shelf'],
                context['current_shelf'].replace('-', ' ').title()
            )

        # Nome do autor filtrado (para exibir no cabeçalho)
        if context['current_author']:
            from core.models import Author
            author = Author.objects.filter(slug=context['current_author']).first()
            if author:
                context['author_name'] = author.name

        # Listar prateleiras disponíveis para filtro rápido
        context['available_shelves'] = Section.objects.filter(
            active=True,
            content_type='books'
        ).exclude(title='').values_list('id', 'title').order_by('order')

        # Total de resultados (para exibir contador)
        context['total_results'] = self.get_queryset().count()

        # Verifica se há filtros ativos
        context['has_filters'] = any([
            context['current_search'],
            context['current_categories'],
            context['current_price_min'],
            context['current_price_max'],
            context['current_sort'] != 'newest',
            context['current_shelf'],
            context['current_author'],
        ])

        return context