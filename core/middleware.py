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

import time
import logging

logger = logging.getLogger(__name__)

class PerformanceMonitoringMiddleware:
    """
    Middleware para monitorar e registrar o tempo de resposta das requisições.
    Útil para identificar gargalos de performance em produção (Render, etc).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        
        # Processa a requisição
        response = self.get_response(request)
        
        duration = time.time() - start_time
        
        # Adiciona header de Server-Timing para inspeção no DevTools do navegador
        response['Server-Timing'] = f"backend;dur={duration * 1000:.2f};desc=\"Django Backend Processing\""
        
        # Loga requisições lentas (mais de 1.5 segundos) como WARNING para fácil visualização
        if duration > 1.5:
            logger.warning(f"[PERFORMANCE ALERTA] Requisição Lenta: {request.method} {request.path} levou {duration:.2f}s")
        # Descomente a linha abaixo se quiser registrar TODAS as requisições no log (pode gerar muito volume)
        # else:
        #     logger.info(f"[PERFORMANCE] {request.method} {request.path} levou {duration:.2f}s")
            
        return response
