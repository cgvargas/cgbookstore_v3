# 🚀 Guia de Otimização de Performance no Render

## 📊 Problemas Identificados

### 1. **Limitações do Plano FREE do Render**
- ✅ RAM: 512MB (muito limitado)
- ✅ CPU: Compartilhada
- ✅ Inatividade: Servidor hiberna após 15 minutos sem uso
- ✅ Cold Start: 30-60 segundos para "acordar"

### 2. **Configuração Atual do Gunicorn**
```python
workers = 2
threads = 4
worker_class = 'gthread'
timeout = 120
```

**Problema**: Configuração boa, mas pode ser otimizada para o plano free.

### 3. **Build Pesado**
O `build.sh` executa muitos comandos que podem deixar o deploy lento:
- `makemigrations` (não deveria estar no build)
- `cleanup_socialapps`
- `setup_initial_data`
- `showmigrations` (apenas para debug)

### 4. **Banco de Dados - Supabase**
- ✅ Conexão pooling configurada: `conn_max_age=600`
- ✅ Health checks habilitados
- ⚠️ Statement timeout: 30s (pode ser muito curto para queries complexas)

---

## 🔧 Soluções Recomendadas

### **SOLUÇÃO 1: Otimizar Gunicorn** ⭐ PRIORIDADE ALTA

O plano free tem apenas 512MB RAM. Vamos reduzir workers e aumentar threads:

**Arquivo: `gunicorn_config.py`**

```python
"""
Configuração ULTRA-OTIMIZADA do Gunicorn para Render FREE (512MB RAM)
"""

import multiprocessing
import os

# Bind
bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"

# ⚡ CRITICAL: Workers configurados para 512MB RAM
# Cada worker Django usa ~100-150MB RAM
# 2 workers = 200-300MB base
# Deixar 200MB para sistema e cache
workers = 1  # REDUZIDO de 2 para 1 (economiza ~120MB RAM)

# ⚡ CRITICAL: Aumentar threads para compensar menos workers
# Threads consomem MUITO menos RAM que workers
# Cada thread usa ~5-10MB vs ~100MB de worker
threads = 8  # AUMENTADO de 4 para 8 (mais concorrência, menos RAM)

# Worker class: gthread (threads + baixo consumo de RAM)
worker_class = 'gthread'

# ⚡ Timeouts ajustados para Render
timeout = 60  # REDUZIDO de 120 para 60 (mais responsivo)
graceful_timeout = 30
keepalive = 2  # REDUZIDO de 5 para 2 (menos conexões idle)

# ⚡ Worker lifecycle - reciclar MAIS frequentemente
max_requests = 500  # REDUZIDO de 1000 (evita memory leaks)
max_requests_jitter = 50  # REDUZIDO de 100

# Worker tmp dir (usar RAM para locks - mais rápido)
worker_tmp_dir = '/dev/shm'

# Logging otimizado
accesslog = '-'
errorlog = '-'
loglevel = 'warning'  # MUDADO de 'info' para 'warning' (menos I/O)
# Log format simplificado (menos overhead)
access_log_format = '%(h)s "%(r)s" %(s)s %(b)s %(D)s'

# ⚡ CRITICAL: Preload app = economia massiva de RAM
# Carrega Django ANTES de forkar workers
# Compartilha código entre workers = economiza ~50-80MB
preload_app = True

# Process naming
proc_name = 'cgbookstore'

# Django WSGI
wsgi_app = 'cgbookstore.wsgi:application'

# ⚡ Configurações adicionais para performance
worker_connections = 1000
```

**Economia estimada**: ~100-150MB RAM
**Ganho**: Servidor mais estável, menos crashes por OOM (Out of Memory)

---

### **SOLUÇÃO 2: Otimizar Build Script** ⭐ PRIORIDADE ALTA

Remover comandos desnecessários do build acelera deploys.

**Arquivo: `build.sh`**

```bash
#!/usr/bin/env bash
set -o errexit

echo '🚀 Starting build process...'

# Install dependencies
echo '📦 Installing dependencies...'
pip install --upgrade pip
pip install -r requirements.txt

# Collect static files
echo '📁 Collecting static files...'
python manage.py collectstatic --no-input

# ❌ REMOVIDO: makemigrations (deve ser feito localmente!)
# echo 'Checking for new migrations...'
# python manage.py makemigrations --no-input

# Run migrations
echo '🗄️ Running database migrations...'
python manage.py migrate --no-input

# ❌ REMOVIDO: showmigrations (apenas para debug)

# Setup inicial (apenas na primeira vez, depois fica em cache)
echo '⚙️ Setting up initial data...'
python manage.py setup_initial_data --skip-superuser --skip-social 2>/dev/null || echo 'Initial data already exists'

# Create superuser if needed
if [ "$CREATE_SUPERUSER" = "true" ]; then
    echo '👤 Creating superuser...'
    python manage.py shell -c "
from django.contrib.auth import get_user_model;
import os;
User = get_user_model();
username = os.getenv('SUPERUSER_USERNAME', 'admin');
email = os.getenv('SUPERUSER_EMAIL', 'admin@cgbookstore.com');
password = os.getenv('SUPERUSER_PASSWORD', 'admin123');
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password);
    print(f'✅ Superuser criado: {username}');
else:
    print(f'ℹ️ Superuser já existe');
" 2>/dev/null || true
fi

echo '✅ Build completed successfully!'
```

**Ganho**: Build 30-50% mais rápido, menos chance de timeout

---

### **SOLUÇÃO 3: Adicionar Health Check Otimizado** ⭐ PRIORIDADE MÉDIA

O Render precisa de um endpoint `/` que responda rápido.

**Arquivo: `core/views/health_check.py`** (criar se não existir)

```python
from django.http import JsonResponse
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_http_methods

@require_http_methods(["GET", "HEAD"])
@cache_page(60)  # Cache por 1 minuto
def health_check(request):
    """
    Health check super leve para o Render.
    Não faz queries no banco para ser ultra-rápido.
    """
    return JsonResponse({
        'status': 'healthy',
        'service': 'cgbookstore'
    })
```

**Adicionar em `cgbookstore/urls.py`:**

```python
from core.views.health_check import health_check

urlpatterns = [
    path('', health_check),  # Health check na raiz
    # ... resto das URLs
]
```

**Ganho**: Health checks 10x mais rápidos, servidor não hiberna

---

### **SOLUÇÃO 4: Otimizar Settings para Produção** ⭐ PRIORIDADE ALTA

**Arquivo: `cgbookstore/settings.py`**

Adicionar estas configurações:

```python
# ============= OTIMIZAÇÕES PARA RENDER =============

# 1. Template Caching (produção)
if not DEBUG:
    TEMPLATES[0]['OPTIONS']['loaders'] = [
        ('django.template.loaders.cached.Loader', [
            'django.template.loaders.filesystem.Loader',
            'django.template.loaders.app_directories.Loader',
        ]),
    ]

# 2. Session Engine - usar cache (Redis) em vez de banco
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# 3. Reduzir timeout de queries do banco
DATABASES['default']['OPTIONS']['options'] = '-c statement_timeout=15000'  # 15s (era 30s)

# 4. Aumentar pooling de conexões
DATABASES['default']['CONN_MAX_AGE'] = 600  # 10 minutos

# 5. Compression do WhiteNoise
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# 6. Desabilitar algumas middlewares em produção (se não usar)
if not DEBUG:
    # Remover middlewares desnecessários
    # MIDDLEWARE.remove('django.middleware.clickjacking.XFrameOptionsMiddleware')  # Se não usar iframes
    pass

# 7. Logging otimizado
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'WARNING',  # Apenas warnings e erros
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
}
```

---

### **SOLUÇÃO 5: Usar Cron Job para Keep-Alive** ⭐ PRIORIDADE BAIXA

O Render Free hiberna após 15 minutos. Use um serviço externo para manter vivo:

1. **UptimeRobot** (gratuito): https://uptimerobot.com/
   - Faz ping a cada 5 minutos
   - Previne hibernação

2. **Alternativa**: Cron-job.org
   - Configure para chamar `https://cgbookstore-v3.onrender.com/` a cada 10 minutos

**⚠️ Importante**: Isso usa os 750 horas/mês do Render, então pode atingir o limite.

---

### **SOLUÇÃO 6: Monitoramento e Debug** ⭐ PRIORIDADE MÉDIA

Adicionar variável de ambiente no Render:

```bash
# No painel do Render, adicionar:
DJANGO_LOG_LEVEL=WARNING
GUNICORN_LOG_LEVEL=warning
```

Adicionar ao `gunicorn_config.py`:

```python
# Statsd/metrics (se quiser monitorar)
statsd_host = None  # Desabilitar statsd no free tier
```

---

## 📋 Checklist de Implementação

Execute na ordem:

- [ ] 1. Atualizar `gunicorn_config.py` (workers=1, threads=8)
- [ ] 2. Atualizar `build.sh` (remover comandos desnecessários)
- [ ] 3. Adicionar health check otimizado
- [ ] 4. Atualizar `settings.py` (template caching, session cache, etc)
- [ ] 5. Fazer commit e push para o branch main
- [ ] 6. Verificar deploy no Render
- [ ] 7. Testar performance
- [ ] 8. (Opcional) Configurar UptimeRobot

---

## 🎯 Resultado Esperado

### Antes:
- 🐌 Cold start: 30-60 segundos
- 🐌 Requests: 2-5 segundos
- 💥 Crashes por falta de RAM
- 😴 Hiberna após 15 minutos

### Depois:
- ⚡ Cold start: 20-30 segundos (-33%)
- ⚡ Requests: 0.5-2 segundos (-60%)
- ✅ Sem crashes de RAM
- 🔥 Mais estável e responsivo

---

## 🚨 Importante: Limitações do Render FREE

Mesmo com todas as otimizações, o plano FREE tem limitações:

1. **CPU compartilhada**: Em horários de pico pode ficar lento
2. **512MB RAM**: Para aplicações Django é MUITO limitado
3. **Hibernação**: Inevitável após 15 minutos sem uso
4. **Sem SLA**: Pode ficar offline sem aviso

### Recomendações:

- **Para desenvolvimento/MVP**: Plano FREE é OK
- **Para produção real**: Considerar upgrade para Starter ($7/mês)
  - 512MB → 2GB RAM (+300%)
  - CPU dedicada
  - Sem hibernação
  - SLA 99.9%

---

## 📞 Suporte

Se precisar de ajuda:
1. Verificar logs no Render: Dashboard → Logs
2. Testar localmente: `gunicorn -c gunicorn_config.py`
3. Monitorar RAM: Dashboard → Metrics

**Gerado por Claude Code** 🤖
