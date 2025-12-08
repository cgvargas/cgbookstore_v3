"""
Configuração ULTRA-OTIMIZADA do Gunicorn para Render FREE (512MB RAM)

Esta configuração maximiza performance com recursos mínimos:
- 1 worker = economia de ~120MB RAM
- 8 threads = alta concorrência com baixo consumo
- Preload app = compartilha código entre threads
- Timeouts reduzidos = mais responsivo
"""

import multiprocessing
import os

# Bind
bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"

# ⚡ CRITICAL: Workers configurados para 512MB RAM
# Cada worker Django usa ~100-150MB RAM
# 1 worker = 100-150MB base
# 8 threads = ~80MB adicional
# Total: ~180-230MB (deixa 300MB para sistema, cache, etc)
workers = 1  # OTIMIZADO: 1 worker ao invés de 2 (economiza ~120MB RAM)

# ⚡ CRITICAL: Threads aumentadas para compensar menos workers
# Threads consomem MUITO menos RAM que workers (~10MB vs ~120MB)
# 8 threads = boa concorrência para Django
threads = 8  # OTIMIZADO: 8 threads ao invés de 4 (2x mais concorrência)

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
