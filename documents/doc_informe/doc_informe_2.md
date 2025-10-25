🎯 **PERFEITO! VAMOS CORRIGIR O CAMINHO**

---

## 📍 **ESTRUTURA CORRIGIDA DO PROJETO**

```
cgbookstore_v3/
├── core/
│   ├── views/
│   │   └── reading_progress_views.py  ← AQUI estão as views
│   └── urls.py  ← Provavelmente aqui estão as rotas de API
│
└── accounts/
    └── models/
        ├── __init__.py
        ├── base_notification.py          ← CRIAR AQUI
        ├── reading_notification.py       ← SUBSTITUIR AQUI
        └── ...
```

---

## 🔧 **AJUSTES NECESSÁRIOS NAS VIEWS**

O arquivo `unified_notification_views.py` que gerei precisa de um pequeno ajuste nos imports.---

## 📝 **GUIA ATUALIZADO - ESTRUTURA CORRETA**

### **LOCALIZAÇÃO DOS ARQUIVOS:**

```
C:\ProjectDjango\cgbookstore_v3\
│
├── core/
│   ├── views/
│   │   └── reading_progress_views.py  ← ADICIONAR VIEWS AQUI (linha final)
│   │
│   └── urls.py  ← PROVAVELMENTE AQUI (ou pode estar em um urlpatterns principal)
│
└── accounts/
    └── models/
        ├── __init__.py                 ← ATUALIZAR IMPORTS
        ├── base_notification.py        ← CRIAR NOVO
        └── reading_notification.py     ← SUBSTITUIR
```

---

## 🔧 **PASSO-A-PASSO CORRIGIDO**

### **1. CRIAR BASE NOTIFICATION**

**Arquivo:** `accounts/models/base_notification.py`

[Download base_notification.py](computer:///mnt/user-data/outputs/base_notification.py)

---

### **2. SUBSTITUIR READING NOTIFICATION**

**Arquivo:** `accounts/models/reading_notification.py`

[Download reading_notification_refactored.py](computer:///mnt/user-data/outputs/reading_notification_refactored.py)

---

### **3. ATUALIZAR __init__.py**

**Arquivo:** `accounts/models/__init__.py`

```python
from .base_notification import BaseNotification, NotificationRegistry
from .reading_notification import ReadingNotification, SystemNotification

__all__ = [
    'BaseNotification',
    'NotificationRegistry', 
    'ReadingNotification',
    'SystemNotification',
    # ... outros models que você já tem
]
```

---

### **4. ADICIONAR VIEWS (VERSÃO CORRIGIDA)**

**Arquivo:** `core/views/reading_progress_views.py`

[Download unified_notification_views_CORRECTED.py](computer:///mnt/user-data/outputs/unified_notification_views_CORRECTED.py)

**⚠️ IMPORTANTE:** Adicione TODO o conteúdo deste arquivo **NO FINAL** de `reading_progress_views.py`

---

### **5. ADICIONAR ROTAS**

**Arquivo:** Provavelmente `core/urls.py`

Se suas rotas de API estão em `core/urls.py`, adicione:

```python
from core.views.reading_progress_views import (
    # ... suas imports existentes ...
    get_all_notifications_unified,
    mark_notification_read_unified,
    delete_selected_notifications_unified,
)

urlpatterns = [
    # ... suas rotas existentes ...
    
    # ✅ NOVAS ROTAS - Sistema Unificado
    path('api/notifications/unified/', get_all_notifications_unified, name='notifications_unified'),
    path('api/notifications/mark-read-unified/', mark_notification_read_unified, name='mark_read_unified'),
    path('api/notifications/delete-unified/', delete_selected_notifications_unified, name='delete_unified'),
]
```

**OU** se as rotas de API estão em um arquivo de URLs principal (ex: `cgbookstore_v3/urls.py`), adicione lá.

---

### **6. VERIFICAR IMPORTS NO reading_progress_views.py**

No TOPO do arquivo `core/views/reading_progress_views.py`, certifique-se de que tem:

```python
from accounts.models import ReadingProgress, ReadingNotification, BookShelf, SystemNotification
# ou
from accounts.models import *
```

Se não tiver `SystemNotification` importado, adicione.

---

## 🗃️ **MIGRATIONS**

Agora sim, rode as migrations:

```bash
cd C:\ProjectDjango\cgbookstore_v3
python manage.py makemigrations accounts
python manage.py migrate accounts
```

---

## ✅ **CHECKLIST ATUALIZADO**

### Arquivos Backend
- [ ] `accounts/models/base_notification.py` criado
- [ ] `accounts/models/reading_notification.py` substituído
- [ ] `accounts/models/__init__.py` atualizado com imports
- [ ] `core/views/reading_progress_views.py` - views unificadas adicionadas no final
- [ ] Imports de `SystemNotification` adicionados no topo de `reading_progress_views.py`
- [ ] URLs atualizadas (em `core/urls.py` ou arquivo principal)

### Migrations
- [ ] `python manage.py makemigrations accounts` executado
- [ ] Migration criada sem erros
- [ ] `python manage.py migrate accounts` executado
- [ ] Tabelas criadas no banco

### Validação
- [ ] Servidor inicia sem erros: `python manage.py runserver`
- [ ] Django shell - Imports funcionam
- [ ] API `/api/notifications/unread-count/` responde
- [ ] API `/api/notifications/unified/` responde

---

## 🎯 **PRÓXIMO PASSO**

Quando completar o checklist, **me avise com:**

✅ **"Backend implementado com sucesso"**

ou

❌ **"Erro em [qual etapa]: [mensagem do erro]"**

E eu vou gerar todo o frontend v3! 🚀