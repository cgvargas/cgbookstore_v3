# 🔧 Troubleshooting - Chatbot Literário

## ❌ Problema: "Unknown command: 'test_gemini'"

### Causa
O Django não está reconhecendo o novo comando. Isso acontece quando:
- Os módulos Python estão em cache
- O Django não recarregou os comandos de management

### ✅ Solução (Windows)

**Opção 1: Limpar cache manualmente**
```powershell
# No diretório do projeto
Get-ChildItem -Path . -Recurse -Filter "__pycache__" | Remove-Item -Recurse -Force
Get-ChildItem -Path . -Recurse -Filter "*.pyc" | Remove-Item -Force
```

**Opção 2: Usar script de limpeza**
```powershell
.\scripts\clear_cache.bat
python manage.py test_gemini
```

**Opção 3: Reiniciar o shell Python**
```powershell
# Feche e abra novamente o PowerShell ou CMD
# Ative novamente o ambiente virtual
.\.venv\Scripts\activate
python manage.py test_gemini
```

### ✅ Solução (Linux/Mac)

```bash
# Limpar cache
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null

# Ou usar o script
chmod +x scripts/clear_cache.sh
./scripts/clear_cache.sh

# Executar comando
python manage.py test_gemini
```

### ✅ Verificar se o comando está disponível

```bash
# Listar todos os comandos disponíveis
python manage.py help

# Procurar por test_gemini
python manage.py help | grep test_gemini  # Linux/Mac
python manage.py help | findstr test_gemini  # Windows
```

Se `test_gemini` aparecer na lista, está funcionando!

---

## ⚠️ Problema: Erro de DNS do Supabase

```
❌ Falha ao resolver DNS: [Errno 11001] getaddrinfo failed
```

### Causa
- Problema de conexão com o banco de dados Supabase
- Ocorre durante a inicialização do Django (antes do comando executar)
- Não afeta o comando `test_gemini` (que não precisa de banco de dados)

### ✅ Solução Temporária (para testar o Gemini)

Você pode ignorar esse erro **se apenas quiser testar o Gemini**. O erro aparece mas o comando deveria executar mesmo assim.

### ✅ Solução Permanente (para produção)

1. **Use Transaction Pooler do Supabase:**
   ```env
   # No .env, troque a URL direta pelo pooler
   DATABASE_URL=postgresql://postgres.xxxxx:password@aws-0-us-east-1.pooler.supabase.com:5432/postgres
   ```

2. **Ou configure IPv4 manualmente:**
   ```powershell
   # Descubra o IP IPv4
   nslookup db.uomjbcuowfgcwhsejatn.supabase.co

   # Adicione ao .env
   DATABASE_IPV4=44.XXX.XXX.XXX
   ```

---

## 🔍 Problema: API Key não está sendo reconhecida

### Verificar se está configurada

```bash
# Windows PowerShell
Get-Content .env | Select-String "GEMINI_API_KEY"

# Linux/Mac
grep GEMINI_API_KEY .env
```

### Formato correto no .env

```env
# ✅ Correto
GEMINI_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# ❌ Errado (com aspas)
GEMINI_API_KEY="AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

# ❌ Errado (com espaços)
GEMINI_API_KEY = AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### Verificar no Django shell

```bash
python manage.py shell
```

```python
from django.conf import settings
print(settings.GEMINI_API_KEY)
# Deve mostrar sua key (ou string vazia se não configurada)
```

---

## 🚀 Teste Rápido sem Banco de Dados

Se você só quer testar o Gemini **sem conectar ao banco**, crie este arquivo de teste:

**test_gemini_standalone.py:**
```python
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'cgbookstore.settings'

# Configurar Django
import django
django.setup()

# Testar Gemini
from chatbot_literario.gemini_service import get_chat_service

chat_service = get_chat_service()
print(f"API Key configurada: {chat_service.is_available()}")

if chat_service.is_available():
    result = chat_service.get_response("Olá! Me recomende um livro de ficção científica.")
    if result['success']:
        print("\n✅ Resposta do Gemini:")
        print(result['response'])
    else:
        print(f"\n❌ Erro: {result['error']}")
else:
    print("❌ Serviço não disponível - configure GEMINI_API_KEY")
```

Execute:
```bash
python test_gemini_standalone.py
```

---

## 📞 Checklist de Diagnóstico

Use esta ordem para resolver problemas:

- [ ] **Limpar cache do Python**
  ```bash
  # Windows
  .\scripts\clear_cache.bat

  # Linux/Mac
  ./scripts/clear_cache.sh
  ```

- [ ] **Verificar se comando existe**
  ```bash
  python manage.py help | grep test_gemini
  ```

- [ ] **Verificar API Key no .env**
  ```bash
  grep GEMINI_API_KEY .env
  ```

- [ ] **Testar no Django shell**
  ```python
  from django.conf import settings
  print(bool(settings.GEMINI_API_KEY))
  ```

- [ ] **Executar teste**
  ```bash
  python manage.py test_gemini
  ```

---

## 🆘 Ainda não funciona?

### Verifique a instalação do app

```python
# No settings.py, verificar se está em INSTALLED_APPS
INSTALLED_APPS = [
    # ...
    'chatbot_literario.apps.ChatbotLiterarioConfig',
    # ou simplesmente:
    'chatbot_literario',
    # ...
]
```

### Verifique a estrutura de arquivos

```
chatbot_literario/
├── management/
│   ├── __init__.py          ← Deve existir
│   └── commands/
│       ├── __init__.py      ← Deve existir
│       └── test_gemini.py   ← Comando
```

### Execute com Python direto

```bash
# Se manage.py não funcionar, tente:
python -c "
import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()
from django.core.management import execute_from_command_line
execute_from_command_line(['manage.py', 'test_gemini'])
"
```

---

## 💡 Dicas

1. **Sempre limpe o cache** após adicionar novos comandos Django
2. **Reinicie o servidor** de desenvolvimento após mudanças em management commands
3. **Use ambiente virtual** para evitar conflitos de dependências
4. **Verifique o .env** está na raiz do projeto (mesmo nível do manage.py)

---

**Documentação completa:** `/chatbot_literario/README.md`
