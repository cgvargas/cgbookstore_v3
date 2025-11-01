# Redis Setup - CG.BookStore v3

Este documento explica como configurar e usar o Redis para cache de recomendações no projeto.

## 📋 Pré-requisitos

- Docker instalado e rodando
- Python 3.x
- Projeto CG.BookStore v3

## 🚀 Início Rápido

### Windows

```bash
# Iniciar apenas o Redis
start_redis.bat

# Ou iniciar Redis + Django juntos
start_dev.bat
```

### Linux/Mac

```bash
# Dar permissão de execução (primeira vez)
chmod +x start_redis.sh

# Iniciar apenas o Redis
./start_redis.sh

# Ou iniciar Redis + Django juntos
python manage.py runserver
```

## 📦 O que foi configurado?

### 1. Docker Compose (`docker-compose.yml`)

O Redis roda em um container Docker com as seguintes configurações:

- **Imagem**: `redis:7-alpine` (versão leve e otimizada)
- **Porta**: `6379` (padrão do Redis)
- **Persistência**: Dados salvos em volume Docker (`redis_data`)
- **Memória máxima**: 256MB
- **Política de eviction**: `allkeys-lru` (remove chaves menos usadas quando atinge o limite)
- **Healthcheck**: Verifica a cada 10s se o Redis está respondendo

### 2. Scripts de Inicialização

#### `start_redis.bat` (Windows) / `start_redis.sh` (Linux/Mac)

- Verifica se Docker está rodando
- Cria o container Redis se não existir
- Inicia o container se estiver parado
- Testa a conexão com Redis
- Mostra instruções úteis

#### `start_dev.bat` (Windows)

- Inicia o Redis automaticamente
- Aguarda Redis ficar pronto
- Inicia o servidor Django
- Mantém Redis rodando em background

### 3. Configuração Django (`cgbookstore/settings.py`)

```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'IGNORE_EXCEPTIONS': True,  # Fallback se Redis cair
        },
        'KEY_PREFIX': 'cgbookstore',
        'TIMEOUT': 300,  # 5 minutos padrão
    }
}

RECOMMENDATIONS_CONFIG = {
    'CACHE_TIMEOUT': 3600,  # 1 hora para recomendações
    'SIMILARITY_CACHE_TIMEOUT': 86400,  # 24 horas para similaridade
}
```

### 4. Melhorias no Sistema de Recomendações IA

#### Backend (`recommendations/gemini_ai.py`)

**Timeout configurado**: 30 segundos para chamadas da API Gemini
```python
self.request_timeout = 30
response = self.model.generate_content(
    prompt,
    request_options={'timeout': self.request_timeout}
)
```

**Logs detalhados**:
- `[CACHE HIT]` - Quando usa cache (instantâneo)
- `[CACHE MISS]` - Quando consulta API (mais lento)
- Tempo de resposta da API Gemini
- Tempo total de processamento

**Tratamento de erros**:
- TimeoutError específico para timeouts
- Fallback gracioso quando API falha
- Logs detalhados para diagnóstico

#### Frontend (`templates/recommendations/recommendations_section.html`)

**Feedback visual de cache**:
- ⚡ **Cache ativo**: Banner verde quando carrega < 1s (cache)
- 🤖 **IA consultada**: Banner azul quando carrega > 1s (API nova)
- Tempo de carregamento exibido
- Mensagens educativas sobre cache

**Mensagens de loading melhoradas**:
- Explica que primeira vez pode demorar
- Avisa que próximas vezes serão instantâneas
- Sugere verificar Redis se houver erro

## 🔧 Comandos Úteis

### Gerenciar Redis

```bash
# Iniciar Redis
docker start cgbookstore_redis

# Parar Redis
docker stop cgbookstore_redis

# Ver logs do Redis
docker logs -f cgbookstore_redis

# Reiniciar Redis
docker restart cgbookstore_redis

# Remover container (dados preservados no volume)
docker rm cgbookstore_redis

# Remover container E dados
docker-compose down -v
```

### Monitorar Redis

```bash
# Conectar ao Redis CLI
docker exec -it cgbookstore_redis redis-cli

# Ver todas as chaves
redis-cli KEYS "cgbookstore:*"

# Ver informações do Redis
docker exec cgbookstore_redis redis-cli INFO

# Monitorar comandos em tempo real
docker exec -it cgbookstore_redis redis-cli MONITOR

# Ver uso de memória
docker exec cgbookstore_redis redis-cli INFO memory
```

### Debug do Cache no Django

```python
# No Django shell
python manage.py shell

>>> from django.core.cache import cache

# Ver todas as chaves (cuidado em produção!)
>>> cache.keys('*')

# Ver valor de uma chave específica
>>> cache.get('gemini_rec:1:6')

# Limpar todo o cache
>>> cache.clear()

# Limpar cache de um usuário específico
>>> cache.delete('gemini_rec:1:6')

# Testar conexão
>>> cache.set('test', 'hello')
>>> cache.get('test')
'hello'
```

## 📊 Como funciona o Cache?

### Chaves de Cache

O sistema usa as seguintes chaves para cache:

1. **Recomendações Gemini**: `gemini_rec:{user_id}:{n}`
   - Duração: 1 hora
   - Exemplo: `gemini_rec:1:6` (6 recomendações para usuário 1)

2. **Explicações de livros**: `gemini_explain:{user_id}:{book_id}`
   - Duração: 24 horas

3. **Insights de leitura**: `gemini_insights:{user_id}`
   - Duração: 24 horas

4. **Recomendações Híbridas**: `hybrid_rec:{user_id}:*`
   - Invalidado quando usuário interage com livros

### Fluxo de Cache

```
1. Usuário pede recomendações IA
   ↓
2. Sistema verifica cache (gemini_rec:1:6)
   ↓
3a. CACHE HIT (< 1s)
   - Retorna dados salvos
   - Banner verde no frontend
   - Log: [CACHE HIT]
   ↓
3b. CACHE MISS (primeira vez ou expirado)
   - Consulta API Gemini (pode demorar até 30s)
   - Salva resultado no cache por 1 hora
   - Banner azul no frontend
   - Log: [CACHE MISS] + tempo de API
```

## ⚡ Benefícios do Cache

### Antes (sem Redis)
- **Primeira requisição**: 3-8 segundos
- **Segunda requisição**: 3-8 segundos (sempre lento!)
- **Custo**: Alta latência + muitas chamadas à API Gemini

### Depois (com Redis)
- **Primeira requisição**: 3-8 segundos (normal)
- **Segunda requisição**: < 0.5 segundos (instantâneo!)
- **Custo**: Baixa latência + economia de chamadas à API

### Economia de API

Se um usuário consulta 10 vezes no mesmo dia:
- **Sem cache**: 10 chamadas à API Gemini
- **Com cache**: 1 chamada à API + 9 cache hits

## 🐛 Troubleshooting

### Redis não inicia

```bash
# Verificar se Docker está rodando
docker info

# Verificar logs do container
docker logs cgbookstore_redis

# Reiniciar Docker Desktop (Windows)
# Restart docker service (Linux)
sudo systemctl restart docker
```

### Cache não funciona

1. **Verificar se Redis está rodando**:
   ```bash
   docker ps | grep cgbookstore_redis
   ```

2. **Testar conexão do Django**:
   ```bash
   python manage.py shell
   >>> from django.core.cache import cache
   >>> cache.set('test', 'works')
   >>> cache.get('test')
   ```

3. **Verificar configuração**:
   - Arquivo `.env` tem `REDIS_URL=redis://127.0.0.1:6379/1`
   - Settings.py está usando `django_redis.cache.RedisCache`

### Recomendações ainda lentas

1. **Verificar logs**:
   ```bash
   # Ver logs do Django para confirmar CACHE HIT/MISS
   tail -f logs/django.log
   ```

2. **Limpar cache e testar novamente**:
   ```python
   python manage.py shell
   >>> from django.core.cache import cache
   >>> cache.clear()
   ```

3. **Verificar timeout**:
   - Primeira vez sempre será lenta (consulta API)
   - Segundas vezes devem ser < 1s
   - Se segunda vez ainda lenta, Redis não está funcionando

### Redis usa muita memória

```bash
# Verificar uso atual
docker exec cgbookstore_redis redis-cli INFO memory

# Configuração atual: maxmemory 256mb
# Se precisar ajustar, edite docker-compose.yml:
# command: redis-server --maxmemory 512mb
```

## 🔐 Segurança

### Produção

Para produção, adicione senha ao Redis:

1. **Editar `docker-compose.yml`**:
   ```yaml
   command: redis-server --requirepass sua_senha_forte --maxmemory 256mb
   ```

2. **Atualizar `settings.py`**:
   ```python
   CACHES = {
       'default': {
           'LOCATION': 'redis://:sua_senha_forte@127.0.0.1:6379/1',
       }
   }
   ```

3. **Usar variável de ambiente**:
   ```python
   # .env
   REDIS_URL=redis://:sua_senha_forte@127.0.0.1:6379/1

   # settings.py
   'LOCATION': config('REDIS_URL'),
   ```

### Rede

- Por padrão, Redis aceita apenas conexões locais (127.0.0.1)
- Em produção, use firewall para proteger porta 6379
- Considere usar Redis em rede privada (não expor publicamente)

## 📈 Monitoramento

### Logs importantes

```bash
# Logs do Django com cache info
tail -f logs/django.log | grep -E "CACHE|Gemini"

# Ver padrões de acesso
docker exec cgbookstore_redis redis-cli MONITOR | grep gemini_rec

# Estatísticas de hit/miss
docker exec cgbookstore_redis redis-cli INFO stats | grep keyspace
```

### Métricas úteis

- **Hit rate**: % de requisições que usaram cache
- **Response time**: Tempo médio de resposta (< 1s = cache ativo)
- **Memory usage**: Uso de memória do Redis
- **Keys count**: Número total de chaves em cache

## 🎯 Próximos Passos

1. ✅ Redis configurado e rodando
2. ✅ Cache de recomendações funcionando
3. ✅ Timeout nas chamadas Gemini
4. ✅ Feedback visual de cache
5. ✅ Logs detalhados

### Melhorias futuras

- [ ] Implementar warming do cache (pré-carregar recomendações populares)
- [ ] Dashboard de monitoramento do cache
- [ ] Métricas de economia de API calls
- [ ] Cache distribuído para múltiplos servidores (produção)
- [ ] Expiração inteligente baseada em padrões de acesso

## 📚 Referências

- [Redis Documentation](https://redis.io/docs/)
- [Django Redis](https://github.com/jazzband/django-redis)
- [Docker Compose](https://docs.docker.com/compose/)
- [Google Gemini API](https://ai.google.dev/docs)

## 💡 Dicas

1. **Sempre inicie Redis antes do Django** para garantir que o cache funcione
2. **Use `start_dev.bat`** para iniciar tudo automaticamente
3. **Monitore os logs** na primeira vez para confirmar que cache está funcionando
4. **Limpe o cache** se mudar a lógica de recomendações
5. **Em produção**, use senha forte e rede privada

---

**Criado em**: 2025-10-31
**Projeto**: CG.BookStore v3
**Versão Redis**: 7-alpine
**Versão Django Redis**: Compatible with django-redis
