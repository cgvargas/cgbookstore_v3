# 🚀 CG Bookstore - Produção (Render.com)

## 📌 Status do Deploy

Aplicação rodando em: https://cgbookstore-v3.onrender.com

## ✅ Correções Implementadas

### 1. Script de Populamento de Dados (`setup_initial_data`)

Criado comando Django que popula automaticamente:
- ✅ Site (django-allauth) com domínio correto
- ✅ 20 categorias de livros (Ficção, Romance, Tecnologia, etc.)
- ✅ 3 livros de exemplo (1984, Fundação, Dom Casmurro)
- ✅ Apps OAuth (Google e Facebook)
- ✅ Opção de criar superusuário

**Executado automaticamente no deploy** via `build.sh`.

### 2. Comando de Health Check (`health_check`)

Diagnóstico completo da aplicação:
- ✅ Conexão com PostgreSQL
- ✅ Conexão com Redis
- ✅ Configuração do Site
- ✅ Apps OAuth configurados
- ✅ Dados cadastrados (categorias, livros)
- ✅ Variáveis de ambiente
- ✅ Configurações de segurança

### 3. Configurações Corrigidas

#### `.env.example`
- ✅ `ALLOWED_HOSTS` SEM https://
- ✅ `CSRF_TRUSTED_ORIGINS` COM https://
- ✅ Variáveis `SITE_DOMAIN` e `SITE_NAME` adicionadas
- ✅ Correção: `GEMINI_API_KEY` (estava `GOOGLE_API_KEY`)

#### `render.yaml`
- ✅ Todas as variáveis de ambiente necessárias
- ✅ Configuração de Site (domain e name)
- ✅ Variáveis OAuth com `sync: false` (configurar manualmente)
- ✅ Variáveis de APIs externas

#### `build.sh`
- ✅ Execução automática do `setup_initial_data`
- ✅ Tratamento de erros (continua mesmo com warnings)

---

## 🛠️ Comandos Disponíveis

### Popular Dados Iniciais

```bash
# Completo (categorias, livros, site, OAuth)
python manage.py setup_initial_data

# Com superusuário customizado
python manage.py setup_initial_data --admin-email seu@email.com --admin-password SuaSenha123

# Pular criação de superusuário
python manage.py setup_initial_data --skip-superuser

# Pular livros de exemplo
python manage.py setup_initial_data --skip-books

# Apenas apps OAuth
python manage.py setup_initial_data --skip-superuser --skip-categories --skip-books
```

### Health Check

```bash
# Diagnóstico completo
python manage.py health_check
```

### Outros Comandos

```bash
# Criar superusuário
python manage.py createsuperuser

# Verificar migrações
python manage.py showmigrations

# Coletar arquivos estáticos
python manage.py collectstatic --no-input
```

---

## 📋 Checklist de Variáveis de Ambiente (Render)

### Essenciais (Já Configuradas via render.yaml)
- [x] `SECRET_KEY` (gerado automaticamente)
- [x] `DEBUG=False`
- [x] `DATABASE_URL` (conectado ao PostgreSQL)
- [x] `REDIS_URL` (conectado ao Redis)
- [x] `ALLOWED_HOSTS`
- [x] `CSRF_TRUSTED_ORIGINS`
- [x] `SITE_DOMAIN`
- [x] `SITE_NAME`

### OAuth (Configurar Manualmente no Painel)
- [ ] `GOOGLE_CLIENT_ID`
- [ ] `GOOGLE_CLIENT_SECRET`
- [ ] `FACEBOOK_APP_ID`
- [ ] `FACEBOOK_APP_SECRET`

### APIs (Configurar Manualmente)
- [ ] `GOOGLE_BOOKS_API_KEY`
- [ ] `GEMINI_API_KEY`

### Supabase Storage (Opcional)
- [ ] `SUPABASE_URL`
- [ ] `SUPABASE_ANON_KEY`
- [ ] `SUPABASE_SERVICE_KEY`

---

## 🔧 Como Corrigir Problemas Comuns

### Banco de Dados Vazio

**Via Shell do Render:**
```bash
python manage.py setup_initial_data
```

### Erro CSRF (403)

**No painel do Render (Environment):**
```
ALLOWED_HOSTS=cgbookstore-v3.onrender.com
CSRF_TRUSTED_ORIGINS=https://cgbookstore-v3.onrender.com
```

### Login OAuth Não Funciona

1. Configurar credenciais no Render (Environment)
2. Executar: `python manage.py setup_initial_data --skip-superuser --skip-categories --skip-books`
3. Configurar URLs de callback nos providers:
   - Google: `https://cgbookstore-v3.onrender.com/accounts/google/login/callback/`
   - Facebook: `https://cgbookstore-v3.onrender.com/accounts/facebook/login/callback/`

---

## 📚 Documentação

- **[CORRECOES_PRODUCAO.md](CORRECOES_PRODUCAO.md)** - Guia rápido de correções
- **[TROUBLESHOOTING_PRODUCAO.md](TROUBLESHOOTING_PRODUCAO.md)** - Troubleshooting completo
- **[.env.example](.env.example)** - Exemplo de variáveis de ambiente

---

## 🎯 Próximos Passos Após Deploy

1. ✅ Deploy feito
2. ✅ Dados populados automaticamente (via build.sh)
3. [ ] Acessar Shell do Render e executar:
   ```bash
   python manage.py health_check
   python manage.py createsuperuser
   ```
4. [ ] Configurar variáveis OAuth (se necessário)
5. [ ] Testar login e funcionalidades principais
6. [ ] Adicionar livros via Admin ou Google Books API

---

## 🆘 Suporte

### Executar Health Check
```bash
python manage.py health_check
```

### Ver Logs
- Render Dashboard → Seu Serviço → **Logs**

### Arquivos de Ajuda
- [CORRECOES_PRODUCAO.md](CORRECOES_PRODUCAO.md) - Soluções rápidas
- [TROUBLESHOOTING_PRODUCAO.md](TROUBLESHOOTING_PRODUCAO.md) - Detalhado

---

## 🎉 Melhorias Implementadas

1. **Automação de Deploy**
   - Dados iniciais populados automaticamente
   - Build script otimizado

2. **Diagnóstico**
   - Comando `health_check` completo
   - Verificação de todas as configurações

3. **Documentação**
   - Guia rápido de correções
   - Troubleshooting detalhado
   - README de produção

4. **Configuração**
   - Variáveis de ambiente corrigidas
   - render.yaml completo
   - .env.example atualizado

---

**Desenvolvido com Django + PostgreSQL + Redis + Render.com**
