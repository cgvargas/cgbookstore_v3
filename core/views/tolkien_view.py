# core/views/tolkien_view.py
"""
View legada do Mundo de Tolkien.
Redireciona permanentemente (HTTP 301) para a nova view dinâmica em /universo/tolkien/.
Preserva completamente o SEO das URLs antigas.
"""

from django.views.generic import RedirectView
from django.urls import reverse_lazy


class TolkienWorldView(RedirectView):
    """
    Redirecionamento permanente 301 da URL antiga /tolkien/
    para o novo módulo dinâmico em /universo/tolkien/.
    """
    permanent = True
    url = reverse_lazy('core:literary_universe', kwargs={'slug': 'tolkien'})
