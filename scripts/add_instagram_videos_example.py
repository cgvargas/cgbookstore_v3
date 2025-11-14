"""
Script de Exemplo: Adicionar Vídeos do Instagram

Execute via Django shell:
    python manage.py shell < scripts/add_instagram_videos_example.py

Ou copie e cole os comandos no shell interativo:
    python manage.py shell
"""

from core.models import Video, Section, SectionItem
from django.contrib.contenttypes.models import ContentType

# ========================================
# PARTE 1: ADICIONAR VÍDEOS DO INSTAGRAM
# ========================================

print("=" * 60)
print("ADICIONANDO VÍDEOS DO INSTAGRAM")
print("=" * 60)

# Exemplo 1: Vídeo Promocional
video1 = Video.objects.create(
    title="Promoção Black Friday 2024",
    description="Confira nossas ofertas imperdíveis! Até 70% de desconto em livros selecionados.",
    platform="instagram",
    video_url="https://www.instagram.com/p/ABC123/",  # ⚠️ SUBSTITUA pela URL real
    video_type="promo",
    duration="0:30",
    featured=True,
    active=True
)
print(f"✅ Vídeo criado: {video1.title} (ID: {video1.id})")

# Exemplo 2: Lançamento de Livros
video2 = Video.objects.create(
    title="Lançamentos de Dezembro",
    description="Os livros mais esperados do mês chegaram! Vem conferir.",
    platform="instagram",
    video_url="https://www.instagram.com/reel/XYZ789/",  # ⚠️ SUBSTITUA pela URL real
    video_type="promo",
    duration="0:45",
    featured=True,
    active=True
)
print(f"✅ Vídeo criado: {video2.title} (ID: {video2.id})")

# Exemplo 3: Depoimento de Cliente
video3 = Video.objects.create(
    title="Depoimento: Cliente Satisfeito",
    description="Veja o que nossos clientes estão falando sobre nós!",
    platform="instagram",
    video_url="https://www.instagram.com/p/DEF456/",  # ⚠️ SUBSTITUA pela URL real
    video_type="promo",
    duration="1:00",
    featured=False,
    active=True
)
print(f"✅ Vídeo criado: {video3.title} (ID: {video3.id})")

# Exemplo 4: Tour pela Loja
video4 = Video.objects.create(
    title="Tour pela Nossa Loja Virtual",
    description="Conheça todos os recursos da nossa plataforma!",
    platform="instagram",
    video_url="https://www.instagram.com/reel/GHI789/",  # ⚠️ SUBSTITUA pela URL real
    video_type="tutorial",
    duration="1:30",
    featured=False,
    active=True
)
print(f"✅ Vídeo criado: {video4.title} (ID: {video4.id})")

print("\n" + "=" * 60)
print(f"TOTAL: {Video.objects.filter(platform='instagram').count()} vídeos do Instagram")
print("=" * 60)

# ========================================
# PARTE 2: CRIAR SEÇÃO NA HOME
# ========================================

print("\n" + "=" * 60)
print("CRIANDO SEÇÃO DE VÍDEOS NA HOME")
print("=" * 60)

# Criar a seção
section, created = Section.objects.get_or_create(
    title="🎬 Nossos Vídeos no Instagram",
    defaults={
        'subtitle': 'Confira nossas propagandas e conteúdos exclusivos',
        'content_type': 'videos',
        'layout': 'carousel',
        'max_items': 6,
        'show_see_more': True,
        'see_more_url': '/videos/instagram/',
        'order': 20,
        'active': True
    }
)

if created:
    print(f"✅ Seção criada: {section.title} (ID: {section.id})")
else:
    print(f"⚠️  Seção já existe: {section.title} (ID: {section.id})")

# ========================================
# PARTE 3: ADICIONAR VÍDEOS À SEÇÃO
# ========================================

print("\n" + "=" * 60)
print("ADICIONANDO VÍDEOS À SEÇÃO")
print("=" * 60)

# Obter content type de Video
video_content_type = ContentType.objects.get_for_model(Video)

# Adicionar vídeos à seção
videos_to_add = [video1, video2, video3, video4]
for index, video in enumerate(videos_to_add, start=1):
    item, created = SectionItem.objects.get_or_create(
        section=section,
        content_type=video_content_type,
        object_id=video.id,
        defaults={
            'order': index
        }
    )
    if created:
        print(f"✅ Vídeo adicionado à seção: {video.title} (Ordem: {index})")
    else:
        print(f"⚠️  Vídeo já está na seção: {video.title}")

# ========================================
# RESUMO FINAL
# ========================================

print("\n" + "=" * 60)
print("RESUMO FINAL")
print("=" * 60)
print(f"Seção: {section.title}")
print(f"Total de vídeos na seção: {section.items.count()}")
print(f"URL da página: /videos/instagram/")
print(f"Status da seção: {'Ativa ✅' if section.active else 'Inativa ❌'}")
print("=" * 60)
print("\n✨ PRONTO! Acesse a home do site para ver a seção de vídeos do Instagram!")
print(f"   👉 {section.see_more_url}")
print("=" * 60)
