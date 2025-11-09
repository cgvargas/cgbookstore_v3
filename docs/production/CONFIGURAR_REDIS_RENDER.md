# Configurar Redis no Render para Recomendações e Cache

## Problema Atual

O sistema de recomendações tem dois problemas:

1. **Redis não configurado no Render**: Cache não funciona em produção
2. **Algoritmos lentos sem cache**: Híbrido, Similares e Conteúdo levam 60+ segundos para processar

**Sintomas:**
- ✅ "Personalizado" funciona (otimizado)
- ✅ "IA Premium" funciona (com cache local)
- ❌ "Híbrido", "Similares", "Conteúdo" demoram mais de 1 minuto (timeout de 5s cancela)
- Página inicial pode ficar lenta aguardando resposta da API

**Solução Temporária Implementada:**
- Botões "Híbrido", "Similares" e "Conteúdo" foram **desabilitados temporariamente**
- Apenas "Personalizado" e "IA Premium" estão visíveis
- Após configurar Redis, os botões serão reabilitados

---

## Solução 1: Adicionar Redis no Render (RECOMENDADO)

O Render oferece Redis gratuitamente no plano Free.

### Passo 1: Criar instância Redis

1. Acesse [Render Dashboard](https://dashboard.render.com/)
2. Clique em **"New +"** → **"Redis"**
3. Configure:
   - **Name**: `cgbookstore-redis`
   - **Region**: `Oregon (US West)` (mesma região do seu web service)
   - **Plan**: `Free` (0 MB - 25 MB)
   - **Maxmemory Policy**: `allkeys-lru` (recomendado para cache)
4. Clique em **"Create Redis"**

### Passo 2: Conectar ao Web Service

1. Vá para o seu Web Service: `cgbookstore`
2. Clique em **"Environment"** no menu lateral
3. Adicione nova variável de ambiente:
   - **Key**: `REDIS_URL`
   - **Value**: Copie a **Internal Redis URL** da instância Redis
     - Formato: `redis://red-xxx:6379`
4. Clique em **"Save Changes"**

O Render vai automaticamente fazer deploy novamente.

### Passo 3: Verificar Conexão

Após o deploy:

```bash
# No shell do Render (via Dashboard → Shell)
python manage.py shell

>>> from django.core.cache import cache
>>> cache.set('test', 'funciona', 60)
>>> print(cache.get('test'))
# Deve retornar: 'funciona'
```

---

## Solução 2: Desabilitar Recomendações (TEMPORÁRIO)

Se não quiser usar Redis agora, pode desabilitar as recomendações:

### Método 1: Remover seção do template

**Arquivo**: `templates/core/home.html`

```html
<!-- Comentar ou remover essa linha -->
<!-- {% include 'recommendations/recommendations_section.html' %} -->
```

### Método 2: Configurar fallback silencioso

**Arquivo**: `cgbookstore/settings.py`

```python
# Adicionar após CACHES
RECOMMENDATIONS_ENABLED = os.getenv('RECOMMENDATIONS_ENABLED', 'True') == 'True'
```

**No Render**:
- Environment Variable: `RECOMMENDATIONS_ENABLED=False`

**No template** (`templates/recommendations/recommendations_section.html`):

```html
{% if settings.RECOMMENDATIONS_ENABLED %}
<!-- Seção de recomendações -->
...
{% endif %}
```

---

## Configuração Atual do Redis (Local)

**Arquivo**: `cgbookstore/settings.py` (linhas ~274-310)

```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True
            },
            'IGNORE_EXCEPTIONS': True,  # Não quebra se Redis falhar
        }
    }
}
```

**Variável de ambiente necessária**:
```bash
REDIS_URL=redis://127.0.0.1:6379/1  # Local
REDIS_URL=redis://red-xxx:6379      # Render (Internal URL)
```

---

## Benefícios do Redis

1. **Cache de recomendações IA**: Evita chamadas repetidas ao Gemini
2. **Cache de sessões**: Melhora performance de login/autenticação
3. **Cache de queries**: Reduz carga no PostgreSQL
4. **Celery broker**: Necessário para tarefas assíncronas

---

## Custos

| Plano | Memória | Conexões | Preço |
|-------|---------|----------|-------|
| Free  | 25 MB   | 10       | $0/mês |
| Starter | 256 MB | 100    | $7/mês |
| Standard | 1 GB  | 500     | $25/mês |

**Recomendação**: Comece com **Free** (suficiente para cache de recomendações).

---

## Troubleshooting

### Erro: "Connection refused"
- Verifique se o Redis está rodando
- Confirme que `REDIS_URL` está correto
- Teste conexão: `redis-cli -u $REDIS_URL ping`

### Erro: "Max connections reached"
- Aumente `max_connections` em settings.py
- Ou faça upgrade do plano Redis

### Recomendações lentas mesmo com Redis
- Verifique se cache está funcionando: `cache.get('test')`
- Aumente TTL do cache (atualmente 1h)
- Considere cache de 24h para IA

---

## Checklist de Implementação

- [ ] Criar instância Redis no Render
- [ ] Adicionar `REDIS_URL` nas variáveis de ambiente
- [ ] Aguardar deploy automático
- [ ] Testar conexão no shell
- [ ] Verificar recomendações na home
- [ ] Confirmar que não há erro "Redis está rodando"

---

## Referências

- [Render Redis Docs](https://render.com/docs/redis)
- [Django Redis Cache](https://github.com/jazzband/django-redis)
- [Celery + Redis](https://docs.celeryproject.org/en/stable/getting-started/backends-and-brokers/redis.html)
