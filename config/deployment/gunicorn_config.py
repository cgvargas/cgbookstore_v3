"""
Configuração OTIMIZADA do Gunicorn para Render STARTER (1GB RAM)

Esta configuração maximiza performance com recursos do Starter:
- 2 workers = melhor concorrência
- 4 threads = balanceado para Django
- Preload app = compartilha código entre workers
- Timeouts ajustados = responsivo
"""

import multiprocessing
import os

# Bind
bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"

# ⚡ STARTER TIER: 2 workers (1GB RAM)
# Cada worker Django usa ~100-150MB RAM
# 2 workers = ~300MB base
# 4 threads cada = ~80MB adicional
# Total: ~380-450MB (deixa ~500MB para sistema, cache, etc)
workers = 2  # STARTER: 2 workers (era 1 no FREE)

# ⚡ Threads por worker
# 4 threads = bom equilíbrio performance/RAM
threads = 4  # STARTER: 4 threads (era 8 no FREE com 1 worker)

# Worker class: gthread (threads + baixo consumo de RAM)
worker_class = 'gthread'

# ⚡ Timeouts ajustados para Render Free
timeout = 60  # OTIMIZADO: 60s ao invés de 120s (mais responsivo)
graceful_timeout = 30
keepalive = 2  # OTIMIZADO: 2s ao invés de 5s (menos conexões idle)

# ⚡ Worker lifecycle - reciclar MAIS frequentemente para evitar leaks
max_requests = 500  # OTIMIZADO: 500 ao invés de 1000
max_requests_jitter = 50  # OTIMIZADO: 50 ao invés de 100

# Worker tmp dir - usar RAM para locks (mais rápido)
worker_tmp_dir = '/dev/shm'

# ⚡ Logging otimizado - menos I/O
accesslog = '-'
errorlog = '-'
loglevel = 'warning'  # OTIMIZADO: warning ao invés de info (menos logs)
# Log format simplificado (menos overhead)
access_log_format = '%(h)s "%(r)s" %(s)s %(b)s %(D)s'

# ⚡ CRITICAL: Preload app = economia massiva de RAM
# Carrega Django ANTES de forkar workers/threads
# Compartilha código = economiza ~50-80MB
preload_app = True

# Process naming
proc_name = 'cgbookstore'

# Django WSGI
wsgi_app = 'cgbookstore.wsgi:application'

# Worker connections
worker_connections = 1000
