"""
View para a página de Política de Privacidade.
"""

from django.views.generic import TemplateView


class PrivacyPolicyView(TemplateView):
    """View para renderizar a página de Política de Privacidade."""
    template_name = 'core/privacy.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Política de Privacidade'
        return context
