#!/usr/bin/env python
"""Script para debugar o banner"""
import os
import sys
import django

# Configurar Django
sys.path.insert(0, 'C:\\ProjectDjango\\cgbookstore_v3')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')

try:
    django.setup()
except Exception as e:
    print(f"❌ Erro ao configurar Django: {e}")
    sys.exit(1)

from core.models import Section
from django.core.cache import cache

print("=" * 80)
print("🔍 DIAGNÓSTICO DO BANNER")
print("=" * 80)

# 1. Verificar se o campo existe no modelo
print("\n1️⃣ Verificando modelo Section...")
try:
    test_section = Section()
    if hasattr(test_section, 'banner_image'):
        print("   ✅ Campo 'banner_image' existe no modelo")
    else:
        print("   ❌ Campo 'banner_image' NÃO existe no modelo!")
        print("   ⚠️  Execute: python manage.py migrate")
except Exception as e:
    print(f"   ❌ Erro ao verificar modelo: {e}")

# 2. Verificar seções ativas
print("\n2️⃣ Verificando seções ativas...")
try:
    sections = Section.objects.filter(active=True).order_by('order')
    print(f"   ✅ Total de seções ativas: {sections.count()}")

    for idx, section in enumerate(sections, 1):
        print(f"\n   📌 Seção {idx}: {section.title}")
        print(f"      - ID: {section.id}")
        print(f"      - Ordem: {section.order}")
        print(f"      - Ativa: {section.active}")

        # Verificar banner_image
        try:
            banner = section.banner_image
            if banner:
                print(f"      - Banner: ✅ CONFIGURADO")
                print(f"      - Nome do arquivo: {banner.name}")
                print(f"      - URL: {banner.url}")

                # Verificar se o arquivo existe
                try:
                    if banner.storage.exists(banner.name):
                        size = banner.size
                        print(f"      - Tamanho: {size / 1024:.2f} KB")
                        print(f"      - ✅ Arquivo existe no storage!")
                    else:
                        print(f"      - ❌ Arquivo NÃO existe no storage!")
                except Exception as e:
                    print(f"      - ⚠️  Erro ao verificar arquivo: {e}")
            else:
                print(f"      - Banner: ❌ NÃO CONFIGURADO")
        except AttributeError:
            print(f"      - ❌ ERRO: Campo 'banner_image' não existe!")
            print(f"      - ⚠️  A migration NÃO foi aplicada!")
        except Exception as e:
            print(f"      - ❌ Erro ao acessar banner: {e}")

except Exception as e:
    print(f"   ❌ Erro ao buscar seções: {e}")

# 3. Verificar cache
print("\n3️⃣ Verificando cache...")
cache_key = 'home_full_context'
cached_data = cache.get(cache_key)
if cached_data:
    print("   ⚠️  CACHE EXISTE!")
    print("   💡 O cache está impedindo que as mudanças apareçam")
    print("   🔧 Solução: Execute o script clear_home_cache.py")

    # Ver se o cache tem banner_image
    if 'sections' in cached_data:
        for section in cached_data['sections']:
            if 'banner_image' in section:
                print(f"   ℹ️  Cache tem 'banner_image' na seção: {section.get('title')}")
            else:
                print(f"   ❌ Cache NÃO tem 'banner_image' na seção: {section.get('title')}")
else:
    print("   ✅ Nenhum cache encontrado")

# 4. Testar construção do contexto
print("\n4️⃣ Testando construção do contexto...")
try:
    from core.views.home_view import HomeView
    view = HomeView()
    sections_data = view._build_sections_as_dicts()

    print(f"   ✅ Método _build_sections_as_dicts() funcionou")
    print(f"   ✅ Retornou {len(sections_data)} seções")

    for section in sections_data:
        title = section.get('title', 'Sem título')
        has_banner = 'banner_image' in section
        banner_value = section.get('banner_image')

        print(f"\n   📌 Seção: {title}")
        print(f"      - Chave 'banner_image' existe? {has_banner}")
        if has_banner:
            print(f"      - Valor: {banner_value}")
            if banner_value:
                print(f"      - ✅ Banner configurado!")
            else:
                print(f"      - ⚠️  Banner é None/vazio")
        else:
            print(f"      - ❌ Chave 'banner_image' NÃO existe no dict!")

except Exception as e:
    print(f"   ❌ Erro ao testar view: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("🏁 DIAGNÓSTICO COMPLETO")
print("=" * 80)
