"""
News Generation Celery Tasks
Tarefas automatizadas para geração de notícias com IA.
"""

from celery import shared_task
from django.core.management import call_command
import logging
import io

logger = logging.getLogger(__name__)


@shared_task(name='news.generate_daily_news')
def generate_daily_news(limit: int = 5, hours_back: int = 24):
    """
    Task para gerar notícias automaticamente.
    
    Executada diariamente via Celery Beat.
    
    Args:
        limit: Número de artigos a gerar
        hours_back: Buscar notícias das últimas X horas
    """
    logger.info(f"🤖 Iniciando geração automática de {limit} notícias...")
    
    try:
        # Capturar output do comando
        out = io.StringIO()
        
        call_command(
            'generate_news_posts',
            limit=limit,
            hours_back=hours_back,
            stdout=out
        )
        
        output = out.getvalue()
        logger.info(f"✅ Geração concluída:\n{output}")
        
        return {
            'status': 'success',
            'limit': limit,
            'output': output[:1000]  # Limitar tamanho
        }
        
    except Exception as e:
        logger.error(f"❌ Erro na geração automática: {str(e)}", exc_info=True)
        return {
            'status': 'error',
            'error': str(e)
        }


@shared_task(name='news.fetch_rss_news')
def fetch_rss_news():
    """
    Task para apenas buscar notícias RSS (sem processar com IA).
    
    Útil para popular o banco com notícias brutas.
    """
    from news.services.rss_aggregator import RSSAggregator
    
    logger.info("📡 Buscando notícias de feeds RSS...")
    
    try:
        aggregator = RSSAggregator()
        news_items = aggregator.fetch_all_feeds(hours_back=24)
        
        logger.info(f"✅ {len(news_items)} notícias coletadas")
        
        return {
            'status': 'success',
            'count': len(news_items)
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao buscar RSS: {str(e)}")
        return {
            'status': 'error',
            'error': str(e)
        }
