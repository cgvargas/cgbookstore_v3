# 🚀 Correções Rápidas - Produção Render.com

Guia rápido para corrigir os problemas em produção do CG Bookstore.

## ⚡ Ações Imediatas (PLANO FREE - SEM SHELL)

### 🎯 IMPORTANTE: Ferramentas Web Disponíveis

Como o plano free do Render não tem acesso ao Shell, criamos ferramentas web para você:

#### 1️⃣ Health Check (Diagnóstico)
```
https://cgbookstore-v3.onrender.com/admin-tools/health/
```
**Requisito:** Estar logado como superusuário

#### 2️⃣ Setup de Dados Iniciais
```
https://cgbookstore-v3.onrender.com/admin-tools/setup/
```
**Requisito:** Estar logado como superusuário

### 🔐 Como Acessar as Ferramentas

1. Acesse: `https://cgbookstore-v3.onrender.com/admin/`
2. **Se não tiver usuário admin:** Ver seção "Criar Primeiro Superusuário" abaixo
3. **Se já tiver admin:** Faça login
4. Acesse as URLs das ferramentas acima

---

## 👤 Criar Primeiro Superusuário (IMPORTANTE!)

Como o plano free não tem Shell, você precisa criar o superusuário de forma alternativa:

### Opção 1: Via Django Admin Sign Up (Se habilitado)

1. Acesse: `https://cgbookstore-v3.onrender.com/admin/`
2. Se houver opção de "Sign up" ou "Register", use-a
3. Após criar conta, você precisa promovê-la a superuser (veja Opção 2)

### Opção 2: Criar via Management Command no Build

Adicione ao final do arquivo `build.sh`:

```bash
echo "Creating superuser..."
python manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@cgbookstore.com', 'admin123');
    print('✅ Superuser created: admin / admin123');
else:
    print('⚠️  Superuser already exists');
" || echo "Superuser creation skipped"
```

**IMPORTANTE:** Altere a senha após primeiro login!

### Opção 3: Via Variável de Ambiente no Render

No painel do Render, em **Environment**, adicione:

```
CREATE_SUPERUSER=true
SUPERUSER_USERNAME=admin
SUPERUSER_EMAIL=admin@cgbookstore.com
SUPERUSER_PASSWORD=SuaSenhaAqui123
```

E adicione ao `build.sh`:

```bash
if [ "$CREATE_SUPERUSER" = "true" ]; then
    python manage.py shell -c "
from django.contrib.auth import get_user_model;
import os;
User = get_user_model();
username = os.getenv('SUPERUSER_USERNAME', 'admin');
email = os.getenv('SUPERUSER_EMAIL', 'admin@example.com');
password = os.getenv('SUPERUSER_PASSWORD', 'admin123');
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password);
    print(f'✅ Superuser created: {username}');
" || echo "Superuser creation skipped"
fi
```

---

## 🔧 Correções por Problema

### 🗄️ PROBLEMA: Banco de Dados Vazio

**Sintoma:** Nenhuma categoria, livro ou usuário no site.

**Solução via WEB (Plano Free):**

1. **Primeiro, crie um superusuário** (ver seção abaixo)
2. Acesse: `https://cgbookstore-v3.onrender.com/admin-tools/setup/`
3. Clique no botão **"Executar Setup de Dados Iniciais"**
4. Aguarde a execução (criará categorias, livros, site, OAuth apps)

**Verificar:**
- Acesse: `https://cgbookstore-v3.onrender.com/admin-tools/health/`
- Verifique se categorias e livros aparecem como OK

---

### 🔒 PROBLEMA: Erro CSRF (403 Forbidden)

**Sintoma:** Formulários não funcionam, erro "CSRF verification failed".

**Solução:**

1. Vá em **Environment** no painel do Render
2. Verifique/adicione estas variáveis:

```
ALLOWED_HOSTS=cgbookstore-v3.onrender.com
CSRF_TRUSTED_ORIGINS=https://cgbookstore-v3.onrender.com
```

**IMPORTANTE:**
- `ALLOWED_HOSTS`: SEM `https://`
- `CSRF_TRUSTED_ORIGINS`: COM `https://`

3. Clique em **Save Changes**
4. Serviço reiniciará automaticamente

---

### 🔐 PROBLEMA: Login OAuth Não Funciona

**Sintoma:** Botões Google/Facebook não aparecem ou dão erro.

**Solução:**

#### Passo 1: Configurar Variáveis de Ambiente

No painel **Environment** do Render, adicione:

```
GOOGLE_CLIENT_ID=seu-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=seu-google-client-secret

FACEBOOK_APP_ID=seu-facebook-app-id
FACEBOOK_APP_SECRET=seu-facebook-app-secret
```

#### Passo 2: Configurar Apps OAuth

```bash
# Via Shell do Render
python manage.py setup_initial_data --skip-superuser --skip-categories --skip-books
```

#### Passo 3: Configurar Callback URLs

**Google Cloud Console:**
- Vá em: https://console.cloud.google.com/apis/credentials
- Edite o OAuth 2.0 Client ID
- Em "URIs de redirecionamento autorizados", adicione:
  ```
  https://cgbookstore-v3.onrender.com/accounts/google/login/callback/
  ```

**Facebook Developers:**
- Vá em: https://developers.facebook.com/apps
- Selecione seu app
- Em "Facebook Login" > "Settings"
- Em "Valid OAuth Redirect URIs", adicione:
  ```
  https://cgbookstore-v3.onrender.com/accounts/facebook/login/callback/
  ```

---

### 💥 PROBLEMA: Página em Branco / Erro 500

**Sintoma:** Site não carrega ou mostra erro interno.

**Solução:**

#### 1. Verificar Logs

No painel do Render:
- Clique em **Logs**
- Procure por erros em vermelho
- Anote a mensagem de erro

#### 2. Verificar Migrações

```bash
# Via Shell do Render
python manage.py showmigrations

# Se houver migrações pendentes (sem [X]):
python manage.py migrate
```

#### 3. Coletar Arquivos Estáticos

```bash
python manage.py collectstatic --no-input
```

#### 4. Rebuild Completo

Se nada funcionar:
1. No painel do Render, clique em **Manual Deploy**
2. Selecione **Clear build cache & deploy**
3. Aguarde o build completo

---

### 🎨 PROBLEMA: CSS/JS Não Carregam

**Sintoma:** Página sem estilos, parece HTML puro.

**Solução:**

```bash
# Via Shell do Render
python manage.py collectstatic --no-input --clear
```

Se não resolver:

1. Vá em **Manual Deploy**
2. **Clear build cache & deploy**

---

### 🔴 PROBLEMA: Redis Não Conecta

**Sintoma:** Avisos sobre cache ou tarefas assíncronas.

**Solução:**

#### 1. Verificar Redis Service

No painel do Render:
- Procure o serviço **cgbookstore-redis**
- Status deve estar **Available**
- Se não existir, crie:
  1. **New** > **Redis**
  2. Name: `cgbookstore-redis`
  3. Plan: Free
  4. Clique em **Create**

#### 2. Conectar Redis ao Web Service

1. Vá no serviço **cgbookstore**
2. **Environment** > **Add Environment Variable**
3. Adicione:
   ```
   REDIS_URL=<URL-DO-REDIS>
   ```
   (Copie a URL do serviço Redis)

#### 3. Verificar Conexão

```bash
# Via Shell do Render
python manage.py shell
>>> from django.core.cache import cache
>>> cache.set('test', 'OK')
>>> cache.get('test')
'OK'
>>> exit()
```

---

## 📋 Checklist de Variáveis de Ambiente

No painel **Environment** do Render, certifique-se de ter:

### Essenciais (Obrigatórias)
- [ ] `SECRET_KEY` (gerado automaticamente)
- [ ] `DEBUG=False`
- [ ] `DATABASE_URL` (conectado automaticamente)
- [ ] `REDIS_URL` (conectado automaticamente)
- [ ] `ALLOWED_HOSTS=cgbookstore-v3.onrender.com`
- [ ] `CSRF_TRUSTED_ORIGINS=https://cgbookstore-v3.onrender.com`
- [ ] `SITE_DOMAIN=cgbookstore-v3.onrender.com`
- [ ] `SITE_NAME=CG Bookstore`

### OAuth (Opcionais)
- [ ] `GOOGLE_CLIENT_ID`
- [ ] `GOOGLE_CLIENT_SECRET`
- [ ] `FACEBOOK_APP_ID`
- [ ] `FACEBOOK_APP_SECRET`

### APIs (Opcionais)
- [ ] `GOOGLE_BOOKS_API_KEY`
- [ ] `GEMINI_API_KEY`

### Supabase (Opcionais)
- [ ] `USE_SUPABASE_STORAGE=true`
- [ ] `SUPABASE_URL`
- [ ] `SUPABASE_ANON_KEY`
- [ ] `SUPABASE_SERVICE_KEY`

---

## 🛠️ Comandos Úteis

### Popular Dados Completos
```bash
python manage.py setup_initial_data
```

### Popular Apenas Categorias
```bash
python manage.py setup_initial_data --skip-superuser --skip-books
```

### Criar Superusuário
```bash
python manage.py createsuperuser
```

### Health Check
```bash
python manage.py health_check
```

### Verificar Migrações
```bash
python manage.py showmigrations
```

### Executar Migrações
```bash
python manage.py migrate
```

### Coletar Estáticos
```bash
python manage.py collectstatic --no-input
```

### Verificar Dados
```bash
# Contar categorias
python manage.py shell -c "from core.models import Category; print(Category.objects.count())"

# Contar livros
python manage.py shell -c "from core.models import Book; print(Book.objects.count())"

# Contar usuários
python manage.py shell -c "from django.contrib.auth import get_user_model; print(get_user_model().objects.count())"
```

---

## 🎯 Solução Rápida para Deploy Novo

Se você acabou de fazer deploy e nada funciona:

```bash
# 1. Popular dados iniciais
python manage.py setup_initial_data

# 2. Criar admin
python manage.py createsuperuser

# 3. Verificar tudo
python manage.py health_check
```

Depois, configure as variáveis de ambiente no painel do Render conforme checklist acima.

---

## 🆘 Precisa de Ajuda?

### 1. Execute Health Check
```bash
python manage.py health_check
```

### 2. Verifique Logs
- Painel Render > Logs
- Copie mensagens de erro

### 3. Verifique Variáveis
- Painel Render > Environment
- Compare com checklist acima

### 4. Force Rebuild
- Manual Deploy > Clear build cache & deploy

---

## 📞 Suporte

- **Logs do Render:** https://dashboard.render.com → seu serviço → Logs
- **Health Check:** `python manage.py health_check`
- **Troubleshooting Completo:** Ver `TROUBLESHOOTING_PRODUCAO.md`

---

**🎉 Após as correções, seu site deve estar 100% funcional!**
