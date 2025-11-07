# Deploy no Render.com - CGBookStore

Este guia fornece instruções completas para fazer deploy da aplicação CGBookStore no Render.com.

## 📋 Pré-requisitos

1. Conta no [Render.com](https://render.com)
2. Repositório Git do projeto
3. Credenciais do Supabase (URL, Anon Key, Service Key)
4. API Key do Google Gemini
5. Credenciais OAuth (Google e/ou Facebook) - opcional
6. Credenciais do Mercado Pago - opcional

## 🚀 Passos para Deploy

### 1. Preparar o Repositório

Certifique-se de que os seguintes arquivos estão no repositório:
- `requirements.txt` - Dependências Python
- `build.sh` - Script de build
- `render.yaml` - Configuração do Render
- `.env.example` - Exemplo de variáveis de ambiente

### 2. Criar Novo Web Service no Render

1. Acesse [Render Dashboard](https://dashboard.render.com/)
2. Clique em **"New +"** → **"Blueprint"**
3. Conecte seu repositório Git
4. O Render detectará automaticamente o `render.yaml`

### 3. Configurar Variáveis de Ambiente

No painel do Render, adicione as seguintes variáveis de ambiente:

#### Essenciais:
```
SECRET_KEY=<gerar-uma-chave-secreta-forte>
DEBUG=False
ALLOWED_HOSTS=<seu-app>.onrender.com
CSRF_TRUSTED_ORIGINS=https://<seu-app>.onrender.com
```

#### Supabase:
```
USE_SUPABASE_STORAGE=True
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_ANON_KEY=sua-anon-key
SUPABASE_SERVICE_KEY=sua-service-key
```

#### Google Gemini AI:
```
GOOGLE_API_KEY=sua-api-key-do-google-gemini
```

#### Social Auth (Opcional):
```
GOOGLE_CLIENT_ID=seu-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=seu-client-secret
FACEBOOK_APP_ID=seu-facebook-app-id
FACEBOOK_APP_SECRET=seu-facebook-app-secret
```

#### Mercado Pago (Opcional):
```
MERCADOPAGO_ACCESS_TOKEN=seu-access-token
MERCADOPAGO_PUBLIC_KEY=sua-public-key
```

**Nota:** `DATABASE_URL` e `REDIS_URL` são fornecidas automaticamente pelo Render.

### 4. Deploy Automático

Após configurar as variáveis:
1. O Render iniciará o build automaticamente
2. Executará `build.sh`:
   - Instalará dependências
   - Coletará arquivos estáticos
   - Executará migrações
3. Iniciará o servidor com Gunicorn

### 5. Configurar OAuth Callbacks (Se usar Social Auth)

#### Google:
1. Acesse [Google Cloud Console](https://console.cloud.google.com/)
2. Vá em **APIs & Services** → **Credentials**
3. Adicione aos **Authorized redirect URIs**:
   ```
   https://<seu-app>.onrender.com/accounts/google/login/callback/
   ```

#### Facebook:
1. Acesse [Facebook Developers](https://developers.facebook.com/)
2. Vá em **Settings** → **Basic**
3. Adicione aos **Valid OAuth Redirect URIs**:
   ```
   https://<seu-app>.onrender.com/accounts/facebook/login/callback/
   ```

### 6. Configurar Domínio Customizado (Opcional)

1. No painel do Render, vá em **Settings** → **Custom Domain**
2. Adicione seu domínio
3. Configure DNS conforme instruções do Render
4. Atualize `ALLOWED_HOSTS` e `CSRF_TRUSTED_ORIGINS`

## 🔍 Verificações Pós-Deploy

1. **Teste a aplicação**: Acesse `https://<seu-app>.onrender.com`
2. **Verifique logs**: Painel do Render → **Logs**
3. **Teste funcionalidades**:
   - Cadastro/Login
   - Upload de imagens (Supabase)
   - Sistema de recomendações (Google Gemini)
   - Social Auth (se configurado)

## ⚠️ Troubleshooting

### Erro 500:
- Verifique logs no painel do Render
- Confirme que todas as variáveis de ambiente estão configuradas
- Verifique conectividade com Supabase e Redis

### Arquivos estáticos não carregam:
- Execute manualmente: `python manage.py collectstatic`
- Verifique configuração do WhiteNoise

### Migrações falharam:
- Execute manualmente via shell do Render:
  ```bash
  python manage.py migrate
  ```

### Redis não conecta:
- Verifique se o serviço Redis foi criado
- Confirme que `REDIS_URL` está definida

## 📊 Monitoramento

- **Logs**: Render Dashboard → Seu serviço → Logs
- **Métricas**: Render Dashboard → Seu serviço → Metrics
- **Alertas**: Configure no painel do Render

## 🔄 Atualizações

Para atualizar a aplicação:
1. Faça push das mudanças para o branch `main`
2. O Render fará deploy automático
3. Monitore os logs durante o deploy

## 💰 Custos

- **Plano Free**: Inclui PostgreSQL, Redis e Web Service
- **Limitações**: Serviço hiberna após 15min de inatividade
- **Upgrade**: Considere planos pagos para produção

## 🔐 Segurança

- ✅ HTTPS automático (Let's Encrypt)
- ✅ Variáveis de ambiente criptografadas
- ✅ Headers de segurança configurados
- ✅ HSTS habilitado em produção
- ✅ CSRF e XSS protection

## 📚 Recursos Adicionais

- [Documentação do Render](https://render.com/docs)
- [Deploy Django no Render](https://render.com/docs/deploy-django)
- [Suporte do Render](https://render.com/support)

---

**Desenvolvido por:** CG.BookStore Team  
**Última atualização:** Novembro 2025
