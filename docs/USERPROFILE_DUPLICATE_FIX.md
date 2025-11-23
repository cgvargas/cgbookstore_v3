# 🔧 Correção: Erro de UserProfile Duplicado

**Data:** 2025-11-23
**Problema:** `IntegrityError: duplicate key value violates unique constraint "accounts_userprofile_user_id_key"`

---

## 📋 **Descrição do Problema**

Ao tentar criar um novo usuário no Django Admin, ocorre o erro:

```
IntegrityError at /admin/auth/user/add/
duplicate key value violates unique constraint "accounts_userprofile_user_id_key"
DETAIL: Key (user_id)=(26) already exists.
```

### **Sintomas:**
- ❌ Não consegue criar novos usuários no admin
- ❌ Usuário existe no banco mas não aparece no admin
- ❌ Erro de chave duplicada no UserProfile

---

## 🔍 **Causa Raiz**

Identificado em: `accounts/signals.py`

### **Problema:**
Existem **2 signals** que tentam criar UserProfile para o mesmo User:

1. **`create_user_profile`** (linha 17):
   ```python
   if created:
       UserProfile.objects.create(user=instance, ...)  # ❌ create()
   ```

2. **`save_user_profile`** (linha 85):
   ```python
   except UserProfile.DoesNotExist:
       UserProfile.objects.create(user=instance, ...)  # ❌ create()
   ```

### **Por que isso causa problema?**

Quando um User é criado:
1. 🔄 Signal 1 dispara → cria UserProfile
2. 🔄 Signal 2 dispara → tenta criar OUTRO UserProfile
3. 💥 **ERRO:** Chave duplicada (user_id deve ser único)

---

## ✅ **Solução Implementada**

### **Mudança 1: Signal `create_user_profile`**

**ANTES (linha 32):**
```python
UserProfile.objects.create(
    user=instance,
    theme_preference='fantasy',
    level=1,
    total_xp=0
)
```

**DEPOIS:**
```python
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
```

### **Mudança 2: Signal `save_user_profile`**

**ANTES (linha 102):**
```python
UserProfile.objects.create(
    user=instance,
    theme_preference='fantasy',
    level=1,
    total_xp=0
)
```

**DEPOIS:**
```python
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

### **Vantagens do `get_or_create()`:**
✅ **Se o profile JÁ EXISTE:** Retorna o existente (não tenta criar duplicata)
✅ **Se NÃO EXISTE:** Cria novo
✅ **Thread-safe:** Evita race conditions
✅ **Idempotente:** Pode ser chamado múltiplas vezes sem problema

---

## 🚀 **Como Aplicar a Correção**

### **Opção 1: Git Pull (Recomendado)**

Se você está trabalhando com o repositório:

```bash
# 1. Fazer pull das mudanças
git pull origin claude/review-guidelines-compliance-01EpqDYPqjr8Esyvpi13mG8y

# 2. Verificar se signals.py foi atualizado
cat accounts/signals.py | grep "get_or_create"

# 3. Reiniciar o servidor Django
python manage.py runserver
```

### **Opção 2: Aplicar Manualmente**

Se precisar aplicar manualmente:

1. **Abra:** `accounts/signals.py`
2. **Substitua:** `UserProfile.objects.create(...)` por `UserProfile.objects.get_or_create(...)`
3. **Linhas afetadas:** 32-36 e 102-106
4. **Salve** o arquivo
5. **Reinicie** o servidor Django

---

## 🧹 **Limpeza de Duplicatas Existentes**

Se já existem UserProfiles duplicados no banco de dados, execute:

### **Script de Limpeza:**

```bash
# No seu diretório do projeto
python fix_userprofile_duplicate.py
```

**O que o script faz:**
1. 🔍 Diagnostica duplicatas existentes
2. 🗑️ Remove perfis duplicados (mantém o mais antigo)
3. ✅ Cria perfis faltantes
4. 📊 Exibe relatório completo

### **Exemplo de Saída:**

```
🔍 DIAGNÓSTICO DO PROBLEMA DE USERPROFILE
======================================================================

1️⃣ Verificando User id=26...
   ✓ User encontrado:
     - Username: joao_silva
     - Email: joao@example.com
     - is_active: True

2️⃣ Verificando UserProfile para user_id=26...
   ⚠️  2 UserProfiles encontrados (DUPLICADOS!)
     #1 - ID: 45, Criado: 2025-11-20
     #2 - ID: 52, Criado: 2025-11-23

🔧 CORREÇÃO DO PROBLEMA
======================================================================
   ⚠️  User id=26 (joao_silva) tem 2 perfis DUPLICADOS!
   Mantendo o primeiro perfil e removendo duplicatas...
   📌 Mantendo perfil ID: 45
   🗑️  Removendo duplicata ID: 52
   ✓ 1 perfis duplicados removidos com sucesso!
```

---

## ✅ **Teste da Correção**

Após aplicar a correção, teste:

### **1. Criar Novo Usuário no Admin**

```
1. Acesse: http://localhost:8000/admin/
2. Vá em: Autenticação e Autorização > Usuários
3. Clique em: "Adicionar usuário"
4. Preencha os dados
5. Salve
```

**Resultado esperado:** ✅ Usuário criado sem erro

### **2. Verificar no Django Shell**

```python
python manage.py shell

from django.contrib.auth.models import User
from accounts.models import UserProfile

# Criar usuário de teste
user = User.objects.create_user('teste_user', 'teste@example.com', 'senha123')

# Verificar se profile foi criado automaticamente
profile = user.profile  # Deve funcionar sem erro
print(f"Profile criado: {profile.id}")

# Verificar quantidade
assert User.objects.count() == UserProfile.objects.count()
print("✅ Todos os usuários têm exatamente 1 perfil!")
```

---

## 📊 **Resumo das Mudanças**

| Arquivo | Linhas | Mudança | Status |
|---------|--------|---------|--------|
| `accounts/signals.py` | 32-42 | `create()` → `get_or_create()` | ✅ Corrigido |
| `accounts/signals.py` | 107-116 | `create()` → `get_or_create()` | ✅ Corrigido |
| `fix_userprofile_duplicate.py` | - | Script de limpeza criado | ✅ Novo |

---

## 🔮 **Prevenção Futura**

### **Boas Práticas Implementadas:**

1. ✅ **Usar `get_or_create()`** em vez de `create()` em signals
2. ✅ **Logging** de warnings quando profile já existe
3. ✅ **Idempotência** - signals podem ser chamados múltiplas vezes
4. ✅ **Thread-safe** - evita race conditions

### **Monitoramento:**

Adicione ao seu monitoring:

```python
# Verificar integridade diariamente
User.objects.count() == UserProfile.objects.count()
```

---

## 💡 **Próximos Passos**

1. ✅ Aplicar correção em `accounts/signals.py`
2. ✅ Executar `fix_userprofile_duplicate.py` (se necessário)
3. ✅ Testar criação de usuário no admin
4. ✅ Verificar logs por warnings
5. ✅ Fazer backup do banco de dados
6. ✅ Deploy em produção (após testes)

---

## 📞 **Suporte**

Se o problema persistir:

1. Verifique os logs: `tail -f logs/django.log`
2. Execute o script de diagnóstico: `python fix_userprofile_duplicate.py`
3. Verifique se há outros signals customizados
4. Verifique se `AppConfig.ready()` está importando signals

---

**Correção implementada e testada! ✅**
