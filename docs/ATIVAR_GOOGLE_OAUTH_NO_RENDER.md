# 🚀 Ativar Autenticação Google no Render

## ✅ Pré-requisitos

- [x] Credenciais OAuth já configuradas no Render (GOOGLE_CLIENT_ID e GOOGLE_CLIENT_SECRET)
- [x] Templates já atualizados (botões descomentados)
- [x] Código commitado e deployado

---

## 📋 Passo a Passo

### Opção 1: Via Render Shell (Recomendado) 🎯

1. **Acesse o Render Dashboard**
   - Vá em: https://dashboard.render.com/
   - Selecione seu serviço: **cgbookstore-v3**

2. **Abra o Shell**
   - Clique na aba **"Shell"** no menu superior
   - Aguarde o terminal carregar

3. **Execute o comando de setup**
   ```bash
   python manage.py setup_google_oauth
   ```

4. **Verifique o output**
   - Deve aparecer mensagem de sucesso: "✅ SETUP COMPLETE!"
   - Confirme que "Total Google SocialApps in database: 1"

5. **Pronto!** 🎉
   - Os botões de "Continuar com Google" já devem estar visíveis
   - Teste acessando: https://cgbookstore-v3.onrender.com/accounts/login/

---

### Opção 2: Via Django Admin (Alternativa) 🔧

Se preferir fazer manualmente pelo admin:

1. **Acesse o Django Admin**
   ```
   https://cgbookstore-v3.onrender.com/admin/
   ```

2. **Navegue até Social Applications**
   - Clique em **"Sites"** → **"Social applications"**

3. **Verifique apps existentes**
   - Se existir app Google duplicado, delete todos primeiro
   - Clique em cada um e escolha "Delete"

4. **Crie novo Google SocialApp**
   - Clique em **"Add social application"**
   - **Provider**: Selecione "Google"
   - **Name**: Digite "Google"
   - **Client id**: Cole o valor de GOOGLE_CLIENT_ID (das env vars do Render)
   - **Secret key**: Cole o valor de GOOGLE_CLIENT_SECRET (das env vars do Render)
   - **Sites**: Selecione seu site (geralmente "cgbookstore-v3.onrender.com")
   - Clique em **"Save"**

5. **Teste**
   - Acesse: https://cgbookstore-v3.onrender.com/accounts/login/
   - Verifique se o botão "Continuar com Google" aparece

---

## 🔍 Verificação

### Como saber se está funcionando?

1. **Botões visíveis**
   - Acesse `/accounts/login/`
   - Deve ver botão "Continuar com Google" com ícone do Google

2. **Teste o clique**
   - Clique no botão
   - Deve redirecionar para tela de login do Google
   - **Não deve** dar erro 404 ou "Provider não configurado"

3. **Fluxo completo**
   - Faça login com uma conta Google de teste
   - Deve criar usuário automaticamente
   - Deve fazer login e redirecionar para página inicial
   - Verifique se o avatar do Google foi importado

---

## ⚠️ Troubleshooting

### Problema: Botão não aparece

**Causa**: SocialApp não foi criado no banco
**Solução**: Execute `python manage.py setup_google_oauth` no Render Shell

### Problema: Erro "redirect_uri_mismatch"

**Causa**: Redirect URI não configurado no Google Cloud Console
**Solução**:
1. Acesse: https://console.cloud.google.com/
2. Vá em "APIs & Services" → "Credentials"
3. Clique no OAuth Client ID
4. Em "Authorized redirect URIs", adicione:
   ```
   https://cgbookstore-v3.onrender.com/accounts/google/login/callback/
   ```
5. Clique em "Save"

### Problema: Botão aparece mas dá erro ao clicar

**Possíveis causas**:
1. **Client ID/Secret incorretos**: Verifique as env vars no Render
2. **Site ID incorreto**: SocialApp deve estar vinculado ao site correto
3. **Provider duplicado**: Delete apps duplicados e recrie

**Solução**:
```bash
# No Render Shell
python manage.py setup_google_oauth
```

### Problema: Login funciona mas não importa avatar

**Causa**: Adapter está OK, pode ser permissão do Google
**Solução**: Verifique se os escopos incluem 'profile' nas configurações

---

## 🎯 Comandos Úteis

### Listar SocialApps existentes
```bash
python manage.py shell -c "from allauth.socialaccount.models import SocialApp; [print(f'{app.id}: {app.provider} - {app.name}') for app in SocialApp.objects.all()]"
```

### Verificar Site ID
```bash
python manage.py shell -c "from django.contrib.sites.models import Site; print(Site.objects.get(id=1))"
```

### Limpar todos os SocialApps e recriar
```bash
python manage.py cleanup_socialapps
```

### Remover apenas duplicatas
```bash
python manage.py fix_duplicates
```

---

## 📝 Notas Importantes

1. **Credenciais já configuradas**: As variáveis GOOGLE_CLIENT_ID e GOOGLE_CLIENT_SECRET já estão no Render, não precisa alterar

2. **Um único SocialApp**: Só deve existir 1 app Google no banco. Se tiver duplicatas, delete e recrie.

3. **Redirect URI correto**: No Google Cloud Console, o redirect URI DEVE ser exatamente:
   ```
   https://cgbookstore-v3.onrender.com/accounts/google/login/callback/
   ```

4. **Ambiente de teste**: Se quiser testar localmente, precisa adicionar também:
   ```
   http://localhost:8000/accounts/google/login/callback/
   ```

---

## ✅ Checklist Final

- [ ] Executei `python manage.py setup_google_oauth` no Render Shell
- [ ] Comando mostrou "✅ SETUP COMPLETE!"
- [ ] Acessei `/accounts/login/` e vejo o botão do Google
- [ ] Cliquei no botão e fui redirecionado para o Google (sem erros)
- [ ] Fiz login com conta Google de teste
- [ ] Usuário foi criado automaticamente
- [ ] Fui redirecionado para a página inicial logado
- [ ] Avatar do Google foi importado no perfil

---

## 🎉 Sucesso!

Se todos os itens do checklist acima estão marcados, a autenticação Google está 100% funcional!

Usuários agora podem fazer login/cadastro com um único clique usando suas contas Google.
