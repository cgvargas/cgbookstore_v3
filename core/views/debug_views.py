"""
View de debug para verificar deployment do módulo de vídeos
TEMPORÁRIO - Remover após verificação
"""
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_GET
import sys


@require_GET
def video_debug_view(request):
    """
    Endpoint de debug para verificar se o código de vídeos foi deployado.
    Acesse: /debug/video-module/
    """
    results = {
        'deployment_status': 'checking...',
        'tests': {}
    }

    # Teste 1: Verificar se video_utils existe
    try:
        from core.utils import video_utils
        results['tests']['video_utils_module'] = {
            'status': 'OK',
            'location': str(video_utils.__file__),
            'functions': dir(video_utils)
        }
    except ImportError as e:
        results['tests']['video_utils_module'] = {
            'status': 'ERRO',
            'error': str(e)
        }
        results['deployment_status'] = 'FAILED - video_utils não encontrado'
        return JsonResponse(results, status=500)

    # Teste 2: Verificar funções
    try:
        from core.utils.video_utils import extract_video_thumbnail
        results['tests']['extract_video_thumbnail'] = {
            'status': 'OK',
            'callable': callable(extract_video_thumbnail)
        }
    except ImportError as e:
        results['tests']['extract_video_thumbnail'] = {
            'status': 'ERRO',
            'error': str(e)
        }

    # Teste 3: Verificar método save() do Video
    try:
        from core.models import Video
        import inspect

        source = inspect.getsource(Video.save)
        has_new_code = 'extract_video_thumbnail' in source

        results['tests']['video_save_method'] = {
            'status': 'OK' if has_new_code else 'ANTIGO',
            'has_extract_video_thumbnail': has_new_code,
            'first_lines': source.split('\n')[:5]
        }

        if not has_new_code:
            results['deployment_status'] = 'FAILED - Código antigo ainda rodando'
        else:
            results['deployment_status'] = 'OK - Código novo deployado'

    except Exception as e:
        results['tests']['video_save_method'] = {
            'status': 'ERRO',
            'error': str(e)
        }

    # Teste 4: requests disponível?
    try:
        import requests
        results['tests']['requests_library'] = {
            'status': 'OK',
            'version': requests.__version__
        }
    except ImportError as e:
        results['tests']['requests_library'] = {
            'status': 'ERRO',
            'error': str(e)
        }

    # Teste 5: Testar extração YouTube
    try:
        from core.utils.video_utils import extract_youtube_thumbnail

        test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        result = extract_youtube_thumbnail(test_url)

        results['tests']['youtube_extraction'] = {
            'status': 'OK' if result else 'FALHOU',
            'result': result
        }
    except Exception as e:
        results['tests']['youtube_extraction'] = {
            'status': 'ERRO',
            'error': str(e)
        }

    # Teste 6: Simular save() de um vídeo
    try:
        from core.models import Video
        from core.utils.video_utils import extract_video_thumbnail

        # Simular criação de vídeo
        test_url_yt = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

        embed_code, thumbnail_url = extract_video_thumbnail('youtube', test_url_yt)

        results['tests']['simulate_save'] = {
            'status': 'OK',
            'youtube_test': {
                'url': test_url_yt,
                'embed_code_extracted': embed_code,
                'thumbnail_extracted': thumbnail_url,
                'would_save_thumbnail': bool(thumbnail_url and not ""),  # Simula: not self.thumbnail_url quando está vazio
                'would_save_if_exists': bool(thumbnail_url and not "http://old.url"),  # Simula: quando já tem valor
            }
        }

    except Exception as e:
        results['tests']['simulate_save'] = {
            'status': 'ERRO',
            'error': str(e)
        }

    # Python version
    results['python_version'] = sys.version

    return JsonResponse(results, json_dumps_params={'indent': 2})
