"""
Context processors para adicionar dados de recomendações aos templates.
"""


def recommendations_available(request):
    """
    Adiciona informação sobre disponibilidade de recomendações ao contexto.
    """
    context = {
        'recommendations_enabled': True,
    }

    if request.user.is_authenticated:
        # Verificar se usuário tem interações suficientes
        from .models import UserBookInteraction
        from django.conf import settings

        min_interactions = settings.RECOMMENDATIONS_CONFIG.get('MIN_INTERACTIONS', 5)
        user_interactions = UserBookInteraction.objects.filter(user=request.user).count()

        context['has_enough_interactions'] = user_interactions >= min_interactions
        context['user_interactions_count'] = user_interactions
        context['min_interactions_required'] = min_interactions

    return context
