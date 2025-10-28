# ✅ CHECKLIST PRÉ-IMPLEMENTAÇÃO - VALIDAÇÃO RÁPIDA

**Projeto:** CGBookStore v3  
**Data:** 27/10/2025

---

## 🔍 **VALIDAÇÕES OBRIGATÓRIAS**

### **1. Ambiente de Desenvolvimento**
```powershell
# Execute no PowerShell:
cd C:\ProjectsDjango\cgbookstore_v3

# Verificar Python
python --version
# ✅ Esperado: Python 3.10.x ou superior

# Verificar ambiente virtual ativo
where python
# ✅ Esperado: C:\ProjectsDjango\cgbookstore_v3\.venv\Scripts\python.exe
```

### **2. Git Status**
```powershell
git status
# ✅ Esperado: "working tree clean" ou apenas status_27102025.md modificado
```

### **3. Servidor Django Funcionando**
```powershell
python manage.py runserver
# ✅ Acessar: http://127.0.0.1:8000
# ✅ Verificar: Site carrega normalmente
# Ctrl+C para parar
```

### **4. Banco de Dados Conectando**
```powershell
python manage.py showmigrations
# ✅ Esperado: Lista de migrations sem [X] ou [ ] pendentes
```

---

## 🔴 **INSTALAÇÃO DO REDIS** (SE NECESSÁRIO)

### **Opção 1: Windows com Chocolatey** ⭐ (Recomendado)
```powershell
# Instalar Chocolatey (se não tiver):
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Instalar Redis:
choco install redis-64 -y

# Iniciar Redis:
redis-server

# Testar (outro terminal):
redis-cli ping
# ✅ Esperado: PONG
```

### **Opção 2: WSL (Windows Subsystem for Linux)**
```powershell
# Instalar Redis no WSL:
wsl sudo apt-get update
wsl sudo apt-get install redis-server -y

# Iniciar Redis:
wsl sudo service redis-server start

# Testar:
wsl redis-cli ping
# ✅ Esperado: PONG
```

### **Opção 3: Docker** 🐳
```powershell
# Baixar e rodar Redis:
docker run -d -p 6379:6379 --name redis-cgbookstore redis:7-alpine

# Testar:
docker exec -it redis-cgbookstore redis-cli ping
# ✅ Esperado: PONG
```

---

## 📦 **BACKUP PRÉ-IMPLEMENTAÇÃO**

### **1. Backup do Código**
```powershell
# Criar branch de backup:
git checkout -b backup-pre-optimizations
git add .
git commit -m "backup: Estado antes das otimizações"
git checkout main
```

### **2. Backup do Banco (via Supabase Dashboard)**
```
1. Acessar: https://supabase.com/dashboard
2. Selecionar projeto: cgbookstore_v3
3. Database → Backups → Create Backup
4. Aguardar confirmação
```

### **3. Backup de Arquivos Críticos**
```powershell
# Criar pasta de backup:
mkdir C:\ProjectsDjango\cgbookstore_v3_backup

# Copiar arquivos importantes:
copy cgbookstore\settings.py C:\ProjectsDjango\cgbookstore_v3_backup\
copy requirements.txt C:\ProjectsDjango\cgbookstore_v3_backup\
copy .env C:\ProjectsDjango\cgbookstore_v3_backup\
```

---

## 🖥️ **PREPARAR TERMINAIS**

Você precisará de **3 terminais simultâneos** após implementação:

### **Terminal 1: Django Server**
```powershell
cd C:\ProjectsDjango\cgbookstore_v3
.venv\Scripts\activate
python manage.py runserver
```

### **Terminal 2: Celery Worker** (após implementação)
```powershell
cd C:\ProjectsDjango\cgbookstore_v3
.venv\Scripts\activate
celery -A cgbookstore worker -l info --pool=solo
```

### **Terminal 3: Celery Beat** (após implementação)
```powershell
cd C:\ProjectsDjango\cgbookstore_v3
.venv\Scripts\activate
celery -A cgbookstore beat -l info
```

---

## ✅ **CHECKLIST FINAL**

Marque TODAS antes de aprovar:

- [ ] Python 3.10+ instalado e verificado
- [ ] Ambiente virtual ativo (.venv)
- [ ] Git status limpo ou controlado
- [ ] Django rodando sem erros
- [ ] Banco de dados conectando
- [ ] Redis instalado e respondendo (redis-cli ping = PONG)
- [ ] Backup do código criado (branch backup)
- [ ] Backup do banco criado (Supabase)
- [ ] Arquivos críticos salvos
- [ ] VSCode aberto no projeto
- [ ] 3 terminais prontos para uso
- [ ] Li o documento de instruções completo
- [ ] Li o resumo executivo
- [ ] Compreendo as mudanças a serem feitas
- [ ] Aceito as novas dependências (~15MB)
- [ ] Tenho 8-10 horas para implementação e testes
- [ ] Estou pronto para iniciar

---

## 🚦 **COMANDOS DE APROVAÇÃO**

### **Se TODOS os checkboxes estão ✅:**

**Para implementação automática completa:**
```
Claude, você está AUTORIZADO a implementar todas as 8 fases das otimizações.
Siga o documento INSTRUCOES_OTIMIZACAO_ESCALABILIDADE.md.
Pause entre fases para validação.
```

**Para implementação faseada:**
```
Claude, comece pela FASE 1 (Instalação de Dependências).
Aguarde minha validação antes de prosseguir para a próxima fase.
```

---

## ⚠️ **SE ALGO FALHOU NO CHECKLIST:**

**Redis não instalado:**
- Siga as instruções de instalação acima
- Valide com `redis-cli ping`
- Só então autorize a implementação

**Git com mudanças não commitadas:**
- `git add .`
- `git commit -m "wip: salvando trabalho atual"`
- Então crie o branch de backup

**Django não rodando:**
- Verifique erros no terminal
- Execute `python manage.py check`
- Resolva problemas antes de aprovar

---

## 📞 **AJUDA RÁPIDA**

### **Erro: "Redis connection refused"**
```powershell
# Verificar se Redis está rodando:
redis-cli ping

# Se não responder, iniciar:
redis-server

# Ou via WSL:
wsl sudo service redis-server start
```

### **Erro: "Python not found"**
```powershell
# Ativar ambiente virtual:
.venv\Scripts\activate

# Verificar:
where python
```

### **Erro: "ModuleNotFoundError"**
```powershell
# Reinstalar dependências:
pip install -r requirements.txt
```

---

## 🎯 **PRÓXIMO PASSO**

Depois de validar TUDO acima:

1. ✅ Marque todos os checkboxes
2. 📄 Leia os documentos completos
3. 💬 Autorize Claude a começar
4. ⏱️ Aguarde implementação fase por fase

---

**Status:** ⏸️ **AGUARDANDO SUA VALIDAÇÃO E AUTORIZAÇÃO**

---

**Criado em:** 27/10/2025  
**Versão:** 1.0
