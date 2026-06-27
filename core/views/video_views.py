"""
Views para Vídeos do YouTube
"""
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView
from django.db.models import Q, Max
from core.models import Video


class VideoListView(ListView):
    """Lista todos os vídeos do YouTube"""
    model = Video
    template_name = 'core/video_list.html'
    context_object_name = 'videos'
    paginate_by = 12  # 12 vídeos por página (grid 3x4)

    def get_queryset(self):
        """Retorna vídeos ativos sem duplicatas (mesma URL ou arquivo), ordenados por data de criação"""
        queryset = Video.objects.filter(active=True)

        # Busca por título ou descrição
        search = self.request.GET.get('q')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search)
            )

        # Filtro por tipo de vídeo
        video_type = self.request.GET.get('video_type')
        if video_type:
            queryset = queryset.filter(video_type=video_type)

        # Identificar IDs de vídeos únicos para evitar repetição (mesmo vídeo em múltiplos volumes/sequências)
        # 1. IDs dos vídeos mais recentes com URL única (desprezando URLs vazias)
        urls_ids = queryset.exclude(video_url='').values('video_url').annotate(max_id=Max('id')).values_list('max_id', flat=True)

        # 2. IDs dos vídeos mais recentes com arquivo de vídeo único (desprezando vazios/nulos)
        files_ids = queryset.exclude(video_file='').exclude(video_file__isnull=True).values('video_file').annotate(max_id=Max('id')).values_list('max_id', flat=True)

        # 3. IDs de vídeos sem URL nem arquivo
        others_ids = queryset.filter(Q(video_url='') & (Q(video_file='') | Q(video_file__isnull=True))).values_list('id', flat=True)

        # Consolidar conjunto de IDs únicos
        unique_ids = set(urls_ids) | set(files_ids) | set(others_ids)

        # Filtrar o queryset original usando os IDs consolidados e aplicar ordenação/select_related
        return Video.objects.filter(id__in=unique_ids).select_related(
            'related_book', 'related_book__author'
        ).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        context['selected_video_type'] = self.request.GET.get('video_type', '')

        # Tipos de vídeo disponíveis para filtro
        context['video_types'] = Video.VIDEO_TYPE_CHOICES

        return context
