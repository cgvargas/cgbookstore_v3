# Configurar Login Social (Google e Facebook)

## Status Atual
✅ Sistema funcionando sem erros
⚠️ Botões de login social ocultos (sem credenciais configuradas)

## Como Adicionar Botões de Login Social

### Passo 1: Obter Credenciais

#### Google OAuth
1. Acesse: https://console.cloud.google.com/
2. Crie um novo projeto ou selecione existente
3. Vá em "APIs & Services" > "Credentials"
4. Clique em "Create Credentials" > "OAuth client ID"
5. Configure OAuth consent screen (se primeira vez)
6. Tipo de aplicação: "Web application"
7. **Authorized redirect URIs**:
   ```
   http://localhost:8000/accounts/google/login/callback/
   http://127.0.0.1:8000/accounts/google/login/callback/
   ```
8. Copie o **Client ID** e **Client Secret**

#### Facebook OAuth
1. Acesse: https://developers.facebook.com/
2. Vá em "My Apps" > "Create App"
3. Escolha tipo: "Consumer"
4. Adicione o produto "Facebook Login"
5. Em Settings > Basic, copie **App ID** e **App Secret**
6. Em Facebook Login > Settings, adicione:
   ```
   http://localhost:8000/accounts/facebook/login/callback/
   http://127.0.0.1:8000/accounts/facebook/login/callback/
   ```

### Passo 2: Configurar no Django Admin

1. **Acesse o Admin**:
   ```
   http://localhost:8000/admin/
   ```

2. **Login como superuser** (se não tiver, crie um):
   ```bash
   cd cgbookstore_v3
   python manage.py createsuperuser
   ```

3. **Adicionar Google App**:
   - Vá em "Social applications" > "Add social application"
   - Provider: `Google`
   - Name: `Google Login` (ou qualquer nome)
   - Client id: Cole o Client ID obtido
   - Secret key: Cole o Client Secret obtido
   - Sites: Selecione `localhost:8000`
   - Salve

4. **Adicionar Facebook App**:
   - Vá em "Social applications" > "Add social application"
   - Provider: `Facebook`
   - Name: `Facebook Login` (ou qualquer nome)
   - Client id: Cole o App ID obtido
   - Secret key: Cole o App Secret obtido
   - Sites: Selecione `localhost:8000`
   - Salve

### Passo 3: Verificar

1. Acesse: http://localhost:8000/accounts/login/
2. Você verá os botões:
   - 🔵 **Entrar com Google**
   - 🔵 **Entrar com Facebook**

## Alternativa: Configurar via Script

Se preferir configurar via código, crie um arquivo `setup_social_auth.py`:

```python
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp

# Obter site atual
site = Site.objects.get_current()

# Configurar Google
google_app = SocialApp.objects.create(
    provider='google',
    name='Google Login',
    client_id='SEU_GOOGLE_CLIENT_ID_AQUI',
    secret='SEU_GOOGLE_CLIENT_SECRET_AQUI',
)
google_app.sites.add(site)

# Configurar Facebook
facebook_app = SocialApp.objects.create(
    provider='facebook',
    name='Facebook Login',
    client_id='SEU_FACEBOOK_APP_ID_AQUI',
    secret='SEU_FACEBOOK_APP_SECRET_AQUI',
)
facebook_app.sites.add(site)

print('Apps sociais configurados com sucesso!')
```

Execute:
```bash
python manage.py shell < setup_social_auth.py
```

## Notas Importantes

1. **Produção**: Para produção, adicione o domínio real nas configurações:
   - Google: `https://seudominio.com/accounts/google/login/callback/`
   - Facebook: `https://seudominio.com/accounts/facebook/login/callback/`

2. **Variáveis de Ambiente**: É recomendado usar `.env` para armazenar as credenciais:
   ```env
   GOOGLE_CLIENT_ID=seu_client_id
   GOOGLE_CLIENT_SECRET=seu_client_secret
   FACEBOOK_APP_ID=seu_app_id
   FACEBOOK_APP_SECRET=seu_app_secret
   ```

3. **Arquivo de exemplo**: Já existe um [.env.example](cgbookstore_v3/.env.example:42-49) com as variáveis

## Troubleshooting

### Erro "MultipleObjectsReturned"
Se aparecer esse erro, há apps duplicados. Limpe todos:
```bash
python manage.py shell -c "from allauth.socialaccount.models import SocialApp; SocialApp.objects.all().delete()"
```

### Botões não aparecem
Verifique se os apps estão vinculados ao site correto:
```bash
python manage.py shell -c "from allauth.socialaccount.models import SocialApp; from django.contrib.sites.models import Site; site = Site.objects.get_current(); [print(f'{app.provider}: {[s.domain for s in app.sites.all()]}') for app in SocialApp.objects.all()]"
```

### Redirect URI mismatch
Certifique-se que a URI no Google/Facebook Console corresponde exatamente à configurada:
- Use `http://` para desenvolvimento local
- Use `https://` para produção
- Verifique se a porta está correta (`:8000`)

## Documentação Oficial

- **Django Allauth**: https://docs.allauth.org/en/latest/
- **Google OAuth**: https://developers.google.com/identity/protocols/oauth2
- **Facebook Login**: https://developers.facebook.com/docs/facebook-login/

---

**Criado em**: 06/11/2025
**Status**: Sistema funcionando, aguardando credenciais OAuth
