#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script para debugar o banner - versão simplificada"""
import os
import sys
import django

# Configurar Django
sys.path.insert(0, 'C:\\ProjectDjango\\cgbookstore_v3')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')

try:
    django.setup()
except Exception as e:
    print(f"ERRO ao configurar Django: {e}")
    sys.exit(1)

from core.models import Section
from django.core.cache import cache

print("="*80)
print("DIAGNOSTICO DO BANNER")
print("="*80)

# 1. Verificar modelo
print("\n1. Verificando modelo Section...")
try:
    test_section = Section()
    if hasattr(test_section, 'banner_image'):
        print("   OK - Campo 'banner_image' existe no modelo")
    else:
        print("   ERRO - Campo 'banner_image' NAO existe no modelo!")
        print("   SOLUCAO: Execute 'python manage.py migrate'")
except Exception as e:
    print(f"   ERRO ao verificar modelo: {e}")

# 2. Verificar seções ativas
print("\n2. Verificando secoes ativas...")
try:
    sections = Section.objects.filter(active=True).order_by('order')
    print(f"   Total de secoes ativas: {sections.count()}")

    for idx, section in enumerate(sections, 1):
        print(f"\n   Secao {idx}: {section.title}")
        print(f"      ID: {section.id}")
        print(f"      Ordem: {section.order}")
        print(f"      Ativa: {section.active}")

        # Verificar banner_image
        try:
            banner = section.banner_image
            if banner:
                print(f"      Banner: CONFIGURADO")
                print(f"      Nome do arquivo: {banner.name}")
                print(f"      URL: {banner.url}")

                # Verificar se existe
                try:
                    if banner.storage.exists(banner.name):
                        size = banner.size
                        print(f"      Tamanho: {size / 1024:.2f} KB")
                        print(f"      OK - Arquivo existe!")
                    else:
                        print(f"      ERRO - Arquivo NAO existe no storage!")
                except Exception as e:
                    print(f"      AVISO - Erro ao verificar arquivo: {e}")
            else:
                print(f"      Banner: NAO CONFIGURADO")
        except AttributeError:
            print(f"      ERRO - Campo 'banner_image' nao existe!")
            print(f"      SOLUCAO - A migration NAO foi aplicada!")
        except Exception as e:
            print(f"      ERRO ao acessar banner: {e}")

except Exception as e:
    print(f"   ERRO ao buscar secoes: {e}")

# 3. Verificar cache
print("\n3. Verificando cache...")
cache_key = 'home_full_context'
cached_data = cache.get(cache_key)
if cached_data:
    print("   CACHE EXISTE - isso pode estar impedindo mudancas")
    print("   SOLUCAO: Execute 'python clear_home_cache.py'")

    # Ver se tem banner_image
    if 'sections' in cached_data:
        for section in cached_data['sections']:
            title = section.get('title', 'sem titulo')
            if 'banner_image' in section:
                print(f"   Cache tem 'banner_image' na secao: {title}")
            else:
                print(f"   Cache NAO tem 'banner_image' na secao: {title}")
else:
    print("   OK - Nenhum cache encontrado")

# 4. Testar view
print("\n4. Testando construcao do contexto...")
try:
    from core.views.home_view import HomeView
    view = HomeView()
    sections_data = view._build_sections_as_dicts()

    print(f"   OK - Metodo _build_sections_as_dicts() funcionou")
    print(f"   Retornou {len(sections_data)} secoes")

    for section in sections_data:
        title = section.get('title', 'Sem titulo')
        has_banner = 'banner_image' in section
        banner_value = section.get('banner_image')

        print(f"\n   Secao: {title}")
        print(f"      Chave 'banner_image' existe? {has_banner}")
        if has_banner:
            print(f"      Valor: {banner_value}")
            if banner_value:
                print(f"      OK - Banner configurado!")
            else:
                print(f"      AVISO - Banner eh None/vazio")
        else:
            print(f"      ERRO - Chave 'banner_image' NAO existe no dict!")

except Exception as e:
    print(f"   ERRO ao testar view: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
print("DIAGNOSTICO COMPLETO")
print("="*80)
