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
        if hasattr(user, 'profile'):
            context['user_profile'] = user.profile
        else:
            context['user_profile'] = None

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

        # Prateleiras personalizadas com contagem e livros
        custom_shelves_list = []

        custom_shelves_data = BookShelf.objects.filter(
            user=user, shelf_type='custom'
        ).values('custom_shelf_name').annotate(
            count=Count('id')
        ).order_by('custom_shelf_name')

        for shelf in custom_shelves_data:
            shelf_name = shelf['custom_shelf_name']
            books = BookShelf.objects.filter(
                user=user,
                shelf_type='custom',
                custom_shelf_name=shelf_name
            ).select_related('book', 'book__author', 'book__category')[:50]

            custom_shelves_list.append({
                'name': shelf_name,
                'count': shelf['count'],
                'books': books
            })

        context['custom_shelves'] = custom_shelves_list

        # Progressos de leitura ativos (incompletos)
        context['reading_progress'] = ReadingProgress.objects.filter(
            user=user
        ).filter(
            current_page__lt=F('total_pages')
        ).select_related('book', 'book__author').order_by('-last_updated')[:5]

        # Estatísticas de gamificação
        if hasattr(user, 'profile'):
            profile = user.profile
            context['total_points'] = profile.points
            context['user_level'] = profile.level
            context['level_name'] = profile.level_name
            context['books_read_this_year'] = profile.books_read_this_year()
            context['reading_goal'] = profile.reading_goal
            context['goal_percentage'] = profile.reading_goal_percentage()
        else:
            context['total_points'] = 0
            context['user_level'] = 1
            context['level_name'] = 'Leitor Iniciante'
            context['books_read_this_year'] = 0
            context['reading_goal'] = 12
            context['goal_percentage'] = 0

        # Avaliações recentes
        context['recent_reviews'] = BookReview.objects.filter(
            user=user
        ).select_related('book').order_by('-created_at')[:5]

        return context