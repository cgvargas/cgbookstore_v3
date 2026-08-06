"""
Views para a Central de Mídias Externas Corporativa.
Inclui a listagem geral (/videos/) e a página individual rica em SEO (/videos/<slug>/).
"""

from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.db.models import Q, Max, F
from core.models import Video


class VideoListView(ListView):
    """Lista todas as mídias ativas da plataforma."""
    model = Video
    template_name = 'core/video_list.html'
    context_object_name = 'videos'
    paginate_by = 12

    def get_queryset(self):
        queryset = Video.objects.filter(active=True)

        # Busca por termo
        search = self.request.GET.get('q')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(short_description__icontains=search) |
                Q(description__icontains=search) |
                Q(channel_name__icontains=search)
            )

        # Filtro por tipo de mídia
        video_type = self.request.GET.get('video_type')
        if video_type:
            queryset = queryset.filter(video_type=video_type)

        # Filtro por canal oficial
        official = self.request.GET.get('official')
        if official == 'true':
            queryset = queryset.filter(is_official_channel=True)

        return queryset.prefetch_related(
            'related_books', 'related_author', 'related_universes'
        ).order_by('display_order', '-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        context['selected_video_type'] = self.request.GET.get('video_type', '')
        context['selected_official'] = self.request.GET.get('official', '')
        context['video_types'] = Video.MEDIA_TYPE_CHOICES
        return context


class VideoDetailView(DetailView):
    """
    Página rica e individual para cada mídia (/videos/<slug>/).
    Incrementa visualizações atomicamente via F() controlado por sessão.
    Gera metadados avançados de SEO e JSON-LD VideoObject.
    """
    model = Video
    template_name = 'core/external_media_detail.html'
    context_object_name = 'video'

    def get_object(self, queryset=None):
        video = super().get_object(queryset)

        # Incremento atômico de visualização por sessão do usuário (máx. 1 visualização por sessão por vídeo)
        session_key = f'viewed_video_{video.id}'
        if not self.request.session.get(session_key, False):
            Video.objects.filter(pk=video.pk).update(views_count=F('views_count') + 1)
            self.request.session[session_key] = True
            video.refresh_from_db(fields=['views_count'])

        return video

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        video = self.object

        # Mídias semelhantes/relacionadas
        related_media = Video.objects.filter(active=True).exclude(pk=video.pk)
        if video.video_type:
            related_media = related_media.filter(video_type=video.video_type)

        context['related_media'] = related_media.prefetch_related('related_books')[:6]

        # SEO JSON-LD VideoObject condicional
        json_ld_data = None
        if video.title and (video.get_embed_url() or video.video_url):
            json_ld_data = {
                "@context": "https://schema.org",
                "@type": "VideoObject",
                "name": video.title,
                "description": video.short_description or video.description[:200] or video.title,
                "thumbnailUrl": [video.get_thumbnail()] if video.get_thumbnail() else [],
                "embedUrl": video.get_embed_url() or video.video_url,
            }
            if video.published_date:
                json_ld_data["uploadDate"] = video.published_date.isoformat()
            if video.formatted_duration:
                # ISO 8601 Duration format
                json_ld_data["duration"] = f"PT{video.formatted_duration.replace(':', 'M')}S"

        context['json_ld_video'] = json_ld_data
        return context
