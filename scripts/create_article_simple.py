# -*- coding: utf-8 -*-
from django.utils import timezone
from news.models import Article, Tag
import shutil
from pathlib import Path

# Copiar imagem
src = Path(r"C:\Users\claud\.gemini\antigravity\brain\30e2b79e-d427-4587-bbf7-9929a63499ca\silmarillion_article_1765737495506.png")
dst_dir = Path(r"c:\ProjectDjango\cgbookstore_v3\media\news\featured")
dst_dir.mkdir(parents=True, exist_ok=True)
dst = dst_dir / "silmarillion_article.png"
if src.exists():
    shutil.copy(src, dst)
    print("Imagem copiada!")

# Criar tags
tag_names = ['Tolkien', 'Fantasia', 'Literatura']
tags = []
for name in tag_names:
    t, c = Tag.objects.get_or_create(name=name, defaults={'slug': name.lower()})
    tags.append(t)
    print(f"Tag: {name}")

# Criar artigo
content = """<h2>A Genese de um Mundo</h2>
<p>Publicado postumamente em 1977, <strong>O Silmarillion</strong> e o coracao pulsante de todo o legendarium tolkieniano.</p>
<h2>A Estrutura da Obra</h2>
<p>O livro divide-se em cinco partes principais: Ainulindale, Valaquenta, Quenta Silmarillion, Akallabeth e Dos Aneis de Poder.</p>
<h2>Por Que Ler O Silmarillion?</h2>
<ul><li>Contexto profundo sobre a Terra-media</li><li>Historias epicas</li><li>Linguagem sublime</li></ul>"""

article, created = Article.objects.update_or_create(
    slug='silmarillion-obra-prima-tolkien',
    defaults={
        'title': 'O Silmarillion: A Obra-Prima Mitologica de J.R.R. Tolkien',
        'subtitle': 'A historia epica que antecede O Senhor dos Aneis',
        'content_type': 'article',
        'excerpt': 'O Silmarillion e considerado por muitos como a maior obra de Tolkien - uma narrativa epica que conta a historia da criacao do mundo de Arda.',
        'content': content,
        'featured_image': 'news/featured/silmarillion_article.png',
        'image_caption': 'As Silmarils: joias sagradas criadas por Feanor',
        'priority': 3,
        'is_featured': True,
        'is_published': True,
        'published_at': timezone.now(),
    }
)
article.tags.set(tags)
print(f"Artigo {'criado' if created else 'atualizado'}: {article.title}")
print(f"ID: {article.id}")
