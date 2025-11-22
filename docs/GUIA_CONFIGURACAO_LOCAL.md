# 🚀 Guia de Configuração Local - CGBookStore

Este guia te ajudará a configurar o ambiente de desenvolvimento local e fazer o módulo de recomendações funcionar.

---

## 🔍 **Diagnóstico Revelou os Problemas**

O script de diagnóstico identificou **5 problemas críticos**:

1. ❌ **Arquivo `.env` não existe** (variáveis de ambiente)
2. ❌ **Django não instalado** (ou ambiente virtual não ativado)
3. ❌ **google-generativeai não instalado**
4. ❌ **redis-py não instalado**
5. ❌ **django-redis não instalado**

**E 2 avisos:**
- ⚠️ Servidor Django não está rodando
- ⚠️ Banco de dados SQLite não encontrado

---

## ✅ **Solução Rápida (3 comandos)**

Se você tem pressa, execute estes 3 comandos:

```bash
# 1. Configurar ambiente (.env)
bash scripts/setup_local_env.sh

# 2. Editar .env e adicionar sua GEMINI_API_KEY
nano .env  # ou use seu editor favorito

# 3. Iniciar tudo
bash scripts/start_local.sh
```

**IMPORTANTE**: No passo 2, você DEVE configurar a `GEMINI_API_KEY`. [Veja como obter](#obter-gemini-api-key) 👇

---

## 📋 **Configuração Passo-a-Passo Completa**

### **Passo 1: Instalar Dependências do Sistema**

#### Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install -y python3 python3-pip redis-server
```

#### macOS:
```bash
brew install python redis
```

#### Windows:
```bash
# Instale Python: https://www.python.org/downloads/
# Instale Redis: https://github.com/microsoftarchive/redis/releases
```

---

### **Passo 2: Criar Ambiente Virtual (Recomendado)**

```bash
# Criar ambiente virtual
python3 -m venv venv

# Ativar (Linux/Mac)
source venv/bin/activate

# Ativar (Windows)
venv\Scripts\activate
```

---

### **Passo 3: Instalar Dependências Python**

```bash
pip install -r requirements.txt
```

**Se `requirements.txt` não existir**, instale manualmente:

```bash
pip install django==5.0 \
    djangorestframework \
    django-redis \
    redis \
    google-generativeai \
    python-decouple \
    dj-database-url \
    requests \
    numpy \
    whitenoise \
    django-allauth \
    pillow
```

---

### **Passo 4: Configurar Variáveis de Ambiente**

Execute o script de configuração:

```bash
bash scripts/setup_local_env.sh
```

Isso criará um arquivo `.env` com valores padrão para desenvolvimento.

---

### **Passo 5: Obter GEMINI_API_KEY** {#obter-gemini-api-key}

🔴 **OBRIGATÓRIO para recomendações por IA funcionarem!**

1. **Acesse**: [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)

2. **Faça login** com sua conta Google

3. **Clique em "Create API Key"** (ou "Get API Key")

4. **Copie a chave** gerada (exemplo: `AIzaSyA...`)

5. **Edite o arquivo `.env`**:
   ```bash
   nano .env  # ou use VS Code, vim, etc
   ```

6. **Cole sua chave** na linha `GEMINI_API_KEY`:
   ```bash
   # ANTES (vazio)
   GEMINI_API_KEY=

   # DEPOIS (com sua chave)
   GEMINI_API_KEY=AIzaSyA_sua_chave_aqui
   ```

7. **Salve o arquivo** (`Ctrl+X` no nano, depois `Y` e `Enter`)

---

### **Passo 6: Aplicar Migrações do Banco de Dados**

```bash
python manage.py migrate
```

---

### **Passo 7: Criar Superusuário (Opcional)**

Para acessar o admin Django:

```bash
python manage.py createsuperuser
```

Siga as instruções na tela.

---

### **Passo 8: Iniciar Redis**

```bash
redis-server --daemonize yes
```

Verificar se está rodando:

```bash
redis-cli ping
# Deve retornar: PONG
```

---

### **Passo 9: Iniciar Servidor Django**

**Opção A - Script Automático (Recomendado):**
```bash
bash scripts/start_local.sh
```

**Opção B - Manual:**
```bash
python manage.py runserver
```

---

### **Passo 10: Testar no Navegador**

1. Abra: [http://localhost:8000/](http://localhost:8000/)

2. Faça login (ou crie uma conta)

3. Vá até a seção **"Para Você"** (recomendações)

4. Clique em:
   - **"Personalizado"** → Recomendações baseadas em prateleiras
   - **"IA Premium"** → Recomendações com Gemini AI

---

## 🧪 **Validar Configuração**

Execute o script de diagnóstico:

```bash
bash scripts/diagnose_recommendations.sh
```

Deve mostrar:
- ✅ 10+ sucessos
- ⚠️ 0 avisos
- ❌ 0 erros

---

## 🔧 **Troubleshooting**

### **Problema: "ModuleNotFoundError: No module named 'django'"**

**Solução:**
```bash
# Ativar ambiente virtual
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Ou instalar globalmente
pip install django
```

---

### **Problema: "Redis connection refused"**

**Solução:**
```bash
# Iniciar Redis
redis-server --daemonize yes

# Verificar
redis-cli ping
```

---

### **Problema: "GEMINI_API_KEY not configured"**

**Solução:**
1. Verifique se `.env` existe: `ls -la .env`
2. Verifique se tem a chave: `grep GEMINI_API_KEY .env`
3. Se vazia, [obtenha a chave](#obter-gemini-api-key)

---

### **Problema: "Timeout ao buscar recomendações por IA"**

**Possíveis causas:**

1. **GEMINI_API_KEY inválida ou vazia**
   - Verifique no `.env`
   - Teste: `python -c "from decouple import config; print(config('GEMINI_API_KEY'))"`

2. **Primeira chamada é lenta (15-30s)**
   - Isso é normal! O Gemini precisa processar
   - Próximas chamadas serão < 1s (cache)

3. **Timeout do frontend**
   - Já corrigido para 30s (era 5s)
   - Se ainda falhar, verifique logs: `python manage.py runserver`

---

### **Problema: "Recomendações personalizadas sempre iguais"**

**Solução:** Já corrigido!
- Cache agora inclui hash das prateleiras
- Muda automaticamente quando você adiciona/remove livros

**Para forçar atualização:**
```bash
bash scripts/clear_all_caches.sh
```

---

### **Problema: "Atualizações não aparecem no navegador"**

**Solução:** Cache do navegador!

1. **Hard Refresh:**
   - Windows/Linux: `Ctrl + Shift + R`
   - Mac: `Cmd + Shift + R`

2. **Ou limpe o cache:**
   - Chrome: `Ctrl + Shift + Delete`
   - Firefox: `Ctrl + Shift + Delete`

3. **Ou teste em modo anônimo:**
   - Chrome: `Ctrl + Shift + N`
   - Firefox: `Ctrl + Shift + P`

**Veja mais:** [TROUBLESHOOTING_CACHE.md](TROUBLESHOOTING_CACHE.md)

---

## 📊 **Estrutura de Arquivos**

```
cgbookstore_v3/
├── .env                          # ⚠️  Variáveis de ambiente (você cria)
├── .env.example                  # 📄 Template do .env
├── manage.py                     # 🎯 Gerenciador Django
├── requirements.txt              # 📦 Dependências Python
├── db.sqlite3                    # 💾 Banco de dados (criado após migrate)
│
├── recommendations/              # 📂 Módulo de Recomendações
│   ├── gemini_ai_enhanced.py     # 🤖 IA com Gemini
│   ├── algorithms_preference_weighted.py  # 📊 Algoritmos de recomendação
│   ├── views_simple.py           # 🌐 Views da API
│   └── urls.py                   # 🔗 Rotas
│
├── templates/
│   └── recommendations/
│       └── recommendations_section.html  # 🎨 Template do frontend
│
└── scripts/                      # 🛠️  Scripts utilitários
    ├── setup_local_env.sh        # ⚙️  Configurar .env
    ├── start_local.sh            # 🚀 Iniciar ambiente
    ├── diagnose_recommendations.sh  # 🔍 Diagnóstico
    └── clear_all_caches.sh       # 🧹 Limpar caches
```

---

## 🎯 **Comandos Úteis**

| Comando | Descrição |
|---------|-----------|
| `bash scripts/diagnose_recommendations.sh` | Diagnosticar problemas |
| `bash scripts/setup_local_env.sh` | Criar arquivo .env |
| `bash scripts/start_local.sh` | Iniciar tudo (Redis + Django) |
| `bash scripts/clear_all_caches.sh` | Limpar todos os caches |
| `redis-cli ping` | Verificar Redis |
| `python manage.py migrate` | Aplicar migrações |
| `python manage.py runserver` | Iniciar servidor |
| `python manage.py createsuperuser` | Criar admin |

---

## 📚 **Próximos Passos Após Configuração**

1. ✅ **Adicione livros ao catálogo** (admin ou fixtures)
2. ✅ **Crie prateleiras** (Favoritos, Lidos, Lendo)
3. ✅ **Teste recomendações personalizadas** (baseadas em prateleiras)
4. ✅ **Teste recomendações por IA** (com Gemini)
5. ✅ **Adicione mais livros às prateleiras** e veja cache invalidar automaticamente!

---

## ❓ **FAQ**

### **Preciso configurar TODAS as APIs do .env?**

**Não!** Para desenvolvimento local e testar recomendações, você só precisa:

- ✅ **GEMINI_API_KEY** (obrigatória para IA)
- ✅ **REDIS_URL** (já configurada por padrão)
- ✅ **DATABASE_URL** (SQLite por padrão)

Opcionais:
- GOOGLE_BOOKS_API_KEY (para buscar livros)
- SUPABASE (para storage)
- Social Auth (para login com Google/Facebook)
- Mercado Pago (para pagamentos)

---

### **O Gemini AI é gratuito?**

**Sim!** O Gemini oferece **free tier generoso**:

- **Flash 2.5**: 10 req/min, 1500 req/dia (GRÁTIS)
- **Pro**: 2 req/min, 50 req/dia (GRÁTIS)

Para desenvolvimento local, o free tier é mais que suficiente!

🔗 Detalhes: [https://ai.google.dev/pricing](https://ai.google.dev/pricing)

---

### **Redis é obrigatório?**

**Não é obrigatório**, mas **ALTAMENTE RECOMENDADO**!

**Com Redis:**
- ⚡ Recomendações instantâneas (< 1s)
- 💰 Economia de chamadas à API do Gemini
- 🚀 Performance 10-30x melhor

**Sem Redis:**
- 🐌 Cada requisição recalcula tudo (15-30s)
- 💸 Gasta cota da API do Gemini
- ❌ Pode atingir rate limits

---

## 🆘 **Precisa de Ajuda?**

1. Execute o diagnóstico: `bash scripts/diagnose_recommendations.sh`
2. Veja os logs do Django no terminal
3. Veja o console do navegador (F12 → Console)
4. Leia [TROUBLESHOOTING_CACHE.md](TROUBLESHOOTING_CACHE.md)

---

## ✅ **Checklist de Configuração**

Use este checklist para garantir que tudo está configurado:

- [ ] Python 3.8+ instalado
- [ ] Redis instalado
- [ ] Ambiente virtual criado (recomendado)
- [ ] Dependências Python instaladas (`pip install -r requirements.txt`)
- [ ] Arquivo `.env` criado
- [ ] **GEMINI_API_KEY** configurada no `.env`
- [ ] Migrações aplicadas (`python manage.py migrate`)
- [ ] Redis rodando (`redis-cli ping` → PONG)
- [ ] Servidor Django rodando (`python manage.py runserver`)
- [ ] Diagnóstico sem erros (`bash scripts/diagnose_recommendations.sh`)
- [ ] Navegador aberto em `http://localhost:8000/`
- [ ] Login feito e recomendações testadas!

---

**Pronto! Agora o módulo de recomendações deve estar funcionando perfeitamente! 🎉**
