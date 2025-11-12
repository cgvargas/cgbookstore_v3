from django.views.generic import TemplateView
from django.utils import timezone


class PrivacyView(TemplateView):
    """
    View para exibir a Política de Privacidade
    """
    template_name = 'core/privacy.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_date'] = timezone.now()
        return context
