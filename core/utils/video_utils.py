"""
Utilitários para processamento de vídeos de diferentes plataformas
"""
import re
import requests
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)


def extract_instagram_thumbnail(video_url):
    """
    Extrai thumbnail de vídeos do Instagram usando múltiplas estratégias.

    Estratégias (em ordem de tentativa):
    1. API oEmbed do Instagram (funciona até outubro/2025)
    2. Extração de metadados HTML (Open Graph tags)
    3. Retorna None se ambas falharem

    Args:
        video_url (str): URL do vídeo do Instagram

    Returns:
        str or None: URL da thumbnail ou None se não conseguir extrair
    """
    if not video_url:
        return None

    # Estratégia 1: Tentar API oEmbed
    try:
        oembed_url = f"https://api.instagram.com/oembed/?url={video_url}"
        response = requests.get(oembed_url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            thumbnail_url = data.get('thumbnail_url')

            if thumbnail_url:
                logger.info(f"Thumbnail extraída via oEmbed: {thumbnail_url}")
                return thumbnail_url
        else:
            logger.warning(f"oEmbed falhou com status {response.status_code}")
    except Exception as e:
        logger.warning(f"Erro ao tentar oEmbed do Instagram: {e}")

    # Estratégia 2: Extrair metadados HTML (Open Graph)
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(video_url, headers=headers, timeout=10)

        if response.status_code == 200:
            # Procurar por og:image no HTML
            og_image_match = re.search(r'<meta\s+property="og:image"\s+content="([^"]+)"', response.text)

            if og_image_match:
                thumbnail_url = og_image_match.group(1)
                logger.info(f"Thumbnail extraída via Open Graph: {thumbnail_url}")
                return thumbnail_url

            # Alternativa: procurar por og:video:thumbnail
            og_video_thumb = re.search(r'<meta\s+property="og:video:thumbnail"\s+content="([^"]+)"', response.text)
            if og_video_thumb:
                thumbnail_url = og_video_thumb.group(1)
                logger.info(f"Thumbnail extraída via og:video:thumbnail: {thumbnail_url}")
                return thumbnail_url
    except Exception as e:
        logger.warning(f"Erro ao extrair metadados HTML do Instagram: {e}")

    logger.error(f"Não foi possível extrair thumbnail para: {video_url}")
    return None


def extract_youtube_video_id(video_url):
    """
    Extrai o ID do vídeo do YouTube de diferentes formatos de URL.

    Args:
        video_url (str): URL do vídeo do YouTube

    Returns:
        str or None: ID do vídeo ou None se não conseguir extrair
    """
    if not video_url:
        return None

    video_id = None

    # Formato: youtube.com/watch?v=VIDEO_ID
    if 'youtube.com/watch?v=' in video_url:
        video_id = video_url.split('watch?v=')[1].split('&')[0]
    # Formato: youtu.be/VIDEO_ID
    elif 'youtu.be/' in video_url:
        video_id = video_url.split('youtu.be/')[1].split('?')[0]
    # Formato: youtube.com/shorts/VIDEO_ID
    elif 'youtube.com/shorts/' in video_url:
        video_id = video_url.split('shorts/')[1].split('?')[0]
    # Formato: youtube.com/embed/VIDEO_ID
    elif 'youtube.com/embed/' in video_url:
        video_id = video_url.split('embed/')[1].split('?')[0]

    return video_id


def extract_youtube_thumbnail(video_url):
    """
    Extrai thumbnail de vídeos do YouTube.

    Args:
        video_url (str): URL do vídeo do YouTube

    Returns:
        str or None: URL da thumbnail ou None
    """
    video_id = extract_youtube_video_id(video_url)

    if video_id:
        # Usar maxresdefault para melhor qualidade
        # Fallback: hqdefault, mqdefault, sddefault, default
        return f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"

    return None


def extract_vimeo_video_id(video_url):
    """
    Extrai o ID do vídeo do Vimeo.

    Args:
        video_url (str): URL do vídeo do Vimeo

    Returns:
        str or None: ID do vídeo ou None
    """
    if not video_url:
        return None

    # Formato: vimeo.com/VIDEO_ID
    match = re.search(r'vimeo\.com/(\d+)', video_url)
    if match:
        return match.group(1)

    return None


def extract_vimeo_thumbnail(video_url):
    """
    Extrai thumbnail de vídeos do Vimeo usando a API oEmbed.

    Args:
        video_url (str): URL do vídeo do Vimeo

    Returns:
        str or None: URL da thumbnail ou None
    """
    try:
        oembed_url = f"https://vimeo.com/api/oembed.json?url={video_url}"
        response = requests.get(oembed_url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            thumbnail_url = data.get('thumbnail_url')

            if thumbnail_url:
                logger.info(f"Thumbnail do Vimeo extraída: {thumbnail_url}")
                return thumbnail_url
    except Exception as e:
        logger.warning(f"Erro ao extrair thumbnail do Vimeo: {e}")

    return None


def extract_tiktok_thumbnail(video_url):
    """
    Extrai thumbnail de vídeos do TikTok usando metadados HTML.

    Args:
        video_url (str): URL do vídeo do TikTok

    Returns:
        str or None: URL da thumbnail ou None
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(video_url, headers=headers, timeout=10)

        if response.status_code == 200:
            # Procurar por og:image no HTML
            og_image_match = re.search(r'<meta\s+property="og:image"\s+content="([^"]+)"', response.text)

            if og_image_match:
                thumbnail_url = og_image_match.group(1)
                logger.info(f"Thumbnail do TikTok extraída: {thumbnail_url}")
                return thumbnail_url
    except Exception as e:
        logger.warning(f"Erro ao extrair thumbnail do TikTok: {e}")

    return None


def extract_video_thumbnail(platform, video_url):
    """
    Extrai thumbnail de vídeo baseado na plataforma.

    Args:
        platform (str): Plataforma do vídeo ('youtube', 'instagram', 'vimeo', 'tiktok')
        video_url (str): URL do vídeo

    Returns:
        tuple: (embed_code, thumbnail_url)
    """
    embed_code = None
    thumbnail_url = None

    if platform == 'youtube':
        embed_code = extract_youtube_video_id(video_url)
        thumbnail_url = extract_youtube_thumbnail(video_url)

    elif platform == 'instagram':
        thumbnail_url = extract_instagram_thumbnail(video_url)
        # Instagram não usa embed_code da mesma forma

    elif platform == 'vimeo':
        embed_code = extract_vimeo_video_id(video_url)
        thumbnail_url = extract_vimeo_thumbnail(video_url)

    elif platform == 'tiktok':
        thumbnail_url = extract_tiktok_thumbnail(video_url)
        # TikTok não usa embed_code da mesma forma

    return embed_code, thumbnail_url
