"""
View para página de FAQ (Perguntas Frequentes).
"""
from django.views.generic import TemplateView


class FAQView(TemplateView):
    """
    View para exibir a página de FAQ (Perguntas Frequentes).
    """
    template_name = 'core/faq.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'FAQ - Perguntas Frequentes'
        return context
