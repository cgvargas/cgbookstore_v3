"""
View para a Biblioteca pessoal do usuário.
Integrada com os models de BookShelf, ReadingProgress, etc.
"""

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, F
from accounts.models import BookShelf, ReadingProgress, BookReview


class LibraryView(LoginRequiredMixin, TemplateView):
    """
    View para a Biblioteca pessoal do usuário.
    Exibe prateleiras, progresso de leitura e estatísticas.
    """
    template_name = 'core/library.html'
    login_url = '/contas/login/'
    redirect_field_name = 'next'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Perfil do usuário
        profile = getattr(user, 'profile', None)
        context['profile'] = profile

        # Tema visual selecionado pelo usuário
        context['selected_theme'] = profile.theme_preference if profile else 'fantasy'

        # Contadores de prateleiras
        context['favorites_count'] = BookShelf.objects.filter(
            user=user, shelf_type='favorites'
        ).count()

        context['to_read_count'] = BookShelf.objects.filter(
            user=user, shelf_type='to_read'
        ).count()

        context['reading_count'] = BookShelf.objects.filter(
            user=user, shelf_type='reading'
        ).count()

        context['read_count'] = BookShelf.objects.filter(
            user=user, shelf_type='read'
        ).count()

        # Prateleiras com livros (limitar a 50 por prateleira)
        context['favorites'] = BookShelf.objects.filter(
            user=user, shelf_type='favorites'
        ).select_related('book', 'book__author', 'book__category')[:50]

        context['to_read'] = BookShelf.objects.filter(
            user=user, shelf_type='to_read'
        ).select_related('book', 'book__author', 'book__category')[:50]

        context['reading'] = BookShelf.objects.filter(
            user=user, shelf_type='reading'
        ).select_related('book', 'book__author', 'book__category')[:50]

        context['read'] = BookShelf.objects.filter(
            user=user, shelf_type='read'
        ).select_related('book', 'book__author', 'book__category')[:50]

        # ========== PRATELEIRAS PERSONALIZADAS (ATUALIZADO) ==========
        custom_shelves_list = []
        custom_shelf_names = []  # <-- Crie esta lista vazia

        if profile:
            shelf_names = profile.get_custom_shelves()
            custom_shelf_names = shelf_names  # <-- Preencha a lista

            for shelf_name in shelf_names:
                # Buscar livros da prateleira (pode estar vazio)
                books = BookShelf.objects.filter(
                    user=user,
                    shelf_type='custom',
                    custom_shelf_name=shelf_name
                ).select_related('book', 'book__author', 'book__category')[:50]

                custom_shelves_list.append({
                    'name': shelf_name,
                    'count': books.count(),
                    'books': books
                })

        context['custom_shelves'] = custom_shelves_list
        # NOVO: Adicione a lista de nomes ao contexto para o modal
        context['custom_shelves_for_modal'] = custom_shelf_names

        # Progressos de leitura ativos (incompletos)
        context['reading_progress'] = ReadingProgress.objects.filter(
            user=user
        ).filter(
            current_page__lt=F('total_pages')
        ).select_related('book', 'book__author').order_by('-last_updated')[:5]

        # Estatísticas de gamificação
        if profile:
            context['total_points'] = profile.total_xp
            context['user_level'] = profile.level
            context['level_name'] = profile.level_name
            context['books_read_this_year'] = profile.books_read_this_year()
            context['reading_goal'] = profile.reading_goal_year
            context['goal_percentage'] = profile.goal_percentage()

            # Novos campos de gamificação
            context['streak_days'] = profile.streak_days
            context['total_badges'] = len(profile.badges) if profile.badges else 0
            context['is_premium'] = profile.is_premium
        else:
            context['total_points'] = 0
            context['user_level'] = 1
            context['level_name'] = 'Leitor Iniciante'
            context['books_read_this_year'] = 0
            context['reading_goal'] = 12
            context['goal_percentage'] = 0
            context['streak_days'] = 0
            context['total_badges'] = 0
            context['is_premium'] = False

        # Avaliações recentes
        context['recent_reviews'] = BookReview.objects.filter(
            user=user
        ).select_related('book').order_by('-created_at')[:5]

        return context