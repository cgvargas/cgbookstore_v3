"""
Script para criar um artigo sobre O Silmarillion na página de notícias.
Executa via: python manage.py shell < scripts/add_silmarillion_article.py
"""
import os
import sys
import django
import shutil
from datetime import datetime
from pathlib import Path

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from django.utils import timezone
from django.contrib.auth import get_user_model
from news.models import Article, Tag
from core.models import Book

User = get_user_model()

# Conteúdo do artigo
ARTICLE_TITLE = "O Silmarillion: A Obra-Prima Mitológica de J.R.R. Tolkien"
ARTICLE_SUBTITLE = "A história épica que antecede O Senhor dos Anéis e revela os segredos da Terra-média"

ARTICLE_EXCERPT = """O Silmarillion é considerado por muitos como a maior obra de J.R.R. Tolkien - uma narrativa épica que conta a história da criação do mundo de Arda, a queda dos elfos, e as guerras pelas joias sagradas conhecidas como Silmarils. Descubra por que este livro é essencial para qualquer fã de Tolkien."""

ARTICLE_CONTENT = """
<h2>A Gênese de um Mundo</h2>

<p>Publicado postumamente em 1977, quatro anos após a morte de J.R.R. Tolkien, <strong>O Silmarillion</strong> não é apenas um livro - é o coração pulsante de todo o legendarium tolkieniano. Organizado e editado por seu filho Christopher Tolkien, esta obra reúne décadas de trabalho do autor, iniciado ainda durante a Primeira Guerra Mundial.</p>

<p>Diferente de "O Hobbit" ou "O Senhor dos Anéis", O Silmarillion não é uma aventura com protagonistas definidos. É uma <em>mitologia completa</em>, escrita no estilo das grandes epopeias clássicas, comparável à Ilíada de Homero ou ao Kalevala finlandês que tanto influenciou Tolkien.</p>

<h2>A Estrutura da Obra</h2>

<p>O livro divide-se em cinco partes principais:</p>

<h3>1. Ainulindalë - A Música dos Ainur</h3>
<p>O relato da criação do universo através da música. Ilúvatar (Deus) e os Ainur (seres angélicos) criam Eä, o mundo que existe, em uma das mais belas descrições de criação já escritas na literatura.</p>

<h3>2. Valaquenta - O Relato dos Valar</h3>
<p>Uma descrição dos Valar e Maiar, os poderes que governam Arda. Aqui conhecemos figuras como Manwë, Varda, Ulmo, Aulë, e também Melkor - que se tornaria Morgoth, o primeiro Senhor do Escuro.</p>

<h3>3. Quenta Silmarillion - A História das Silmarils</h3>
<p>O coração do livro. Narra a chegada dos Elfos, a criação das três Silmarils por Fëanor, o roubo das joias por Morgoth, e as terríveis guerras que se seguiram. É aqui que encontramos as histórias de Beren e Lúthien, Túrin Turambar, e a queda de Gondolin.</p>

<h3>4. Akallabêth - A Queda de Númenor</h3>
<p>A história do grande reino dos homens, sua ascensão e catastrófica queda, ecoando o mito de Atlântida. Os sobreviventes fundariam os reinos de Gondor e Arnor.</p>

<h3>5. Dos Anéis de Poder e da Terceira Era</h3>
<p>Uma ponte entre O Silmarillion e O Senhor dos Anéis, narrando a forja dos Anéis e a ascensão de Sauron.</p>

<h2>Por Que Ler O Silmarillion?</h2>

<p>Se você é fã de Tolkien, O Silmarillion oferece:</p>

<ul>
<li><strong>Contexto profundo:</strong> Entenda de onde veio Sauron, quem era Morgoth, e por que os Elfos estão deixando a Terra-média</li>
<li><strong>Histórias épicas:</strong> Romances trágicos, batalhas lendárias, e heróis inesquecíveis</li>
<li><strong>Linguagem sublime:</strong> Tolkien em seu estilo mais elevado e poético</li>
<li><strong>Riqueza mitológica:</strong> Uma cosmologia completa rivalizada apenas pelas grandes mitologias mundiais</li>
</ul>

<h2>Dicas para a Leitura</h2>

<p>O Silmarillion pode ser desafiador para novos leitores. Algumas sugestões:</p>

<ol>
<li>Leia primeiro os apêndices de O Senhor dos Anéis para familiarizar-se com nomes élficos</li>
<li>Tenha em mãos o mapa de Beleriand (incluído no livro)</li>
<li>Não tente memorizar todos os nomes na primeira leitura</li>
<li>Deixe-se levar pelo tom épico e pela beleza da prosa</li>
</ol>

<blockquote>
<p><em>"E assim foi que os Elfos despertaram junto às águas de Cuiviénen, sob as estrelas da Terra-média, e seu primeiro som foi o som da água que fluía sobre as pedras."</em></p>
</blockquote>

<h2>Conclusão</h2>

<p>O Silmarillion é mais do que um livro - é a chave que abre todas as portas da Terra-média. É uma obra que recompensa releituras e que cresce em significado a cada nova visita. Para qualquer leitor que deseja ir além da Sociedade do Anel e mergulhar nas profundezas da imaginação de Tolkien, O Silmarillion não é opcional - é <strong>essencial</strong>.</p>

<p>Na CG.BookStore, você encontra O Silmarillion e outras obras do legendarium tolkieniano em nossa seção especial dedicada ao mestre da fantasia.</p>
"""


def create_silmarillion_article():
    """Cria o artigo sobre O Silmarillion."""
    
    print("=" * 60)
    print("📰 Criando artigo sobre O Silmarillion")
    print("=" * 60)
    
    # Verificar se já existe
    if Article.objects.filter(slug='silmarillion-obra-prima-tolkien').exists():
        print("⚠️ Artigo já existe! Atualizando...")
        article = Article.objects.get(slug='silmarillion-obra-prima-tolkien')
    else:
        article = Article()
    
    # Obter ou criar tags
    tags_names = ['Tolkien', 'Fantasia', 'Literatura', 'Terra-média', 'Clássicos', 'Mitologia']
    tags = []
    for tag_name in tags_names:
        tag, created = Tag.objects.get_or_create(
            name=tag_name,
            defaults={'slug': tag_name.lower().replace('-', '').replace(' ', '-')}
        )
        tags.append(tag)
        if created:
            print(f"   ✅ Tag criada: {tag_name}")
    
    # Tentar encontrar o livro O Silmarillion
    related_book = None
    try:
        related_book = Book.objects.filter(title__icontains='silmarillion').first()
        if related_book:
            print(f"   📚 Livro relacionado: {related_book.title}")
    except Exception as e:
        print(f"   ⚠️ Livro não encontrado: {e}")
    
    # Obter ou criar usuário admin
    try:
        author = User.objects.filter(is_superuser=True).first()
        if not author:
            author = User.objects.first()
    except Exception:
        author = None
    
    # Copiar imagem para media
    source_image = Path(r"C:\Users\claud\.gemini\antigravity\brain\30e2b79e-d427-4587-bbf7-9929a63499ca\silmarillion_article_1765737495506.png")
    dest_dir = Path(r"c:\ProjectDjango\cgbookstore_v3\media\news\featured")
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_image = dest_dir / "silmarillion_article.png"
    
    if source_image.exists():
        shutil.copy(source_image, dest_image)
        print(f"   🖼️ Imagem copiada: {dest_image}")
    
    # Configurar artigo
    article.title = ARTICLE_TITLE
    article.slug = 'silmarillion-obra-prima-tolkien'
    article.subtitle = ARTICLE_SUBTITLE
    article.content_type = 'article'  # Tipo: artigo
    article.excerpt = ARTICLE_EXCERPT
    article.content = ARTICLE_CONTENT
    article.featured_image = 'news/featured/silmarillion_article.png'
    article.image_caption = 'As Silmarils: joias sagradas criadas por Fëanor'
    article.author = author
    article.related_book = related_book
    article.priority = 3  # Alta
    article.is_featured = True  # Destaque
    article.is_published = True
    article.published_at = timezone.now()
    
    article.save()
    
    # Adicionar tags
    article.tags.set(tags)
    
    print()
    print("✅ Artigo criado com sucesso!")
    print(f"   📝 Título: {article.title}")
    print(f"   🔗 Slug: {article.slug}")
    print(f"   📅 Publicado: {article.published_at}")
    print(f"   🏷️ Tags: {', '.join(t.name for t in tags)}")
    print(f"   ⭐ Em destaque: Sim")
    print()
    print(f"🌐 Acesse: /noticias/artigo/{article.slug}/")
    print("=" * 60)
    
    return article


if __name__ == '__main__':
    create_silmarillion_article()
