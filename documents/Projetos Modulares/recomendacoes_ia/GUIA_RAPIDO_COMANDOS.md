# 🚀 GUIA RÁPIDO DE COMANDOS - OTIMIZAÇÕES

**Tenha este documento aberto durante a implementação para consulta rápida.**

---

## 📂 **NAVEGAÇÃO**

```powershell
# Ir para o projeto
cd C:\ProjectsDjango\cgbookstore_v3

# Ativar ambiente virtual
.venv\Scripts\activate

# Abrir no VSCode
code .
```

---

## 🔴 **REDIS**

```powershell
# Iniciar Redis
redis-server

# Testar Redis (outro terminal)
redis-cli ping
# Esperado: PONG

# Verificar dados no Redis
redis-cli
> KEYS *
> GET cgbookstore:chave_exemplo
> exit

# Limpar todo o cache
redis-cli FLUSHALL
```

---

## 🐍 **DJANGO**

```powershell
# Rodar servidor
python manage.py runserver

# Verificar configurações
python manage.py check

# Criar migrations
python manage.py makemigrations

# Aplicar migrations
python manage.py migrate

# Shell interativo
python manage.py shell

# Listar migrations
python manage.py showmigrations

# Criar superuser (se necessário)
python manage.py createsuperuser
```

---

## 🔄 **CELERY**

```powershell
# Terminal 1: Worker
celery -A cgbookstore worker -l info --pool=solo

# Terminal 2: Beat (tarefas agendadas)
celery -A cgbookstore beat -l info

# Terminal 3: Monitor (Flower) - OPCIONAL
celery -A cgbookstore flower
# Acesse: http://localhost:5555

# Parar todos os workers
# Ctrl+C em cada terminal

# Limpar tasks pendentes
celery -A cgbookstore purge
```

---

## 📦 **DEPENDÊNCIAS**

```powershell
# Instalar requirements
pip install -r requirements.txt

# Ver dependências instaladas
pip list

# Ver dependências específicas
pip list | grep -E "redis|celery"

# Atualizar pip
python -m pip install --upgrade pip

# Verificar dependências quebradas
pip check
```

---

## 🗄️ **BANCO DE DADOS**

```powershell
# Conectar ao PostgreSQL (via Supabase URL)
# Use a DATABASE_URL do .env

# Shell do Django para queries
python manage.py shell
```

```python
# No shell do Django:
from debates.models import DebateTopic
from django.db import connection

# Ver queries executadas
from django.db import reset_queries
reset_queries()
# ... fazer operações ...
print(len(connection.queries))  # Ver número de queries

# Testar modelo
DebateTopic.objects.all().count()
```

---

## 🧪 **TESTES E VALIDAÇÃO**

```powershell
# Rodar script de performance
python manage.py shell < test_performance.py

# Verificar queries com Debug Toolbar
# Acesse qualquer página com ?debug no final
# Ex: http://127.0.0.1:8000/debates/?debug

# Testar cache manualmente
python manage.py shell
```

```python
from django.core.cache import cache

# Set
cache.set('test', 'valor', timeout=60)

# Get
print(cache.get('test'))

# Delete
cache.delete('test')

# Clear all
cache.clear()
```

```powershell
# Testar Celery task
python manage.py shell
```

```python
from core.tasks import test_async_task

# Executar task
result = test_async_task.delay("Hello!")
print(result.id)
print(result.get(timeout=10))
```

---

## 📊 **MONITORING**

```powershell
# Ver logs do Django
# (aparecem no terminal onde rodou runserver)

# Ver logs do Celery
# (aparecem no terminal do worker)

# Ver logs do Redis
redis-cli
> MONITOR
# (mostra comandos em tempo real)
```

---

## 🔍 **DEBUGGING**

```powershell
# Verificar configurações do Django
python manage.py diffsettings

# Shell do Django com imports automáticos
python manage.py shell_plus  # (se tiver django-extensions)

# Testar imports
python -c "import redis; print(redis.__version__)"
python -c "import celery; print(celery.__version__)"
python -c "import django_ratelimit; print('OK')"
```

---

## 🔄 **GIT**

```powershell
# Status
git status

# Adicionar arquivos
git add .

# Commit
git commit -m "perf: mensagem"

# Ver histórico
git log --oneline

# Criar branch de backup
git checkout -b backup-antes-otimizacoes
git checkout main

# Reverter última mudança
git reset --hard HEAD~1

# Reverter arquivo específico
git checkout HEAD -- caminho/arquivo.py
```

---

## 🚨 **TROUBLESHOOTING**

### **Erro: Redis connection refused**
```powershell
# Verificar se Redis está rodando
redis-cli ping

# Iniciar Redis
redis-server

# Ou via WSL
wsl sudo service redis-server start
```

### **Erro: Port 8000 already in use**
```powershell
# Matar processo na porta 8000
netstat -ano | findstr :8000
taskkill /PID <PID_NUMBER> /F

# Ou usar porta diferente
python manage.py runserver 8001
```

### **Erro: Celery não conecta**
```powershell
# Verificar se Redis está rodando
redis-cli ping

# Verificar URL do Redis no .env
echo $env:REDIS_URL

# Testar conexão manualmente
python -c "import redis; r = redis.from_url('redis://127.0.0.1:6379/0'); print(r.ping())"
```

### **Erro: ModuleNotFoundError**
```powershell
# Ativar ambiente virtual
.venv\Scripts\activate

# Reinstalar requirements
pip install -r requirements.txt

# Verificar se instalou
pip list | grep <module_name>
```

### **Erro: Migration conflito**
```powershell
# Ver status
python manage.py showmigrations

# Aplicar migrations em ordem
python manage.py migrate <app_name> <migration_number>

# Fake migration (se necessário)
python manage.py migrate <app_name> <migration_number> --fake
```

---

## 📝 **VARIÁVEIS DE AMBIENTE (.env)**

```env
# Copie para seu .env:

DEBUG=True
DATABASE_URL=postgresql://user:pass@host:5432/db
SECRET_KEY=your-secret-key

SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key

# NOVAS VARIÁVEIS:
REDIS_URL=redis://127.0.0.1:6379/1
REDIS_CACHE_TIMEOUT=300
```

---

## ⚡ **COMANDOS DE PERFORMANCE**

```powershell
# Medir tempo de resposta
curl -w "\nTempo: %{time_total}s\n" http://127.0.0.1:8000/debates/

# Ver memória usada pelo Python
python manage.py shell
```

```python
import psutil
import os

process = psutil.Process(os.getpid())
print(f"Memória: {process.memory_info().rss / 1024 / 1024:.2f} MB")
```

```powershell
# Verificar uso de disco
du -h .

# Verificar tamanho do banco
# (via Supabase Dashboard ou pgAdmin)
```

---

## 🎯 **COMANDOS MAIS USADOS**

```powershell
# Sequência padrão para iniciar tudo:
cd C:\ProjectsDjango\cgbookstore_v3
.venv\Scripts\activate

# Terminal 1
python manage.py runserver

# Terminal 2 (nova janela)
cd C:\ProjectsDjango\cgbookstore_v3
.venv\Scripts\activate
celery -A cgbookstore worker -l info --pool=solo

# Terminal 3 (nova janela)
cd C:\ProjectsDjango\cgbookstore_v3
.venv\Scripts\activate
celery -A cgbookstore beat -l info
```

---

## 💾 **BACKUP RÁPIDO**

```powershell
# Antes de modificações importantes:
git add .
git commit -m "checkpoint: antes de X"

# Copiar arquivo antes de editar
copy arquivo.py arquivo.py.backup

# Backup de pasta
xcopy /E /I pasta pasta_backup
```

---

## 🔧 **VALIDAÇÃO RÁPIDA**

```powershell
# Testar tudo de uma vez:
python manage.py check &&
redis-cli ping &&
python -c "from django.core.cache import cache; cache.set('x','y'); print(cache.get('x'))" &&
echo "✅ Tudo funcionando!"
```

---

## 📞 **AJUDA RÁPIDA**

- **Django não inicia:** `python manage.py check`
- **Redis não conecta:** `redis-cli ping`
- **Celery não roda:** Verificar REDIS_URL no .env
- **Imports quebrados:** `pip install -r requirements.txt`
- **Port ocupado:** `netstat -ano | findstr :8000`
- **Módulo não encontrado:** `.venv\Scripts\activate`

---

**Mantenha este guia aberto durante toda a implementação!** 📌
