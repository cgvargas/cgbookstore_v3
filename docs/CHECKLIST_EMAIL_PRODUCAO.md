# ✅ Checklist: Configurar Email em Produção

## 📋 Passo a Passo Rápido

### 1️⃣ SendGrid - Verificar Single Sender (5 minutos)

- [ ] Acessar: https://app.sendgrid.com/settings/sender_auth/senders
- [ ] Clicar em **"Create New Sender"**
- [ ] Preencher formulário:
  - From Name: `CGBookStore`
  - From Email: Seu email pessoal (Gmail/Outlook)
  - Reply To: Mesmo email acima
  - Company: Dados fictícios (endereço, cidade, etc.)
- [ ] Clicar em **"Create"**
- [ ] Abrir sua caixa de email
- [ ] Procurar email do SendGrid
- [ ] Clicar no link de confirmação
- [ ] Voltar para SendGrid e verificar status **"Verified"** ✅

### 2️⃣ Render - Adicionar Variáveis (3 minutos)

- [ ] Acessar: https://dashboard.render.com/
- [ ] Selecionar seu Web Service (cgbookstore)
- [ ] Clicar em **"Environment"** no menu lateral
- [ ] Adicionar as seguintes variáveis (uma por vez):

```
DEFAULT_FROM_EMAIL → seuemail@gmail.com (o que você verificou!)
EMAIL_BACKEND → django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST → smtp.sendgrid.net
EMAIL_PORT → 587
EMAIL_USE_TLS → True
EMAIL_HOST_USER → apikey
EMAIL_HOST_PASSWORD → SG.YOUR_SENDGRID_API_KEY_HERE
```

- [ ] Clicar em **"Save Changes"**
- [ ] Aguardar deploy terminar (1-2 minutos)
- [ ] Verificar logs: sem erros ✅

### 3️⃣ Testar em Produção (5 minutos)

- [ ] Acessar: `https://seu-app.onrender.com/accounts/signup/`
- [ ] Criar novo usuário com **seu email real**
- [ ] Preencher formulário e enviar
- [ ] Verificar caixa de entrada (email chegou?) ✅
- [ ] Se não chegou: verificar SPAM
- [ ] Clicar no link de confirmação
- [ ] Fazer login
- [ ] Fazer logout e login novamente
- [ ] Verificar que NÃO pede confirmação de novo ✅

### 4️⃣ Monitorar (Opcional)

- [ ] Acessar: https://app.sendgrid.com/email_activity
- [ ] Ver emails enviados e status
- [ ] Verificar limite: https://app.sendgrid.com/statistics
- [ ] Tudo funcionando! 🎉

## 🚨 Problemas Comuns

### ❌ Email não chega

**Checklist:**
- [ ] Single Sender está "Verified"?
- [ ] `DEFAULT_FROM_EMAIL` é o mesmo email verificado?
- [ ] Verificou pasta de SPAM?
- [ ] SendGrid Activity mostra envio? (https://app.sendgrid.com/email_activity)

**Solução:** Verificar logs do Render e SendGrid Activity Feed

### ❌ Erro "Connection closed"

**Checklist:**
- [ ] API Key está correta?
- [ ] Single Sender verificado?
- [ ] Variáveis salvas no Render?
- [ ] Deploy terminou?

**Solução:** Verificar API Key e criar nova se necessário

### ❌ Email vai para SPAM

**Checklist:**
- [ ] Verificou pasta de SPAM?
- [ ] Marcou como "não spam"?

**Solução:** Normal em primeira vez, depois melhora

## 📝 Informações Importantes

### API Key SendGrid
```
SG.YOUR_SENDGRID_API_KEY_HERE
```

### URLs Úteis

- **SendGrid Single Sender**: https://app.sendgrid.com/settings/sender_auth/senders
- **SendGrid Activity Feed**: https://app.sendgrid.com/email_activity
- **SendGrid API Keys**: https://app.sendgrid.com/settings/api_keys
- **Render Dashboard**: https://dashboard.render.com/

### Limites

- **Plano Free SendGrid**: 100 emails/dia
- **Suficiente para**: Testes e pequenos projetos

## ✅ Status

- [x] Local (desenvolvimento): Console backend funcionando
- [ ] Produção (Render): Aguardando configuração
- [ ] Teste em produção: Aguardando

## 🎯 Próximo Passo

**AGORA**: Seguir passos 1, 2 e 3 acima para configurar em produção!

**Documentação completa**: [CONFIGURAR_EMAIL_RENDER.md](CONFIGURAR_EMAIL_RENDER.md)

**Variáveis para copiar**: [VARIAVEIS_RENDER_EMAIL.txt](VARIAVEIS_RENDER_EMAIL.txt)

---

**Boa sorte! Se tiver problemas, me avise.** 🚀
