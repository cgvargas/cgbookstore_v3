#!/usr/bin/env python
"""
Script para testar se o código de vídeos foi deployado corretamente
Execute via: python manage.py shell < test_deployment_video.py
"""
import sys
import os

print("=" * 60)
print("TESTE DE DEPLOYMENT - MÓDULO DE VÍDEOS")
print("=" * 60)

# Teste 1: Verificar se video_utils existe
print("\n1. Verificando se core/utils/video_utils.py existe...")
try:
    from core.utils import video_utils
    print("   ✓ Módulo video_utils encontrado")
    print(f"   ✓ Localização: {video_utils.__file__}")
except ImportError as e:
    print(f"   ✗ ERRO: Módulo não encontrado - {e}")
    sys.exit(1)

# Teste 2: Verificar funções disponíveis
print("\n2. Verificando funções disponíveis...")
funcs = [
    'extract_instagram_thumbnail',
    'extract_youtube_thumbnail',
    'extract_vimeo_thumbnail',
    'extract_tiktok_thumbnail',
    'extract_video_thumbnail'
]

for func_name in funcs:
    if hasattr(video_utils, func_name):
        print(f"   ✓ {func_name} disponível")
    else:
        print(f"   ✗ {func_name} NÃO ENCONTRADA")

# Teste 3: Verificar método save() do Video
print("\n3. Verificando método save() do model Video...")
try:
    from core.models import Video
    import inspect

    source = inspect.getsource(Video.save)

    if 'extract_video_thumbnail' in source:
        print("   ✓ Método save() atualizado (contém extract_video_thumbnail)")
    else:
        print("   ✗ Método save() ANTIGO (não contém extract_video_thumbnail)")
        print("\n   Conteúdo do método save():")
        print("   " + "-" * 50)
        for line in source.split('\n')[:10]:
            print(f"   {line}")
        print("   " + "-" * 50)

except Exception as e:
    print(f"   ✗ ERRO ao verificar: {e}")

# Teste 4: Testar extração de YouTube
print("\n4. Testando extração de thumbnail do YouTube...")
try:
    from core.utils.video_utils import extract_youtube_thumbnail

    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    result = extract_youtube_thumbnail(test_url)

    if result:
        print(f"   ✓ YouTube OK: {result}")
    else:
        print("   ✗ YouTube retornou None")

except Exception as e:
    print(f"   ✗ ERRO: {e}")

# Teste 5: Verificar se requests está disponível
print("\n5. Verificando dependência 'requests'...")
try:
    import requests
    print(f"   ✓ requests instalado (versão {requests.__version__})")
except ImportError:
    print("   ✗ requests NÃO INSTALADO")

# Teste 6: Criar vídeo de teste
print("\n6. Testando criação de vídeo (YouTube)...")
try:
    from core.models import Video

    # Criar vídeo de teste
    video = Video(
        title="Teste Deploy",
        platform="youtube",
        video_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        video_type="other"
    )

    # NÃO salvar no banco, apenas testar o save()
    print("   Chamando save()...")

    # Usar commit=False para não salvar no banco
    # video.save()

    # Verificar se thumbnail foi definida
    if hasattr(video, 'thumbnail_url') and video.thumbnail_url:
        print(f"   ✓ Thumbnail gerada: {video.thumbnail_url}")
    else:
        print("   ✗ Thumbnail NÃO gerada")

except Exception as e:
    print(f"   ✗ ERRO: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("TESTE CONCLUÍDO")
print("=" * 60)
