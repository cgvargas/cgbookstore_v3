"""
Template tags customizados para o CGBookStore
"""
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def render_stars(rating):
    """
    Renderiza 5 estrelas baseado na avaliação.
    """
    if not rating:
        rating = 0

    rating = max(0, min(5, float(rating)))

    stars_html = '<span class="rating-stars">'

    full_stars = int(rating)
    has_half = (rating - full_stars) >= 0.5
    empty_stars = 5 - full_stars - (1 if has_half else 0)

    for i in range(full_stars):
        stars_html += '<i class="fas fa-star star filled"></i>'

    if has_half:
        stars_html += '<i class="fas fa-star-half-alt star filled"></i>'

    for i in range(empty_stars):
        stars_html += '<i class="far fa-star star"></i>'

    stars_html += f'<span class="rating-value">({rating:.1f})</span>'
    stars_html += '</span>'
    
    return mark_safe(stars_html)