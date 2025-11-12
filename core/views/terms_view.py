from django.views.generic import TemplateView
from django.utils import timezone


class TermsView(TemplateView):
    """
    View para exibir os Termos de Serviço
    """
    template_name = 'core/terms.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_date'] = timezone.now()
        return context
