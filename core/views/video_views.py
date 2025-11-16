"""
Views para Vídeos do YouTube
"""
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView
from django.db.models import Q
from core.models import Video


class VideoListView(ListView):
    """Lista todos os vídeos (YouTube, Instagram, Vimeo, TikTok)"""
    model = Video
    template_name = 'core/video_list.html'
    context_object_name = 'videos'
    paginate_by = 12  # 12 vídeos por página (grid 3x4)

    def get_queryset(self):
        """Retorna vídeos ativos ordenados por data de criação"""
        queryset = Video.objects.filter(active=True).order_by('-created_at')

        # Filtro por plataforma (Instagram, YouTube, Vimeo, TikTok)
        platform = self.kwargs.get('platform')
        if platform:
            queryset = queryset.filter(platform=platform)

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

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        context['selected_video_type'] = self.request.GET.get('video_type', '')
        context['platform'] = self.kwargs.get('platform', '')

        # Tipos de vídeo disponíveis para filtro
        context['video_types'] = Video.VIDEO_TYPE_CHOICES

        # Plataformas disponíveis
        context['platforms'] = Video.PLATFORM_CHOICES

        # Nome amigável da plataforma
        platform = self.kwargs.get('platform')
        if platform:
            platform_dict = dict(Video.PLATFORM_CHOICES)
            context['platform_name'] = platform_dict.get(platform, platform.capitalize())

        return context
