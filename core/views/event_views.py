"""
Views para Eventos Literários
"""
from django.views.generic import ListView, DetailView
from django.utils import timezone
from core.models import Event


class EventDetailView(DetailView):
    """
    View para exibir detalhes completos de um evento.
    """
    model = Event
    template_name = 'core/event_detail.html'
    context_object_name = 'event'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        """Retorna apenas eventos ativos"""
        return Event.objects.filter(active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = self.object
        now = timezone.now()

        # Status do evento
        context['is_upcoming'] = event.start_date > now
        context['is_ongoing'] = event.start_date <= now <= event.end_date
        context['is_finished'] = event.end_date < now

        # Dias até o evento
        if context['is_upcoming']:
            delta = event.start_date - now
            context['days_until'] = delta.days
            context['hours_until'] = delta.seconds // 3600

        # Outros eventos futuros (para sugestões)
        context['other_events'] = Event.objects.filter(
            active=True,
            start_date__gt=now
        ).exclude(pk=event.pk).order_by('start_date')[:3]

        return context


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