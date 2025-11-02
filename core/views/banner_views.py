"""
Views para tracking de banners
"""
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from core.models import Banner


@require_POST
def track_banner_view(request, banner_id):
    """Registra visualização de um banner."""
    try:
        banner = Banner.objects.get(id=banner_id)
        banner.increment_views()
        return JsonResponse({'success': True})
    except Banner.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Banner não encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_POST
def track_banner_click(request, banner_id):
    """Registra clique em um banner."""
    try:
        banner = Banner.objects.get(id=banner_id)
        banner.increment_clicks()
        return JsonResponse({'success': True})
    except Banner.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Banner não encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
