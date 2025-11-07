# 🔧 Troubleshooting - Produção (Render.com)

Este guia ajuda a resolver problemas comuns em produção no Render.com.

## 📋 Índice

1. [Diagnóstico Rápido](#diagnostico-rapido)
2. [Banco de Dados Vazio](#banco-de-dados-vazio)
3. [Erros de CSRF](#erros-de-csrf)
4. [Problemas de Login OAuth](#problemas-de-login-oauth)
5. [Páginas em Branco ou Erro 500](#paginas-em-branco-ou-erro-500)
6. [Arquivos Estáticos Não Carregam](#arquivos-estaticos-nao-carregam)
7. [Redis Não Conecta](#redis-nao-conecta)
8. [Logs e Monitoramento](#logs-e-monitoramento)

---

## 🩺 Diagnóstico Rápido

### 1. Executar Health Check

Use o comando de health check para diagnosticar problemas:

```bash
# Via Render Shell (no painel do Render)
python manage.py health_check
```

Este comando verifica:
- ✅ Conexão com banco de dados
- ✅ Conexão com Redis
- ✅ Configuração do Site
- ✅ Apps OAuth configurados
- ✅ Categorias e livros cadastrados
- ✅ Variáveis de ambiente
- ✅ Configurações de segurança

### 2. Verificar Logs

No painel do Render:
1. Acesse seu serviço web
2. Clique em **Logs**
3. Procure por erros em vermelho

---

## 🗄️ Banco de Dados Vazio

### Problema
Após deploy, o site não tem categorias, livros ou usuários.

### Solução

#### Opção 1: Popular Dados Automaticamente (Recomendado)

O script `setup_initial_data` já é executado automaticamente durante o build, mas você pode executá-lo manualmente:

```bash
# Via Render Shell
python manage.py setup_initial_data
```

Isso criará:
- ✅ Site configurado (django-allauth)
- ✅ 20 categorias de livros
- ✅ 3 livros de exemplo
- ✅ Apps OAuth (Google e Facebook)

#### Opção 2: Criar Superusuário Manualmente

```bash
# Via Render Shell
python manage.py createsuperuser
```

Siga as instruções e depois acesse `/admin` para adicionar conteúdo.

#### Opção 3: Popular com Dados Customizados

```bash
# Criar superusuário com email específico
python manage.py setup_initial_data --admin-email seu@email.com --admin-password SuaSenha123

# Pular criação de livros de exemplo
python manage.py setup_initial_data --skip-books
```

### Verificação

```bash
python manage.py shell
>>> from core.models import Category, Book
>>> Category.objects.count()  # Deve retornar > 0
>>> Book.objects.count()      # Deve retornar > 0
```

---

## 🔒 Erros de CSRF

### Problema
Erro `CSRF verification failed` ao tentar fazer login ou submit de formulários.

### Sintomas
- Erro 403 Forbidden
- Mensagem: "CSRF token missing or incorrect"

### Solução

#### 1. Verificar CSRF_TRUSTED_ORIGINS

No painel do Render, vá em **Environment** e verifique:

```
CSRF_TRUSTED_ORIGINS=https://cgbookstore-v3.onrender.com
```

**IMPORTANTE:**
- ✅ Incluir `https://` no início
- ❌ NÃO adicionar barra no final
- ✅ Usar o domínio exato do Render

#### 2. Verificar ALLOWED_HOSTS

```
ALLOWED_HOSTS=cgbookstore-v3.onrender.com
```

**IMPORTANTE:**
- ❌ NÃO incluir `https://` aqui
- ✅ Apenas o domínio

#### 3. Reiniciar Aplicação

Após alterar variáveis de ambiente:
1. Clique em **Manual Deploy** > **Deploy latest commit**
2. OU adicione uma variável fictícia para forçar restart

---

## 🔐 Problemas de Login OAuth

### Problema
Login com Google ou Facebook não funciona.

### Sintomas
- Botão de login social não aparece
- Erro de redirect após autorizar
- "Social app not configured"

### Solução

#### 1. Verificar Apps OAuth Configurados

```bash
# Via Render Shell
python manage.py shell
>>> from allauth.socialaccount.models import SocialApp
>>> SocialApp.objects.all()
```

Se vazio, execute:

```bash
python manage.py setup_initial_data --skip-superuser --skip-categories --skip-books
```

#### 2. Configurar Credenciais OAuth

No painel do Render, adicione as variáveis:

**Google OAuth:**
```
GOOGLE_CLIENT_ID=seu-client-id-aqui.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-seu-secret-aqui
```

**Facebook OAuth:**
```
FACEBOOK_APP_ID=seu-app-id-aqui
FACEBOOK_APP_SECRET=seu-app-secret-aqui
```

#### 3. Configurar URLs de Callback

**Google Cloud Console:**
- URI de redirecionamento autorizado: `https://cgbookstore-v3.onrender.com/accounts/google/login/callback/`

**Facebook Developers:**
- URL de redirecionamento OAuth válido: `https://cgbookstore-v3.onrender.com/accounts/facebook/login/callback/`

#### 4. Atualizar Apps Sociais

Após configurar as credenciais, atualize os apps:

```bash
# Via Render Shell
python manage.py setup_initial_data --skip-superuser --skip-categories --skip-books
```

---

## 💥 Páginas em Branco ou Erro 500

### Problema
Página não carrega ou mostra erro 500.

### Diagnóstico

#### 1. Verificar Logs

```bash
# Logs do Render (interface web)
# Procure por:
# - DatabaseError
# - TemplateDoesNotExist
# - ImportError
# - KeyError
```

#### 2. Verificar Migrações

```bash
# Via Render Shell
python manage.py showmigrations
# Todos devem ter [X]

# Se houver migrações pendentes:
python manage.py migrate
```

#### 3. Verificar Variáveis Essenciais

```bash
python manage.py health_check
```

### Soluções Comuns

#### Erro de Template
```
TemplateDoesNotExist at /
```

**Solução:**
```bash
# Coletar arquivos estáticos
python manage.py collectstatic --no-input
```

#### Erro de Banco
```
relation "core_book" does not exist
```

**Solução:**
```bash
# Executar migrações
python manage.py migrate
```

#### Erro de Import
```
ModuleNotFoundError: No module named 'X'
```

**Solução:**
1. Adicionar dependência ao `requirements.txt`
2. Fazer commit e push
3. Redeploy automático no Render

---

## 🎨 Arquivos Estáticos Não Carregam

### Problema
CSS, JS e imagens não aparecem.

### Sintomas
- Página sem estilos
- Erro 404 para `/static/...`

### Solução

#### 1. Coletar Arquivos Estáticos

```bash
# Via Render Shell
python manage.py collectstatic --no-input
```

#### 2. Verificar WhiteNoise no settings.py

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # ← Deve estar aqui
    # ...
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

#### 3. Rebuild

Se ainda não funcionar, faça um rebuild completo:
1. **Manual Deploy** > **Clear build cache & deploy**

---

## 🔴 Redis Não Conecta

### Problema
Cache ou Celery não funcionam.

### Sintomas
- Warning: "Redis not available"
- Tarefas assíncronas não executam

### Solução

#### 1. Verificar Redis Service no Render

No painel do Render:
1. Verifique se o serviço `cgbookstore-redis` está **ativo**
2. Status deve ser "Available"

#### 2. Verificar Variável REDIS_URL

```bash
# Via Render Shell
echo $REDIS_URL
# Deve retornar algo como: redis://red-xxxxx:6379
```

Se vazio:
1. Vá em **Environment**
2. Verifique se `REDIS_URL` está conectado ao Redis service

#### 3. Testar Conexão

```bash
# Via Render Shell
python manage.py shell
>>> from django.core.cache import cache
>>> cache.set('test', 'OK')
>>> cache.get('test')
'OK'
```

#### 4. Fallback: Desabilitar Redis

Se Redis não for crítico, você pode usar sessões em banco:

Em `settings.py` (já configurado):
```python
# Sessões em banco de dados (fallback)
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
```

---

## 📊 Logs e Monitoramento

### Ver Logs em Tempo Real

No painel do Render:
1. Acesse seu serviço
2. Clique em **Logs**
3. Use filtros: `Error`, `Warning`, `Info`

### Comandos Úteis via Shell

```bash
# Health check completo
python manage.py health_check

# Verificar migrações
python manage.py showmigrations

# Verificar usuários
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print(f'Usuários: {User.objects.count()}')"

# Verificar livros
python manage.py shell -c "from core.models import Book; print(f'Livros: {Book.objects.count()}')"

# Verificar categorias
python manage.py shell -c "from core.models import Category; print(f'Categorias: {Category.objects.count()}')"

# Testar email (se configurado)
python manage.py sendtestemail seu@email.com
```

### Ativar Logs Detalhados

No painel do Render, adicione:

```
DJANGO_LOG_LEVEL=DEBUG
```

**⚠️ ATENÇÃO:** Reverta para `INFO` após diagnosticar.

---

## 🆘 Problemas Não Resolvidos?

### 1. Execute Health Check Completo

```bash
python manage.py health_check > health_report.txt
```

### 2. Verifique as Configurações

```bash
# Verificar todas as variáveis de ambiente
env | grep -E "(DEBUG|DATABASE|REDIS|ALLOWED|CSRF|GOOGLE|FACEBOOK)"
```

### 3. Reset Completo (Última Opção)

```bash
# 1. Limpar banco (cuidado!)
python manage.py flush --no-input

# 2. Re-executar migrações
python manage.py migrate

# 3. Popular dados iniciais
python manage.py setup_initial_data

# 4. Criar superusuário
python manage.py createsuperuser
```

---

## 📚 Referências

- [Documentação Render.com](https://render.com/docs)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [Django-allauth Documentation](https://django-allauth.readthedocs.io/)
- [WhiteNoise Documentation](http://whitenoise.evans.io/)

---

## 🎯 Checklist de Deploy

Antes de fazer deploy:

- [ ] `DEBUG=False` em produção
- [ ] `SECRET_KEY` configurado e único
- [ ] `ALLOWED_HOSTS` configurado corretamente
- [ ] `CSRF_TRUSTED_ORIGINS` com `https://`
- [ ] Migrações executadas (`python manage.py migrate`)
- [ ] Arquivos estáticos coletados (`collectstatic`)
- [ ] Dados iniciais populados (`setup_initial_data`)
- [ ] Health check executado sem erros críticos
- [ ] URLs OAuth configuradas nos providers
- [ ] Variáveis de ambiente sensíveis configuradas
- [ ] Logs verificados sem erros críticos

---

**Última atualização:** Novembro 2025
