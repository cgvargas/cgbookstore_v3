# 🔄 Workflow de Desenvolvimento - CG Bookstore

Guia completo do fluxo de trabalho de desenvolvimento para deploy em produção.

---

## 📊 Fluxo de Trabalho

```
┌─────────────────────────────────────────────────────────────┐
│                   CICLO DE DESENVOLVIMENTO                   │
└─────────────────────────────────────────────────────────────┘

1. 💻 Desenvolvimento Local
   ↓
2. 🧪 Testes Locais
   ↓
3. ✅ Verificação (migrações, dependências)
   ↓
4. 📝 Git Commit
   ↓
5. 🚀 Git Push (GitHub)
   ↓
6. ☁️ Deploy Automático (Render)
   ↓
7. 🔍 Verificação em Produção
```

---

## 🛠️ Passo a Passo Detalhado

### 1️⃣ Desenvolvimento Local

Faça suas alterações no código:

```bash
# Ative o ambiente virtual
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate     # Windows

# Execute o servidor local
python manage.py runserver
```

**Acesse:** http://localhost:8000

---

### 2️⃣ Testes Locais

Teste todas as funcionalidades modificadas:

```bash
# Teste básico
python manage.py check

# Se modificou models
python manage.py makemigrations
python manage.py migrate

# Teste a aplicação
python manage.py runserver
# Navegue e teste manualmente
```

**Checklist de Testes:**
- [ ] Funcionalidade principal funciona
- [ ] Sem erros no console do navegador
- [ ] Sem erros no terminal do Django
- [ ] Formulários salvam corretamente
- [ ] Páginas carregam sem erros 500/404

---

### 3️⃣ Verificações Antes do Commit

#### Verificar Migrações

```bash
python manage.py makemigrations --check --dry-run
python manage.py showmigrations
```

#### Verificar Dependências

Se adicionou pacotes novos:

```bash
pip freeze > config/requirements.txt
cp config/requirements.txt requirements.txt
```

#### Verificar Arquivos Estáticos

```bash
python manage.py collectstatic --no-input --dry-run
```

---

### 4️⃣ Git Commit

Faça commit das alterações:

```bash
# Ver status
git status

# Adicionar arquivos
git add .

# Commit com mensagem clara
git commit -m "Feature: Descrição clara da mudança

- Detalhe 1
- Detalhe 2
- Detalhe 3"
```

**Exemplos de Mensagens:**

```bash
# Feature nova
git commit -m "Feature: Adicionar filtro de busca avançada"

# Correção de bug
git commit -m "Fix: Corrigir erro 500 na página de checkout"

# Melhorias
git commit -m "Improvement: Otimizar query de recomendações"

# Documentação
git commit -m "Docs: Atualizar guia de deploy"

# Refatoração
git commit -m "Refactor: Reorganizar estrutura de templates"
```

---

### 5️⃣ Git Push

Envie para o GitHub:

```bash
# Push para branch main
git push origin main

# ou simplesmente
git push
```

**O que acontece:**
- Código é enviado para GitHub
- Render detecta mudança automaticamente
- Inicia deploy automático

---

### 6️⃣ Deploy Automático no Render

O Render executará automaticamente:

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Coletar arquivos estáticos
python manage.py collectstatic --no-input

# 3. Migrações
python manage.py makemigrations --no-input
python manage.py migrate --no-input

# 4. Setup inicial (se necessário)
python manage.py setup_initial_data --skip-superuser

# 5. Criar superuser (se configurado)
# Se CREATE_SUPERUSER=true
```

**Acompanhar Deploy:**
1. Acesse https://dashboard.render.com
2. Clique no serviço `cgbookstore`
3. Veja **Logs** em tempo real

---

### 7️⃣ Verificação em Produção

Após deploy completo:

```bash
# Verificar health check
https://cgbookstore-v3.onrender.com/admin-tools/health/

# Testar funcionalidade principal
https://cgbookstore-v3.onrender.com

# Verificar admin
https://cgbookstore-v3.onrender.com/admin/
```

**Checklist Pós-Deploy:**
- [ ] Site carrega sem erros
- [ ] Nova funcionalidade funciona
- [ ] Admin acessível
- [ ] Sem erros 500 nos logs
- [ ] Arquivos estáticos carregam

---

## ✅ Boas Práticas

### 🎯 Sempre Faça

1. **Teste Localmente Primeiro**
   - NUNCA faça push sem testar
   - Execute `python manage.py check`
   - Navegue pela aplicação

2. **Commits Pequenos e Frequentes**
   - Commits menores são mais fáceis de debugar
   - Use mensagens descritivas
   - Um commit = uma funcionalidade/correção

3. **Verifique Migrações**
   - Sempre rode `makemigrations` antes de commit
   - Verifique se migrações foram criadas
   - Teste migrate localmente

4. **Atualizar requirements.txt**
   - Se instalou pacote novo, atualize requirements.txt
   - Copie para raiz: `cp config/requirements.txt .`

5. **Documentar Mudanças**
   - Atualize README se necessário
   - Documente APIs/endpoints novos
   - Comente código complexo

---

### ❌ Evite

1. **Push de Código Não Testado**
   - ❌ NUNCA faça push direto sem testar
   - ❌ Produção NÃO é ambiente de teste

2. **Commits Gigantes**
   - ❌ Evite commits com 50+ arquivos
   - ❌ Dificulta identificar problemas

3. **Credenciais no Código**
   - ❌ NUNCA commite `.env`
   - ❌ NUNCA coloque senhas/tokens no código
   - ✅ Use variáveis de ambiente

4. **Testar Direto em Produção**
   - ❌ Não use produção como ambiente de teste
   - ❌ Não modifique dados de produção diretamente

5. **Ignorar Erros nos Logs**
   - ❌ Sempre verifique logs após deploy
   - ❌ Não ignore warnings/errors

---

## 🚨 Problemas Comuns

### Deploy Falhou?

```bash
# 1. Ver logs no Render
Dashboard > Seu serviço > Logs

# 2. Procurar por erros
# - ModuleNotFoundError: falta pacote no requirements.txt
# - TemplateDoesNotExist: arquivo de template faltando
# - DatabaseError: problema em migração
```

**Soluções:**
- Adicionar pacote faltante ao `requirements.txt`
- Verificar se todos os arquivos foram commitados
- Verificar migrações localmente

---

### Site em Branco/Erro 500?

```bash
# Health check
https://seu-site.onrender.com/admin-tools/health/

# Ver logs detalhados
Dashboard Render > Logs > filtrar "ERROR"
```

**Soluções Comuns:**
- Executar `collectstatic` novamente
- Verificar se todas as migrações rodaram
- Verificar variáveis de ambiente

---

### Migrações Conflitantes?

```bash
# Local: resetar migrações de conflito
python manage.py migrate app_name zero
python manage.py migrate app_name

# Produção: forçar redeploy
Dashboard > Manual Deploy > Clear build cache & deploy
```

---

## 🔧 Comandos Úteis

### Desenvolvimento Local

```bash
# Iniciar servidor
python manage.py runserver

# Criar migrações
python manage.py makemigrations

# Aplicar migrações
python manage.py migrate

# Popular dados
python manage.py setup_initial_data

# Health check
python manage.py health_check

# Shell interativo
python manage.py shell

# Criar superuser
python manage.py createsuperuser
```

---

### Git

```bash
# Status
git status

# Adicionar arquivos
git add .

# Commit
git commit -m "mensagem"

# Push
git push

# Ver histórico
git log --oneline -10

# Desfazer último commit (local)
git reset --soft HEAD~1

# Ver diferenças
git diff
```

---

### Render (via Dashboard)

- **Logs:** Ver logs em tempo real
- **Manual Deploy:** Forçar redeploy
- **Environment:** Configurar variáveis
- **Clear build cache:** Rebuild completo

---

## 📋 Checklist Completo

### Antes de Cada Deploy

- [ ] Código testado localmente
- [ ] `python manage.py check` sem erros
- [ ] Migrações criadas e testadas
- [ ] `requirements.txt` atualizado (se necessário)
- [ ] Nenhuma credencial no código
- [ ] Commit com mensagem clara
- [ ] Push para GitHub

### Após Cada Deploy

- [ ] Deploy completou sem erros
- [ ] Health check OK (`/admin-tools/health/`)
- [ ] Site carrega normalmente
- [ ] Nova funcionalidade funciona
- [ ] Logs sem erros críticos
- [ ] Admin acessível

---

## 🎓 Exemplos Práticos

### Exemplo 1: Adicionar Nova Feature

```bash
# 1. Desenvolver
# ... codificar nova feature ...

# 2. Testar
python manage.py runserver
# ... testar manualmente ...

# 3. Commit
git add .
git commit -m "Feature: Sistema de avaliações de livros"

# 4. Push
git push

# 5. Verificar deploy no Render
# Dashboard > Logs
```

---

### Exemplo 2: Corrigir Bug

```bash
# 1. Identificar e corrigir bug localmente
# ... corrigir código ...

# 2. Testar correção
python manage.py runserver

# 3. Commit
git add .
git commit -m "Fix: Corrigir erro ao salvar avaliação"

# 4. Push
git push

# 5. Verificar em produção
```

---

### Exemplo 3: Atualizar Dependência

```bash
# 1. Instalar nova versão
pip install django==5.2

# 2. Atualizar requirements
pip freeze > config/requirements.txt
cp config/requirements.txt .

# 3. Testar localmente
python manage.py check

# 4. Commit
git add requirements.txt config/requirements.txt
git commit -m "Update: Atualizar Django para 5.2"

# 5. Push
git push
```

---

## 🆘 Suporte

### Problemas?

1. **Health Check:** `/admin-tools/health/`
2. **Logs Render:** Dashboard > Logs
3. **Documentação:** [docs/troubleshooting/](troubleshooting/)

### Recursos

- **README:** [../README.md](../README.md)
- **Estrutura:** [../ESTRUTURA_PROJETO.md](../ESTRUTURA_PROJETO.md)
- **Deploy:** [deployment/DEPLOY_RENDER.md](deployment/DEPLOY_RENDER.md)
- **Troubleshooting:** [troubleshooting/TROUBLESHOOTING_PRODUCAO.md](troubleshooting/TROUBLESHOOTING_PRODUCAO.md)

---

**Desenvolvido com boas práticas de DevOps e CI/CD! 🚀**

**Última atualização:** Novembro 2025
