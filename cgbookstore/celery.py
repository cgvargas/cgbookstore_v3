"""
Configuração do Celery para tarefas assíncronas.
"""

import os
import platform
from celery import Celery
from celery.schedules import crontab

# Ajuste de segurança para execução no Windows (evita conflitos de fork/processos)
if platform.system() == 'Windows':
    os.environ.setdefault('FORKED_BY_MULTIPROCESSING', '1')

# Define o settings module do Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')

# Cria instância do Celery
app = Celery('cgbookstore')

# Carrega configuração do settings.py
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-descoberta de tasks em todos os apps
app.autodiscover_tasks()

# Configuração de tarefas periódicas (Beat)
app.conf.beat_schedule = {
    # Cache: limpar cache a cada 6 horas
    'clear-expired-cache': {
        'task': 'core.tasks.clear_expired_cache',
        'schedule': crontab(minute=0, hour='*/6'),
    },

    # Recomendações: calcular similaridades diariamente às 3h
    # ATUALIZA matriz de similaridade entre livros (TF-IDF + Cosine Similarity)
    'compute-book-similarities': {
        'task': 'recommendations.tasks.compute_book_similarities',
        'schedule': crontab(minute=0, hour=3),  # Todos os dias às 3h da manhã
    },

    # Recomendações: gerar recomendações para todos os usuários a cada hora
    'batch-generate-recommendations': {
        'task': 'recommendations.tasks.batch_generate_recommendations',
        'schedule': crontab(minute=0),  # A cada hora
    },

    # Recomendações: limpar recomendações expiradas diariamente às 4h
    'cleanup-expired-recommendations': {
        'task': 'recommendations.tasks.cleanup_expired_recommendations',
        'schedule': crontab(minute=0, hour=4),
    },

    # Recomendações: pré-calcular livros em alta a cada 6 horas
    'precompute-trending-books': {
        'task': 'recommendations.tasks.precompute_trending_books',
        'schedule': crontab(minute=0, hour='*/6'),
    },
}

@app.task(bind=True)
def debug_task(self):
    """Task de debug."""
    print(f'Request: {self.request!r}')
