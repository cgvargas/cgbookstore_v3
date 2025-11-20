"""
Script para testar valores de transparência das seções.
Execute: python scripts/test_section_opacity.py
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from core.models import Section

print("=" * 60)
print("TESTE: Valores de Opacidade e Cor das Seções")
print("=" * 60)

sections = Section.objects.filter(active=True).order_by('order')

if not sections.exists():
    print("\n⚠️  Nenhuma seção ativa encontrada!")
else:
    for section in sections:
        print(f"\n📚 Seção: {section.title}")
        print(f"   Ordem: {section.order}")
        print(f"   Tipo: {section.get_content_type_display()}")
        print(f"   Cor de Fundo: {section.background_color if section.background_color else '(padrão: var(--card-bg))'}")
        print(f"   Opacidade: {section.container_opacity}")
        print(f"   CSS Class: {section.css_class if section.css_class else '(padrão: books-carousel-section)'}")

        # Verificar se valores são funcionais
        if section.container_opacity < 1.0:
            print(f"   ✓ Transparência ativa ({int(section.container_opacity * 100)}% opaco)")
        else:
            print(f"   ✓ Totalmente opaco (padrão)")

print("\n" + "=" * 60)
print("✅ Teste concluído!")
print("=" * 60)
print("\n💡 Para testar a transparência:")
print("   1. Acesse /admin/core/section/")
print("   2. Edite uma seção")
print("   3. Em 'Estilo Visual', ajuste 'Opacidade do Container':")
print("      - 1.0 = Totalmente opaco (padrão)")
print("      - 0.8 = 80% opaco (levemente transparente)")
print("      - 0.5 = 50% opaco (meio transparente - efeito Crunchyroll)")
print("      - 0.0 = Totalmente transparente")
print("   4. Salve e recarregue a home")
print("\n")
