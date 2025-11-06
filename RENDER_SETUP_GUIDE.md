# 📝 Guia de Preenchimento - Render.com

## 🎯 Passo a Passo Completo

### 1️⃣ Criar Conta no Render

1. Acesse: https://dashboard.render.com/register
2. Escolha uma opção:
   - **GitHub** (recomendado)
   - **GitLab**
   - Email
3. Autorize o Render a acessar seus repositórios

---

### 2️⃣ Conectar Repositório

1. No Dashboard do Render, clique em **"New +"**
2. Selecione **"Blueprint"**
3. Clique em **"Connect a repository"**
4. Selecione seu repositório: `cgbookstore_v3`
5. Clique em **"Connect"**

O Render detectará automaticamente o arquivo `render.yaml`

---

### 3️⃣ Configurar o Blueprint

#### Informações que o Render vai mostrar:

**Services que serão criados:**
- ✅ Web Service: `cgbookstore`
- ✅ PostgreSQL: `cgbookstore-db`
- ✅ Redis: `cgbookstore-redis`

**Clique em "Apply"** para aceitar a configuração

---

### 4️⃣ Configurar Variáveis de Ambiente

Após criar o blueprint, configure as variáveis de ambiente:

#### 🔴 OBRIGATÓRIAS (Sistema não funcionará sem elas):

```
Nome: SECRET_KEY
Valor: [Clique em "Generate" para gerar automaticamente]
```

```
Nome: DEBUG
Valor: False
```

```
Nome: ALLOWED_HOSTS
Valor: cgbookstore.onrender.com
Nota: Substitua "cgbookstore" pelo nome que você escolheu para seu app
```

```
Nome: CSRF_TRUSTED_ORIGINS
Valor: https://cgbookstore.onrender.com
Nota: Substitua "cgbookstore" pelo nome que você escolheu para seu app
```

```
Nome: SUPABASE_URL
Valor: https://seu-projeto.supabase.co
Onde obter: Dashboard do Supabase → Settings → API
```

```
Nome: SUPABASE_ANON_KEY
Valor: sua-chave-anonima-aqui
Onde obter: Dashboard do Supabase → Settings → API → anon public
```

```
Nome: SUPABASE_SERVICE_KEY
Valor: sua-chave-de-servico-aqui
Onde obter: Dashboard do Supabase → Settings → API → service_role (⚠️ Manter secreta!)
```

```
Nome: GOOGLE_API_KEY
Valor: sua-google-gemini-api-key
Onde obter: https://makersuite.google.com/app/apikey
```

#### 🟡 OPCIONAIS (Para funcionalidades específicas):

**Social Authentication (Google):**
```
Nome: GOOGLE_CLIENT_ID
Valor: seu-client-id.apps.googleusercontent.com
Onde obter: Google Cloud Console → APIs & Services → Credentials
```

```
Nome: GOOGLE_CLIENT_SECRET
Valor: seu-client-secret
Onde obter: Google Cloud Console → APIs & Services → Credentials
```

**Social Authentication (Facebook):**
```
Nome: FACEBOOK_APP_ID
Valor: seu-facebook-app-id
Onde obter: Facebook Developers → Settings → Basic
```

```
Nome: FACEBOOK_APP_SECRET
Valor: seu-facebook-app-secret
Onde obter: Facebook Developers → Settings → Basic
```

**Mercado Pago:**
```
Nome: MERCADOPAGO_ACCESS_TOKEN
Valor: seu-access-token
Onde obter: Mercado Pago → Suas integrações → Credenciais de produção
```

```
Nome: MERCADOPAGO_PUBLIC_KEY
Valor: sua-public-key
Onde obter: Mercado Pago → Suas integrações → Credenciais de produção
```

#### ⚙️ Variáveis Automáticas (NÃO adicione manualmente):

Estas são fornecidas automaticamente pelo Render:
- ❌ `DATABASE_URL` - Fornecida pelo PostgreSQL
- ❌ `REDIS_URL` - Fornecida pelo Redis

---

### 5️⃣ Como Adicionar Variáveis de Ambiente

1. No Dashboard do Render, clique no seu **Web Service** (`cgbookstore`)
2. No menu lateral, clique em **"Environment"**
3. Role até **"Environment Variables"**
4. Clique em **"Add Environment Variable"**
5. Preencha:
   - **Key**: Nome da variável (ex: `SECRET_KEY`)
   - **Value**: Valor da variável
6. Clique em **"Save Changes"**
7. Repita para cada variável

---

### 6️⃣ Verificar Configurações do Web Service

No painel do Web Service, verifique:

#### Build & Deploy
```
Build Command: ./build.sh
Start Command: gunicorn cgbookstore.wsgi:application
```

#### Environment
```
Python Version: 3.11.0 (ou superior)
Branch: main
Auto-Deploy: Yes (recomendado)
```

#### Instance Type
```
Plan: Free (para testes)
      Starter (para produção - $7/mês)
```

---

### 7️⃣ Configurar OAuth Callbacks (Se usar Social Auth)

Após o primeiro deploy, você terá a URL final. Configure:

#### Google OAuth:
1. Acesse: https://console.cloud.google.com/
2. Vá em **APIs & Services** → **Credentials**
3. Clique no seu OAuth 2.0 Client
4. Em **"Authorized redirect URIs"**, adicione:
   ```
   https://seu-app.onrender.com/accounts/google/login/callback/
   ```
5. Salve

#### Facebook OAuth:
1. Acesse: https://developers.facebook.com/
2. Selecione seu app
3. Vá em **Settings** → **Basic**
4. Em **"Valid OAuth Redirect URIs"**, adicione:
   ```
   https://seu-app.onrender.com/accounts/facebook/login/callback/
   ```
5. Salve

---

### 8️⃣ Primeiro Deploy

1. Após configurar todas as variáveis, clique em **"Manual Deploy"** → **"Deploy latest commit"**
2. O Render irá:
   - ✅ Instalar dependências (1-2 min)
   - ✅ Executar `build.sh` (30s-1min)
   - ✅ Iniciar aplicação com Gunicorn
3. Aguarde aparecer **"Live"** no status
4. Clique na URL para acessar sua aplicação

---

### 9️⃣ Verificar Logs

Se algo der errado:

1. Clique no **Web Service**
2. Menu lateral → **"Logs"**
3. Procure por erros (linhas em vermelho)
4. Erros comuns:
   - ❌ Variável de ambiente faltando
   - ❌ Erro de conexão com banco/redis
   - ❌ Erro nas migrações

---

### 🔟 Pós-Deploy Checklist

Teste as seguintes funcionalidades:

- [ ] Acesso à página inicial
- [ ] Cadastro de novo usuário
- [ ] Login
- [ ] Upload de imagem (teste o Supabase)
- [ ] Sistema de recomendações (teste Google Gemini)
- [ ] Social login (se configurado)
- [ ] Adicionar livro à biblioteca

---

## 📊 Exemplo de Preenchimento Real

### Cenário: Deploy básico (sem OAuth)

```env
# Obrigatórias
SECRET_KEY=django-insecure-ab12cd34ef56gh78ij90kl12mn34op56qr78st90uv  ← Gerar nova
DEBUG=False
ALLOWED_HOSTS=meu-bookstore.onrender.com
CSRF_TRUSTED_ORIGINS=https://meu-bookstore.onrender.com

# Supabase
SUPABASE_URL=https://xyzabcdef.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Google Gemini
GOOGLE_API_KEY=AIzaSyD-9tSrke72PouQMnMX-a7eZSW0jkFMBWY
```

---

## 🆘 Troubleshooting Rápido

### Erro: "Application failed to respond"
**Solução**: Verifique logs → Procure variáveis de ambiente faltando

### Erro: "Database connection failed"
**Solução**: Aguarde 1-2 min → PostgreSQL está inicializando

### Erro: "Redis connection refused"
**Solução**: Verifique se Redis foi criado → Veja em "Services"

### Erro 500 na aplicação
**Solução**:
1. Ative `DEBUG=True` temporariamente
2. Veja erro detalhado
3. Corrija
4. Volte `DEBUG=False`

---

## 🎓 Dicas Importantes

1. **SECRET_KEY**: SEMPRE gere uma nova, nunca use a do código
2. **HTTPS**: Render fornece HTTPS automático via Let's Encrypt
3. **Domínio**: Use um domínio customizado depois (opcional)
4. **Hibernação**: Plano Free hiberna após 15min sem uso
5. **Logs**: Sempre verifique logs após deploy

---

## 📞 Suporte

- 📧 Render Support: https://render.com/support
- 📚 Documentação: https://render.com/docs
- 💬 Discord: https://render.com/discord

---

**Status**: ✅ Guia completo de configuração
**Tempo estimado**: 15-30 minutos
**Dificuldade**: Intermediário
