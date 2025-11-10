# Configuração SendGrid - CGBookStore

## Status: ✅ CONFIGURADO

Data: 10/11/2025

## 📧 Informações da Configuração

### SendGrid API Key
- **Status**: Ativa
- **Plano**: Free (100 emails/dia)
- **Configurado em**: `.env`

### Configurações Aplicadas

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=SG.YOUR_SENDGRID_API_KEY_HERE
DEFAULT_FROM_EMAIL=noreply@cgbookstore.com
```

## 🧪 Como Testar

### Teste Rápido (Script)

Execute o script de teste:

```bash
.venv\Scripts\python test_sendgrid.py
```

Quando solicitado, digite um email válido para receber o teste.

### Teste Completo (Cadastro Real)

1. **Iniciar servidor**:
   ```bash
   .venv\Scripts\python manage.py runserver
   ```

2. **Criar novo usuário**:
   - Acesse: http://localhost:8000/accounts/signup/
   - Preencha o formulário com dados válidos
   - Use um email real que você tenha acesso

3. **Verificar email**:
   - Verifique sua caixa de entrada
   - Se não aparecer, cheque o SPAM
   - Clique no link de confirmação

4. **Fazer login**:
   - Após confirmar, faça login normalmente
   - Deve entrar sem pedir confirmação novamente

## 📋 Sistema de Confirmação de Email

### Como Funciona

O sistema está configurado com `ACCOUNT_EMAIL_VERIFICATION = 'mandatory'`:

1. **No Cadastro**:
   - Usuário preenche formulário de cadastro
   - Sistema envia email de confirmação automaticamente
   - Usuário NÃO pode fazer login até confirmar

2. **Após Confirmação**:
   - Usuário clica no link do email
   - Conta é ativada
   - Usuário pode fazer login normalmente
   - **NUNCA MAIS** pede confirmação

3. **Em Logins Futuros**:
   - Sistema reconhece que email já foi verificado
   - Login funciona normalmente
   - Sem pedir confirmação novamente

### ⚠️ IMPORTANTE: Quando Pede Confirmação

Se o sistema está pedindo confirmação **toda vez** que você faz login:

**Causa**: O usuário nunca confirmou o email de verdade!

**Motivos possíveis**:
1. Email não foi enviado (backend estava em console)
2. Usuário não clicou no link
3. Conta foi criada ANTES de configurar SendGrid

**Solução**:
1. Deletar usuário antigo do banco
2. Criar novo usuário APÓS configurar SendGrid
3. Confirmar email corretamente
4. Testar login/logout múltiplas vezes

## 🔍 Verificar Usuários no Banco

Para verificar se um usuário tem email confirmado:

```python
python manage.py shell

from allauth.account.models import EmailAddress

# Ver todos os emails registrados
for email in EmailAddress.objects.all():
    print(f"{email.email} - Verificado: {email.verified}")

# Ver usuários sem email verificado
not_verified = EmailAddress.objects.filter(verified=False)
for email in not_verified:
    print(f"NÃO VERIFICADO: {email.email} - Usuário: {email.user.username}")
```

## 📊 Monitorar Envios

- **Dashboard SendGrid**: https://app.sendgrid.com/
- **Activity Feed**: Ver emails enviados, entregas, bounces
- **Limites**: 100 emails/dia no plano Free

## 🚨 Troubleshooting

### Emails não chegam

1. **Verificar configurações**:
   ```python
   python manage.py shell
   from django.conf import settings
   print(settings.EMAIL_BACKEND)
   print(settings.EMAIL_HOST)
   ```

2. **Verificar SendGrid Dashboard**:
   - Ver se email foi enviado
   - Checar se teve bounce/erro

3. **Testar com script**:
   ```bash
   .venv\Scripts\python test_sendgrid.py
   ```

### Erro de autenticação SMTP

- API Key pode estar expirada
- Verificar no SendGrid se key está ativa
- Criar nova key se necessário

### Domínio não verificado

Para produção, é necessário:
1. Ter domínio próprio
2. Verificar domínio no SendGrid
3. Configurar DNS (SPF, DKIM)

Em desenvolvimento, `noreply@cgbookstore.com` funciona normalmente.

## 📝 Próximos Passos

- [ ] Testar envio com script de teste
- [ ] Criar novo usuário e confirmar email
- [ ] Verificar que login funciona sem pedir confirmação
- [ ] Em produção: verificar domínio real no SendGrid
- [ ] Monitorar limite de 100 emails/dia

## 🔗 Links Úteis

- SendGrid Dashboard: https://app.sendgrid.com/
- Docs SendGrid: https://docs.sendgrid.com/
- Django-allauth Docs: https://docs.allauth.org/
