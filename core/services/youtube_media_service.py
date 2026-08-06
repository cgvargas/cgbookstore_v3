# core/services/youtube_media_service.py
"""
Serviço desacoplado para parsing de URLs do YouTube, extração de IDs,
geração de embeds privativos (youtube-nocookie), fallback de thumbnails
e verificação de disponibilidade via YouTube Data API (quando disponível).
"""

import os
import logging
import requests
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


class YouTubeMediaService:
    """
    Serviço central de integração e auditoria com o YouTube.
    """

    NOCOOKIE_EMBED_BASE = "https://www.youtube-nocookie.com/embed/"
    THUMBNAIL_BASE = "https://img.youtube.com/vi/"

    @classmethod
    def extract_video_id(cls, url):
        """
        Extrai e normaliza o ID do vídeo de múltiplos formatos de URL:
        - https://www.youtube.com/watch?v=VIDEO_ID
        - https://youtu.be/VIDEO_ID
        - https://www.youtube.com/embed/VIDEO_ID
        - https://www.youtube.com/shorts/VIDEO_ID
        """
        if not url:
            return None

        url = url.strip()

        if 'watch?v=' in url:
            return url.split('watch?v=')[1].split('&')[0].split('?')[0]
        elif 'youtu.be/' in url:
            return url.split('youtu.be/')[1].split('?')[0].split('&')[0]
        elif 'youtube.com/shorts/' in url:
            return url.split('shorts/')[1].split('?')[0].split('&')[0]
        elif 'youtube.com/embed/' in url:
            return url.split('embed/')[1].split('?')[0].split('&')[0]

        return None

    @classmethod
    def get_nocookie_embed_url(cls, video_id):
        """Retorna a URL de incorporação com alta privacidade (youtube-nocookie)."""
        if not video_id:
            return None
        return f"{cls.NOCOOKIE_EMBED_BASE}{video_id.strip()}"

    @classmethod
    def get_thumbnail_fallback_urls(cls, video_id):
        """
        Retorna lista ordenada de URLs de thumbnail para fallback:
        maxresdefault -> sddefault -> hqdefault -> default
        """
        if not video_id:
            return []
        v_id = video_id.strip()
        return [
            f"{cls.THUMBNAIL_BASE}{v_id}/maxresdefault.jpg",
            f"{cls.THUMBNAIL_BASE}{v_id}/sddefault.jpg",
            f"{cls.THUMBNAIL_BASE}{v_id}/hqdefault.jpg",
            f"{cls.THUMBNAIL_BASE}{v_id}/default.jpg",
        ]

    @classmethod
    def check_video_health(cls, video_instance):
        """
        Verifica a disponibilidade da mídia via YouTube Data API v3 se a chave YOUTUBE_DATA_API_KEY estiver presente.
        Se a API não estiver configurada ou a quota exceder, marca status como 'unknown' sem falhar a aplicação.
        """
        if not video_instance or video_instance.platform != 'youtube' or not video_instance.embed_code:
            video_instance.media_status = 'unknown'
            video_instance.health_check_source = 'none'
            video_instance.last_health_check = timezone.now()
            video_instance.health_check_message = "Mídia não elegível para checagem via YouTube API."
            video_instance.save(update_fields=['media_status', 'health_check_source', 'last_health_check', 'health_check_message'])
            return

        api_key = getattr(settings, 'YOUTUBE_DATA_API_KEY', os.environ.get('YOUTUBE_DATA_API_KEY'))

        if not api_key:
            video_instance.media_status = 'unknown'
            video_instance.health_check_source = 'none'
            video_instance.last_health_check = timezone.now()
            video_instance.health_check_message = "YouTube Data API Key não configurada no ambiente. Status mantido como Desconhecido."
            video_instance.save(update_fields=['media_status', 'health_check_source', 'last_health_check', 'health_check_message'])
            return

        # Chamada oficial à API Data v3 do YouTube
        api_url = f"https://www.googleapis.com/youtube/v3/videos?id={video_instance.embed_code}&key={api_key}&part=status,contentDetails,snippet"
        
        try:
            res = requests.get(api_url, timeout=5)
            if res.status_code == 200:
                data = res.json()
                items = data.get('items', [])
                if not items:
                    video_instance.media_status = 'removed'
                    video_instance.is_embeddable = False
                    video_instance.health_check_message = "Vídeo não encontrado na API do YouTube (removido ou excluído)."
                else:
                    item = items[0]
                    status_data = item.get('status', {})
                    privacy = status_data.get('privacyStatus', 'public')
                    embeddable = status_data.get('embeddable', True)

                    video_instance.is_embeddable = embeddable

                    if privacy == 'private':
                        video_instance.media_status = 'private'
                        video_instance.health_check_message = "Vídeo marcado como Privado pelo proprietário."
                    elif not embeddable:
                        video_instance.media_status = 'embed_blocked'
                        video_instance.health_check_message = "Incorporação (Embed) desativada pelo criador do vídeo."
                    else:
                        video_instance.media_status = 'active'
                        video_instance.health_check_message = "Vídeo ativo, público e com incorporação autorizada."

                    # Atualizar canal se disponível
                    snippet = item.get('snippet', {})
                    if snippet.get('channelTitle') and not video_instance.channel_name:
                        video_instance.channel_name = snippet.get('channelTitle')
                    if snippet.get('channelId') and not video_instance.channel_id:
                        video_instance.channel_id = snippet.get('channelId')

                video_instance.health_check_source = 'youtube_api'
                video_instance.last_health_check = timezone.now()
                video_instance.save()

            else:
                logger.warning(f"Erro na requisição YouTube Data API ({res.status_code}): {res.text}")
                video_instance.media_status = 'unknown'
                video_instance.health_check_source = 'none'
                video_instance.last_health_check = timezone.now()
                video_instance.health_check_message = f"Falha na resposta da API ({res.status_code}). Status mantido como Desconhecido."
                video_instance.save(update_fields=['media_status', 'health_check_source', 'last_health_check', 'health_check_message'])

        except Exception as e:
            logger.exception("Exceção ao checar saúde do vídeo via YouTube API")
            video_instance.media_status = 'unknown'
            video_instance.health_check_source = 'none'
            video_instance.last_health_check = timezone.now()
            video_instance.health_check_message = f"Erro na conexão com a API: {str(e)}"
            video_instance.save(update_fields=['media_status', 'health_check_source', 'last_health_check', 'health_check_message'])
