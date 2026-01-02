"""
View para a página de Termos de Uso.
"""

from django.views.generic import TemplateView


class TermsOfServiceView(TemplateView):
    """View para renderizar a página de Termos de Uso."""
    template_name = 'core/terms.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Termos de Uso'
        return context
