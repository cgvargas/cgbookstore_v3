# 📧 Configurar Email no Render (Produção)

Data: 10/11/2025

## 🎯 Objetivo

Configurar SendGrid para enviar emails reais em produção no Render.

## 📋 Pré-requisitos

- ✅ API Key do SendGrid: `SG.YOUR_SENDGRID_API_KEY_HERE`
- ⚠️ **Single Sender precisa ser verificado**

## 🔧 Passo 1: Verificar Single Sender no SendGrid

### 1.1. Acessar SendGrid

1. Acesse: https://app.sendgrid.com/settings/sender_auth/senders
2. Faça login com sua conta SendGrid

### 1.2. Criar Single Sender

Clique em **"Create New Sender"** e preencha:

```
From Name: CGBookStore
From Email Address: SEU_EMAIL_PESSOAL@gmail.com (ou outlook.com)
Reply To: SEU_EMAIL_PESSOAL@gmail.com
Company Address: Rua Exemplo, 123
Company City: Sua Cidade
Company State: SP (ou seu estado)
Company Zip Code: 00000-000
Company Country: Brazil
```

**IMPORTANTE**: Use um email pessoal que você tenha acesso (Gmail, Outlook, etc.)

### 1.3. Confirmar Email

1. SendGrid vai enviar um email para `SEU_EMAIL_PESSOAL@gmail.com`
2. Abra seu email e procure mensagem do SendGrid
3. Clique no link de confirmação
4. Pronto! Single Sender verificado ✅

### 1.4. Verificar Status

Volte para: https://app.sendgrid.com/settings/sender_auth/senders

Você deve ver seu sender com status **"Verified"** ✅

## 🚀 Passo 2: Configurar Variáveis de Ambiente no Render

### 2.1. Acessar Render Dashboard

1. Acesse: https://dashboard.render.com/
2. Selecione seu Web Service (cgbookstore)
3. Vá em **"Environment"** no menu lateral

### 2.2. Adicionar/Atualizar Variáveis

Adicione ou atualize as seguintes variáveis de ambiente:

```bash
# Email Configuration (SendGrid)
DEFAULT_FROM_EMAIL=SEU_EMAIL_VERIFICADO@gmail.com
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=SG.YOUR_SENDGRID_API_KEY_HERE
```

**IMPORTANTE**:
- Substitua `SEU_EMAIL_VERIFICADO@gmail.com` pelo email que você verificou no passo 1
- Use o mesmo email que aparece como "Verified" no SendGrid

### 2.3. Exemplo de Preenchimento no Render

| Key | Value |
|-----|-------|
| `DEFAULT_FROM_EMAIL` | `seuemail@gmail.com` |
| `EMAIL_BACKEND` | `django.core.mail.backends.smtp.EmailBackend` |
| `EMAIL_HOST` | `smtp.sendgrid.net` |
| `EMAIL_PORT` | `587` |
| `EMAIL_USE_TLS` | `True` |
| `EMAIL_HOST_USER` | `apikey` |
| `EMAIL_HOST_PASSWORD` | `SG.YOUR_SENDGRID_API_KEY_HERE` |

### 2.4. Salvar Configurações

1. Clique em **"Save Changes"**
2. Render vai reiniciar automaticamente seu serviço
3. Aguarde o deploy terminar (1-2 minutos)

## 🧪 Passo 3: Testar em Produção

### 3.1. Criar Novo Usuário

1. Acesse seu site em produção: `https://seu-app.onrender.com/accounts/signup/`
2. Crie um usuário com **seu email real** (que você tem acesso)
3. Preencha o formulário e clique em "Sign Up"

### 3.2. Verificar Email

1. Verifique sua caixa de entrada (Gmail, Outlook, etc.)
2. Procure email com assunto: `[CGBookStore] Confirme seu cadastro na CGBookStore`
3. **Se não aparecer**: Verifique pasta de SPAM
4. Clique no link de confirmação

### 3.3. Fazer Login

1. Após confirmar, faça login: `https://seu-app.onrender.com/accounts/login/`
2. Use o username ou email + senha
3. Deve entrar normalmente ✅

### 3.4. Verificar Que Não Pede Confirmação Novamente

1. Faça logout
2. Faça login novamente
3. Deve entrar direto sem pedir confirmação ✅

## 📊 Passo 4: Monitorar Envios

### 4.1. SendGrid Activity Feed

1. Acesse: https://app.sendgrid.com/email_activity
2. Veja todos os emails enviados
3. Status de entrega, aberturas, cliques, etc.

### 4.2. Verificar Limites

- Plano Free: **100 emails/dia**
- Monitore em: https://app.sendgrid.com/statistics

## ⚠️ Troubleshooting

### Email não chega

**1. Verificar SendGrid Activity Feed**
- Acesse: https://app.sendgrid.com/email_activity
- Veja se o email foi enviado
- Cheque status: "Delivered", "Bounced", "Dropped"

**2. Verificar Single Sender**
- Acesse: https://app.sendgrid.com/settings/sender_auth/senders
- Status deve ser "Verified" ✅
- Email em `DEFAULT_FROM_EMAIL` deve ser o mesmo verificado

**3. Verificar Logs do Render**
- Render Dashboard → Seu serviço → Logs
- Procure por erros de SMTP ou email

**4. Email caiu no SPAM**
- Verifique pasta de spam/lixo eletrônico
- Marque como "não spam" para futuros emails

### Erro de Autenticação SMTP

**Causa**: API Key inválida ou Single Sender não verificado

**Solução**:
1. Verifique se Single Sender está "Verified"
2. Verifique se `DEFAULT_FROM_EMAIL` é o mesmo email verificado
3. Verifique se API Key está correta no Render

### Erro "Connection unexpectedly closed"

**Causa**: Firewall do Render ou API Key inválida

**Solução**:
1. Verificar API Key no SendGrid: https://app.sendgrid.com/settings/api_keys
2. Se necessário, criar nova API Key com "Mail Send" Full Access
3. Atualizar `EMAIL_HOST_PASSWORD` no Render

## 📋 Checklist Final

Antes de testar em produção, confirme:

- [ ] Single Sender verificado no SendGrid ✅
- [ ] Email verificado aparece com status "Verified"
- [ ] Variáveis de ambiente adicionadas no Render
- [ ] `DEFAULT_FROM_EMAIL` é o mesmo email verificado
- [ ] Deploy do Render concluído com sucesso
- [ ] Pronto para testar cadastro!

## 🎯 Diferenças: Desenvolvimento vs Produção

| Aspecto | Desenvolvimento (Local) | Produção (Render) |
|---------|------------------------|-------------------|
| **Backend** | `console.EmailBackend` | `smtp.EmailBackend` |
| **Emails** | Aparecem no terminal | Chegam na caixa real |
| **Single Sender** | Não necessário | **Obrigatório** |
| **DEFAULT_FROM_EMAIL** | Qualquer email | Email verificado |
| **Teste** | Copiar link do terminal | Abrir email na caixa |

## 📝 Variáveis de Ambiente - Resumo

```bash
# Produção (Render) - USE ESTAS
DEFAULT_FROM_EMAIL=seuemail@gmail.com
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=SG.YOUR_SENDGRID_API_KEY_HERE
```

## 🔐 Segurança

**NUNCA** commite a API Key no Git!

- ✅ Use variáveis de ambiente (Render Environment)
- ✅ `.env` está no `.gitignore`
- ❌ Não adicione API Key no código

## 📞 Suporte

Se tiver problemas:

1. **Verificar logs do Render**: Dashboard → Logs
2. **Verificar SendGrid Activity**: https://app.sendgrid.com/email_activity
3. **Documentação SendGrid**: https://docs.sendgrid.com/
4. **Render Docs**: https://render.com/docs

## ✅ Próximos Passos

Após configurar:

1. ✅ Testar cadastro em produção
2. ✅ Verificar email chega na caixa
3. ✅ Confirmar que login funciona
4. ✅ Monitorar SendGrid dashboard
5. ✅ Verificar limite de 100 emails/dia

**Boa configuração! 🚀**
