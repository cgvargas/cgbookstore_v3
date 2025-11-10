# Configuração de Email - CGBookStore

## Visão Geral

O sistema de confirmação de email está configurado usando **django-allauth** com verificação obrigatória (`mandatory`).

Quando um usuário se cadastra:
1. ✉️ Recebe um email de confirmação
2. 🔗 Clica no link de ativação
3. ✅ Email é verificado
4. 🎉 Pode fazer login na plataforma

---

## Configuração em Desenvolvimento

### 1. Console Backend (Padrão)

Em desenvolvimento, os emails são exibidos no console/terminal:

```bash
# .env
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

✅ **Vantagem**: Não precisa configurar SMTP
✅ **Uso**: Teste local rápido

Quando você criar um usuário, o email aparecerá no terminal onde o servidor está rodando.

---

## Configuração em Produção

### Opção 1: Gmail (Recomendado para testes)

#### Passo 1: Criar senha de aplicativo no Gmail

1. Acesse https://myaccount.google.com/security
2. Ative **Verificação em duas etapas**
3. Em "Senhas de app", gere uma nova senha
4. Copie a senha gerada (16 caracteres)

#### Passo 2: Configurar variáveis de ambiente

```bash
# .env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
DEFAULT_FROM_EMAIL=seu-email@gmail.com
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=xxxx-xxxx-xxxx-xxxx  # Senha de app gerada
```

#### Passo 3: Adicionar no Render

No Render Dashboard, adicione as variáveis de ambiente:

```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=xxxx-xxxx-xxxx-xxxx
DEFAULT_FROM_EMAIL=seu-email@gmail.com
```

---

### Opção 2: SendGrid (Recomendado para produção)

SendGrid oferece **100 emails gratuitos por dia**.

#### Passo 1: Criar conta no SendGrid

1. Acesse https://sendgrid.com/
2. Crie conta gratuita
3. Gere uma API Key

#### Passo 2: Configurar variáveis

```bash
# .env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
DEFAULT_FROM_EMAIL=noreply@seudominio.com
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=SG.xxxxxxxxxxxxxxxxxxxx  # API Key do SendGrid
```

---

### Opção 3: Mailgun

Mailgun oferece **5.000 emails gratuitos por mês**.

#### Configuração:

```bash
# .env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.mailgun.org
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=postmaster@seu-dominio.mailgun.org
EMAIL_HOST_PASSWORD=sua-senha-mailgun
DEFAULT_FROM_EMAIL=noreply@seu-dominio.mailgun.org
```

---

## Testando o Sistema

### 1. Criar um usuário de teste

```bash
python manage.py shell
```

```python
from django.contrib.auth.models import User

# Criar usuário
user = User.objects.create_user(
    username='teste',
    email='seu-email@gmail.com',
    password='senha123'
)

# Enviar email de confirmação manualmente (se necessário)
from allauth.account.models import EmailAddress
EmailAddress.objects.create(
    user=user,
    email=user.email,
    primary=True,
    verified=False
)
```

### 2. Verificar email enviado

- **Desenvolvimento**: Verifique o console/terminal
- **Produção**: Verifique a caixa de entrada do email

### 3. Confirmar email

Clique no link ou acesse manualmente:
```
http://localhost:8000/accounts/confirm-email/<KEY>/
```

---

## Troubleshooting

### Problema: "Email não está sendo enviado"

**Solução 1**: Verificar variáveis de ambiente
```bash
python manage.py shell
from django.conf import settings
print(settings.EMAIL_BACKEND)
print(settings.EMAIL_HOST_USER)
```

**Solução 2**: Verificar logs
```bash
# Verificar erros no console
tail -f logs/django.log
```

**Solução 3**: Testar envio manual
```python
from django.core.mail import send_mail

send_mail(
    'Teste',
    'Mensagem de teste',
    'noreply@cgbookstore.com',
    ['seu-email@gmail.com'],
    fail_silently=False,
)
```

### Problema: "Link de confirmação expirado"

O link expira em 3 dias (configurável em `ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS`).

**Solução**: Reenviar email de confirmação em:
```
http://localhost:8000/accounts/email/
```

### Problema: "Gmail bloqueia envio"

**Solução**: Use **senha de aplicativo**, não a senha normal do Gmail.

---

## Configurações Avançadas

### Customizar templates de email

Os templates estão em:
```
templates/account/email/
├── email_confirmation_subject.txt       # Assunto do email
├── email_confirmation_message.txt       # Versão texto
└── email_confirmation_message.html      # Versão HTML
```

### Alterar prazo de expiração

```python
# settings.py
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 7  # 7 dias
```

### Customizar remetente

```python
# settings.py
DEFAULT_FROM_EMAIL = 'CGBookStore <noreply@cgbookstore.com>'
ACCOUNT_EMAIL_SUBJECT_PREFIX = '[CGBookStore] '
```

---

## Desabilitar Verificação (Não Recomendado)

Para desabilitar temporariamente:

```python
# settings.py
ACCOUNT_EMAIL_VERIFICATION = 'optional'  # ou 'none'
```

⚠️ **Aviso**: Isso permite que usuários criem contas sem email válido.

---

## Checklist de Deploy

- [ ] Configurar variáveis de ambiente no Render
- [ ] Testar envio de email
- [ ] Verificar templates de email
- [ ] Confirmar link de ativação funciona
- [ ] Testar fluxo completo: cadastro → email → confirmação → login
- [ ] Verificar pasta de spam

---

## Suporte

Para mais informações:
- 📚 Documentação django-allauth: https://docs.allauth.org/
- 📧 SendGrid Docs: https://docs.sendgrid.com/
- 📧 Mailgun Docs: https://documentation.mailgun.com/
