# C:\Users\claud\OneDrive\ProjectsDjango\CGBookStore_v3\core\views\library_view.py

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin


class LibraryView(LoginRequiredMixin, TemplateView):
    """
    View para a Biblioteca pessoal do usuário.

    Funcionalidades planejadas:
    - Prateleiras (Favoritos, Vou Ler, Lendo, Lidos)
    - Prateleiras personalizadas
    - Cartão de perfil personalizável
    - Sistema de avaliação (estrelas)
    - Gamificação (pontos, conquistas)
    - Progresso de leitura (%)
    - Gerenciamento de livros (editar, transferir, excluir)

    Requer autenticação obrigatória.
    """
    template_name = 'core/library.html'
    login_url = '/contas/login/'
    redirect_field_name = 'next'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # TODO: Implementar após criação dos models
        # context['favorites'] = UserBookShelf.objects.filter(user=self.request.user, shelf_type='favorites')
        # context['to_read'] = UserBookShelf.objects.filter(user=self.request.user, shelf_type='to_read')
        # context['reading'] = UserBookShelf.objects.filter(user=self.request.user, shelf_type='reading')
        # context['read'] = UserBookShelf.objects.filter(user=self.request.user, shelf_type='read')
        # context['custom_shelves'] = UserBookShelf.objects.filter(user=self.request.user, shelf_type='custom')
        # context['user_profile'] = UserProfile.objects.get(user=self.request.user)
        # context['reading_progress'] = ReadingProgress.objects.filter(user=self.request.user)

        return context