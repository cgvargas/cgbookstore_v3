"""
Middlewares customizados.
"""

from django.http import JsonResponse
from django.shortcuts import render
from django_ratelimit.exceptions import Ratelimited


class RateLimitMiddleware:
    """
    Middleware para tratar exceções de rate limiting.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        if isinstance(exception, Ratelimited):
            # Se for requisição AJAX/JSON, retornar JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'error': 'Limite de requisições excedido. Tente novamente mais tarde.',
                    'status': 429
                }, status=429)

            # Senão, retornar página HTML
            return render(request, 'errors/429.html', {
                'message': 'Você atingiu o limite de requisições. Por favor, aguarde alguns minutos.'
            }, status=429)

        return None
