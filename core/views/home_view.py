# C:\Users\claud\OneDrive\ProjectsDjango\CGBookStore_v3\core\views\home_view.py

from django.views.generic import TemplateView
from django.utils import timezone
from core.models import Section, Event


class HomeView(TemplateView):
    """
    View para a página inicial.
    Exibe seções dinâmicas gerenciadas pelo admin e widget de evento.
    """
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Buscar todas as seções ativas ordenadas
        sections = Section.objects.filter(active=True).prefetch_related(
            'items',
            'items__content_type',
            'items__content_object'
        ).order_by('order')

        context['sections'] = sections

        # Buscar evento em destaque (próximo evento futuro)
        now = timezone.now()
        featured_event = Event.objects.filter(
            active=True,
            featured=True,
            start_date__gt=now
        ).exclude(
            status='cancelled'
        ).order_by('start_date').first()

        context['featured_event'] = featured_event

        return context