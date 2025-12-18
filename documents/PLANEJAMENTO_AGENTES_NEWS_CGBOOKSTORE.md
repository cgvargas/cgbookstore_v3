# 🤖 Sistema de Agentes para Geração Automática de Notícias
## CGBookStore v3 - Módulo News

---

**Projeto:** CGBookStore v3  
**Módulo:** `news` (Caminho: `C:\ProjectDjango\cgbookstore_v3\news`)  
**Data:** 18/12/2024  
**Autor:** CGVargas  
**Status:** Planejamento  
**Custo:** R$ 0,00 (Solução 100% Gratuita)

---

## 📋 ÍNDICE

1. [Visão Geral](#visão-geral)
2. [Objetivos](#objetivos)
3. [Arquitetura da Solução](#arquitetura-da-solução)
4. [Tecnologias Utilizadas](#tecnologias-utilizadas)
5. [Estrutura de Dados](#estrutura-de-dados)
6. [Implementação por Fases](#implementação-por-fases)
7. [APIs e Integrações](#apis-e-integrações)
8. [Workflow de Automação](#workflow-de-automação)
9. [Custos e Recursos](#custos-e-recursos)
10. [Roadmap de Desenvolvimento](#roadmap-de-desenvolvimento)
11. [Manutenção e Monitoramento](#manutenção-e-monitoramento)

---

## 🎯 VISÃO GERAL

Sistema automatizado de agregação, processamento e publicação de notícias literárias para o blog do CGBookStore, utilizando agentes de IA para:

- **Coletar** notícias de múltiplas fontes RSS
- **Filtrar** conteúdo relevante sobre literatura, livros e autores
- **Processar** com IA (Gemini + Claude) para criar artigos originais
- **Publicar** automaticamente no blog com imagens e SEO otimizado

### Diferenciais da Solução

✅ **100% Gratuita** - Usa apenas recursos gratuitos e já contratados  
✅ **Conteúdo Original** - IA reescreve notícias para evitar duplicação  
✅ **Multi-Fonte** - Agrega de várias fontes RSS confiáveis  
✅ **SEO-Friendly** - Otimização automática para mecanismos de busca  
✅ **Moderação** - Sistema de aprovação antes da publicação  
✅ **Imagens Automáticas** - Busca e adiciona imagens de alta qualidade

---

## 🎯 OBJETIVOS

### Objetivos Principais

1. **Automatizar** a criação de conteúdo para o blog
2. **Reduzir custos** de produção de conteúdo (R$ 0,00)
3. **Manter frequência** de publicação (diária/semanal)
4. **Aumentar tráfego** orgânico através de SEO
5. **Engajar audiência** com conteúdo relevante sobre literatura

### Métricas de Sucesso

- [ ] 30-50 posts/mês publicados
- [ ] 0% custo com ferramentas de IA
- [ ] 80%+ aprovação de rascunhos gerados
- [ ] Aumento de 50%+ em tráfego orgânico em 3 meses
- [ ] Tempo médio de moderação < 10 min/post

---

## 🏗️ ARQUITETURA DA SOLUÇÃO

### Fluxo de Dados

```
┌─────────────────────────────────────────────────────────────┐
│                    COLETA DE NOTÍCIAS                       │
│  Google News RSS + Feeds Literários (PublishNews, etc)     │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│               FILTRAGEM COM GEMINI (Gratuito)               │
│  • Analisa 50-100 notícias coletadas                        │
│  • Filtra por relevância literária                          │
│  • Seleciona top 5-10 melhores                              │
│  • Cria resumos executivos                                  │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│          CRIAÇÃO COM CLAUDE (Já contratado)                 │
│  • Transforma resumos em artigos completos (800-1200 pal.)  │
│  • Gera título SEO-friendly                                 │
│  • Cria meta-description                                    │
│  • Define tags relevantes                                   │
│  • Mantém tom literário e profissional                      │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│            BUSCA DE IMAGENS (Unsplash API)                  │
│  • Busca imagens relacionadas ao tema                       │
│  • Download e upload para Supabase Storage                  │
│  • Adiciona como featured_image                             │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                 SALVAMENTO NO BANCO                         │
│  Status: 'pending' (aguardando moderação)                   │
│  Notificação para admin revisar                             │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              MODERAÇÃO MANUAL (Admin)                       │
│  • Revisa conteúdo                                          │
│  • Edita se necessário                                      │
│  • Aprova ou rejeita                                        │
│  • Agenda publicação                                        │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    PUBLICAÇÃO                               │
│  Status: 'published'                                        │
│  Disponível no blog público                                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 💻 TECNOLOGIAS UTILIZADAS

### Backend

- **Django 5.0.3** - Framework web
- **PostgreSQL (Supabase)** - Banco de dados
- **Celery** - Task queue para automação
- **Redis** - Message broker do Celery

### APIs de IA

| Serviço | Função | Custo |
|---------|--------|-------|
| **Claude API (Anthropic)** | Criação de artigos completos | R$ 0 (já incluído no plano) |
| **Gemini Pro (Google)** | Filtragem e resumo de notícias | R$ 0 (plano gratuito - 60 req/min) |

### APIs de Conteúdo

| Serviço | Função | Custo | Limite |
|---------|--------|-------|--------|
| **Google News RSS** | Agregação de notícias | R$ 0 | Ilimitado |
| **PublishNews RSS** | Notícias específicas de livros | R$ 0 | Ilimitado |
| **Unsplash API** | Imagens de alta qualidade | R$ 0 | 50 req/hora |

### Storage

- **Supabase Storage** - Armazenamento de imagens

### Bibliotecas Python

```python
# requirements.txt (adicionar)
feedparser==6.0.10           # Parser de RSS feeds
google-generativeai==0.3.2   # Gemini API
anthropic==0.7.8             # Claude API (se usar SDK)
requests==2.31.0             # HTTP requests
pillow==10.1.0               # Processamento de imagens
celery==5.3.4                # Task scheduling
redis==5.0.1                 # Celery broker
python-decouple==3.8         # Variáveis de ambiente
```

---

## 📊 ESTRUTURA DE DADOS

### Models Django

**Localização:** `C:\ProjectDjango\cgbookstore_v3\news\models\`

#### 1. NewsCategory

```python
class NewsCategory(models.Model):
    """
    Categorias de notícias do blog
    Ex: Lançamentos, Resenhas, Entrevistas, Mercado Editorial
    """
    name = models.CharField(max_length=100, verbose_name="Nome")
    slug = models.SlugField(unique=True, verbose_name="Slug")
    description = models.TextField(blank=True, verbose_name="Descrição")
    icon = models.CharField(max_length=50, blank=True, help_text="Classe do ícone Bootstrap")
    order = models.IntegerField(default=0, verbose_name="Ordem de exibição")
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Categoria de Notícia"
        verbose_name_plural = "Categorias de Notícias"
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name
```

#### 2. NewsPost

```python
class NewsPost(models.Model):
    """
    Post de notícia do blog
    """
    STATUS_CHOICES = [
        ('draft', 'Rascunho'),
        ('pending', 'Aguardando Revisão'),
        ('published', 'Publicado'),
        ('rejected', 'Rejeitado'),
    ]
    
    # Conteúdo principal
    title = models.CharField(max_length=200, verbose_name="Título")
    slug = models.SlugField(unique=True, verbose_name="Slug")
    category = models.ForeignKey(
        NewsCategory, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='posts',
        verbose_name="Categoria"
    )
    
    excerpt = models.TextField(
        max_length=300, 
        verbose_name="Resumo",
        help_text="Breve descrição para listagens e SEO"
    )
    content = models.TextField(verbose_name="Conteúdo completo")
    
    # Imagens
    featured_image = models.URLField(
        blank=True,
        verbose_name="Imagem destacada",
        help_text="URL da imagem no Supabase Storage"
    )
    featured_image_alt = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Texto alternativo da imagem"
    )
    
    # Fonte original
    source_url = models.URLField(
        blank=True, 
        verbose_name="URL da fonte",
        help_text="Link para notícia original"
    )
    source_name = models.CharField(
        max_length=100, 
        blank=True,
        verbose_name="Nome da fonte"
    )
    
    # Metadados de IA
    ai_generated = models.BooleanField(
        default=False, 
        verbose_name="Gerado por IA"
    )
    ai_model_primary = models.CharField(
        max_length=50, 
        blank=True,
        verbose_name="Modelo IA principal",
        help_text="Ex: claude-3-sonnet, gemini-pro"
    )
    ai_model_secondary = models.CharField(
        max_length=50, 
        blank=True,
        verbose_name="Modelo IA secundário"
    )
    ai_processing_time = models.FloatField(
        null=True,
        blank=True,
        verbose_name="Tempo de processamento (segundos)"
    )
    
    # SEO
    tags = models.JSONField(
        default=list,
        verbose_name="Tags",
        help_text="Lista de palavras-chave"
    )
    meta_description = models.CharField(
        max_length=160,
        blank=True,
        verbose_name="Meta descrição (SEO)"
    )
    
    # Controle de publicação
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='draft',
        verbose_name="Status"
    )
    author = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='news_posts',
        verbose_name="Autor"
    )
    published_at = models.DateTimeField(
        null=True, 
        blank=True,
        verbose_name="Data de publicação"
    )
    
    # Métricas
    views_count = models.IntegerField(
        default=0,
        verbose_name="Visualizações"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Post de Notícia"
        verbose_name_plural = "Posts de Notícias"
        ordering = ['-published_at', '-created_at']
        indexes = [
            models.Index(fields=['status', '-published_at']),
            models.Index(fields=['slug']),
            models.Index(fields=['category', 'status']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        # Auto-gerar slug se não existir
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.title)
        
        # Auto-definir published_at quando publicar
        if self.status == 'published' and not self.published_at:
            from django.utils import timezone
            self.published_at = timezone.now()
        
        super().save(*args, **kwargs)
    
    @property
    def reading_time(self):
        """Calcula tempo de leitura estimado (palavras/min)"""
        words = len(self.content.split())
        minutes = max(1, words // 200)  # 200 palavras por minuto
        return minutes
```

#### 3. NewsSource

```python
class NewsSource(models.Model):
    """
    Fontes RSS para agregação de notícias
    """
    SOURCE_TYPE_CHOICES = [
        ('rss', 'RSS Feed'),
        ('atom', 'Atom Feed'),
        ('json', 'JSON Feed'),
    ]
    
    name = models.CharField(max_length=100, verbose_name="Nome da fonte")
    url = models.URLField(unique=True, verbose_name="URL do feed")
    source_type = models.CharField(
        max_length=10,
        choices=SOURCE_TYPE_CHOICES,
        default='rss',
        verbose_name="Tipo de feed"
    )
    
    # Configurações
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    priority = models.IntegerField(
        default=1,
        verbose_name="Prioridade",
        help_text="1-10, quanto maior mais importante"
    )
    
    # Filtros
    keywords_include = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Palavras-chave (incluir)",
        help_text="Notícias devem conter pelo menos uma dessas palavras"
    )
    keywords_exclude = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Palavras-chave (excluir)",
        help_text="Notícias com essas palavras serão ignoradas"
    )
    
    # Estatísticas
    last_fetch_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Última busca"
    )
    last_fetch_status = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Status da última busca"
    )
    total_items_fetched = models.IntegerField(
        default=0,
        verbose_name="Total de itens buscados"
    )
    total_items_published = models.IntegerField(
        default=0,
        verbose_name="Total de itens publicados"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Fonte de Notícias"
        verbose_name_plural = "Fontes de Notícias"
        ordering = ['-priority', 'name']
    
    def __str__(self):
        return f"{self.name} ({'Ativo' if self.is_active else 'Inativo'})"
```

---

## 🔧 IMPLEMENTAÇÃO POR FASES

### FASE 1: Estrutura Base (1-2 dias)

**Objetivo:** Criar estrutura básica do módulo news

#### Tarefas:

1. **Criar models**
   - [ ] `NewsCategory`
   - [ ] `NewsPost`
   - [ ] `NewsSource`
   
2. **Migrations**
   ```bash
   python manage.py makemigrations news
   python manage.py migrate
   ```

3. **Admin básico**
   ```python
   # news/admin.py
   
   @admin.register(NewsPost)
   class NewsPostAdmin(admin.ModelAdmin):
       list_display = ['title', 'category', 'status', 'ai_generated', 'published_at']
       list_filter = ['status', 'category', 'ai_generated']
       search_fields = ['title', 'content']
       prepopulated_fields = {'slug': ('title',)}
   ```

4. **URLs básicas**
   ```python
   # news/urls.py
   
   urlpatterns = [
       path('', NewsListView.as_view(), name='news_list'),
       path('categoria/<slug:slug>/', NewsCategoryView.as_view(), name='news_category'),
       path('<slug:slug>/', NewsDetailView.as_view(), name='news_detail'),
   ]
   ```

5. **Views básicas**
   - ListView para listagem
   - DetailView para post individual
   - CategoryView para posts por categoria

6. **Templates básicos**
   - `news/news_list.html`
   - `news/news_detail.html`
   - `news/partials/news_card.html`

**Commit:** `feat(news): estrutura base do módulo news`

---

### FASE 2: Serviço de Agregação RSS (1-2 dias)

**Objetivo:** Implementar coleta de notícias de feeds RSS

#### Tarefas:

1. **Criar serviço de agregação**

```python
# news/services/rss_aggregator.py

import feedparser
from datetime import datetime, timedelta
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class RSSAggregator:
    """
    Serviço para agregar notícias de múltiplos feeds RSS
    """
    
    def __init__(self):
        self.sources = []
        self.load_active_sources()
    
    def load_active_sources(self):
        """Carrega fontes ativas do banco"""
        from news.models import NewsSource
        self.sources = NewsSource.objects.filter(is_active=True)
    
    def fetch_all_feeds(self, hours_back: int = 24) -> List[Dict]:
        """
        Busca notícias de todos os feeds ativos
        
        Args:
            hours_back: Buscar notícias das últimas X horas
        
        Returns:
            Lista de dicionários com as notícias
        """
        all_news = []
        cutoff_date = datetime.now() - timedelta(hours=hours_back)
        
        for source in self.sources:
            try:
                news_items = self.fetch_single_feed(source, cutoff_date)
                all_news.extend(news_items)
                
                # Atualizar estatísticas
                source.last_fetch_at = datetime.now()
                source.last_fetch_status = 'success'
                source.total_items_fetched += len(news_items)
                source.save()
                
                logger.info(f"Fetched {len(news_items)} items from {source.name}")
                
            except Exception as e:
                logger.error(f"Error fetching {source.name}: {str(e)}")
                source.last_fetch_status = f'error: {str(e)[:50]}'
                source.save()
        
        return all_news
    
    def fetch_single_feed(self, source, cutoff_date: datetime) -> List[Dict]:
        """
        Busca notícias de um único feed
        
        Args:
            source: Objeto NewsSource
            cutoff_date: Data de corte para notícias antigas
        
        Returns:
            Lista de dicionários com as notícias
        """
        feed = feedparser.parse(source.url)
        news_items = []
        
        for entry in feed.entries:
            # Parse da data
            published_date = self._parse_entry_date(entry)
            
            # Filtrar por data
            if published_date and published_date < cutoff_date:
                continue
            
            # Extrair dados
            news_item = {
                'title': entry.get('title', ''),
                'link': entry.get('link', ''),
                'description': entry.get('description', entry.get('summary', '')),
                'published_date': published_date,
                'source_name': source.name,
                'source_url': source.url,
                'source_priority': source.priority,
            }
            
            # Aplicar filtros de palavras-chave
            if self._passes_keyword_filters(news_item, source):
                news_items.append(news_item)
        
        return news_items
    
    def _parse_entry_date(self, entry) -> datetime:
        """Parse da data do entry RSS"""
        date_fields = ['published_parsed', 'updated_parsed']
        for field in date_fields:
            if hasattr(entry, field):
                time_struct = getattr(entry, field)
                if time_struct:
                    return datetime(*time_struct[:6])
        return datetime.now()
    
    def _passes_keyword_filters(self, news_item: Dict, source) -> bool:
        """
        Verifica se a notícia passa pelos filtros de palavras-chave
        """
        text = f"{news_item['title']} {news_item['description']}".lower()
        
        # Filtro de exclusão
        if source.keywords_exclude:
            for keyword in source.keywords_exclude:
                if keyword.lower() in text:
                    return False
        
        # Filtro de inclusão (se configurado)
        if source.keywords_include:
            for keyword in source.keywords_include:
                if keyword.lower() in text:
                    return True
            return False  # Nenhuma palavra-chave encontrada
        
        return True
```

2. **Criar fontes RSS padrão**

```python
# news/management/commands/setup_news_sources.py

from django.core.management.base import BaseCommand
from news.models import NewsSource

class Command(BaseCommand):
    help = 'Configura fontes RSS padrão de notícias literárias'
    
    def handle(self, *args, **options):
        sources = [
            {
                'name': 'Google News - Livros Literatura',
                'url': 'https://news.google.com/rss/search?q=livros+literatura+when:7d&hl=pt-BR&gl=BR&ceid=BR:pt-419',
                'priority': 10,
                'keywords_include': ['livro', 'autor', 'literatura', 'editora', 'lançamento'],
            },
            {
                'name': 'Google News - Bestsellers',
                'url': 'https://news.google.com/rss/search?q=bestseller+literatura+livro&hl=pt-BR&gl=BR&ceid=BR:pt-419',
                'priority': 9,
            },
            {
                'name': 'PublishNews',
                'url': 'https://publishnews.com.br/feed',
                'priority': 10,
            },
            # Adicionar mais fontes conforme necessário
        ]
        
        for source_data in sources:
            source, created = NewsSource.objects.get_or_create(
                url=source_data['url'],
                defaults=source_data
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Criada: {source.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'○ Já existe: {source.name}'))
```

**Commit:** `feat(news): implementa agregação RSS`

---

### FASE 3: Integração com Gemini (Filtragem) (1-2 dias)

**Objetivo:** Usar Gemini para filtrar e selecionar melhores notícias

#### Tarefas:

1. **Configurar variáveis de ambiente**

```python
# .env
GEMINI_API_KEY=sua_chave_aqui
```

2. **Criar serviço Gemini**

```python
# news/services/gemini_service.py

import google.generativeai as genai
from typing import List, Dict
import json
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class GeminiNewsFilter:
    """
    Serviço para filtrar notícias usando Gemini
    """
    
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-pro')
    
    def filter_and_rank_news(
        self, 
        news_items: List[Dict], 
        limit: int = 10
    ) -> List[Dict]:
        """
        Filtra e ranqueia notícias por relevância
        
        Args:
            news_items: Lista de notícias coletadas
            limit: Número de notícias a retornar
        
        Returns:
            Lista das melhores notícias com resumos
        """
        try:
            # Preparar prompt
            prompt = self._build_filter_prompt(news_items, limit)
            
            # Chamar Gemini
            response = self.model.generate_content(prompt)
            
            # Parse da resposta JSON
            selected_news = json.loads(response.text)
            
            logger.info(f"Gemini selected {len(selected_news)} news from {len(news_items)}")
            
            return selected_news
            
        except Exception as e:
            logger.error(f"Error filtering with Gemini: {str(e)}")
            # Fallback: retornar as mais recentes
            return sorted(news_items, key=lambda x: x['published_date'], reverse=True)[:limit]
    
    def _build_filter_prompt(self, news_items: List[Dict], limit: int) -> str:
        """Constrói prompt para o Gemini"""
        
        # Formatar notícias para o prompt
        news_text = "\n\n".join([
            f"ID: {i}\n"
            f"Título: {item['title']}\n"
            f"Descrição: {item['description'][:200]}...\n"
            f"Fonte: {item['source_name']}"
            for i, item in enumerate(news_items)
        ])
        
        prompt = f"""
Você é um especialista em literatura e curadoria de conteúdo para um blog literário chamado CGBookStore.

Analise as seguintes {len(news_items)} notícias sobre literatura, livros e autores:

{news_text}

TAREFA:
1. Selecione as {limit} notícias MAIS RELEVANTES e interessantes para leitores apaixonados por literatura
2. Priorize notícias sobre:
   - Lançamentos de livros importantes
   - Entrevistas com autores
   - Prêmios literários
   - Tendências do mercado editorial
   - Eventos literários relevantes

3. EVITE notícias sobre:
   - Celebridades que não são autores
   - Política (a menos que seja sobre censura/liberdade de expressão literária)
   - Notícias muito genéricas ou superficiais

Para cada notícia selecionada, crie um resumo executivo em português brasileiro (150-200 palavras).

RETORNE APENAS um JSON válido neste formato:
[
  {{
    "id": 0,
    "relevance_score": 9.5,
    "summary": "Resumo executivo aqui...",
    "suggested_category": "Lançamentos",
    "suggested_tags": ["tag1", "tag2", "tag3"]
  }}
]

NÃO inclua nenhum texto antes ou depois do JSON.
"""
        return prompt
```

**Commit:** `feat(news): integra Gemini para filtragem`

---

### FASE 4: Integração com Claude (Criação de Conteúdo) (2-3 dias)

**Objetivo:** Usar Claude para criar artigos completos

#### Tarefas:

1. **Configurar variáveis de ambiente**

```python
# .env
CLAUDE_API_KEY=sua_chave_aqui  # Se usar API
# OU usar via interface (você já paga)
```

2. **Criar serviço Claude**

```python
# news/services/claude_service.py

from anthropic import Anthropic
from typing import Dict
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class ClaudeArticleCreator:
    """
    Serviço para criar artigos completos usando Claude
    """
    
    def __init__(self):
        self.client = Anthropic(api_key=settings.CLAUDE_API_KEY)
    
    def create_article(self, news_data: Dict) -> Dict:
        """
        Cria artigo completo a partir de resumo
        
        Args:
            news_data: Dict com resumo e dados da notícia
        
        Returns:
            Dict com artigo completo
        """
        try:
            prompt = self._build_article_prompt(news_data)
            
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4096,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Parse do conteúdo
            article_data = self._parse_claude_response(message.content[0].text)
            
            logger.info(f"Claude created article: {article_data['title'][:50]}...")
            
            return article_data
            
        except Exception as e:
            logger.error(f"Error creating article with Claude: {str(e)}")
            raise
    
    def _build_article_prompt(self, news_data: Dict) -> str:
        """Constrói prompt para o Claude"""
        
        prompt = f"""
Você é um escritor especializado em literatura para o blog CGBookStore, um portal dedicado a leitores apaixonados por livros.

INFORMAÇÕES DA NOTÍCIA:
Título original: {news_data['title']}
Resumo: {news_data['summary']}
Fonte: {news_data['source_name']}
Link: {news_data['link']}

TAREFA:
Crie um artigo completo em português brasileiro sobre esta notícia, seguindo estas diretrizes:

ESTRUTURA:
1. Título cativante e SEO-friendly (máximo 70 caracteres)
2. Introdução envolvente (2-3 parágrafos)
3. Corpo do artigo com desenvolvimento (4-6 parágrafos)
4. Conclusão interessante (1-2 parágrafos)

ESTILO:
- Tom: Profissional mas acessível, apaixonado por literatura
- Linguagem: Clara, envolvente, evitando jargões excessivos
- Tamanho: 800-1200 palavras
- Foco: Valor para o leitor (por que isso importa?)

SEO:
- Use palavras-chave naturalmente
- Inclua sinônimos e variações
- Estruture com parágrafos curtos

IMPORTANTE:
- NÃO copie o texto original
- Adicione contexto e análise própria
- Mantenha fatos e informações precisas
- Cite a fonte original ao final

RETORNE no formato JSON:
{{
  "title": "Título do artigo",
  "content": "Conteúdo completo em HTML (use <p>, <h2>, <strong>, etc)",
  "excerpt": "Resumo de 200-300 caracteres",
  "meta_description": "Meta description SEO (150-160 caracteres)",
  "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"]
}}
"""
        return prompt
    
    def _parse_claude_response(self, response_text: str) -> Dict:
        """Parse da resposta do Claude"""
        import json
        import re
        
        # Remover markdown se houver
        json_text = re.sub(r'```json\n?', '', response_text)
        json_text = re.sub(r'```\n?', '', json_text)
        
        # Parse JSON
        article_data = json.loads(json_text.strip())
        
        return article_data
```

**Commit:** `feat(news): integra Claude para criação de artigos`

---

### FASE 5: Busca de Imagens (Unsplash) (1 dia)

**Objetivo:** Buscar imagens automaticamente

#### Tarefas:

1. **Configurar Unsplash API**

```python
# .env
UNSPLASH_ACCESS_KEY=sua_chave_aqui
```

2. **Criar serviço de imagens**

```python
# news/services/image_service.py

import requests
from typing import Optional
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class UnsplashImageService:
    """
    Serviço para buscar imagens no Unsplash
    """
    
    BASE_URL = "https://api.unsplash.com"
    
    def __init__(self):
        self.access_key = settings.UNSPLASH_ACCESS_KEY
    
    def search_image(
        self, 
        keywords: list, 
        orientation: str = 'landscape'
    ) -> Optional[Dict]:
        """
        Busca imagem relacionada às palavras-chave
        
        Args:
            keywords: Lista de palavras-chave
            orientation: 'landscape', 'portrait' ou 'squarish'
        
        Returns:
            Dict com dados da imagem ou None
        """
        try:
            # Construir query
            query = ' '.join(keywords[:3])  # Usar até 3 keywords
            
            # Fazer requisição
            response = requests.get(
                f"{self.BASE_URL}/search/photos",
                params={
                    'query': query,
                    'per_page': 5,
                    'orientation': orientation,
                },
                headers={
                    'Authorization': f'Client-ID {self.access_key}'
                }
            )
            
            response.raise_for_status()
            data = response.json()
            
            if data['results']:
                # Pegar primeira imagem
                image = data['results'][0]
                
                return {
                    'url': image['urls']['regular'],
                    'download_url': image['links']['download_location'],
                    'photographer': image['user']['name'],
                    'photographer_url': image['user']['links']['html'],
                    'alt_description': image.get('alt_description', query),
                }
            
            logger.warning(f"No images found for: {query}")
            return None
            
        except Exception as e:
            logger.error(f"Error searching Unsplash: {str(e)}")
            return None
    
    def download_image(self, image_data: Dict) -> Optional[bytes]:
        """
        Faz download da imagem
        
        Returns:
            Bytes da imagem ou None
        """
        try:
            # Notificar Unsplash do download (requerido pela API)
            requests.get(
                image_data['download_url'],
                headers={'Authorization': f'Client-ID {self.access_key}'}
            )
            
            # Fazer download
            response = requests.get(image_data['url'])
            response.raise_for_status()
            
            return response.content
            
        except Exception as e:
            logger.error(f"Error downloading image: {str(e)}")
            return None
```

3. **Integrar com Supabase Storage**

```python
# news/services/storage_service.py

from supabase import create_client
from django.conf import settings
import uuid
from typing import Optional

class SupabaseStorageService:
    """
    Serviço para upload de imagens no Supabase Storage
    """
    
    def __init__(self):
        self.client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY
        )
        self.bucket = 'news-images'
    
    def upload_image(
        self, 
        image_data: bytes, 
        filename: Optional[str] = None
    ) -> Optional[str]:
        """
        Faz upload da imagem para Supabase Storage
        
        Returns:
            URL pública da imagem ou None
        """
        try:
            # Gerar nome único
            if not filename:
                filename = f"{uuid.uuid4()}.jpg"
            
            # Upload
            response = self.client.storage.from_(self.bucket).upload(
                filename,
                image_data,
                {'content-type': 'image/jpeg'}
            )
            
            # Obter URL pública
            public_url = self.client.storage.from_(self.bucket).get_public_url(filename)
            
            return public_url
            
        except Exception as e:
            logger.error(f"Error uploading to Supabase: {str(e)}")
            return None
```

**Commit:** `feat(news): implementa busca e upload de imagens`

---

### FASE 6: Management Command Principal (1-2 dias)

**Objetivo:** Criar comando Django que orquestra todo o processo

#### Tarefas:

1. **Criar comando principal**

```python
# news/management/commands/generate_news_posts.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from news.models import NewsPost, NewsCategory
from news.services.rss_aggregator import RSSAggregator
from news.services.gemini_service import GeminiNewsFilter
from news.services.claude_service import ClaudeArticleCreator
from news.services.image_service import UnsplashImageService
from news.services.storage_service import SupabaseStorageService
import logging
import time

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Gera posts de notícias automaticamente usando IA'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=10,
            help='Número de posts a gerar'
        )
        parser.add_argument(
            '--hours-back',
            type=int,
            default=24,
            help='Buscar notícias das últimas X horas'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simular sem salvar no banco'
        )
    
    def handle(self, *args, **options):
        limit = options['limit']
        hours_back = options['hours_back']
        dry_run = options['dry_run']
        
        self.stdout.write(self.style.NOTICE(f'\n🤖 Iniciando geração de {limit} posts...'))
        
        start_time = time.time()
        
        try:
            # 1. AGREGAÇÃO
            self.stdout.write('\n📡 FASE 1: Agregando notícias de RSS feeds...')
            aggregator = RSSAggregator()
            raw_news = aggregator.fetch_all_feeds(hours_back=hours_back)
            self.stdout.write(self.style.SUCCESS(f'  ✓ {len(raw_news)} notícias coletadas'))
            
            if not raw_news:
                self.stdout.write(self.style.WARNING('  ⚠ Nenhuma notícia encontrada'))
                return
            
            # 2. FILTRAGEM COM GEMINI
            self.stdout.write('\n🔍 FASE 2: Filtrando com Gemini...')
            gemini_filter = GeminiNewsFilter()
            selected_news = gemini_filter.filter_and_rank_news(raw_news, limit=limit)
            self.stdout.write(self.style.SUCCESS(f'  ✓ {len(selected_news)} notícias selecionadas'))
            
            # 3. CRIAÇÃO COM CLAUDE
            self.stdout.write('\n✍️  FASE 3: Criando artigos com Claude...')
            claude_creator = ClaudeArticleCreator()
            
            for i, news_item in enumerate(selected_news, 1):
                self.stdout.write(f'\n  [{i}/{len(selected_news)}] Processando: {news_item["title"][:50]}...')
                
                try:
                    # 3.1 Criar artigo
                    article_data = claude_creator.create_article(news_item)
                    
                    # 3.2 Buscar imagem
                    self.stdout.write('    🖼️  Buscando imagem...')
                    image_service = UnsplashImageService()
                    image_data = image_service.search_image(article_data['tags'])
                    
                    image_url = None
                    if image_data:
                        # Download e upload
                        image_bytes = image_service.download_image(image_data)
                        if image_bytes:
                            storage = SupabaseStorageService()
                            image_url = storage.upload_image(image_bytes)
                            self.stdout.write(self.style.SUCCESS('    ✓ Imagem adicionada'))
                    
                    # 3.3 Determinar categoria
                    category = self._get_or_create_category(
                        news_item.get('suggested_category', 'Geral')
                    )
                    
                    # 3.4 Salvar no banco
                    if not dry_run:
                        post = NewsPost.objects.create(
                            title=article_data['title'],
                            content=article_data['content'],
                            excerpt=article_data['excerpt'],
                            meta_description=article_data['meta_description'],
                            tags=article_data['tags'],
                            
                            category=category,
                            featured_image=image_url or '',
                            featured_image_alt=image_data.get('alt_description', '') if image_data else '',
                            
                            source_url=news_item['link'],
                            source_name=news_item['source_name'],
                            
                            ai_generated=True,
                            ai_model_primary='claude-3-5-sonnet',
                            ai_model_secondary='gemini-pro',
                            
                            status='pending',  # Aguardando moderação
                        )
                        
                        self.stdout.write(self.style.SUCCESS(f'    ✓ Post salvo (ID: {post.id})'))
                    else:
                        self.stdout.write(self.style.WARNING('    ○ [DRY RUN] Post não salvo'))
                    
                    # Pausa para não sobrecarregar APIs
                    time.sleep(2)
                    
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'    ✗ Erro: {str(e)}'))
                    logger.error(f"Error processing news {i}: {str(e)}")
                    continue
            
            # RESUMO
            elapsed = time.time() - start_time
            self.stdout.write(self.style.SUCCESS(f'\n\n✅ Processo concluído em {elapsed:.1f}s'))
            
            if not dry_run:
                pending_count = NewsPost.objects.filter(status='pending').count()
                self.stdout.write(f'📊 {pending_count} posts aguardando moderação')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n❌ Erro geral: {str(e)}'))
            logger.error(f"Fatal error: {str(e)}")
    
    def _get_or_create_category(self, name: str):
        """Obtém ou cria categoria"""
        from django.utils.text import slugify
        category, _ = NewsCategory.objects.get_or_create(
            slug=slugify(name),
            defaults={'name': name}
        )
        return category
```

2. **Testar comando**

```bash
# Teste sem salvar
python manage.py generate_news_posts --limit 3 --dry-run

# Geração real
python manage.py generate_news_posts --limit 5
```

**Commit:** `feat(news): implementa comando de geração automática`

---

### FASE 7: Automação com Celery (1-2 dias)

**Objetivo:** Automatizar execução diária

#### Tarefas:

1. **Configurar Celery**

```python
# cgbookstore/celery.py

from celery import Celery
from celery.schedules import crontab
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')

app = Celery('cgbookstore')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Configurar schedule
app.conf.beat_schedule = {
    'generate-daily-news': {
        'task': 'news.tasks.generate_daily_news',
        'schedule': crontab(hour=6, minute=0),  # Todo dia às 6h
        'kwargs': {'limit': 10},
    },
}
```

2. **Criar tasks**

```python
# news/tasks.py

from celery import shared_task
from django.core.management import call_command
import logging

logger = logging.getLogger(__name__)

@shared_task
def generate_daily_news(limit=10):
    """
    Task para gerar notícias diariamente
    """
    try:
        logger.info(f"Starting daily news generation (limit={limit})")
        
        call_command('generate_news_posts', limit=limit, hours_back=24)
        
        logger.info("Daily news generation completed")
        
    except Exception as e:
        logger.error(f"Error in daily news generation: {str(e)}")
        raise
```

3. **Configurar no settings**

```python
# cgbookstore/settings.py

# Celery
CELERY_BROKER_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'America/Sao_Paulo'
```

4. **Comandos para rodar Celery**

```bash
# Worker
celery -A cgbookstore worker -l info

# Beat (scheduler)
celery -A cgbookstore beat -l info

# Ou ambos juntos
celery -A cgbookstore worker --beat -l info
```

**Commit:** `feat(news): adiciona automação com Celery`

---

### FASE 8: Interface Admin e Moderação (1 dia)

**Objetivo:** Melhorar interface admin para moderação

#### Tarefas:

1. **Admin avançado**

```python
# news/admin.py

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import NewsPost, NewsCategory, NewsSource

@admin.register(NewsPost)
class NewsPostAdmin(admin.ModelAdmin):
    list_display = [
        'title_link',
        'category',
        'status_badge',
        'ai_badge',
        'views_count',
        'published_at',
        'actions_column',
    ]
    list_filter = [
        'status',
        'category',
        'ai_generated',
        'published_at',
    ]
    search_fields = ['title', 'content', 'tags']
    prepopulated_fields = {'slug': ('title',)}
    
    fieldsets = (
        ('Conteúdo', {
            'fields': ('title', 'slug', 'category', 'excerpt', 'content')
        }),
        ('Mídia', {
            'fields': ('featured_image', 'featured_image_alt')
        }),
        ('Fonte', {
            'fields': ('source_url', 'source_name')
        }),
        ('SEO', {
            'fields': ('tags', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('Metadados IA', {
            'fields': (
                'ai_generated',
                'ai_model_primary',
                'ai_model_secondary',
                'ai_processing_time'
            ),
            'classes': ('collapse',)
        }),
        ('Publicação', {
            'fields': ('status', 'author', 'published_at')
        }),
    )
    
    def title_link(self, obj):
        url = reverse('admin:news_newspost_change', args=[obj.id])
        return format_html('<a href="{}">{}</a>', url, obj.title[:60])
    title_link.short_description = 'Título'
    
    def status_badge(self, obj):
        colors = {
            'draft': 'gray',
            'pending': 'orange',
            'published': 'green',
            'rejected': 'red',
        }
        return format_html(
            '<span style="color: {};">●</span> {}',
            colors.get(obj.status, 'gray'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def ai_badge(self, obj):
        if obj.ai_generated:
            return format_html('🤖 IA')
        return '✍️ Manual'
    ai_badge.short_description = 'Origem'
    
    def actions_column(self, obj):
        if obj.status == 'pending':
            approve_url = reverse('admin:news_newspost_approve', args=[obj.id])
            reject_url = reverse('admin:news_newspost_reject', args=[obj.id])
            return format_html(
                '<a class="button" href="{}">✓ Aprovar</a> '
                '<a class="button" href="{}">✗ Rejeitar</a>',
                approve_url,
                reject_url
            )
        return '-'
    actions_column.short_description = 'Ações'
    
    actions = ['approve_posts', 'reject_posts', 'publish_posts']
    
    def approve_posts(self, request, queryset):
        updated = queryset.filter(status='pending').update(status='published')
        self.message_user(request, f'{updated} posts aprovados')
    approve_posts.short_description = 'Aprovar posts selecionados'
    
    def reject_posts(self, request, queryset):
        updated = queryset.filter(status='pending').update(status='rejected')
        self.message_user(request, f'{updated} posts rejeitados')
    reject_posts.short_description = 'Rejeitar posts selecionados'

@admin.register(NewsCategory)
class NewsCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'posts_count', 'is_active', 'order']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['order', 'is_active']
    
    def posts_count(self, obj):
        return obj.posts.filter(status='published').count()
    posts_count.short_description = 'Posts publicados'

@admin.register(NewsSource)
class NewsSourceAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'source_type',
        'is_active',
        'priority',
        'success_rate',
        'last_fetch_at',
    ]
    list_filter = ['is_active', 'source_type']
    list_editable = ['is_active', 'priority']
    
    def success_rate(self, obj):
        if obj.total_items_fetched == 0:
            return '-'
        rate = (obj.total_items_published / obj.total_items_fetched) * 100
        return f'{rate:.1f}%'
    success_rate.short_description = 'Taxa de sucesso'
```

**Commit:** `feat(news): melhora interface admin`

---

## 📊 WORKFLOW DE AUTOMAÇÃO

### Fluxo Diário Automático

```
06:00 - Celery Beat dispara task
│
├─> 06:00-06:02: Buscar feeds RSS (Google News + fontes)
│   └─> Coletar 50-100 notícias das últimas 24h
│
├─> 06:02-06:05: Filtrar com Gemini
│   └─> Selecionar top 10 mais relevantes
│   └─> Criar resumos executivos
│
├─> 06:05-06:20: Criar artigos com Claude (10x)
│   ├─> Para cada notícia:
│   │   ├─> Gerar artigo completo (800-1200 palavras)
│   │   ├─> Buscar imagem (Unsplash)
│   │   ├─> Upload imagem (Supabase)
│   │   └─> Salvar como 'pending'
│   └─> Pausa de 2s entre cada
│
└─> 06:20: Notificar admin
    └─> Email/Slack: "10 posts aguardam moderação"
```

### Fluxo Manual de Moderação

```
Admin acessa /admin/news/newspost/
│
├─> Filtrar: status='pending'
│
├─> Para cada post:
│   ├─> Ler título e excerpt
│   ├─> Revisar conteúdo
│   ├─> (Opcional) Editar
│   ├─> Verificar imagem
│   └─> Decisão:
│       ├─> Aprovar → status='published'
│       ├─> Rejeitar → status='rejected'
│       └─> Deixar draft → status='draft'
│
└─> Posts aprovados aparecem no blog
```

---

## 💰 CUSTOS E RECURSOS

### Breakdown de Custos

| Recurso | Plano | Limite | Custo/mês |
|---------|-------|--------|-----------|
| **Claude API** | Pro (existente) | Incluído no plano | R$ 0* |
| **Gemini Pro** | Free | 60 req/min, 1500/dia | R$ 0 |
| **Google News RSS** | - | Ilimitado | R$ 0 |
| **Unsplash API** | Free | 50 req/hora | R$ 0 |
| **Supabase Storage** | Free | 1GB storage | R$ 0 |
| **Redis** | Free/Self-hosted | - | R$ 0 |
| **TOTAL** | | | **R$ 0** |

*Já incluído no plano pago existente

### Consumo Estimado (30 posts/mês)

- **Gemini:** ~3 chamadas/dia × 30 dias = 90 chamadas/mês ✅
- **Claude:** ~10 chamadas/dia × 30 dias = 300 chamadas/mês ✅
- **Unsplash:** ~10 imagens/dia × 30 dias = 300 imagens/mês ✅

**Todos dentro dos limites gratuitos!**

---

## 🗓️ ROADMAP DE DESENVOLVIMENTO

### Sprint 1 (Semana 1-2) - MVP

- [ ] Fase 1: Estrutura base
- [ ] Fase 2: Agregação RSS
- [ ] Fase 3: Integração Gemini
- [ ] Teste manual do fluxo completo

### Sprint 2 (Semana 3-4) - Automação

- [ ] Fase 4: Integração Claude
- [ ] Fase 5: Busca de imagens
- [ ] Fase 6: Management command
- [ ] Deploy inicial

### Sprint 3 (Semana 5-6) - Produção

- [ ] Fase 7: Celery automação
- [ ] Fase 8: Interface admin
- [ ] Testes de carga
- [ ] Documentação final

### Melhorias Futuras (Backlog)

- [ ] Sistema de agendamento de publicações
- [ ] Analytics de performance de posts
- [ ] A/B testing de títulos
- [ ] Integração com redes sociais (auto-post)
- [ ] Newsletter automática
- [ ] Recomendação de livros relacionados
- [ ] Comentários e engajamento
- [ ] API pública do blog

---

## 🔧 MANUTENÇÃO E MONITORAMENTO

### Métricas a Acompanhar

1. **Performance de Agregação**
   - Número de notícias coletadas/dia
   - Taxa de sucesso por fonte RSS
   - Tempo médio de coleta

2. **Qualidade da IA**
   - Taxa de aprovação de posts (pending → published)
   - Taxa de rejeição
   - Tempo médio de moderação

3. **Performance de Publicação**
   - Posts publicados/semana
   - Visualizações por post
   - Taxa de engajamento

4. **Custos de API**
   - Chamadas Claude/mês (monitor dentro do limite)
   - Chamadas Gemini/mês
   - Downloads Unsplash/mês
   - Storage Supabase usado

### Logs Importantes

```python
# Configurar logging detalhado
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file_news': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/news_generation.log',
        },
    },
    'loggers': {
        'news': {
            'handlers': ['file_news'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

### Alertas Recomendados

- ⚠️ Taxa de erro > 20% na agregação
- ⚠️ Nenhum post gerado por 24h
- ⚠️ Fila de moderação > 50 posts
- ⚠️ Erros 500 nas APIs
- ⚠️ Storage > 80% do limite

---

## 📞 CONTATOS E REFERÊNCIAS

### Documentações

- **Claude API:** https://docs.anthropic.com/
- **Gemini API:** https://ai.google.dev/docs
- **Unsplash API:** https://unsplash.com/documentation
- **Feedparser:** https://feedparser.readthedocs.io/
- **Celery:** https://docs.celeryproject.org/

### Fontes RSS Literárias

- Google News Literatura: `https://news.google.com/rss/search?q=literatura`
- PublishNews: `https://publishnews.com.br/feed`
- (Adicionar mais conforme descobrir)

---

## 📝 NOTAS FINAIS

### Pontos de Atenção

1. **Moderação é essencial** - Mesmo com IA, revisar antes de publicar
2. **Citação de fontes** - Sempre incluir link para notícia original
3. **Originalidade** - IA deve reescrever, não copiar
4. **SEO** - Focar em conteúdo de qualidade, não apenas quantidade
5. **Escalabilidade** - Começar com 10 posts/dia, ajustar conforme necessário

### Próximos Passos Imediatos

1. ✅ Aprovar este planejamento
2. ⏭️ Iniciar Fase 1 (estrutura base)
3. ⏭️ Configurar APIs (Gemini, Unsplash)
4. ⏭️ Testar fluxo manualmente
5. ⏭️ Implementar automação

---

**Documento gerado em:** 18/12/2024  
**Última atualização:** 18/12/2024  
**Versão:** 1.0  
**Status:** 📋 Planejamento aprovado, aguardando implementação

---

