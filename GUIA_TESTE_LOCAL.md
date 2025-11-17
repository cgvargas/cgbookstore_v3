# 🧪 Guia de Teste Local - Branch Integrada

Este guia te ajudará a testar localmente **TODAS as correções** antes de fazer deploy no Render.

**Branch:** `claude/integrated-recommendations-and-ux-013suojTnoYABUtLhNEbLp49`

---

## ✅ **O que foi corrigido?**

### 1. **IA com Timeout Aumentado** ⏱️
- **Antes:** 20s (muito curto)
- **Agora:** 40s (suficiente para Render)
- **Benefício:** IA funciona sem timeout

### 2. **Fallback Inteligente** 🛡️
- **Antes:** Se IA falhar → erro vazio na tela
- **Agora:** Se IA falhar → automaticamente usa recomendações personalizadas
- **Benefício:** Usuário sempre recebe recomendações

### 3. **Cache por Hash de Prateleiras** 🔄
- **Antes:** Recomendações sempre iguais
- **Agora:** Cache muda quando você altera prateleiras
- **Benefício:** Recomendações dinâmicas

### 4. **Design Completo** 🎨
- ✅ Banner carousel
- ✅ Cards de autores (altura uniforme)
- ✅ Sistema de opacidade
- ✅ Navbar e Footer ajustados

### 5. **Documentação Preservada** 📚
- ✅ Todos os guias
- ✅ Todos os scripts de diagnóstico
- ✅ Nada foi perdido no merge!

---

## 📋 **Pré-requisitos**

Antes de começar, verifique se você tem:

- ✅ Python 3.8+ instalado
- ✅ Git instalado
- ✅ Redis instalado (ou acesso a Redis Cloud)
- ✅ Conta Google (para obter GEMINI_API_KEY)

---

## 🚀 **Passo-a-Passo Completo**

### **PASSO 1: Validar a Branch**

Execute o script de validação automático:

```bash
bash scripts/test_integrated_branch.sh
```

**Resultado esperado:**
```
✓ Passaram: 19
⚠ Avisos: 5 (dependências não instaladas - é normal)
✗ Falharam: 0
```

Se falhou, siga as instruções na tela.

---

### **PASSO 2: Configurar Ambiente (.env)**

```bash
# Criar arquivo .env baseado no template
bash scripts/setup_local_env.sh
```

Isso cria um arquivo `.env` com valores padrão.

---

### **PASSO 3: Obter GEMINI API KEY** (CRÍTICO!)

**Sem essa chave, a IA NÃO funcionará!**

1. Acesse: **https://aistudio.google.com/app/apikey**
2. Faça login com sua conta Google
3. Clique em **"Create API Key"**
4. Copie a chave gerada (ex: `AIzaSyA...`)

---

### **PASSO 4: Adicionar GEMINI_API_KEY ao .env**

Edite o arquivo `.env`:

```bash
nano .env
# ou
code .env  # VS Code
# ou
vim .env
```

Encontre a linha:
```bash
GEMINI_API_KEY=
```

Cole sua chave:
```bash
GEMINI_API_KEY=AIzaSyA_sua_chave_aqui
```

**Salve o arquivo** (Ctrl+X no nano, depois Y e Enter)

---

### **PASSO 5: Instalar Dependências Python**

```bash
pip install -r requirements.txt
```

**Se estiver usando ambiente virtual (recomendado):**

```bash
# Criar ambiente virtual
python3 -m venv venv

# Ativar (Linux/Mac)
source venv/bin/activate

# Ativar (Windows)
venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt
```

---

### **PASSO 6: Iniciar Redis**

#### Linux/Mac:
```bash
redis-server --daemonize yes
```

#### Windows:
```bash
# Baixe e instale: https://github.com/microsoftarchive/redis/releases
redis-server
```

#### Verificar se está rodando:
```bash
redis-cli ping
# Deve retornar: PONG
```

---

### **PASSO 7: Limpar Cache Antigo do Redis**

**IMPORTANTE:** Limpe o cache para garantir que testa com dados novos!

```bash
redis-cli FLUSHALL
```

**OU** use o script:
```bash
bash scripts/clear_all_caches.sh
```

---

### **PASSO 8: Aplicar Migrações do Banco de Dados**

```bash
python manage.py migrate
```

**Se não tiver banco de dados criado ainda:**

```bash
# Criar superusuário
python manage.py createsuperuser

# Popular dados iniciais (categorias, livros de exemplo)
python manage.py setup_initial_data
```

---

### **PASSO 9: Iniciar Servidor Django**

#### Opção A - Script Automático (Recomendado):
```bash
bash scripts/start_local.sh
```

Isso inicia:
- ✅ Redis (se não estiver rodando)
- ✅ Django development server

#### Opção B - Manual:
```bash
python manage.py runserver
```

**Saída esperada:**
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

---

### **PASSO 10: Testar no Navegador**

Abra seu navegador em: **http://localhost:8000/**

---

## 🧪 **Checklist de Testes**

Use este checklist para garantir que tudo está funcionando:

### ✅ **1. Teste de Login**
- [ ] Consegue fazer login?
- [ ] Consegue criar conta?

### ✅ **2. Teste de Recomendações Personalizadas**

1. **Adicione livros às prateleiras:**
   - [ ] Adicione 3-5 livros aos "Favoritos"
   - [ ] Adicione 2-3 livros aos "Lidos"

2. **Acesse a home e role até "Para Você"**

3. **Clique em "Personalizado":**
   - [ ] Carrega recomendações em < 2s?
   - [ ] Mostra livros diferentes dos que você adicionou?

4. **Adicione mais 2 livros aos Favoritos**

5. **Recarregue a página (F5):**
   - [ ] Recomendações mudaram? ✅ (cache por hash funcionando!)

### ✅ **3. Teste de IA Premium**

**IMPORTANTE:** Primeira chamada pode demorar até 30s. Seja paciente!

1. **Clique em "IA Premium":**
   - [ ] Mostra "Consultando IA... Isso pode levar alguns segundos"?
   - [ ] Carrega em < 40s?
   - [ ] Mostra livros do Google Books (badge "Novo")?

2. **Clique em "IA Premium" novamente:**
   - [ ] Agora carrega em < 1s? ✅ (cache Redis funcionando!)
   - [ ] Mostra banner: "Cache ativo! Recomendações carregadas em 0.XX s"?

### ✅ **4. Teste de Fallback** (Simulação de Erro)

**Como testar:**

1. **Pare o servidor:** `Ctrl+C`

2. **Temporariamente corrompa a GEMINI_API_KEY:**
   ```bash
   # .env
   GEMINI_API_KEY=CHAVE_INVALIDA_PARA_TESTE
   ```

3. **Reinicie o servidor:**
   ```bash
   python manage.py runserver
   ```

4. **Clique em "IA Premium":**
   - [ ] Mostra erro por alguns segundos?
   - [ ] Automaticamente carrega recomendações personalizadas? ✅ (fallback!)
   - [ ] Console do navegador (F12) mostra: `Gemini AI failed. Falling back...`?

5. **Restaure a chave correta no .env**

### ✅ **5. Teste de Design**

1. **Banner Carousel:**
   - [ ] Banner está visível no topo da home?
   - [ ] Alterna automaticamente?

2. **Cards de Autores:**
   - [ ] Todos os cards têm a mesma altura?
   - [ ] Texto da biografia está limitado a 3 linhas?

3. **Navbar e Footer:**
   - [ ] Navbar está estilizada corretamente?
   - [ ] Footer está posicionado no final?

4. **Opacidade das Seções:**
   - [ ] Seções têm fundo levemente transparente?

### ✅ **6. Teste de Performance**

Abra o **DevTools** (F12) → **Network**:

1. **Primeira chamada à IA:**
   - [ ] Tempo: < 40s

2. **Segunda chamada (cache):**
   - [ ] Tempo: < 1s

3. **Recomendações Personalizadas:**
   - [ ] Tempo: < 2s

---

## 🐛 **Troubleshooting**

### **Problema: "ModuleNotFoundError: No module named 'django'"**

**Solução:**
```bash
# Ative o ambiente virtual
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Instale dependências
pip install -r requirements.txt
```

---

### **Problema: "Redis connection refused"**

**Solução:**
```bash
# Iniciar Redis
redis-server --daemonize yes

# Verificar
redis-cli ping  # Deve retornar PONG
```

---

### **Problema: "Gemini API timeout"**

**Causas:**
1. **Primeira chamada é lenta** (normal, 15-30s)
   - Aguarde! Próximas serão rápidas (cache)

2. **GEMINI_API_KEY inválida**
   - Verifique se copiou corretamente
   - Teste: `python -c "from decouple import config; print(config('GEMINI_API_KEY'))"`

3. **Problema de rede**
   - Verifique sua conexão com a internet

---

### **Problema: "Recomendações sempre iguais"**

**Solução:**
```bash
# Limpar cache
redis-cli FLUSHALL

# Reiniciar servidor
python manage.py runserver
```

---

### **Problema: "Design quebrado / estilos não aplicados"**

**Solução:**

1. **Hard Refresh no navegador:**
   - Windows/Linux: `Ctrl + Shift + R`
   - Mac: `Cmd + Shift + R`

2. **Coletar arquivos estáticos:**
   ```bash
   python manage.py collectstatic --no-input
   ```

3. **Limpar cache do navegador:**
   - Chrome: `Ctrl + Shift + Delete`

---

## 📊 **Logs Úteis**

### **Ver logs do Django:**
Os logs aparecem no terminal onde você rodou `python manage.py runserver`

**Logs importantes:**
```
✓ "GET /recommendations/api/recommendations/ HTTP/1.1" 200
✓ "Using cached enhanced recommendations for username"
✓ "Gemini AI called successfully"
⚠ "Gemini AI failed: ... Falling back to preference_hybrid"
```

### **Ver logs do Redis:**
```bash
redis-cli monitor
```

### **Ver cache do Redis:**
```bash
redis-cli KEYS "*"
redis-cli GET "gemini_enhanced:1:6:..."
```

---

## ✅ **Resultado Esperado**

Se todos os testes passaram:

✅ **IA Premium funciona** (40s timeout + fallback)
✅ **Recomendações Personalizadas dinâmicas** (cache por hash)
✅ **Design impecável** (Banner, Cards, Navbar, Footer)
✅ **Fallback automático** (nunca tela vazia)
✅ **Performance excelente** (< 1s com cache)

**🎉 PARABÉNS! Está pronto para deploy no Render!**

---

## 🚀 **Próximo Passo: Deploy no Render**

Depois de testar localmente e confirmar que tudo funciona:

1. **Acesse o Dashboard do Render**

2. **Limpe o cache do Redis (PRODUÇÃO):**
   - Render Dashboard → Redis → Shell
   - Execute: `FLUSHALL`

3. **Configure o deploy:**
   - Render Dashboard → Web Service → Settings
   - Branch: `claude/integrated-recommendations-and-ux-013suojTnoYABUtLhNEbLp49`

4. **Deploy:**
   - Manual Deploy → Deploy latest commit

5. **Teste em produção:**
   - Repita os testes do checklist acima
   - URL: `https://seu-app.onrender.com`

---

## 🆘 **Precisa de Ajuda?**

1. **Execute o diagnóstico:**
   ```bash
   bash scripts/diagnose_recommendations.sh
   ```

2. **Veja os logs do Django no terminal**

3. **Veja o console do navegador (F12 → Console)**

4. **Leia a documentação:**
   - [GUIA_CONFIGURACAO_LOCAL.md](GUIA_CONFIGURACAO_LOCAL.md)
   - [TROUBLESHOOTING_CACHE.md](TROUBLESHOOTING_CACHE.md)

---

**Boa sorte com os testes! 🚀**
