"""
Views para Vídeos (YouTube, Instagram, etc)
"""
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView
from django.db.models import Q
from core.models import Video


class VideoListView(ListView):
    """Lista todos os vídeos do YouTube"""
    model = Video
    template_name = 'core/video_list.html'
    context_object_name = 'videos'
    paginate_by = 12  # 12 vídeos por página (grid 3x4)

    def get_queryset(self):
        """Retorna vídeos ativos do YouTube ordenados por data de criação"""
        queryset = Video.objects.filter(active=True, platform='youtube').order_by('-created_at')

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

        # Tipos de vídeo disponíveis para filtro
        context['video_types'] = Video.VIDEO_TYPE_CHOICES

        return context


class InstagramVideoListView(ListView):
    """Lista todos os vídeos do Instagram (propaganda da empresa)"""
    model = Video
    template_name = 'core/instagram_video_list.html'
    context_object_name = 'videos'
    paginate_by = 12  # 12 vídeos por página (grid 3x4)

    def get_queryset(self):
        """Retorna vídeos ativos do Instagram ordenados por data de criação"""
        queryset = Video.objects.filter(active=True, platform='instagram').order_by('-created_at')

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

        # Tipos de vídeo disponíveis para filtro
        context['video_types'] = Video.VIDEO_TYPE_CHOICES

        return context
