# Plano de Implementação: Django-allauth

**Data:** 2025-11-05
**Projeto:** CGBookstore v3
**Objetivo:** Adicionar autenticação social (Google, Facebook, GitHub) mantendo sistema existente

---

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Estratégia de Implementação](#estratégia-de-implementação)
3. [Fase 1: Setup Básico](#fase-1-setup-básico)
4. [Fase 2: Google OAuth](#fase-2-google-oauth)
5. [Fase 3: Providers Adicionais](#fase-3-providers-adicionais)
6. [Fase 4: Customizações](#fase-4-customizações)
7. [Fase 5: Testes e Deploy](#fase-5-testes-e-deploy)
8. [Troubleshooting](#troubleshooting)
9. [Checklist Final](#checklist-final)

---

## Visão Geral

### O Que É Django-allauth?

Django-allauth é um pacote completo de autenticação que fornece:
- ✅ Autenticação social (50+ providers)
- ✅ Login/registro tradicional
- ✅ Email verification
- ✅ Password reset
- ✅ Account management
- ✅ 100% compatível com Django auth existente

### Por Que Escolhemos Allauth?

| Critério | Django-allauth | Alternativas |
|----------|----------------|--------------|
| Maturidade | ⭐⭐⭐⭐⭐ 12 anos | Variável |
| Providers | 50+ | Limitado |
| Manutenção | Ativa | Variável |
| Documentação | Excelente | Variável |
| Comunidade | Grande | Menor |
| Compatibilidade | 100% Django | Pode variar |

### O Que Vamos Implementar

**Fase 1 (Essencial):**
- ✅ Instalação e configuração base
- ✅ Migração de templates
- ✅ Google OAuth
- ✅ Password reset

**Fase 2 (Importante):**
- ✅ Facebook OAuth
- ✅ GitHub OAuth
- ✅ Email verification

**Fase 3 (Desejável):**
- ✅ Microsoft OAuth
- ✅ Rate limiting
- ✅ Customizações avançadas

---

## Estratégia de Implementação

### Princípios

1. **Zero Breaking Changes**: Sistema existente continua funcionando
2. **Gradual Migration**: Adicionar recursos sem remover existentes
3. **Testing First**: Testar cada etapa antes de avançar
4. **Rollback Ready**: Manter capacidade de reverter mudanças

### Arquitetura Proposta

```
ANTES:
┌──────────────────────────────────────┐
│         Django Auth Built-in         │
│                                      │
│  ┌──────────┐     ┌──────────┐     │
│  │  Login   │     │ Register │     │
│  └──────────┘     └──────────┘     │
│                                      │
│  ┌──────────────────────────┐      │
│  │     ModelBackend         │      │
│  │  (username + password)   │      │
│  └──────────────────────────┘      │
└──────────────────────────────────────┘

DEPOIS:
┌──────────────────────────────────────────────────────┐
│              Django-allauth                          │
│                                                      │
│  ┌──────────┐  ┌──────────┐  ┌─────────────────┐  │
│  │  Login   │  │ Register │  │  Social Login   │  │
│  │ (native) │  │ (native) │  │  ┌────┐ ┌────┐ │  │
│  └──────────┘  └──────────┘  │  │ G  │ │ FB │ │  │
│                               │  └────┘ └────┘ │  │
│  ┌──────────────────────┐    │  ┌────┐ ┌────┐ │  │
│  │   Password Reset     │    │  │ GH │ │ MS │ │  │
│  └──────────────────────┘    │  └────┘ └────┘ │  │
│                               └─────────────────┘  │
│  ┌──────────────────────────────────────────┐     │
│  │  Multiple Authentication Backends        │     │
│  │  • ModelBackend (username/password)      │     │
│  │  • allauth.account.auth_backends.        │     │
│  │    AuthenticationBackend (email)         │     │
│  └──────────────────────────────────────────┘     │
└──────────────────────────────────────────────────────┘
```

### Timeline Estimado

| Fase | Descrição | Duração | Complexidade |
|------|-----------|---------|--------------|
| 1 | Setup básico | 2-3 horas | 🟢 Baixa |
| 2 | Google OAuth | 3-4 horas | 🟡 Média |
| 3 | Providers adicionais | 2-3 horas cada | 🟡 Média |
| 4 | Customizações | 4-6 horas | 🟠 Alta |
| 5 | Testes e deploy | 2-3 horas | 🟡 Média |

**Total: 15-25 horas (2-3 dias de trabalho)**

---

## Fase 1: Setup Básico

### 1.1 Instalação

**Comando:**
```bash
pip install django-allauth
```

**Versão recomendada:** `0.57.0` ou superior

**Adicionar ao `requirements.txt`:**
```txt
django-allauth>=0.57.0
```

### 1.2 Configuração em `settings.py`

**Passo 1: Adicionar apps**

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',  # ← ADICIONAR (requerido pelo allauth)

    # Apps de terceiros
    'allauth',                              # ← ADICIONAR
    'allauth.account',                      # ← ADICIONAR
    'allauth.socialaccount',                # ← ADICIONAR
    # Providers virão depois:
    # 'allauth.socialaccount.providers.google',
    # 'allauth.socialaccount.providers.facebook',
    # 'allauth.socialaccount.providers.github',

    # Nossas apps
    'core',
    'books',
    'accounts',
    'finance',
]
```

**Passo 2: Configurar authentication backends**

```python
AUTHENTICATION_BACKENDS = [
    # Backend nativo do Django (username + password)
    'django.contrib.auth.backends.ModelBackend',

    # Backend do allauth (email + password, social)
    'allauth.account.auth_backends.AuthenticationBackend',
]
```

**Passo 3: Configurar Site Framework**

```python
SITE_ID = 1  # ← ADICIONAR
```

**Passo 4: Configurações do allauth**

```python
# ============================================================
# DJANGO-ALLAUTH CONFIGURATION
# ============================================================

# Método de autenticação: username_email permite login com ambos
ACCOUNT_AUTHENTICATION_METHOD = 'username_email'

# Email é obrigatório para registro
ACCOUNT_EMAIL_REQUIRED = True

# Verificação de email: 'optional', 'mandatory', ou 'none'
ACCOUNT_EMAIL_VERIFICATION = 'optional'  # Começar com optional, depois mandatory

# Username é obrigatório (manter compatibilidade com sistema existente)
ACCOUNT_USERNAME_REQUIRED = True

# Permitir usuários registrarem-se
ACCOUNT_SIGNUP_ENABLED = True

# Redirecionamento após login
ACCOUNT_LOGIN_REDIRECT_URL = '/'  # Já existe como LOGIN_REDIRECT_URL

# Redirecionamento após logout
ACCOUNT_LOGOUT_REDIRECT_URL = '/books/'  # Já existe como LOGOUT_REDIRECT_URL

# Confirmar email ao fazer logout de contas sociais
ACCOUNT_LOGOUT_ON_GET = False

# Página de login
ACCOUNT_LOGIN_URL = '/accounts/login/'

# Preservar query parameters após login
ACCOUNT_LOGIN_ON_GET = False

# Formulários customizados (vamos criar depois)
# ACCOUNT_FORMS = {
#     'signup': 'accounts.forms.CustomSignupForm',
# }

# Adapter customizado (para lógica extra)
# ACCOUNT_ADAPTER = 'accounts.adapters.CustomAccountAdapter'

# Social account adapter
# SOCIALACCOUNT_ADAPTER = 'accounts.adapters.CustomSocialAccountAdapter'

# Auto-signup com social account (sem confirmação extra)
SOCIALACCOUNT_AUTO_SIGNUP = True

# Perguntar email se provider não fornecer
SOCIALACCOUNT_QUERY_EMAIL = True

# Conectar accounts existentes por email
SOCIALACCOUNT_EMAIL_AUTHENTICATION = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True

# Providers configuration (vamos adicionar depois)
SOCIALACCOUNT_PROVIDERS = {
    # 'google': {...},
    # 'facebook': {...},
}
```

### 1.3 URLs

**Adicionar em `cgbookstore/urls.py`:**

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # Allauth URLs (ADICIONAR ANTES de accounts/)
    path('accounts/', include('allauth.urls')),

    # Nossas URLs de accounts (vão sobrescrever algumas do allauth)
    # path('accounts/', include('accounts.urls')),  # Comentar temporariamente

    # Outras URLs
    path('books/', include('books.urls')),
    path('', include('core.urls')),
    path('finance/', include('finance.urls')),
]
```

**⚠️ IMPORTANTE:** A ordem importa! URLs do allauth devem vir ANTES das nossas para funcionar corretamente.

**Estratégia de URLs:**

```python
# OPÇÃO A: Allauth gerencia tudo
path('accounts/', include('allauth.urls')),

# OPÇÃO B: Hybrid (recomendado)
path('accounts/', include('allauth.urls')),      # Login, logout, social, etc.
path('profile/', include('accounts.urls')),      # Nossas views customizadas
```

### 1.4 Migrações

**Executar migrações do allauth:**

```bash
python manage.py migrate
```

**Isso criará tabelas:**
- `django_site` (Site framework)
- `account_emailaddress` (Emails verificados)
- `account_emailconfirmation` (Tokens de confirmação)
- `socialaccount_socialaccount` (Contas sociais linkadas)
- `socialaccount_socialapp` (Apps configurados: Google, FB, etc.)
- `socialaccount_socialtoken` (Tokens OAuth)

### 1.5 Configurar Site no Admin

**Método 1: Via Django Shell**

```bash
python manage.py shell
```

```python
from django.contrib.sites.models import Site

# Atualizar o site padrão
site = Site.objects.get(pk=1)
site.domain = 'localhost:8000'  # Ou seu domínio em produção
site.name = 'CGBookstore'
site.save()
```

**Método 2: Via Admin**

1. Acessar `http://localhost:8000/admin/sites/site/`
2. Editar o site ID=1
3. Configurar:
   - Domain: `localhost:8000` (dev) ou `cgbookstore.com` (prod)
   - Display name: `CGBookstore`

### 1.6 Testar Instalação

**Verificar URLs disponíveis:**

```bash
python manage.py show_urls | grep account
```

**Saída esperada:**
```
/accounts/login/                        account_login
/accounts/logout/                       account_logout
/accounts/signup/                       account_signup
/accounts/password/reset/               account_reset_password
/accounts/password/reset/done/          account_reset_password_done
/accounts/confirm-email/                account_email_verification_sent
...
```

**Acessar página de login:**
```
http://localhost:8000/accounts/login/
```

**Deve mostrar template padrão do allauth (feio, mas funcional).**

### 1.7 Checkpoint

✅ Antes de prosseguir, verificar:
- [ ] `pip install django-allauth` executado
- [ ] Apps adicionados em `INSTALLED_APPS`
- [ ] `SITE_ID = 1` configurado
- [ ] Backends de autenticação configurados
- [ ] URLs do allauth adicionados
- [ ] Migrações executadas sem erro
- [ ] Site configurado no admin
- [ ] URLs do allauth acessíveis

---

## Fase 2: Google OAuth

### 2.1 Criar Projeto no Google Cloud

**Passo 1: Acessar Google Cloud Console**

1. Ir para https://console.cloud.google.com/
2. Fazer login com conta Google
3. Criar novo projeto:
   - Nome: `CGBookstore`
   - ID: `cgbookstore` (ou similar)
   - Clicar em "Create"

**Passo 2: Habilitar Google+ API**

1. No menu, ir em "APIs & Services" > "Library"
2. Buscar "Google+ API"
3. Clicar em "Enable"

**Nota:** A partir de 2023, pode ser necessário usar "Google Identity Services" ao invés de Google+ API.

**Passo 3: Criar OAuth 2.0 Credentials**

1. Ir em "APIs & Services" > "Credentials"
2. Clicar em "Create Credentials" > "OAuth client ID"
3. Configurar OAuth consent screen (se primeira vez):

   **Tipo de usuário:**
   - Desenvolvimento: "External" (qualquer conta Google pode testar)
   - Produção: "Internal" ou "External" verificado

   **Informações do app:**
   - App name: `CGBookstore`
   - User support email: seu@email.com
   - Developer contact: seu@email.com

   **Scopes:**
   - `.../auth/userinfo.email`
   - `.../auth/userinfo.profile`

   **Test users (se External em desenvolvimento):**
   - Adicionar emails que poderão testar

4. Criar OAuth Client ID:
   - Application type: "Web application"
   - Name: `CGBookstore Web Client`
   - Authorized JavaScript origins:
     - `http://localhost:8000` (dev)
     - `https://cgbookstore.com` (prod)
   - Authorized redirect URIs:
     - `http://localhost:8000/accounts/google/login/callback/` (dev)
     - `https://cgbookstore.com/accounts/google/login/callback/` (prod)

5. Clicar em "Create"

**Passo 4: Copiar Credenciais**

Você receberá:
- **Client ID**: `123456789-abcdefghijklmnop.apps.googleusercontent.com`
- **Client Secret**: `GOCSPX-aBcDeFgHiJkLmNoPqRsTuVwXyZ`

⚠️ **IMPORTANTE:** Guardar em local seguro! Nunca commitar no Git!

### 2.2 Configurar Provider no Django

**Adicionar app em `settings.py`:**

```python
INSTALLED_APPS = [
    # ...
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',  # ← ADICIONAR
    # ...
]
```

**Configurar provider em `settings.py`:**

```python
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        'APP': {
            'client_id': '123456789-abcdefghijklmnop.apps.googleusercontent.com',
            'secret': 'GOCSPX-aBcDeFgHiJkLmNoPqRsTuVwXyZ',
            'key': ''
        }
    }
}
```

**⚠️ MELHOR PRÁTICA:** Usar variáveis de ambiente:

```python
# settings.py
import os

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        'APP': {
            'client_id': os.environ.get('GOOGLE_CLIENT_ID'),
            'secret': os.environ.get('GOOGLE_CLIENT_SECRET'),
            'key': ''
        }
    }
}
```

**Criar arquivo `.env`:**

```bash
# .env (NÃO COMMITAR!)
GOOGLE_CLIENT_ID=123456789-abcdefghijklmnop.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-aBcDeFgHiJkLmNoPqRsTuVwXyZ
```

**Instalar python-decouple:**

```bash
pip install python-decouple
```

**Carregar variáveis em `settings.py`:**

```python
from decouple import config

GOOGLE_CLIENT_ID = config('GOOGLE_CLIENT_ID', default='')
GOOGLE_CLIENT_SECRET = config('GOOGLE_CLIENT_SECRET', default='')

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
        'APP': {
            'client_id': GOOGLE_CLIENT_ID,
            'secret': GOOGLE_CLIENT_SECRET,
            'key': ''
        }
    }
}
```

### 2.3 Configurar Social App no Admin

**Método 1: Via Admin (Recomendado)**

1. Executar migrações (se ainda não executou):
   ```bash
   python manage.py migrate
   ```

2. Acessar admin: `http://localhost:8000/admin/`

3. Ir em "Social applications" (dentro de SOCIAL ACCOUNTS)

4. Clicar em "Add social application"

5. Preencher:
   - **Provider:** Google
   - **Name:** Google (pode ser qualquer nome)
   - **Client id:** `123456789-abcdefghijklmnop.apps.googleusercontent.com`
   - **Secret key:** `GOCSPX-aBcDeFgHiJkLmNoPqRsTuVwXyZ`
   - **Sites:** Mover "cgbookstore.com" ou "localhost:8000" para "Chosen sites"

6. Salvar

**Método 2: Via Django Shell**

```bash
python manage.py shell
```

```python
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site

site = Site.objects.get(pk=1)

google_app = SocialApp.objects.create(
    provider='google',
    name='Google',
    client_id='123456789-abcdefghijklmnop.apps.googleusercontent.com',
    secret='GOCSPX-aBcDeFgHiJkLmNoPqRsTuVwXyZ',
)

google_app.sites.add(site)
print('Google OAuth configurado com sucesso!')
```

### 2.4 Adicionar Botão de Login no Template

**Atualizar `templates/accounts/login.html`:**

```html
{% load socialaccount %}

<div class="login-container">
    <div class="login-card">
        <h2>Bem-vindo de volta!</h2>

        <!-- Botões de Login Social -->
        <div class="social-login-buttons">
            <a href="{% provider_login_url 'google' %}" class="btn btn-google">
                <i class="fab fa-google"></i>
                Continuar com Google
            </a>
        </div>

        <div class="divider">
            <span>ou</span>
        </div>

        <!-- Formulário tradicional -->
        <form method="post" id="loginForm">
            {% csrf_token %}
            <!-- campos existentes -->
        </form>
    </div>
</div>

<style>
.social-login-buttons {
    margin-bottom: 20px;
}

.btn-google {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    padding: 12px;
    background: #4285F4;
    color: white;
    border: none;
    border-radius: 4px;
    font-size: 16px;
    cursor: pointer;
    text-decoration: none;
    transition: background 0.3s;
}

.btn-google:hover {
    background: #357AE8;
}

.btn-google i {
    margin-right: 10px;
    font-size: 20px;
}

.divider {
    display: flex;
    align-items: center;
    margin: 20px 0;
    color: #999;
}

.divider::before,
.divider::after {
    content: '';
    flex: 1;
    height: 1px;
    background: #ddd;
}

.divider span {
    padding: 0 15px;
}
</style>
```

**Adicionar Font Awesome (se ainda não tem):**

```html
<!-- Em base.html ou login.html -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
```

### 2.5 Testar Login com Google

**Passo a passo:**

1. Acessar `http://localhost:8000/accounts/login/`
2. Clicar em "Continuar com Google"
3. Será redirecionado para tela de login do Google
4. Fazer login com conta Google
5. Autorizar acesso ao CGBookstore
6. Será redirecionado de volta para o site
7. Verificar se está logado

**Verificar no Admin:**

1. Acessar `http://localhost:8000/admin/auth/user/`
2. Deve ter novo usuário criado
3. Acessar `http://localhost:8000/admin/socialaccount/socialaccount/`
4. Deve ter registro da conta social linkada

**Debug:**

```bash
python manage.py shell
```

```python
from django.contrib.auth.models import User
from allauth.socialaccount.models import SocialAccount

# Listar usuários
users = User.objects.all()
for user in users:
    print(f'{user.username} - {user.email}')

# Listar contas sociais
social_accounts = SocialAccount.objects.all()
for sa in social_accounts:
    print(f'{sa.user.username} - {sa.provider} - {sa.uid}')
```

### 2.6 Checkpoint

✅ Antes de prosseguir, verificar:
- [ ] Projeto criado no Google Cloud
- [ ] OAuth 2.0 credentials criadas
- [ ] Redirect URI configurado corretamente
- [ ] Provider adicionado em `INSTALLED_APPS`
- [ ] Configurações em `settings.py` corretas
- [ ] SocialApp criado no admin
- [ ] Botão "Login com Google" aparece no template
- [ ] Login funciona e cria usuário
- [ ] SocialAccount é criado e linkado

---

## Fase 3: Providers Adicionais

### 3.1 Facebook OAuth

**Passo 1: Criar App no Facebook Developers**

1. Acessar https://developers.facebook.com/
2. Ir em "My Apps" > "Create App"
3. Escolher "Consumer" como tipo
4. Preencher:
   - Display name: `CGBookstore`
   - Contact email: seu@email.com
5. Clicar em "Create App"

**Passo 2: Configurar Facebook Login**

1. No dashboard do app, adicionar produto "Facebook Login"
2. Ir em "Settings" > "Basic":
   - App Domains: `localhost` (dev) e `cgbookstore.com` (prod)
   - Privacy Policy URL: `https://cgbookstore.com/privacy`
   - Terms of Service URL: `https://cgbookstore.com/terms`

3. Ir em "Facebook Login" > "Settings":
   - Valid OAuth Redirect URIs:
     - `http://localhost:8000/accounts/facebook/login/callback/`
     - `https://cgbookstore.com/accounts/facebook/login/callback/`

4. Copiar credenciais em "Settings" > "Basic":
   - App ID: `1234567890123456`
   - App Secret: `abcdef1234567890abcdef1234567890`

**Passo 3: Adicionar provider no Django**

```python
# settings.py
INSTALLED_APPS = [
    # ...
    'allauth.socialaccount.providers.facebook',  # ← ADICIONAR
]

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        # ... configuração Google existente
    },
    'facebook': {
        'METHOD': 'oauth2',
        'SCOPE': ['email', 'public_profile'],
        'AUTH_PARAMS': {'auth_type': 'reauthenticate'},
        'INIT_PARAMS': {'cookie': True},
        'FIELDS': [
            'id',
            'email',
            'name',
            'first_name',
            'last_name',
            'verified',
            'locale',
            'timezone',
            'link',
            'gender',
            'updated_time',
        ],
        'EXCHANGE_TOKEN': True,
        'VERIFIED_EMAIL': False,
        'VERSION': 'v18.0',
        'APP': {
            'client_id': config('FACEBOOK_APP_ID', default=''),
            'secret': config('FACEBOOK_APP_SECRET', default=''),
            'key': ''
        }
    }
}
```

**Passo 4: Adicionar no `.env`:**

```bash
FACEBOOK_APP_ID=1234567890123456
FACEBOOK_APP_SECRET=abcdef1234567890abcdef1234567890
```

**Passo 5: Criar Social App no Admin**

Igual ao Google, mas:
- Provider: Facebook
- Name: Facebook
- Client ID: App ID do Facebook
- Secret: App Secret do Facebook

**Passo 6: Adicionar botão no template**

```html
<a href="{% provider_login_url 'facebook' %}" class="btn btn-facebook">
    <i class="fab fa-facebook-f"></i>
    Continuar com Facebook
</a>

<style>
.btn-facebook {
    background: #1877F2;
}
.btn-facebook:hover {
    background: #166FE5;
}
</style>
```

### 3.2 GitHub OAuth

**Passo 1: Criar OAuth App no GitHub**

1. Acessar https://github.com/settings/developers
2. Clicar em "New OAuth App"
3. Preencher:
   - Application name: `CGBookstore`
   - Homepage URL: `http://localhost:8000` (dev)
   - Authorization callback URL: `http://localhost:8000/accounts/github/login/callback/`
4. Clicar em "Register application"
5. Copiar:
   - Client ID: `Iv1.abcdef1234567890`
   - Client Secret: (clicar em "Generate a new client secret")

**Passo 2: Adicionar provider no Django**

```python
# settings.py
INSTALLED_APPS = [
    # ...
    'allauth.socialaccount.providers.github',  # ← ADICIONAR
]

SOCIALACCOUNT_PROVIDERS = {
    # ... Google e Facebook existentes
    'github': {
        'SCOPE': [
            'user',
            'repo',
            'read:org',
        ],
        'APP': {
            'client_id': config('GITHUB_CLIENT_ID', default=''),
            'secret': config('GITHUB_CLIENT_SECRET', default=''),
            'key': ''
        }
    }
}
```

**Passo 3: `.env`:**

```bash
GITHUB_CLIENT_ID=Iv1.abcdef1234567890
GITHUB_CLIENT_SECRET=ghp_abcdefghijklmnopqrstuvwxyz123456
```

**Passo 4: Criar Social App no Admin**

Provider: GitHub

**Passo 5: Botão no template**

```html
<a href="{% provider_login_url 'github' %}" class="btn btn-github">
    <i class="fab fa-github"></i>
    Continuar com GitHub
</a>

<style>
.btn-github {
    background: #24292e;
}
.btn-github:hover {
    background: #1b1f23;
}
</style>
```

### 3.3 Microsoft OAuth (Opcional)

**Passo 1: Criar App no Azure**

1. Acessar https://portal.azure.com/
2. Ir em "Azure Active Directory" > "App registrations"
3. Clicar em "New registration"
4. Preencher:
   - Name: `CGBookstore`
   - Supported account types: "Accounts in any organizational directory and personal Microsoft accounts"
   - Redirect URI: `http://localhost:8000/accounts/microsoft/login/callback/`
5. Copiar:
   - Application (client) ID
   - Criar Client Secret em "Certificates & secrets"

**Passo 2: Adicionar provider no Django**

```python
# settings.py
INSTALLED_APPS = [
    # ...
    'allauth.socialaccount.providers.microsoft',  # ← ADICIONAR
]

SOCIALACCOUNT_PROVIDERS = {
    # ... outros providers
    'microsoft': {
        'APP': {
            'client_id': config('MICROSOFT_CLIENT_ID', default=''),
            'secret': config('MICROSOFT_CLIENT_SECRET', default=''),
            'key': ''
        }
    }
}
```

### 3.4 Template Completo com Todos os Providers

```html
{% load socialaccount %}

<div class="social-login-buttons">
    <!-- Google -->
    <a href="{% provider_login_url 'google' %}" class="btn btn-social btn-google">
        <i class="fab fa-google"></i>
        Continuar com Google
    </a>

    <!-- Facebook -->
    <a href="{% provider_login_url 'facebook' %}" class="btn btn-social btn-facebook">
        <i class="fab fa-facebook-f"></i>
        Continuar com Facebook
    </a>

    <!-- GitHub -->
    <a href="{% provider_login_url 'github' %}" class="btn btn-social btn-github">
        <i class="fab fa-github"></i>
        Continuar com GitHub
    </a>

    <!-- Microsoft (Opcional) -->
    <a href="{% provider_login_url 'microsoft' %}" class="btn btn-social btn-microsoft">
        <i class="fab fa-microsoft"></i>
        Continuar com Microsoft
    </a>
</div>

<style>
.social-login-buttons {
    display: flex;
    flex-direction: column;
    gap: 12px;
    margin-bottom: 24px;
}

.btn-social {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    padding: 12px 20px;
    border: none;
    border-radius: 6px;
    font-size: 15px;
    font-weight: 500;
    color: white;
    text-decoration: none;
    transition: all 0.2s ease;
    cursor: pointer;
}

.btn-social:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.btn-social i {
    margin-right: 12px;
    font-size: 18px;
}

.btn-google {
    background: #4285F4;
}
.btn-google:hover {
    background: #357AE8;
}

.btn-facebook {
    background: #1877F2;
}
.btn-facebook:hover {
    background: #166FE5;
}

.btn-github {
    background: #24292e;
}
.btn-github:hover {
    background: #1b1f23;
}

.btn-microsoft {
    background: #00A4EF;
}
.btn-microsoft:hover {
    background: #0078D4;
}
</style>
```

---

## Fase 4: Customizações

### 4.1 Conectar UserProfile Automaticamente

**Problema:** Quando usuário faz login social, User é criado mas UserProfile não é preenchido com dados do provider.

**Solução:** Criar adapter customizado.

**Criar `accounts/adapters.py`:**

```python
from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings


class CustomAccountAdapter(DefaultAccountAdapter):
    """
    Adapter para customizar comportamento de accounts.
    """

    def is_open_for_signup(self, request):
        """
        Permite ou bloqueia novos registros.
        """
        return getattr(settings, 'ACCOUNT_ALLOW_REGISTRATION', True)

    def save_user(self, request, user, form, commit=True):
        """
        Salva usuário com dados extras.
        """
        user = super().save_user(request, user, form, commit=False)

        # Adicionar lógica customizada aqui se necessário

        if commit:
            user.save()

        return user


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Adapter para customizar comportamento de social accounts.
    """

    def pre_social_login(self, request, sociallogin):
        """
        Chamado quando usuário faz social login.
        Conecta conta social a User existente se email bater.
        """
        # Se usuário já está logado, não fazer nada
        if request.user.is_authenticated:
            return

        # Se não tem email, não pode conectar
        if not sociallogin.email_addresses:
            return

        # Pegar email do social login
        email = sociallogin.email_addresses[0].email

        # Buscar User existente com esse email
        from django.contrib.auth.models import User
        try:
            user = User.objects.get(email=email)
            # Conectar social account ao user existente
            sociallogin.connect(request, user)
        except User.DoesNotExist:
            pass

    def populate_user(self, request, sociallogin, data):
        """
        Popula User com dados do provider social.
        """
        user = super().populate_user(request, sociallogin, data)

        # Extrair dados do provider
        provider = sociallogin.account.provider
        extra_data = sociallogin.account.extra_data

        # Preencher campos do User
        if provider == 'google':
            user.first_name = extra_data.get('given_name', '')
            user.last_name = extra_data.get('family_name', '')

        elif provider == 'facebook':
            user.first_name = extra_data.get('first_name', '')
            user.last_name = extra_data.get('last_name', '')

        elif provider == 'github':
            # GitHub não fornece nome separado
            name = extra_data.get('name', '')
            if name:
                parts = name.split(' ', 1)
                user.first_name = parts[0]
                user.last_name = parts[1] if len(parts) > 1 else ''

        return user

    def save_user(self, request, sociallogin, form=None):
        """
        Salva User após social login.
        Atualiza UserProfile com dados do provider.
        """
        user = super().save_user(request, sociallogin, form)

        # Pegar ou criar UserProfile (signal já deve ter criado)
        try:
            profile = user.userprofile
        except:
            from accounts.models import UserProfile
            profile = UserProfile.objects.create(user=user)

        # Extrair dados do provider
        provider = sociallogin.account.provider
        extra_data = sociallogin.account.extra_data

        # Preencher UserProfile
        if provider == 'google':
            # Avatar do Google
            if 'picture' in extra_data:
                profile.avatar = extra_data['picture']

            # Localização (locale)
            if 'locale' in extra_data:
                profile.preferred_language = extra_data['locale']

        elif provider == 'facebook':
            # Avatar do Facebook
            if 'id' in extra_data:
                profile.avatar = f"https://graph.facebook.com/{extra_data['id']}/picture?type=large"

            # Localização
            if 'location' in extra_data:
                profile.location = extra_data['location'].get('name', '')

        elif provider == 'github':
            # Avatar do GitHub
            if 'avatar_url' in extra_data:
                profile.avatar = extra_data['avatar_url']

            # Website
            if 'blog' in extra_data and extra_data['blog']:
                profile.website = extra_data['blog']

            # Localização
            if 'location' in extra_data:
                profile.location = extra_data['location']

            # Bio
            if 'bio' in extra_data and extra_data['bio']:
                profile.bio = extra_data['bio']

        profile.save()

        return user
```

**Configurar em `settings.py`:**

```python
ACCOUNT_ADAPTER = 'accounts.adapters.CustomAccountAdapter'
SOCIALACCOUNT_ADAPTER = 'accounts.adapters.CustomSocialAccountAdapter'
```

### 4.2 Customizar Templates

**Estratégia:** Criar templates que sobrescrevem os do allauth.

**Estrutura:**

```
templates/
├── account/               # Sobrescreve allauth/templates/account/
│   ├── login.html
│   ├── signup.html
│   ├── logout.html
│   ├── password_reset.html
│   └── email/
│       ├── email_confirmation_message.txt
│       └── password_reset_key_message.txt
└── socialaccount/         # Sobrescreve allauth/templates/socialaccount/
    ├── connections.html   # Página de gerenciar contas sociais
    └── signup.html        # Signup via social (pedir dados extras)
```

**Exemplo: `templates/account/login.html`**

Já mostramos anteriormente, mas agora integrado com base.html:

```html
{% extends 'base.html' %}
{% load socialaccount %}

{% block title %}Login - CGBookstore{% endblock %}

{% block content %}
<div class="auth-container">
    <div class="auth-card">
        <h1 class="auth-title">Bem-vindo de volta!</h1>
        <p class="auth-subtitle">Faça login para continuar sua jornada literária</p>

        <!-- Social Login Buttons -->
        <div class="social-login-buttons">
            <a href="{% provider_login_url 'google' %}" class="btn btn-social btn-google">
                <i class="fab fa-google"></i>
                <span>Continuar com Google</span>
            </a>

            <a href="{% provider_login_url 'facebook' %}" class="btn btn-social btn-facebook">
                <i class="fab fa-facebook-f"></i>
                <span>Continuar com Facebook</span>
            </a>

            <a href="{% provider_login_url 'github' %}" class="btn btn-social btn-github">
                <i class="fab fa-github"></i>
                <span>Continuar com GitHub</span>
            </a>
        </div>

        <!-- Divider -->
        <div class="divider">
            <span>ou continue com email</span>
        </div>

        <!-- Traditional Login Form -->
        <form method="post" class="auth-form">
            {% csrf_token %}

            {% if form.non_field_errors %}
                <div class="alert alert-error">
                    {{ form.non_field_errors }}
                </div>
            {% endif %}

            <div class="form-group">
                <label for="id_login">Usuário ou Email</label>
                <input
                    type="text"
                    name="login"
                    id="id_login"
                    class="form-control"
                    placeholder="Digite seu usuário ou email"
                    required
                    autofocus
                >
                {% if form.login.errors %}
                    <span class="error-message">{{ form.login.errors }}</span>
                {% endif %}
            </div>

            <div class="form-group">
                <label for="id_password">Senha</label>
                <input
                    type="password"
                    name="password"
                    id="id_password"
                    class="form-control"
                    placeholder="Digite sua senha"
                    required
                >
                {% if form.password.errors %}
                    <span class="error-message">{{ form.password.errors }}</span>
                {% endif %}
            </div>

            <div class="form-options">
                <label class="checkbox-label">
                    <input type="checkbox" name="remember" id="id_remember">
                    <span>Lembrar de mim</span>
                </label>

                <a href="{% url 'account_reset_password' %}" class="link-secondary">
                    Esqueceu a senha?
                </a>
            </div>

            <button type="submit" class="btn btn-primary btn-block">
                Entrar
            </button>
        </form>

        <!-- Sign Up Link -->
        <div class="auth-footer">
            <p>Não tem uma conta? <a href="{% url 'account_signup' %}">Cadastre-se grátis</a></p>
        </div>
    </div>
</div>

<style>
/* Adicionar estilos customizados */
</style>
{% endblock %}
```

**Exemplo: `templates/socialaccount/connections.html`**

Página para gerenciar contas sociais linkadas:

```html
{% extends 'base.html' %}
{% load socialaccount %}

{% block title %}Contas Conectadas - CGBookstore{% endblock %}

{% block content %}
<div class="container">
    <div class="profile-section">
        <h1>Contas Conectadas</h1>
        <p>Gerencie suas contas sociais conectadas ao CGBookstore</p>

        {% if form.accounts %}
            <div class="connected-accounts">
                {% for base_account in form.accounts %}
                    {% with base_account.get_provider_account as account %}
                        <div class="account-card">
                            <div class="account-icon">
                                {% if account.provider == 'google' %}
                                    <i class="fab fa-google"></i>
                                {% elif account.provider == 'facebook' %}
                                    <i class="fab fa-facebook-f"></i>
                                {% elif account.provider == 'github' %}
                                    <i class="fab fa-github"></i>
                                {% endif %}
                            </div>

                            <div class="account-info">
                                <h3>{{ account.get_provider.name }}</h3>
                                <p>{{ account }}</p>
                            </div>

                            <div class="account-actions">
                                <form method="post" action="{% url 'socialaccount_connections' %}">
                                    {% csrf_token %}
                                    <input type="hidden" name="account" value="{{ base_account.id }}">
                                    <button type="submit" class="btn btn-danger btn-sm">
                                        Desconectar
                                    </button>
                                </form>
                            </div>
                        </div>
                    {% endwith %}
                {% endfor %}
            </div>
        {% else %}
            <p class="no-accounts">Você ainda não conectou nenhuma conta social.</p>
        {% endif %}

        <!-- Add New Account -->
        <div class="add-accounts">
            <h2>Conectar Nova Conta</h2>

            <div class="social-buttons">
                <a href="{% provider_login_url 'google' process='connect' %}" class="btn btn-google">
                    <i class="fab fa-google"></i> Conectar Google
                </a>

                <a href="{% provider_login_url 'facebook' process='connect' %}" class="btn btn-facebook">
                    <i class="fab fa-facebook-f"></i> Conectar Facebook
                </a>

                <a href="{% provider_login_url 'github' process='connect' %}" class="btn btn-github">
                    <i class="fab fa-github"></i> Conectar GitHub
                </a>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

### 4.3 Customizar Emails

**Sobrescrever templates de email:**

**`templates/account/email/email_confirmation_subject.txt`:**
```
Confirme seu email - CGBookstore
```

**`templates/account/email/email_confirmation_message.txt`:**
```
Olá {{ user.username }},

Obrigado por se cadastrar no CGBookstore!

Para confirmar seu email, clique no link abaixo:
{{ activate_url }}

Se você não se cadastrou no CGBookstore, ignore este email.

Atenciosamente,
Equipe CGBookstore
```

**`templates/account/email/password_reset_key_message.txt`:**
```
Olá {{ user.username }},

Você solicitou redefinir sua senha no CGBookstore.

Para criar uma nova senha, clique no link abaixo:
{{ password_reset_url }}

Se você não solicitou isso, ignore este email.

Atenciosamente,
Equipe CGBookstore
```

### 4.4 Adicionar Link "Gerenciar Contas" no Perfil

**Em `templates/accounts/edit_profile.html`:**

```html
<div class="profile-section">
    <h2>Contas Conectadas</h2>
    <p>Conecte ou desconecte contas sociais</p>
    <a href="{% url 'socialaccount_connections' %}" class="btn btn-secondary">
        Gerenciar Contas Sociais
    </a>
</div>
```

---

## Fase 5: Testes e Deploy

### 5.1 Testes Manuais

**Checklist de Testes:**

#### Login Tradicional
- [ ] Login com username funciona
- [ ] Login com email funciona
- [ ] Senha incorreta mostra erro apropriado
- [ ] Campos vazios mostram erro
- [ ] Redirecionamento após login está correto

#### Registro Tradicional
- [ ] Registro com dados válidos cria User
- [ ] UserProfile é criado automaticamente
- [ ] Email duplicado mostra erro
- [ ] Username duplicado mostra erro
- [ ] Senhas não coincidentes mostram erro
- [ ] Login automático após registro funciona

#### Password Reset
- [ ] Formulário de reset envia email
- [ ] Email contém link válido
- [ ] Link permite criar nova senha
- [ ] Nova senha funciona para login

#### Google OAuth
- [ ] Botão "Login com Google" redireciona para Google
- [ ] Após autorizar, retorna ao site
- [ ] User é criado com dados do Google
- [ ] UserProfile é criado e preenchido (avatar, etc.)
- [ ] SocialAccount é criado e linkado
- [ ] Login subsequente reconhece usuário existente

#### Facebook OAuth
- [ ] Mesmo checklist do Google

#### GitHub OAuth
- [ ] Mesmo checklist do Google

#### Conexão de Contas
- [ ] User logado pode conectar conta social
- [ ] User logado pode desconectar conta social
- [ ] Email matching conecta contas automaticamente

#### Logout
- [ ] Logout via GET funciona (se permitido)
- [ ] Logout via POST funciona
- [ ] Redirecionamento após logout está correto

### 5.2 Testes Automatizados

**Criar `accounts/tests/test_allauth.py`:**

```python
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from allauth.socialaccount.models import SocialAccount, SocialApp
from django.contrib.sites.models import Site


class AllauthIntegrationTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.site = Site.objects.get_current()

    def test_login_page_loads(self):
        """Testa se página de login carrega"""
        response = self.client.get(reverse('account_login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Login')

    def test_signup_page_loads(self):
        """Testa se página de cadastro carrega"""
        response = self.client.get(reverse('account_signup'))
        self.assertEqual(response.status_code, 200)

    def test_user_can_signup(self):
        """Testa registro de novo usuário"""
        response = self.client.post(reverse('account_signup'), {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
        })

        # Verifica se user foi criado
        self.assertTrue(User.objects.filter(username='testuser').exists())

        # Verifica se UserProfile foi criado
        user = User.objects.get(username='testuser')
        self.assertTrue(hasattr(user, 'userprofile'))

    def test_user_can_login(self):
        """Testa login de usuário"""
        # Criar user
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        # Tentar login
        response = self.client.post(reverse('account_login'), {
            'login': 'testuser',
            'password': 'testpass123',
        })

        # Verifica se está autenticado
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_social_app_exists(self):
        """Testa se social apps estão configurados"""
        google_app = SocialApp.objects.filter(provider='google').first()
        self.assertIsNotNone(google_app)
        self.assertIn(self.site, google_app.sites.all())


class SocialAccountTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_social_account_creation(self):
        """Testa criação de conta social"""
        social_account = SocialAccount.objects.create(
            user=self.user,
            provider='google',
            uid='123456789',
            extra_data={'email': 'test@example.com'}
        )

        self.assertEqual(social_account.user, self.user)
        self.assertEqual(social_account.provider, 'google')

    def test_user_can_have_multiple_social_accounts(self):
        """Testa se user pode ter múltiplas contas sociais"""
        SocialAccount.objects.create(
            user=self.user,
            provider='google',
            uid='123456789'
        )

        SocialAccount.objects.create(
            user=self.user,
            provider='facebook',
            uid='987654321'
        )

        self.assertEqual(self.user.socialaccount_set.count(), 2)
```

**Executar testes:**

```bash
python manage.py test accounts.tests.test_allauth
```

### 5.3 Preparar para Produção

**1. Variáveis de Ambiente**

Criar `cgbookstore/settings/production.py`:

```python
from .base import *

DEBUG = False

ALLOWED_HOSTS = ['cgbookstore.com', 'www.cgbookstore.com']

# HTTPS
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Social auth URLs (produção)
# Atualizar redirect URIs nos providers para usar HTTPS
```

**2. Atualizar Redirect URIs nos Providers**

**Google Cloud Console:**
- Authorized redirect URIs: `https://cgbookstore.com/accounts/google/login/callback/`

**Facebook Developers:**
- Valid OAuth Redirect URIs: `https://cgbookstore.com/accounts/facebook/login/callback/`

**GitHub OAuth:**
- Authorization callback URL: `https://cgbookstore.com/accounts/github/login/callback/`

**3. Atualizar Site no Admin**

```python
from django.contrib.sites.models import Site

site = Site.objects.get(pk=1)
site.domain = 'cgbookstore.com'
site.name = 'CGBookstore'
site.save()
```

**4. Configurar Email Backend**

```python
# settings/production.py

# Usar serviço real (SendGrid, Mailgun, SES, etc.)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'apikey'
EMAIL_HOST_PASSWORD = config('SENDGRID_API_KEY')
DEFAULT_FROM_EMAIL = 'noreply@cgbookstore.com'
```

**5. Verificação de Email em Produção**

```python
# settings/production.py
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'  # Obrigatório em produção
```

### 5.4 Deploy Checklist

✅ Antes de fazer deploy:
- [ ] Todas as variáveis de ambiente configuradas
- [ ] `.env` file não está commitado
- [ ] Redirect URIs atualizados para produção
- [ ] Site configurado com domínio de produção
- [ ] HTTPS habilitado e funcionando
- [ ] SESSION_COOKIE_SECURE = True
- [ ] CSRF_COOKIE_SECURE = True
- [ ] Email backend configurado
- [ ] Testes manuais realizados
- [ ] Testes automatizados passando
- [ ] Documentação atualizada

---

## Troubleshooting

### Erro: "The redirect_uri MUST match the registered callback URL"

**Causa:** Redirect URI configurado no provider não bate com o URL real.

**Solução:**
1. Verificar URL exata em `http://localhost:8000/accounts/<provider>/login/callback/`
2. Conferir se está configurado exatamente assim no provider
3. Atenção: `http` vs `https`, trailing slash, porta

### Erro: "SocialApp matching query does not exist"

**Causa:** Provider não foi configurado no admin.

**Solução:**
1. Acessar admin: `/admin/socialaccount/socialapp/`
2. Criar social app para o provider
3. Verificar se Site está selecionado

### Erro: "Invalid client_id"

**Causa:** Client ID incorreto ou não configurado.

**Solução:**
1. Verificar `.env` file
2. Conferir se variável está sendo carregada: `python manage.py shell` → `from django.conf import settings` → `print(settings.GOOGLE_CLIENT_ID)`
3. Recriar credentials no provider se necessário

### Erro: Email verification not working

**Causa:** Email backend não configurado ou bloqueado.

**Solução:**
1. Em desenvolvimento: `EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'`
2. Em produção: Configurar SMTP real
3. Verificar logs do Django

### Erro: UserProfile not created for social login

**Causa:** Signal não disparou ou adapter não está configurado.

**Solução:**
1. Verificar se `SOCIALACCOUNT_ADAPTER` está configurado
2. Verificar se signal está registrado em `apps.py`
3. Debug: adicionar `print()` statements no adapter

### Erro: "This account is already connected to another user"

**Causa:** Tentando conectar conta social que já está linkada.

**Solução:**
1. Desconectar do outro usuário primeiro
2. Ou fazer login com o usuário original
3. Verificar em `/admin/socialaccount/socialaccount/`

### Provider não aparece na lista

**Causa:** App não adicionado em `INSTALLED_APPS`.

**Solução:**
1. Adicionar `allauth.socialaccount.providers.<provider>` em `INSTALLED_APPS`
2. Executar `python manage.py migrate`
3. Reiniciar servidor

---

## Checklist Final

### Configuração
- [ ] django-allauth instalado
- [ ] Apps adicionados em `INSTALLED_APPS`
- [ ] `SITE_ID = 1` configurado
- [ ] Authentication backends configurados
- [ ] URLs adicionados corretamente
- [ ] Migrações executadas
- [ ] Site configurado no admin

### Google OAuth
- [ ] Projeto criado no Google Cloud
- [ ] OAuth credentials criadas
- [ ] Redirect URI configurado
- [ ] Provider app instalado
- [ ] Configurações em `settings.py`
- [ ] Social App criado no admin
- [ ] Botão funcionando no template
- [ ] Login testado e funcionando

### Providers Adicionais
- [ ] Facebook configurado (se aplicável)
- [ ] GitHub configurado (se aplicável)
- [ ] Microsoft configurado (se aplicável)
- [ ] Todos os botões no template
- [ ] Todos testados

### Customizações
- [ ] Adapters criados
- [ ] UserProfile populado com dados sociais
- [ ] Templates customizados
- [ ] Emails customizados
- [ ] Página de gerenciar contas criada

### Testes
- [ ] Login tradicional funciona
- [ ] Registro funciona
- [ ] Password reset funciona
- [ ] Google OAuth funciona
- [ ] Outros providers funcionam
- [ ] Conexão de contas funciona
- [ ] Testes automatizados passando

### Produção
- [ ] Variáveis de ambiente configuradas
- [ ] Redirect URIs atualizados
- [ ] HTTPS habilitado
- [ ] Email backend configurado
- [ ] Verificação de email habilitada
- [ ] Site configurado com domínio de produção

---

## Próximos Passos (Além deste Plano)

1. **Two-Factor Authentication (2FA)**
   - Instalar `django-allauth-2fa`
   - Configurar TOTP
   - Adicionar backup codes

2. **Rate Limiting**
   - Instalar `django-ratelimit`
   - Limitar tentativas de login
   - Proteger contra brute force

3. **Account Management**
   - Permitir deletar conta
   - Exportar dados pessoais (GDPR)
   - Gerenciar privacidade

4. **Analytics**
   - Rastrear métodos de login
   - Taxas de conversão
   - Providers mais usados

5. **UX Enhancements**
   - Loading states nos botões
   - Mensagens de erro melhores
   - Animações

---

**Documento criado em:** 2025-11-05
**Última atualização:** 2025-11-05
**Versão:** 1.0
**Status:** Pronto para implementação
