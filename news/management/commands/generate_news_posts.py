"""
Generate News Posts Command
Comando principal que orquestra todo o fluxo de geração automática de notícias.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify
from django.core.files.base import ContentFile
from news.models import Article, Category, Tag, NewsSource
from news.services.rss_aggregator import RSSAggregator
from news.services.gemini_service import GeminiNewsService
from news.services.image_service import UnsplashImageService
from news.services.storage_service import StorageService, LocalImageSaver
import logging
import time
import os

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Gera posts de notícias automaticamente usando IA (Gemini + RSS + Unsplash)'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=5,
            help='Número de posts a gerar (padrão: 5)'
        )
        parser.add_argument(
            '--hours-back',
            type=int,
            default=24,
            help='Buscar notícias das últimas X horas (padrão: 24)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simular sem salvar no banco'
        )
        parser.add_argument(
            '--skip-images',
            action='store_true',
            help='Pular busca de imagens (mais rápido)'
        )
        parser.add_argument(
            '--category',
            type=str,
            default='',
            help='Categoria específica para os posts (slug)'
        )
    
    def handle(self, *args, **options):
        limit = options['limit']
        hours_back = options['hours_back']
        dry_run = options['dry_run']
        skip_images = options['skip_images']
        category_slug = options['category']
        
        self.stdout.write('')
        self.stdout.write(self.style.NOTICE('=' * 60))
        self.stdout.write(self.style.NOTICE('🤖 GERADOR AUTOMÁTICO DE NOTÍCIAS - CGBookStore'))
        self.stdout.write(self.style.NOTICE('=' * 60))
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\n⚠️  MODO DRY-RUN: Nada será salvo no banco\n'))
        
        start_time = time.time()
        stats = {'collected': 0, 'filtered': 0, 'created': 0, 'errors': 0}
        
        try:
            # ═══════════════════════════════════════════════════════════
            # FASE 1: AGREGAÇÃO RSS
            # ═══════════════════════════════════════════════════════════
            self.stdout.write(self.style.NOTICE('\n📡 FASE 1: Agregando notícias de RSS feeds...'))
            
            aggregator = RSSAggregator()
            raw_news = aggregator.fetch_all_feeds(hours_back=hours_back)
            stats['collected'] = len(raw_news)
            
            if not raw_news:
                self.stdout.write(self.style.WARNING('  ⚠️ Nenhuma notícia encontrada'))
                return
            
            self.stdout.write(self.style.SUCCESS(f'  ✓ {len(raw_news)} notícias coletadas'))
            
            # ═══════════════════════════════════════════════════════════
            # FASE 2: FILTRAGEM COM GEMINI
            # ═══════════════════════════════════════════════════════════
            self.stdout.write(self.style.NOTICE('\n🔍 FASE 2: Filtrando com Gemini AI...'))
            
            gemini_service = GeminiNewsService()
            
            if not gemini_service.is_available():
                self.stdout.write(self.style.WARNING('  ⚠️ Gemini não disponível, usando filtro simples'))
            
            selected_news = gemini_service.filter_and_rank_news(raw_news, limit=limit)
            stats['filtered'] = len(selected_news)
            
            self.stdout.write(self.style.SUCCESS(f'  ✓ {len(selected_news)} notícias selecionadas'))
            
            # ═══════════════════════════════════════════════════════════
            # FASE 3: CRIAR ARTIGOS
            # ═══════════════════════════════════════════════════════════
            self.stdout.write(self.style.NOTICE('\n✍️  FASE 3: Criando artigos com Gemini AI...'))
            
            # Serviços de imagem
            image_service = UnsplashImageService() if not skip_images else None
            storage_service = LocalImageSaver()  # Usar storage local para simplicidade
            
            # Categoria padrão
            default_category = self._get_or_create_category(category_slug or 'noticias')
            
            for i, news_item in enumerate(selected_news, 1):
                self.stdout.write(f'\n  [{i}/{len(selected_news)}] Processando...')
                self.stdout.write(f'      📰 {news_item["title"][:60]}...')
                
                try:
                    # 3.0 Verificar duplicatas (por URL fonte ou título similar)
                    source_url = news_item.get('link', '')
                    if source_url and Article.objects.filter(source_url=source_url).exists():
                        self.stdout.write(self.style.WARNING('      ⏭️ DUPLICADO: URL fonte já existe'))
                        continue
                    
                    # Verificar título similar (dos últimos 7 dias)
                    news_title = news_item.get('title', '').lower()
                    recent_date = timezone.now() - timezone.timedelta(days=7)
                    recent_articles = Article.objects.filter(created_at__gte=recent_date).values_list('title', flat=True)
                    
                    is_duplicate = False
                    for existing_title in recent_articles:
                        similarity = self._calculate_similarity(news_title, existing_title.lower())
                        if similarity > 0.7:  # 70% similar = duplicado
                            self.stdout.write(self.style.WARNING(f'      ⏭️ DUPLICADO: Título similar ({similarity:.0%})'))
                            is_duplicate = True
                            break
                    
                    if is_duplicate:
                        continue
                    
                    # 3.1 Criar artigo com IA
                    article_data = gemini_service.create_article(news_item)
                    
                    # 3.2 Buscar imagem (opcional)
                    image_content = None
                    image_caption = ''
                    image_filename = 'image.jpg'
                    
                    if image_service and image_service.is_available():
                        self.stdout.write('      🖼️  Buscando imagem...')
                        
                        # Usar tags sugeridas para buscar imagem
                        keywords = article_data.get('tags', ['books', 'reading'])
                        image_data = image_service.search_image(
                            keywords,
                            fallback_keywords=['literatura', 'livros', 'biblioteca']
                        )
                        
                        if image_data:
                            # Download da imagem
                            image_bytes = image_service.download_image(image_data)
                            if image_bytes:
                                image_content = image_bytes
                                image_caption = image_service.get_attribution(image_data)
                                image_filename = f"{image_data.get('id', 'img')}.jpg"
                                self.stdout.write(self.style.SUCCESS('      ✓ Imagem baixada'))
                    
                    # 3.3 Determinar categoria
                    suggested_category = news_item.get('suggested_category', 'Geral')
                    category = self._get_or_create_category(
                        slugify(suggested_category)
                    ) or default_category
                    
                    # 3.4 Salvar no banco
                    if not dry_run:
                        tags_objects = self._get_or_create_tags(article_data.get('tags', []))
                        
                        # Truncar título com segurança
                        raw_title = article_data.get('title', 'Sem título')[:195]
                        
                        # Gerar slug único
                        base_slug = slugify(raw_title)
                        slug = self._generate_unique_slug(base_slug)
                        
                        # Criar artigo
                        article = Article.objects.create(
                            title=raw_title,
                            slug=slug,
                            subtitle=(article_data.get('excerpt', '') or '')[:295],
                            content_type='news',
                            excerpt=(article_data.get('excerpt', '') or '')[:495],
                            content=article_data.get('content', '') or '',
                            category=category,
                            
                            # Campos de IA
                            ai_generated=True,
                            ai_model=article_data.get('ai_model', 'groq-llama-3.3')[:50],
                            ai_processing_time=article_data.get('processing_time'),
                            source_url=(news_item.get('link', '') or '')[:200],
                            source_name=(news_item.get('source_name', '') or '')[:100],
                            meta_description=(article_data.get('meta_description', '') or '')[:160],
                            
                            # Imagem com legenda
                            image_caption=image_caption[:200] if image_caption else '',
                            
                            # Status
                            is_published=False,  # Aguardando moderação
                            priority=2,
                        )
                        
                        # Salvar imagem no campo featured_image
                        if image_content:
                            article.featured_image.save(
                                image_filename,
                                ContentFile(image_content),
                                save=True
                            )
                            self.stdout.write(self.style.SUCCESS('      ✓ Imagem anexada ao artigo'))
                        
                        # Adicionar tags
                        if tags_objects:
                            article.tags.set(tags_objects)
                        
                        stats['created'] += 1
                        self.stdout.write(self.style.SUCCESS(f'      ✓ Artigo salvo (ID: {article.id})'))
                    else:
                        stats['created'] += 1
                        self.stdout.write(self.style.WARNING('      ○ [DRY RUN] Artigo não salvo'))
                    
                    # Pausa entre requisições para não sobrecarregar APIs
                    time.sleep(2)
                    
                except Exception as e:
                    stats['errors'] += 1
                    self.stdout.write(self.style.ERROR(f'      ✗ Erro: {str(e)}'))
                    logger.error(f"Erro ao processar notícia {i}: {str(e)}", exc_info=True)
                    continue
            
            # ═══════════════════════════════════════════════════════════
            # RESUMO FINAL
            # ═══════════════════════════════════════════════════════════
            elapsed = time.time() - start_time
            
            self.stdout.write('')
            self.stdout.write(self.style.NOTICE('=' * 60))
            self.stdout.write(self.style.SUCCESS(f'✅ PROCESSO CONCLUÍDO em {elapsed:.1f}s'))
            self.stdout.write(self.style.NOTICE('=' * 60))
            self.stdout.write(f"  📡 Notícias coletadas: {stats['collected']}")
            self.stdout.write(f"  🔍 Notícias filtradas: {stats['filtered']}")
            self.stdout.write(f"  ✍️  Artigos criados: {stats['created']}")
            if stats['errors']:
                self.stdout.write(self.style.ERROR(f"  ❌ Erros: {stats['errors']}"))
            
            if not dry_run:
                pending = Article.objects.filter(is_published=False, ai_generated=True).count()
                self.stdout.write('')
                self.stdout.write(self.style.NOTICE(f'📋 {pending} artigos aguardando moderação'))
                self.stdout.write(self.style.NOTICE('   Acesse /admin/news/article/?ai_generated=1'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n❌ Erro fatal: {str(e)}'))
            logger.error(f"Erro fatal na geração: {str(e)}", exc_info=True)
    
    def _get_or_create_category(self, slug: str):
        """Obtém ou cria categoria pelo slug."""
        if not slug:
            return None
        
        # Mapeamento de nomes amigáveis
        name_map = {
            'noticias': 'Notícias',
            'lancamentos': 'Lançamentos',
            'autores': 'Autores',
            'mercado-editorial': 'Mercado Editorial',
            'premios': 'Prêmios',
            'eventos': 'Eventos',
            'adaptacoes': 'Adaptações',
            'geral': 'Geral',
        }
        
        name = name_map.get(slug, slug.replace('-', ' ').title())
        
        category, created = Category.objects.get_or_create(
            slug=slug,
            defaults={
                'name': name,
                'is_active': True,
            }
        )
        
        if created:
            logger.info(f"Categoria criada: {name}")
        
        return category
    
    def _get_or_create_tags(self, tag_names: list):
        """Obtém ou cria tags pelos nomes."""
        tags = []
        for name in tag_names[:10]:  # Limitar a 10 tags
            if not name:
                continue
            slug = slugify(name)
            if not slug:
                continue
            
            tag, _ = Tag.objects.get_or_create(
                slug=slug,
                defaults={'name': name[:50]}
            )
            tags.append(tag)
        
        return tags
    
    def _generate_unique_slug(self, base_slug: str) -> str:
        """Gera slug único adicionando sufixo se necessário."""
        slug = base_slug[:190]  # Deixar espaço para sufixo
        
        if not Article.objects.filter(slug=slug).exists():
            return slug
        
        # Adicionar sufixo numérico
        counter = 1
        while True:
            new_slug = f"{slug}-{counter}"
            if not Article.objects.filter(slug=new_slug).exists():
                return new_slug
            counter += 1
            if counter > 100:  # Segurança
                import uuid
                return f"{slug}-{uuid.uuid4().hex[:8]}"
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calcula similaridade entre dois textos usando Jaccard.
        Retorna valor entre 0 (diferentes) e 1 (iguais).
        """
        # Remover pontuação e normalizar
        import re
        clean1 = re.sub(r'[^\w\s]', '', text1.lower())
        clean2 = re.sub(r'[^\w\s]', '', text2.lower())
        
        # Dividir em palavras (ignorando palavras muito curtas)
        words1 = set(w for w in clean1.split() if len(w) > 2)
        words2 = set(w for w in clean2.split() if len(w) > 2)
        
        if not words1 or not words2:
            return 0.0
        
        # Calcular similaridade de Jaccard
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0
