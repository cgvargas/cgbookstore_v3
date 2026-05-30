"""
View para geração de formulários de contribuição de conteúdo.

URL: /gerar-formulario/<form_type>/?format=xlsx|txt|pdf
Acesso: apenas superusuários.

Arquitetura extensível:
    - O parâmetro `form_type` consulta o FORM_REGISTRY
    - Para adicionar um novo tipo, basta registrar em registry.py
    - Nenhuma alteração nesta view é necessária
"""

import logging
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
from django.shortcuts import render

from core.services.form_generator.registry import FORM_REGISTRY, get_generator, get_available_types

logger = logging.getLogger(__name__)

# Tipos MIME e extensões por formato de saída
FORMAT_CONFIG = {
    'xlsx': {
        'content_type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'extension': 'xlsx',
        'method': 'generate_xlsx',
        'label': 'Excel (XLSX)',
    },
    'txt': {
        'content_type': 'text/plain; charset=utf-8',
        'extension': 'txt',
        'method': 'generate_txt',
        'label': 'Texto Simples (TXT)',
    },
    'pdf': {
        'content_type': 'application/pdf',
        'extension': 'pdf',
        'method': 'generate_pdf',
        'label': 'PDF',
    },
}


@login_required(login_url='account_login')
def generate_contribution_form(request, form_type):
    """
    Gera e faz download de um formulário de contribuição de conteúdo.

    Acesso restrito a superusuários. Tipo e formato são configuráveis via URL.

    Args:
        request: HttpRequest
        form_type: Tipo do formulário (deve existir no FORM_REGISTRY)

    Query Params:
        format: Formato de saída — 'xlsx' (padrão), 'txt' ou 'pdf'
    """
    # ── Verificação de permissão ──────────────────────────────────────────
    if not request.user.is_superuser:
        logger.warning(
            "Tentativa de acesso não autorizado ao gerador de formulários. "
            "Usuário: %s | form_type: %s",
            request.user.username, form_type
        )
        raise Http404("Página não encontrada.")

    # ── Validar tipo de formulário ────────────────────────────────────────
    if form_type not in FORM_REGISTRY:
        logger.warning(
            "Tipo de formulário inválido solicitado: '%s' pelo usuário %s",
            form_type, request.user.username
        )
        raise Http404(f"Tipo de formulário '{form_type}' não existe.")

    # ── Validar formato de saída ──────────────────────────────────────────
    output_format = request.GET.get('format', 'xlsx').lower()
    if output_format not in FORMAT_CONFIG:
        output_format = 'xlsx'  # Fallback seguro

    fmt = FORMAT_CONFIG[output_format]

    # ── Gerar o formulário ────────────────────────────────────────────────
    try:
        generator = get_generator(form_type)
        generate_method = getattr(generator, fmt['method'])
        buffer = generate_method()

        # Nome do arquivo
        filename = f"{generator.get_filename_base()}.{fmt['extension']}"

        logger.info(
            "Formulário gerado com sucesso: tipo='%s', formato='%s', "
            "usuário='%s', arquivo='%s'",
            form_type, output_format, request.user.username, filename
        )

        # ── Resposta HTTP com download ────────────────────────────────────
        response = HttpResponse(buffer.read(), content_type=fmt['content_type'])
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    except ImportError as exc:
        logger.error(
            "Dependência ausente para gerar formulário '%s' em '%s': %s",
            form_type, output_format, exc
        )
        # Fallback: tentar TXT se a dependência XLSX/PDF não estiver disponível
        if output_format != 'txt':
            try:
                generator = get_generator(form_type)
                buffer = generator.generate_txt()
                filename = f"{generator.get_filename_base()}.txt"
                response = HttpResponse(buffer.read(), content_type='text/plain; charset=utf-8')
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
                logger.info("Fallback para TXT aplicado para formulário '%s'.", form_type)
                return response
            except Exception as fallback_exc:
                logger.error("Falha no fallback TXT: %s", fallback_exc)

        raise Http404("Não foi possível gerar o formulário. Contate o suporte.")

    except Exception as exc:
        logger.error(
            "Erro inesperado ao gerar formulário '%s' em '%s': %s",
            form_type, output_format, exc
        )
        raise Http404("Erro interno ao gerar o formulário. Contate o suporte.")


def form_generator_info(request):
    """
    Endpoint de diagnóstico — lista os tipos disponíveis no registry.
    Apenas para superusuários, retorna JSON com os tipos disponíveis.
    Útil para integração futura com frontend ou API.
    """
    if not request.user.is_authenticated or not request.user.is_superuser:
        raise Http404()

    from django.http import JsonResponse
    available = get_available_types()
    return JsonResponse({
        'available_form_types': available,
        'supported_formats': list(FORMAT_CONFIG.keys()),
        'url_pattern': '/gerar-formulario/<form_type>/?format=<xlsx|txt|pdf>',
    })
