# C:\Users\claud\OneDrive\ProjectsDjango\CGBookStore_v3\core\views\about_view.py

from django.views.generic import TemplateView


class AboutView(TemplateView):
    """
    View para a página institucional 'Sobre'.
    Exibe informações sobre a CG.BookStore.
    """
    template_name = 'core/about.html'