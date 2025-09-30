"""
Views para Eventos Literários
"""
from django.views.generic import ListView
from django.utils import timezone
from core.models import Event


class EventListView(ListView):
    """
    View para listar todos os eventos ativos.
    Separa eventos futuros dos finalizados.
    """
    model = Event
    template_name = 'core/events.html'
    context_object_name = 'events'
    paginate_by = 12

    def get_queryset(self):
        """Retorna apenas eventos ativos, ordenados por data"""
        return Event.objects.filter(
            active=True
        ).exclude(
            status='cancelled'
        ).order_by('start_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        now = timezone.now()
        all_events = self.get_queryset()

        # Separar eventos por status
        context['upcoming_events'] = all_events.filter(
            start_date__gt=now
        ).order_by('start_date')

        context['ongoing_events'] = all_events.filter(
            start_date__lte=now,
            end_date__gte=now
        ).order_by('start_date')

        context['past_events'] = all_events.filter(
            end_date__lt=now
        ).order_by('-end_date')[:6]  # Últimos 6 eventos finalizados

        # Evento em destaque (para hero section)
        context['featured_event'] = all_events.filter(
            featured=True,
            start_date__gt=now
        ).first()

        return context