# 🚀 GUIA DE ATUALIZAÇÃO: MIGRAÇÃO RENDER → SUPABASE

## ✅ STATUS DA MIGRAÇÃO

- ✅ **Banco Supabase:** Configurado e testado
- ✅ **Dados:** Sincronizados (355 registros em ambos)
- ✅ **Conexão Local:** Funcionando perfeitamente
- ✅ **Sistema:** Rodando com Supabase sem erros

---

## 📋 PRÓXIMOS PASSOS: ATUALIZAR RENDER.COM

### **PASSO 1: Acessar Dashboard do Render**

1. Acesse: https://dashboard.render.com/
2. Faça login na sua conta
3. Selecione seu serviço web (cgbookstore ou similar)

---

### **PASSO 2: Atualizar Variável de Ambiente DATABASE_URL**

1. No menu lateral, clique em **"Environment"**
2. Procure a variável `DATABASE_URL`
3. Clique em **"Edit"** (ícone de lápis)
4. **Substitua o valor atual por:**

```
postgresql://postgres:Oa023568910@@db.uomjbcuowfgcwhsejatn.supabase.co:5432/postgres
```

5. Clique em **"Save Changes"**

---

### **PASSO 3: Configurar Redis (Opcional mas Recomendado)**

Se você ainda não tem Redis configurado no Render:

1. Na seção **"Environment Variables"**, clique em **"Add Environment Variable"**
2. **Key:** `REDIS_URL`
3. **Value:** `redis://red-xxxxx.render.com:6379` (você precisará criar um Redis no Render)

**OU** use Redis externo (Upstash, Redis Cloud, etc.)

---

### **PASSO 4: Verificar Outras Variáveis**

Certifique-se que estas variáveis estão configuradas:

```bash
# Supabase Storage
SUPABASE_URL=https://uomjbcuowfgcwhsejatn.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Django
SECRET_KEY=Oa023568910@
DEBUG=False
ALLOWED_HOSTS=seu-app.onrender.com

# CSRF Trusted Origins
CSRF_TRUSTED_ORIGINS=https://seu-app.onrender.com

# APIs
GEMINI_API_KEY=AIzaSyBZhQQCkxlrncJ3_FTVjK5a8X0ePnkPvu4
GOOGLE_BOOKS_API_KEY=AIzaSyBF5W5NktgXZRfTnZXe3pVxqB_TCkXGzx0
```

---

### **PASSO 5: Forçar Deploy**

Após salvar as variáveis:

1. Vá para a aba **"Manual Deploy"**
2. Clique em **"Deploy latest commit"**
3. **OU** faça um push no GitHub (se auto-deploy estiver ativado)

---

### **PASSO 6: Monitorar Deploy**

1. Vá para a aba **"Logs"**
2. Acompanhe o processo de deploy
3. Aguarde a mensagem: **"Your service is live"**

---

### **PASSO 7: Verificar Sistema em Produção**

1. Acesse seu site: `https://seu-app.onrender.com`
2. Teste:
   - ✅ Home page carrega
   - ✅ Login funciona
   - ✅ Livros aparecem
   - ✅ Imagens carregam (Supabase Storage)
   - ✅ Criar/editar funciona

---

## 🎯 CHECKLIST FINAL

- [ ] DATABASE_URL atualizada no Render
- [ ] Deploy realizado com sucesso
- [ ] Site em produção funcionando
- [ ] Banco Render pode ser desativado (após confirmar tudo OK)

---

## ⚠️ ROLLBACK (Se necessário)

Se algo der errado, você pode voltar rapidamente:

1. Acesse Environment Variables no Render
2. Mude DATABASE_URL de volta para Render:
```
postgresql://cgbookstore_user:VbtzEhwlTr8nMc6gF3yWtjIyGOezK7PL@dpg-d46ttd8gjchc73enjuo0-a.oregon-postgres.render.com/cgbookstore
```
3. Fazer novo deploy

---

## 📊 INFORMAÇÕES IMPORTANTES

### **Banco Render (Temporário - EXPIRA EM DEZEMBRO)**
- Host: `dpg-d46ttd8gjchc73enjuo0-a.oregon-postgres.render.com`
- Database: `cgbookstore`
- User: `cgbookstore_user`
- Status: ⚠️ **TEMPORÁRIO - Desativar após migração confirmada**

### **Banco Supabase (Permanente)**
- Host: `db.uomjbcuowfgcwhsejatn.supabase.co`
- Database: `postgres`
- User: `postgres`
- Status: ✅ **PERMANENTE - Sem data de expiração**

---

## 🆘 SUPORTE

Se encontrar problemas:

1. **Logs do Render:** Aba "Logs" no dashboard
2. **Teste Local:** Sistema está funcionando localmente com Supabase
3. **Backup:** Você tem backup do .env antigo (`.env.backup_render_20251121`)

---

## ✨ BENEFÍCIOS DA MIGRAÇÃO

- ✅ **Banco permanente** (sem data de expiração)
- ✅ **Mesma infraestrutura** do Storage (Supabase)
- ✅ **Dados já sincronizados** (355 registros)
- ✅ **Zero downtime** (ambos bancos funcionando)
- ✅ **Performance mantida**

---

**Data da Migração:** 21/11/2025
**Status:** ✅ Pronto para deploy em produção
