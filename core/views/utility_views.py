"""
Views de utilidade e endpoints de API para o app Core.
"""

from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json


@require_POST
def set_theme(request):
    """
    Salva a preferência de tema do usuário ('light', 'dark', 'auto') na sessão.
    Este endpoint é chamado pelo JavaScript do theme-switcher.
    """
    try:
        data = json.loads(request.body)
        theme = data.get('theme')

        # Valida se o tema é uma das opções válidas
        if theme in ['light', 'dark', 'auto']:
            request.session['theme'] = theme
            return JsonResponse({'success': True, 'message': f"Tema '{theme}' salvo na sessão."})
        else:
            return JsonResponse({'success': False, 'error': 'Tema inválido'}, status=400)

    except Exception as e:
        # Log do erro seria útil aqui em um projeto real
        return JsonResponse({'success': False, 'error': 'Requisição inválida'}, status=400)