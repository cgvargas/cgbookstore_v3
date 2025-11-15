#!/usr/bin/env python
"""
Script de teste para extração de thumbnails de vídeos
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from core.utils.video_utils import (
    extract_youtube_thumbnail,
    extract_instagram_thumbnail,
    extract_vimeo_thumbnail,
    extract_tiktok_thumbnail,
    extract_video_thumbnail
)


def test_youtube():
    """Testar extração de thumbnails do YouTube"""
    print("\n" + "="*60)
    print("TESTANDO YOUTUBE")
    print("="*60)

    test_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://youtu.be/dQw4w9WgXcQ",
        "https://www.youtube.com/shorts/abc123",
    ]

    for url in test_urls:
        print(f"\nURL: {url}")
        thumbnail = extract_youtube_thumbnail(url)
        print(f"Thumbnail: {thumbnail}")


def test_instagram():
    """Testar extração de thumbnails do Instagram"""
    print("\n" + "="*60)
    print("TESTANDO INSTAGRAM")
    print("="*60)

    # Use URLs reais de Instagram para testar
    test_urls = [
        "https://www.instagram.com/p/C0aBC1234/",  # Exemplo - substitua por URL real
        "https://www.instagram.com/reel/C0aBC1234/",  # Exemplo - substitua por URL real
    ]

    print("\nNOTA: Use URLs reais do Instagram para testar a extração")
    print("As URLs de exemplo acima podem não funcionar\n")

    for url in test_urls:
        print(f"\nURL: {url}")
        try:
            thumbnail = extract_instagram_thumbnail(url)
            if thumbnail:
                print(f"✓ Thumbnail extraída: {thumbnail}")
            else:
                print("✗ Não foi possível extrair thumbnail")
        except Exception as e:
            print(f"✗ Erro: {e}")


def test_vimeo():
    """Testar extração de thumbnails do Vimeo"""
    print("\n" + "="*60)
    print("TESTANDO VIMEO")
    print("="*60)

    test_urls = [
        "https://vimeo.com/123456789",  # Exemplo - substitua por URL real
    ]

    print("\nNOTA: Use URLs reais do Vimeo para testar a extração\n")

    for url in test_urls:
        print(f"\nURL: {url}")
        try:
            thumbnail = extract_vimeo_thumbnail(url)
            if thumbnail:
                print(f"✓ Thumbnail extraída: {thumbnail}")
            else:
                print("✗ Não foi possível extrair thumbnail")
        except Exception as e:
            print(f"✗ Erro: {e}")


def test_integration():
    """Testar função integrada extract_video_thumbnail"""
    print("\n" + "="*60)
    print("TESTANDO FUNÇÃO INTEGRADA")
    print("="*60)

    tests = [
        ('youtube', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'),
        ('instagram', 'https://www.instagram.com/p/C0aBC1234/'),
        ('vimeo', 'https://vimeo.com/123456789'),
    ]

    for platform, url in tests:
        print(f"\nPlataforma: {platform}")
        print(f"URL: {url}")
        try:
            embed_code, thumbnail = extract_video_thumbnail(platform, url)
            print(f"Embed Code: {embed_code}")
            print(f"Thumbnail: {thumbnail}")
        except Exception as e:
            print(f"✗ Erro: {e}")


if __name__ == '__main__':
    print("\n" + "="*60)
    print("TESTE DE EXTRAÇÃO DE THUMBNAILS DE VÍDEOS")
    print("="*60)

    test_youtube()
    test_instagram()
    test_vimeo()
    test_integration()

    print("\n" + "="*60)
    print("TESTES CONCLUÍDOS")
    print("="*60)
    print("\nPara testar com URLs reais do Instagram:")
    print("1. Vá até instagram.com e encontre um vídeo/reel")
    print("2. Copie a URL (ex: https://www.instagram.com/p/ABC123/)")
    print("3. Execute: python test_video_thumbnails.py")
    print("4. Ou teste diretamente no Django Admin ao adicionar um vídeo")
    print("="*60 + "\n")
