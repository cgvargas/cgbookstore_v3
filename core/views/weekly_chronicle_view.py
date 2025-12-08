"""
View para exibir a Crônica Semanal.
"""

from django.shortcuts import render
from django.views.generic import TemplateView
from core.models import WeeklyChronicle


class WeeklyChronicleView(TemplateView):
    """
    View para exibir a crônica semanal mais recente publicada.
    """
    template_name = 'core/weekly_chronicle.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Buscar a crônica mais recente publicada
        chronicle = WeeklyChronicle.objects.filter(
            is_published=True
        ).order_by('-published_date').first()

        context['chronicle'] = chronicle

        return context


def weekly_chronicle_view(request):
    """
    View baseada em função para exibir a crônica semanal.
    """
    # Buscar a crônica mais recente publicada
    chronicle = WeeklyChronicle.objects.filter(
        is_published=True
    ).order_by('-published_date').first()

    context = {
        'chronicle': chronicle,
    }

    return render(request, 'core/weekly_chronicle.html', context)
