"""
RSS Aggregator Service
Serviço para agregar notícias de múltiplos feeds RSS/Atom.
"""

import feedparser
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
from django.utils import timezone

logger = logging.getLogger(__name__)


class RSSAggregator:
    """
    Serviço para agregar notícias de múltiplos feeds RSS.
    
    Exemplo de uso:
        aggregator = RSSAggregator()
        news_items = aggregator.fetch_all_feeds(hours_back=24)
    """
    
    def __init__(self):
        self.sources = []
        self.load_active_sources()
    
    def load_active_sources(self):
        """Carrega fontes ativas do banco de dados."""
        from news.models import NewsSource
        self.sources = list(NewsSource.objects.filter(is_active=True))
        logger.info(f"Carregadas {len(self.sources)} fontes ativas")
    
    def fetch_all_feeds(self, hours_back: int = 24) -> List[Dict]:
        """
        Busca notícias de todos os feeds ativos.
        
        Args:
            hours_back: Buscar notícias das últimas X horas
        
        Returns:
            Lista de dicionários com as notícias coletadas
        """
        all_news = []
        cutoff_date = timezone.now() - timedelta(hours=hours_back)
        
        for source in self.sources:
            try:
                news_items = self.fetch_single_feed(source, cutoff_date)
                all_news.extend(news_items)
                
                # Atualizar estatísticas da fonte
                source.last_fetch_at = timezone.now()
                source.last_fetch_status = 'success'
                source.total_items_fetched += len(news_items)
                source.save(update_fields=[
                    'last_fetch_at', 
                    'last_fetch_status', 
                    'total_items_fetched'
                ])
                
                logger.info(f"✓ {source.name}: {len(news_items)} notícias coletadas")
                
            except Exception as e:
                error_msg = str(e)[:50]
                logger.error(f"✗ {source.name}: {error_msg}")
                source.last_fetch_at = timezone.now()
                source.last_fetch_status = f'error: {error_msg}'
                source.save(update_fields=['last_fetch_at', 'last_fetch_status'])
        
        logger.info(f"Total: {len(all_news)} notícias coletadas de {len(self.sources)} fontes")
        return all_news
    
    def fetch_single_feed(self, source, cutoff_date: datetime) -> List[Dict]:
        """
        Busca notícias de um único feed.
        
        Args:
            source: Objeto NewsSource
            cutoff_date: Data de corte para notícias antigas
        
        Returns:
            Lista de dicionários com as notícias
        """
        feed = feedparser.parse(source.url)
        news_items = []
        
        if feed.bozo and not feed.entries:
            raise Exception(f"Feed inválido ou vazio: {feed.bozo_exception}")
        
        for entry in feed.entries:
            # Parse da data
            published_date = self._parse_entry_date(entry)
            
            # Filtrar por data (apenas notícias recentes)
            if published_date and published_date < cutoff_date:
                continue
            
            # Extrair dados do entry
            news_item = {
                'title': self._clean_text(entry.get('title', '')),
                'link': entry.get('link', ''),
                'description': self._clean_text(
                    entry.get('description', entry.get('summary', ''))
                ),
                'published_date': published_date,
                'source_name': source.name,
                'source_url': source.url,
                'source_priority': source.priority,
            }
            
            # Aplicar filtros de palavras-chave
            if self._passes_keyword_filters(news_item, source):
                news_items.append(news_item)
        
        return news_items
    
    def _parse_entry_date(self, entry) -> Optional[datetime]:
        """Parse da data do entry RSS."""
        date_fields = ['published_parsed', 'updated_parsed', 'created_parsed']
        
        for field in date_fields:
            if hasattr(entry, field):
                time_struct = getattr(entry, field)
                if time_struct:
                    try:
                        dt = datetime(*time_struct[:6])
                        # Tornar aware se necessário
                        if timezone.is_naive(dt):
                            dt = timezone.make_aware(dt)
                        return dt
                    except (ValueError, TypeError):
                        continue
        
        # Fallback: usar hora atual
        return timezone.now()
    
    def _clean_text(self, text: str) -> str:
        """Remove HTML tags e limpa o texto."""
        import re
        from html import unescape
        
        # Decodificar entidades HTML
        text = unescape(text)
        
        # Remover tags HTML
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remover múltiplos espaços/quebras de linha
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def _passes_keyword_filters(self, news_item: Dict, source) -> bool:
        """
        Verifica se a notícia passa pelos filtros de palavras-chave.
        
        Returns:
            True se a notícia deve ser incluída, False caso contrário
        """
        text = f"{news_item['title']} {news_item['description']}".lower()
        
        # Filtro de exclusão (prioridade)
        if source.keywords_exclude:
            for keyword in source.keywords_exclude:
                if keyword.lower() in text:
                    logger.debug(f"Excluída por keyword '{keyword}': {news_item['title'][:50]}")
                    return False
        
        # Filtro de inclusão (se configurado)
        if source.keywords_include:
            for keyword in source.keywords_include:
                if keyword.lower() in text:
                    return True
            # Nenhuma palavra-chave de inclusão encontrada
            logger.debug(f"Sem keywords de inclusão: {news_item['title'][:50]}")
            return False
        
        # Se não há filtros de inclusão, aceitar tudo que passou pela exclusão
        return True
