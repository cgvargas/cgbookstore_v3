# Guia Completo: Configuração OAuth (Google e Facebook)

**Data:** 2025-11-05
**Projeto:** CGBookstore v3
**Objetivo:** Passo-a-passo completo para configurar autenticação social

---

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Google OAuth - Configuração Completa](#google-oauth---configuração-completa)
3. [Facebook OAuth - Configuração Completa](#facebook-oauth---configuração-completa)
4. [Configurar no Django Admin](#configurar-no-django-admin)
5. [Testar Autenticação](#testar-autenticação)
6. [Troubleshooting](#troubleshooting)

---

## Visão Geral

### O Que Você Precisa

- Conta Google (para Google OAuth)
- Conta Facebook (para Facebook OAuth)
- Acesso ao admin do Django
- Servidor local rodando (`python manage.py runserver`)

### Tempo Estimado

- **Google OAuth:** 15-20 minutos
- **Facebook OAuth:** 15-20 minutos
- **Configuração Django:** 5 minutos
- **Testes:** 10 minutos

**Total: ~1 hora**

### O Que Será Criado

✅ Login com Google
✅ Login com Facebook
✅ Cadastro via redes sociais
✅ Conexão de contas existentes
✅ Página de gerenciar contas sociais

---

## Google OAuth - Configuração Completa

### Passo 1: Acessar Google Cloud Console

1. Abra o navegador
2. Acesse: https://console.cloud.google.com/
3. Faça login com sua conta Google

### Passo 2: Criar Novo Projeto

1. No topo da página, clique em **"Select a project"** (dropdown)
2. Clique em **"NEW PROJECT"**
3. Preencha:
   - **Project name:** `CGBookstore`
   - **Organization:** (deixe padrão)
   - **Location:** (deixe padrão)
4. Clique em **"CREATE"**
5. Aguarde alguns segundos até o projeto ser criado
6. Selecione o projeto recém-criado no dropdown

### Passo 3: Configurar OAuth Consent Screen

**⚠️ IMPORTANTE:** Você DEVE configurar o OAuth Consent Screen ANTES de criar as credenciais.

1. No menu lateral (☰), vá em:
   - **APIs & Services** → **OAuth consent screen**

2. Selecione **User Type:**
   - **External** (permite qualquer usuário testar)
   - Clique em **"CREATE"**

3. **Passo 1: App information**
   - **App name:** `CGBookstore`
   - **User support email:** Seu email
   - **App logo:** (opcional, pode deixar vazio)
   - **App domain:** (deixe vazio por enquanto)
   - **Authorized domains:** (deixe vazio por enquanto)
   - **Developer contact information:** Seu email
   - Clique em **"SAVE AND CONTINUE"**

4. **Passo 2: Scopes**
   - Clique em **"ADD OR REMOVE SCOPES"**
   - Selecione:
     - ☑ `.../auth/userinfo.email`
     - ☑ `.../auth/userinfo.profile`
     - ☑ `openid`
   - Clique em **"UPDATE"**
   - Clique em **"SAVE AND CONTINUE"**

5. **Passo 3: Test users** (apenas se External)
   - Clique em **"ADD USERS"**
   - Adicione emails de usuários que vão testar (incluindo o seu)
   - Clique em **"ADD"**
   - Clique em **"SAVE AND CONTINUE"**

6. **Passo 4: Summary**
   - Revise as informações
   - Clique em **"BACK TO DASHBOARD"**

### Passo 4: Criar OAuth Client ID

1. No menu lateral, vá em:
   - **APIs & Services** → **Credentials**

2. Clique em **"+ CREATE CREDENTIALS"** (topo)

3. Selecione **"OAuth client ID"**

4. **Application type:** Selecione **"Web application"**

5. Preencha:
   - **Name:** `CGBookstore Web Client`

6. **Authorized JavaScript origins:**
   - Clique em **"+ ADD URI"**
   - Digite: `http://localhost:8000`
   - (Em produção, adicione: `https://seu-dominio.com`)

7. **Authorized redirect URIs:**
   - Clique em **"+ ADD URI"**
   - Digite: `http://localhost:8000/accounts/google/login/callback/`
   - **⚠️ ATENÇÃO:**
     - Copie EXATAMENTE como está acima
     - Inclua a barra `/` no final
     - `http` (não `https`) para desenvolvimento local
   - (Em produção, adicione: `https://seu-dominio.com/accounts/google/login/callback/`)

8. Clique em **"CREATE"**

### Passo 5: Copiar Credenciais

Aparecerá um popup com suas credenciais:

```
Client ID: 123456789-abcdefghijklmnop.apps.googleusercontent.com
Client Secret: GOCSPX-aBcDeFgHiJkLmNoPqRsTuVwXyZ
```

**⚠️ MUITO IMPORTANTE:**
- **Copie ambos** para um local seguro (Bloco de Notas)
- Você vai precisar deles no próximo passo
- Se perder, pode gerar novo Client Secret depois

### Passo 6: Adicionar Credenciais no .env

1. Abra o arquivo `.env` na raiz do projeto
   - Se não existe, crie copiando `.env.example`

2. Adicione as credenciais:

```bash
# Google OAuth
GOOGLE_CLIENT_ID=123456789-abcdefghijklmnop.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-aBcDeFgHiJkLmNoPqRsTuVwXyZ
```

3. Salve o arquivo

**⚠️ NUNCA COMMITE O .env NO GIT!**

### Passo 7: Configurar Social App no Django Admin

Vá para [Configurar no Django Admin](#configurar-no-django-admin) → Seção Google.

---

## Facebook OAuth - Configuração Completa

### Passo 1: Acessar Facebook Developers

1. Abra o navegador
2. Acesse: https://developers.facebook.com/
3. Faça login com sua conta Facebook
4. Se for primeira vez, aceite os termos

### Passo 2: Criar Novo App

1. No topo direito, clique em **"My Apps"**
2. Clique em **"Create App"**
3. Selecione caso de uso:
   - **"Consumer"** (para usuários comuns)
   - Clique em **"Next"**

4. Preencha informações do app:
   - **App name:** `CGBookstore`
   - **App contact email:** Seu email
   - **Business Account:** (deixe vazio)
   - Clique em **"Create app"**

5. Complete o desafio de segurança (se solicitado)

6. Você será redirecionado para o dashboard do app

### Passo 3: Adicionar Produto "Facebook Login"

1. No dashboard, na seção **"Add products to your app"**
2. Encontre **"Facebook Login"**
3. Clique em **"Set Up"**
4. Selecione plataforma: **"Web"**
5. Site URL: `http://localhost:8000`
6. Clique em **"Save"**
7. Clique em **"Continue"**
8. Pode pular os outros passos (já configuramos no Django)

### Passo 4: Configurar Facebook Login

1. No menu lateral, vá em:
   - **"Facebook Login"** → **"Settings"**

2. Em **"Valid OAuth Redirect URIs":**
   - Digite: `http://localhost:8000/accounts/facebook/login/callback/`
   - **⚠️ ATENÇÃO:**
     - Copie EXATAMENTE como está acima
     - Inclua a barra `/` no final
     - `http` (não `https`) para desenvolvimento local
   - (Em produção, adicione: `https://seu-dominio.com/accounts/facebook/login/callback/`)

3. Role para baixo e clique em **"Save Changes"**

### Passo 5: Configurar Informações Básicas do App

1. No menu lateral, vá em:
   - **"Settings"** → **"Basic"**

2. Preencha informações obrigatórias:
   - **App Domains:** `localhost` (desenvolvimento)
   - **Privacy Policy URL:** `http://localhost:8000/privacy/` (criar depois)
   - **Terms of Service URL:** `http://localhost:8000/terms/` (criar depois)
   - **User Data Deletion:** (pode deixar para depois)

3. Role para baixo e clique em **"Save Changes"**

### Passo 6: Copiar Credenciais

1. Ainda em **"Settings"** → **"Basic"**
2. Você verá:

```
App ID: 1234567890123456
App Secret: [Clique em "Show" para revelar]
```

3. Clique em **"Show"** no App Secret
4. Digite sua senha do Facebook
5. **Copie ambos** para um local seguro (Bloco de Notas)

### Passo 7: Adicionar Credenciais no .env

1. Abra o arquivo `.env` na raiz do projeto

2. Adicione as credenciais:

```bash
# Facebook OAuth
FACEBOOK_APP_ID=1234567890123456
FACEBOOK_APP_SECRET=abcdef1234567890abcdef1234567890
```

3. Salve o arquivo

### Passo 8: Modo de Desenvolvimento

**⚠️ IMPORTANTE:** Por padrão, apps do Facebook ficam em modo "Development".

**Em modo Development:**
- ✅ Você pode testar
- ✅ Usuários adicionados em "Roles" podem testar
- ❌ Usuários externos NÃO podem usar

**Para adicionar testadores:**
1. Menu lateral: **"Roles"** → **"Roles"**
2. Clique em **"Add Testers"**
3. Digite emails ou IDs de usuários do Facebook
4. Clique em **"Submit"**

**Para modo Production (depois):**
1. Menu lateral: **"Settings"** → **"Basic"**
2. No topo, altere status de **"Development"** para **"Live"**
3. Será necessário passar por revisão do Facebook (fornecendo políticas de privacidade, etc.)

### Passo 9: Configurar Social App no Django Admin

Vá para [Configurar no Django Admin](#configurar-no-django-admin) → Seção Facebook.

---

## Configurar no Django Admin

### Passo 1: Iniciar Servidor (se não estiver rodando)

```bash
python manage.py runserver
```

### Passo 2: Acessar Admin

1. Abra o navegador
2. Acesse: `http://localhost:8000/admin/`
3. Faça login com sua conta de superusuário

### Passo 3: Verificar Site

1. No admin, procure por **"Sites"** (SITES)
2. Clique em **"Sites"**
3. Deve existir 1 site:
   - **Domain name:** `localhost:8000`
   - **Display name:** `CGBookstore`
4. Se não existe ou está errado:
   - Edite o site com ID=1
   - Configure domain e name corretos
   - Salve

### Passo 4: Configurar Google (Social Applications)

1. No admin, procure por **"Social applications"** (SOCIAL ACCOUNTS)
2. Clique em **"Social applications"**
3. Clique em **"ADD SOCIAL APPLICATION"** (canto superior direito)
4. Preencha:

   - **Provider:** Selecione **"Google"** no dropdown
   - **Name:** `Google` (pode ser qualquer nome, é apenas para identificação)
   - **Client id:** Cole o Client ID que copiou do Google Cloud
   - **Secret key:** Cole o Client Secret que copiou do Google Cloud
   - **Key:** (deixe vazio)
   - **Sites:**
     - No campo "Available sites", selecione `localhost:8000`
     - Clique na seta → para mover para "Chosen sites"
   - **Settings:** (deixe vazio, JSON será gerado automaticamente)

5. Clique em **"SAVE"**

### Passo 5: Configurar Facebook (Social Applications)

1. Ainda em **"Social applications"**
2. Clique em **"ADD SOCIAL APPLICATION"** novamente
3. Preencha:

   - **Provider:** Selecione **"Facebook"** no dropdown
   - **Name:** `Facebook`
   - **Client id:** Cole o App ID que copiou do Facebook
   - **Secret key:** Cole o App Secret que copiou do Facebook
   - **Key:** (deixe vazio)
   - **Sites:**
     - Selecione `localhost:8000`
     - Clique na seta → para "Chosen sites"

4. Clique em **"SAVE"**

### Passo 6: Verificar Configuração

Você deve ter agora 2 Social Applications:
- ✅ Google
- ✅ Facebook

Ambos com o site `localhost:8000` selecionado.

---

## Testar Autenticação

### Teste 1: Login com Google

1. Abra o navegador (modo anônimo/privado recomendado)
2. Acesse: `http://localhost:8000/accounts/login/`
3. Você deve ver:
   - Botão "Continuar com Google" (azul)
   - Botão "Continuar com Facebook" (azul)
   - Formulário tradicional de login

4. Clique em **"Continuar com Google"**

5. Será redirecionado para página do Google

6. Faça login com sua conta Google

7. Autorize o app "CGBookstore"

8. Será redirecionado de volta para `http://localhost:8000/`

9. **Verifique:**
   - Você está logado (nome aparece no topo)
   - User foi criado no Django
   - UserProfile foi criado e populado com dados do Google

10. **No admin**, verifique:
    - `http://localhost:8000/admin/auth/user/`
    - Deve ter novo usuário com seu email do Google
    - `http://localhost:8000/admin/socialaccount/socialaccount/`
    - Deve ter registro da conta Google linkada

### Teste 2: Login com Facebook

1. Faça logout: `http://localhost:8000/accounts/logout/`

2. Vá para login: `http://localhost:8000/accounts/login/`

3. Clique em **"Continuar com Facebook"**

4. Faça login no Facebook

5. Autorize o app "CGBookstore"

6. Será redirecionado de volta

7. **Verifique** (igual ao Google)

### Teste 3: Conectar Conta Existente

**Cenário:** Usuário já tem conta com email `teste@example.com`, depois faz login social com mesmo email.

1. Crie um usuário tradicional:
   - `http://localhost:8000/accounts/signup/`
   - Username: `teste_user`
   - Email: `teste@example.com`
   - Senha: `senha123`

2. Faça logout

3. No Google Cloud Console ou Facebook, adicione `teste@example.com` como testador

4. Vá para login: `http://localhost:8000/accounts/login/`

5. Clique em "Continuar com Google"

6. Faça login com `teste@example.com`

7. **Resultado esperado:**
   - Conta Google é **conectada** ao usuário existente `teste_user`
   - Não cria usuário duplicado
   - Pode fazer login com Google OU email/senha

### Teste 4: Gerenciar Contas Sociais

1. Faça login

2. Vá para: `http://localhost:8000/socialaccount/connections/`

3. Você deve ver:
   - Lista de contas conectadas (Google e/ou Facebook)
   - Botões para conectar novas contas
   - Botões para desconectar contas

4. Teste conectar uma segunda conta (se só conectou Google, conecte Facebook)

5. Teste desconectar uma conta
   - Clique em "Desconectar"
   - Confirme
   - Conta deve ser removida da lista

### Teste 5: Dados do UserProfile

1. Faça login social (Google ou Facebook)

2. Vá para: `http://localhost:8000/profile/edit/`

3. **Verifique:**
   - Avatar foi preenchido com foto do Google/Facebook
   - Preferred language foi configurado
   - (Se Facebook) Location pode estar preenchida

4. **No código:**
```bash
python manage.py shell
```

```python
from django.contrib.auth.models import User

user = User.objects.get(username='seu_username')
print(f"Avatar: {user.userprofile.avatar}")
print(f"Language: {user.userprofile.preferred_language}")
print(f"Location: {user.userprofile.location}")

# Ver dados da conta social
from allauth.socialaccount.models import SocialAccount
social = SocialAccount.objects.get(user=user)
print(f"Provider: {social.provider}")
print(f"Extra Data: {social.extra_data}")
```

---

## Troubleshooting

### Erro: "redirect_uri_mismatch"

**Causa:** Redirect URI configurado no Google/Facebook não bate com o usado pelo Django.

**Solução:**
1. Verificar URL exata que Django está usando:
   - Para Google: `http://localhost:8000/accounts/google/login/callback/`
   - Para Facebook: `http://localhost:8000/accounts/facebook/login/callback/`

2. Conferir se está **exatamente** assim no Google Cloud / Facebook:
   - Mesma porta (8000)
   - Barra `/` no final
   - `http` (não `https` em dev)

3. Depois de corrigir, aguarde alguns minutos (cache)

### Erro: "invalid_client" ou "App Not Setup"

**Causa:** Credenciais incorretas ou Social Application não configurado.

**Solução:**
1. Verificar `.env`:
   ```bash
   python manage.py shell
   >>> from django.conf import settings
   >>> print(settings.GOOGLE_CLIENT_ID)
   >>> print(settings.GOOGLE_CLIENT_SECRET)
   ```

2. Verificar Social Application no admin:
   - Client ID correto
   - Secret key correto
   - Site selecionado

3. Reiniciar servidor após mudar `.env`:
   ```bash
   Ctrl+C
   python manage.py runserver
   ```

### Erro: "SocialApp matching query does not exist"

**Causa:** Social Application não foi criado no admin.

**Solução:**
1. Acessar: `http://localhost:8000/admin/socialaccount/socialapp/`
2. Criar Social Application para Google e/ou Facebook
3. Verificar se Site está selecionado

### Erro: "Site matching query does not exist"

**Causa:** Site não configurado ou SITE_ID incorreto.

**Solução:**
```bash
python manage.py shell
```

```python
from django.contrib.sites.models import Site

# Ver sites existentes
sites = Site.objects.all()
for site in sites:
    print(f"ID: {site.id}, Domain: {site.domain}, Name: {site.name}")

# Atualizar site ID=1
site = Site.objects.get(pk=1)
site.domain = 'localhost:8000'
site.name = 'CGBookstore'
site.save()
```

### Botões Sociais Não Aparecem

**Causa:** Template não está carregando `{% load socialaccount %}`.

**Solução:**
1. Verificar se no topo do template tem:
   ```django
   {% load socialaccount %}
   ```

2. Verificar se botões usam:
   ```django
   {% provider_login_url 'google' %}
   {% provider_login_url 'facebook' %}
   ```

### UserProfile Não Populado com Dados

**Causa:** Adapter não está configurado ou signal não está funcionando.

**Solução:**
1. Verificar `settings.py`:
   ```python
   SOCIALACCOUNT_ADAPTER = 'accounts.adapters.CustomSocialAccountAdapter'
   ```

2. Verificar se `accounts/adapters.py` existe

3. Reiniciar servidor

4. Fazer novo login social (logout primeiro)

### Facebook: "App Not Setup"

**Causa:** App em modo Development e você não é testador.

**Solução:**
1. No Facebook Developers:
   - **"Roles"** → **"Roles"**
   - Adicione seu email como testador

2. Ou coloque app em modo Live (requer políticas de privacidade)

### Facebook: "Given URL is not allowed by the Application configuration"

**Causa:** Redirect URI não está em "Valid OAuth Redirect URIs".

**Solução:**
1. Facebook Developers
2. **"Facebook Login"** → **"Settings"**
3. Adicionar `http://localhost:8000/accounts/facebook/login/callback/`
4. Salvar

### Google: "Access blocked: Authorization Error"

**Causa:** App não verificado ou usuário não é testador.

**Solução:**
1. No Google Cloud Console:
   - **"OAuth consent screen"**
   - Adicionar usuários em **"Test users"**

2. Ou publicar app (requer verificação do Google)

### Conta Social Não Conecta a User Existente

**Causa:** Emails não batem ou configuração de auto-connect desabilitada.

**Solução:**
1. Verificar `settings.py`:
   ```python
   SOCIALACCOUNT_EMAIL_AUTHENTICATION = True
   SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True
   ```

2. Verificar se emails são exatamente iguais

3. Verificar se email foi verificado

---

## 🎯 Checklist Final

Antes de considerar completo, verifique:

### Google OAuth
- [ ] Projeto criado no Google Cloud
- [ ] OAuth Consent Screen configurado
- [ ] OAuth Client ID criado
- [ ] Redirect URI correto (`http://localhost:8000/accounts/google/login/callback/`)
- [ ] Credenciais adicionadas no `.env`
- [ ] Social Application criada no admin
- [ ] Botão "Continuar com Google" aparece
- [ ] Login funciona e cria usuário
- [ ] UserProfile populado com avatar

### Facebook OAuth
- [ ] App criado no Facebook Developers
- [ ] Facebook Login configurado
- [ ] Valid OAuth Redirect URI correto
- [ ] Credenciais adicionadas no `.env`
- [ ] Social Application criada no admin
- [ ] Botão "Continuar com Facebook" aparece
- [ ] Login funciona e cria usuário
- [ ] UserProfile populado com avatar

### Django
- [ ] `SITE_ID = 1` em settings.py
- [ ] Authentication backends configurados
- [ ] Adapters configurados
- [ ] Templates customizados
- [ ] Página de connections acessível
- [ ] Conexão de contas existentes funciona

---

## 📚 Recursos Adicionais

### Google
- Documentação: https://developers.google.com/identity/protocols/oauth2
- Console: https://console.cloud.google.com/

### Facebook
- Documentação: https://developers.facebook.com/docs/facebook-login
- Dashboard: https://developers.facebook.com/apps/

### Django-allauth
- Documentação: https://docs.allauth.org/
- GitHub: https://github.com/pennersr/django-allauth

---

**Documento criado em:** 2025-11-05
**Última atualização:** 2025-11-05
**Versão:** 1.0
