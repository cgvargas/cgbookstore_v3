# INSTRUÇÕES PARA CONFIGURAR VARIÁVEIS NO RENDER

## ⚠️ IMPORTANTE: Verificar Deploy

Antes de testar, **aguarde o deploy terminar no Render**:

1. Acesse: https://dashboard.render.com
2. Vá em "cgbookstore" (seu web service)
3. Aguarde até ver: **"Deploy live"** (bolinha verde)

---

## 📧 VARIÁVEIS DE EMAIL (Brevo)

**IMPORTANTE**: Certifique-se de que estas variáveis estão configuradas no Render:

### Opção 1: Usar Brevo API (Recomendado)

```
USE_BREVO_API=True
EMAIL_HOST_PASSWORD=<SUA_BREVO_API_KEY_AQUI>
DEFAULT_FROM_EMAIL=cg.bookstore.online@outlook.com
```

**NOTA**: A API key do Brevo já está configurada no Render. Não precisa mudar!

### Opção 2: Usar SMTP Console (para debug)

```
USE_BREVO_API=False
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

---

## 🔧 COMO ADICIONAR/EDITAR VARIÁVEIS NO RENDER

1. Acesse https://dashboard.render.com
2. Clique no seu serviço "cgbookstore"
3. Vá na aba **"Environment"**
4. Procure a variável que deseja editar OU clique em **"Add Environment Variable"**
5. Configure:
   - **Key**: `USE_BREVO_API`
   - **Value**: `True`
6. Clique em **"Save Changes"**
7. **IMPORTANTE**: Render vai fazer redeploy automático

---

## 🧪 TESTAR APÓS DEPLOY

### 1. Limpar Cache do Navegador
- Chrome/Edge: `Ctrl + Shift + Delete` → Limpar cache
- Ou abrir janela anônima: `Ctrl + Shift + N`

### 2. Testar Login (NÃO signup!)
1. Acesse: https://cgbookstore-v3.onrender.com/accounts/login/
2. Use suas credenciais:
   - **Email ou Username**: claud
   - **Senha**: sua senha
3. **NÃO** acesse a página de CADASTRO (/signup/)!

### 3. Se Pedir Confirmação de Email
Se mesmo após login correto ele pedir confirmação:

**Verifique no Render Logs**:
1. No dashboard do Render → aba "Logs"
2. Procure por erros de email
3. Me passe os logs para análise

---

## 🐛 DEBUG EM PRODUÇÃO

Para verificar o que está acontecendo em produção, rode este comando no Render Shell:

```bash
# No dashboard do Render → aba "Shell"
python manage.py shell -c "from allauth.account.models import EmailAddress; from django.contrib.auth.models import User; u = User.objects.get(username='claud'); ea = EmailAddress.objects.get(user=u); print(f'Verified: {ea.verified}, Primary: {ea.primary}')"
```

---

## ✅ CHECKLIST

- [ ] Deploy no Render terminou (status "Deploy live")
- [ ] Variável `USE_BREVO_API=True` está configurada
- [ ] Variável `EMAIL_HOST_PASSWORD` tem a API key do Brevo
- [ ] Variável `DEFAULT_FROM_EMAIL` está configurada
- [ ] Cache do navegador foi limpo
- [ ] Testando com LOGIN (não signup)

---

## 🚨 SE O PROBLEMA PERSISTIR

Me envie:
1. Screenshot da tela que aparece ao fazer login
2. Logs do Render (últimas 50 linhas)
3. Confirmação de que as variáveis estão configuradas

**IMPORTANTE**: O problema pode ser que você está acessando a página de CADASTRO ao invés de LOGIN!

- ✅ CORRETO: https://cgbookstore-v3.onrender.com/accounts/login/
- ❌ ERRADO: https://cgbookstore-v3.onrender.com/accounts/signup/
