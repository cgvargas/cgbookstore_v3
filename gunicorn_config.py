"""
Configuração otimizada do Gunicorn para Render (Plano Free)

Esta configuração equilibra performance e uso de memória
para aproveitar ao máximo os recursos limitados do plano free.
"""

import multiprocessing
import os

# Bind
bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"

# Workers
# Plano free tem ~512MB RAM
# Fórmula: (2 x $num_cores) + 1
# Mas limitamos a 2 workers para não exceder RAM
workers = 2

# Threads por worker (gthread)
# Permite concorrência sem usar muita RAM
threads = 4

# Worker class
# gthread = threads + menos memória que gevent/eventlet
worker_class = 'gthread'

# Timeouts
timeout = 120  # 2 minutos
graceful_timeout = 30
keepalive = 5

# Worker lifecycle
# Reciclar workers para evitar memory leaks
max_requests = 1000
max_requests_jitter = 100

# Worker tmp dir
# Usar /dev/shm (RAM) em vez de disco para locks
worker_tmp_dir = '/dev/shm'

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Preload app
# Carrega app antes de forkar workers = economia de RAM
preload_app = True

# Process naming
proc_name = 'cgbookstore_gunicorn'

# Django WSGI callable
wsgi_app = 'cgbookstore.wsgi:application'
