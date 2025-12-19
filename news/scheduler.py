"""
News Agent Scheduler
Agendador nativo Django usando APScheduler.
Executa automaticamente com base nas configurações do admin.
"""

import logging
from datetime import datetime
from django.utils import timezone
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)

# Scheduler global
_scheduler = None


def run_news_agent():
    """Executa o agente de notícias."""
    from django.core.management import call_command
    from news.models import NewsAgentConfig
    
    try:
        config = NewsAgentConfig.get_active()
        
        # Verificar se modo automático está ativo
        if config.mode != 'automatic':
            logger.info(f"Agente em modo {config.mode} - não executando automaticamente")
            return
        
        logger.info(f"🤖 Iniciando execução automática do Agente de Notícias...")
        
        # Executar comando
        call_command(
            'generate_news_posts',
            limit=config.articles_per_run,
            skip_images=not config.include_images,
        )
        
        # Atualizar estatísticas
        from news.models import Article
        recent_count = Article.objects.filter(
            ai_generated=True,
            created_at__gte=timezone.now() - timezone.timedelta(minutes=5)
        ).count()
        
        config.last_run = timezone.now()
        config.last_run_articles = recent_count
        config.total_articles_generated += recent_count
        config.save()
        
        logger.info(f"✅ Agente executado! {recent_count} artigos criados.")
        
    except Exception as e:
        logger.error(f"❌ Erro ao executar agente: {e}")


def get_trigger_from_config(config):
    """Cria trigger APScheduler baseado na configuração."""
    
    schedule = config.schedule
    hour = config.schedule_hour
    minute = config.schedule_minute
    
    if schedule == 'hourly':
        # Roda todo minuto configurado de cada hora
        return CronTrigger(minute=minute)
    
    elif schedule == 'every_6h':
        # Roda a cada 6 horas (0, 6, 12, 18)
        return CronTrigger(hour='0,6,12,18', minute=minute)
    
    elif schedule == 'every_12h':
        # Roda a cada 12 horas (hora configurada e +12)
        return CronTrigger(hour=f"{hour},{(hour+12) % 24}", minute=minute)
    
    elif schedule == 'daily':
        return CronTrigger(hour=hour, minute=minute)
    
    elif schedule == 'twice_daily':
        # Roda no horário configurado e 12h depois
        return CronTrigger(hour=f"{hour},{(hour+12) % 24}", minute=minute)
    
    elif schedule == 'weekly':
        return CronTrigger(day_of_week='mon', hour=hour, minute=minute)
    
    else:
        return CronTrigger(hour=hour, minute=minute)


def start_scheduler():
    """Inicia o scheduler."""
    global _scheduler
    
    if _scheduler is not None:
        logger.info("Scheduler já está rodando")
        return
    
    try:
        from news.models import NewsAgentConfig
        config = NewsAgentConfig.get_active()
        
        if config.mode != 'automatic':
            logger.info(f"📋 Agente em modo {config.mode} - scheduler não iniciado")
            return
        
        _scheduler = BackgroundScheduler()
        
        trigger = get_trigger_from_config(config)
        
        _scheduler.add_job(
            run_news_agent,
            trigger=trigger,
            id='news_agent_job',
            name='News Agent Scheduled Job',
            replace_existing=True
        )
        
        _scheduler.start()
        
        logger.info(f"🚀 Scheduler iniciado! Próxima execução configurada.")
        logger.info(f"   📅 Frequência: {config.get_schedule_display()}")
        logger.info(f"   🕐 Horário: {config.schedule_hour:02d}:{config.schedule_minute:02d}")
        
    except Exception as e:
        logger.error(f"Erro ao iniciar scheduler: {e}")


def stop_scheduler():
    """Para o scheduler."""
    global _scheduler
    
    if _scheduler is not None:
        _scheduler.shutdown()
        _scheduler = None
        logger.info("Scheduler parado")


def restart_scheduler():
    """Reinicia o scheduler (usado quando configuração muda)."""
    stop_scheduler()
    start_scheduler()
