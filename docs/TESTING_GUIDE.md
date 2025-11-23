# 🧪 Guia de Testes - Correções Implementadas

**Branch:** `claude/review-guidelines-compliance-01EpqDYPqjr8Esyvpi13mG8y`
**Data:** 2025-11-23
**Status:** ✅ Código commitado e enviado - Pronto para testes

---

## 📋 Resumo das Correções Implementadas

### 1. ✅ **Correção do Chatbot Gemini AI**

**Problema Original:**
- Chatbot ignorava orientações
- Não usava o nome do usuário
- Muito verboso
- Temperature muito alta (0.9)
- Dizia "vendemos livros" (incorreto)

**Correções Aplicadas:**

| Arquivo | Mudança | Status |
|---------|---------|--------|
| `chatbot_literario/gemini_service.py` | Temperature: 0.9 → 0.3 | ✅ |
| `chatbot_literario/gemini_service.py` | top_p: 0.95 → 0.8 | ✅ |
| `chatbot_literario/gemini_service.py` | top_k: 40 → 20 | ✅ |
| `chatbot_literario/gemini_service.py` | System prompt dinâmico com {username} | ✅ |
| `chatbot_literario/gemini_service.py` | Prompt reduzido (~87 → ~40 linhas) | ✅ |
| `chatbot_literario/views.py` | Passagem do username para o serviço | ✅ |

**Mudanças Chave:**

```python
# ANTES
SYSTEM_PROMPT = """..."""  # Estático, sem nome do usuário
model = genai.GenerativeModel(
    generation_config={
        'temperature': 0.9,  # Muito criativo
        'top_p': 0.95,
        'top_k': 40,
    }
)

# DEPOIS
SYSTEM_PROMPT_TEMPLATE = """
Você é o Assistente Literário da CG.BookStore.

NOME DO USUÁRIO: {username}

REGRAS ABSOLUTAS (SIGA RIGOROSAMENTE):
1. SEMPRE use o nome "{username}" em TODAS as respostas
2. CG.BookStore é COMUNIDADE/APLICAÇÃO WEB - NÃO vendemos livros
...
"""

generation_config = {
    'temperature': 0.3,  # Mais obediente
    'top_p': 0.8,
    'top_k': 20,
}
```

---

### 2. ✅ **Correção de UserProfile Duplicado**

**Problema Original:**
```
IntegrityError: duplicate key value violates unique constraint "accounts_userprofile_user_id_key"
```

**Causa Raiz:**
- Dois signals usando `.create()` em vez de `.get_or_create()`
- Ambos tentavam criar UserProfile para o mesmo usuário

**Correção Aplicada:**

| Arquivo | Linha | Mudança | Status |
|---------|-------|---------|--------|
| `accounts/signals.py` | 32-42 | `.create()` → `.get_or_create()` | ✅ |
| `accounts/signals.py` | 107-116 | `.create()` → `.get_or_create()` | ✅ |

**Código Corrigido:**

```python
# Signal 1: create_user_profile
profile, profile_created = UserProfile.objects.get_or_create(
    user=instance,
    defaults={
        'theme_preference': 'fantasy',
        'level': 1,
        'total_xp': 0
    }
)
if not profile_created:
    logger.warning(f"UserProfile já existia para {instance.username}")

# Signal 2: save_user_profile
profile, created = UserProfile.objects.get_or_create(
    user=instance,
    defaults={
        'theme_preference': 'fantasy',
        'level': 1,
        'total_xp': 0
    }
)
if created:
    logger.info(f"UserProfile criado via fallback para {instance.username}")
```

---

## 🧪 Plano de Testes

### **Pré-requisitos:**

```powershell
# 1. Ir para o diretório do projeto
cd C:\ProjectDjango\cgbookstore_v3

# 2. Ativar ambiente virtual (se usar)
.\venv\Scripts\activate

# 3. Fazer pull das mudanças
git pull origin claude/review-guidelines-compliance-01EpqDYPqjr8Esyvpi13mG8y

# 4. Verificar status
git status
```

---

### **Teste 1: Verificar Integridade de UserProfiles** ⏳

**Objetivo:** Verificar se há duplicatas ou usuários sem perfil

```powershell
# Executar script de verificação
python verify_userprofiles.py
```

**Saída Esperada:**

```
======================================================================
📊 VERIFICAÇÃO COMPLETA DE USERPROFILES
======================================================================

📈 Estatísticas:
   Total de Users: 25
   Total de UserProfiles: 25
   Diferença: 0
   ✅ Quantidade OK (1 perfil por usuário)

🔍 Verificando duplicatas...
   ✅ Nenhuma duplicata encontrada

✅ Todos os usuários têm perfil

📋 Últimos 5 usuários criados:
   ✅ ID: 25, Username: joao_silva, Criado: 2025-11-23 14:30
   ✅ ID: 24, Username: maria_santos, Criado: 2025-11-23 10:15
   ...

✅ Verificação concluída!
```

**❓ Se houver problemas:**

```powershell
# Executar script de correção
python fix_userprofile_duplicate.py

# Escolher 's' quando perguntar se quer corrigir
```

---

### **Teste 2: Criar Novo Usuário no Admin** ⏳

**Objetivo:** Verificar se a correção de signals funciona

```powershell
# 1. Iniciar servidor
python manage.py runserver
```

**Passos:**

1. Acesse: `http://localhost:8000/admin/`
2. Login com superuser
3. Navegue: **Autenticação e Autorização** → **Usuários**
4. Clique: **Adicionar usuário**
5. Preencha:
   - **Username:** `teste_user_001`
   - **Password:** `senha_teste_123`
6. Clique: **Salvar**
7. Verifique se o usuário foi criado **SEM ERRO**

**Resultado Esperado:**

✅ **Sucesso:** Usuário criado, redirecionado para página de edição
❌ **Erro:** IntegrityError sobre UserProfile duplicado

**Verificação Adicional:**

```powershell
# Verificar no Django shell
python manage.py shell

>>> from django.contrib.auth.models import User
>>> from accounts.models import UserProfile
>>>
>>> # Pegar o usuário criado
>>> user = User.objects.get(username='teste_user_001')
>>>
>>> # Verificar se tem profile (deve funcionar sem erro)
>>> profile = user.profile
>>> print(f"Profile ID: {profile.id}, Theme: {profile.theme_preference}")
>>>
>>> # Verificar se há duplicatas (deve ser 1)
>>> count = UserProfile.objects.filter(user=user).count()
>>> print(f"Profiles para {user.username}: {count}")
>>> assert count == 1, "ERRO: Mais de 1 perfil!"
>>> print("✅ Teste passou!")
```

---

### **Teste 3: Validar Chatbot Gemini** ⏳

**Objetivo:** Verificar se chatbot usa nome do usuário e segue orientações

```powershell
# 1. Iniciar servidor (se não estiver rodando)
python manage.py runserver

# 2. Abrir navegador
start http://localhost:8000/chatbot/
```

**Cenários de Teste:**

#### **Cenário 1: Verificar Nome do Usuário**

**Ação:**
1. Login com seu usuário (ex: `Dbit`)
2. Enviar mensagem: `"Olá!"`

**Resultado Esperado:**

```
✅ Olá, Dbit! 🎭 Bem-vindo à CG.BookStore!
Como posso ajudar você hoje?
```

**❌ Resultado Incorreto:**

```
❌ Olá! Como posso ajudar? (SEM usar o nome)
```

---

#### **Cenário 2: Verificar Concisão**

**Ação:**
Enviar: `"Me recomende um livro"`

**Resultado Esperado:**

✅ **Resposta curta (2-3 frases):**

```
Dbit, recomendo "1984" de George Orwell! 📚
Uma distopia clássica sobre controle e liberdade.
Perfeito para reflexões profundas! 🤔
```

**❌ Resultado Incorreto (muito verboso):**

```
❌ Olá! Claro, vou recomendar um livro maravilhoso para você! [...]
[20 linhas de texto explicando tudo em detalhes...]
```

---

#### **Cenário 3: Verificar "Não Vendemos Livros"**

**Ação:**
Enviar: `"Onde posso comprar este livro?"`

**Resultado Esperado:**

```
✅ Dbit, a CG.BookStore é uma comunidade, não vendemos livros diretamente.
Você pode comprar na Amazon (nosso parceiro).
```

**❌ Resultado Incorreto:**

```
❌ Você pode comprar aqui na nossa loja! (ERRADO)
```

---

#### **Cenário 4: Verificar Temperatura (Obediência)**

**Ação:**
Enviar: `"Seja breve ao responder"`

**Resultado Esperado:**

```
✅ Ok, Dbit! Vou ser breve. 👍
```

**❌ Resultado Incorreto:**

```
❌ Claro! Vou tentar ser mais breve, mas deixa eu explicar primeiro que [...]
[Continua sendo verboso mesmo após pedido]
```

---

## 📊 Checklist de Validação

Marque conforme completar os testes:

### **Integridade de UserProfiles:**
- [ ] `verify_userprofiles.py` executado sem erros
- [ ] Nenhuma duplicata encontrada
- [ ] Todos os usuários têm perfil

### **Criação de Usuários:**
- [ ] Novo usuário criado no admin sem `IntegrityError`
- [ ] UserProfile criado automaticamente
- [ ] Nenhuma duplicata criada

### **Chatbot Gemini:**
- [ ] ✅ Usa nome do usuário em todas as respostas
- [ ] ✅ Respostas concisas (2-3 frases)
- [ ] ✅ Diz que é comunidade (não vende livros)
- [ ] ✅ Indica Amazon como parceiro
- [ ] ✅ Obedece instruções (temperature baixa)

---

## 🐛 Solução de Problemas

### **Problema 1: Merge Conflicts**

```powershell
# Se ainda houver conflitos de merge
git reset --hard origin/claude/review-guidelines-compliance-01EpqDYPqjr8Esyvpi13mG8y

# Verificar
python manage.py check
```

---

### **Problema 2: Erro de Importação**

```powershell
# Se houver ModuleNotFoundError
pip install -r requirements.txt

# Verificar Django
python manage.py check
```

---

### **Problema 3: Banco de Dados**

```powershell
# Se houver erro de conexão com banco
# Verificar .env
type .env

# Verificar se DATABASE_URL está correto
# Testar conexão
python manage.py migrate --check
```

---

### **Problema 4: Chatbot Ainda Verboso**

**Possível causa:** Código antigo em cache

**Solução:**

```powershell
# 1. Parar o servidor (Ctrl+C)

# 2. Limpar cache Python
python -c "import shutil; shutil.rmtree('__pycache__', ignore_errors=True)"
python -c "import glob, os; [os.remove(f) for f in glob.glob('**/*.pyc', recursive=True)]"

# 3. Reiniciar servidor
python manage.py runserver
```

---

## 📁 Arquivos de Referência

| Arquivo | Descrição |
|---------|-----------|
| `docs/chatbot-optimization-analysis.md` | Análise completa das otimizações do chatbot |
| `docs/USERPROFILE_DUPLICATE_FIX.md` | Documentação da correção de UserProfile |
| `docs/FIX_MERGE_CONFLICT.md` | Solução para conflitos de merge |
| `verify_userprofiles.py` | Script de verificação de integridade |
| `fix_userprofile_duplicate.py` | Script de correção de duplicatas |

---

## ✅ Próximos Passos

Após completar todos os testes:

1. ✅ **Todos os testes passaram?**
   - Criar commit final com resultados
   - Fazer merge para branch principal (se aplicável)
   - Deploy em produção

2. ❌ **Algum teste falhou?**
   - Documentar o problema encontrado
   - Informar quais testes falharam
   - Providenciar logs de erro

---

## 📞 Suporte

Se encontrar problemas:

1. Verifique os logs: `tail -f logs/django.log`
2. Execute diagnóstico: `python fix_userprofile_duplicate.py`
3. Verifique configuração: `cat .env`
4. Teste conexão DB: `python manage.py dbshell`

---

**✨ Boa sorte com os testes!**
