# C:\Users\claud\OneDrive\ProjectsDjango\CGBookStore_v3\core\views\home_view.py

from django.views.generic import TemplateView
from django.utils import timezone
from django.db.models import Count, Q
from core.models import Section, Event, Book, Banner


class HomeView(TemplateView):
    """
    View para a página inicial.
    Exibe seções dinâmicas gerenciadas pelo admin e widget de evento.
    """
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Buscar banners ativos e visíveis para o carrossel
        now = timezone.now()
        banners = Banner.objects.filter(active=True).filter(
            Q(start_date__isnull=True) | Q(start_date__lte=now)
        ).filter(
            Q(end_date__isnull=True) | Q(end_date__gte=now)
        ).order_by('order')

        context['banners'] = banners

        # Buscar todas as seções ativas ordenadas
        sections = Section.objects.filter(active=True).prefetch_related(
            'items',
            'items__content_type',
            'items__content_object'
        ).order_by('order')

        # Adicionar contagem de reviews aos livros de cada seção
        for section in sections:
            if section.content_type == 'books':
                for item in section.get_items():
                    if hasattr(item.content_object, 'user_reviews'):
                        # Adicionar reviews_count dinamicamente ao objeto livro
                        item.content_object.reviews_count = item.content_object.user_reviews.count()

        context['sections'] = sections

        # Buscar evento em destaque (próximo evento futuro)
        featured_event = Event.objects.filter(
            active=True,
            featured=True,
            start_date__gt=now
        ).exclude(
            status='cancelled'
        ).order_by('start_date').first()

        context['featured_event'] = featured_event

        return context