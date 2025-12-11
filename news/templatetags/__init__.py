"""
Template tags personalizados para o app news.
"""
import re
from django import template

register = template.Library()


@register.filter
def youtube_id(url):
    """
    Extrai o ID do vídeo de uma URL do YouTube.
    
    Suporta formatos:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://www.youtube.com/embed/VIDEO_ID
    
    Retorna o ID do vídeo ou string vazia se não encontrar.
    """
    if not url:
        return ''
    
    # Padrões de URL do YouTube
    patterns = [
        r'(?:youtube\.com\/watch\?v=)([a-zA-Z0-9_-]{11})',
        r'(?:youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',
        r'(?:youtu\.be\/)([a-zA-Z0-9_-]{11})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return ''


@register.filter
def youtube_thumbnail(url):
    """
    Retorna a URL da thumbnail de máxima resolução de um vídeo do YouTube.
    """
    video_id = youtube_id(url)
    if video_id:
        return f'https://img.youtube.com/vi/{video_id}/maxresdefault.jpg'
    return ''


@register.simple_tag
def youtube_embed_url(url):
    """
    Retorna a URL de embed do YouTube a partir de qualquer formato de URL.
    """
    video_id = youtube_id(url)
    if video_id:
        return f'https://www.youtube.com/embed/{video_id}?rel=0&modestbranding=1'
    return ''
