# ✅ Checklist de Teste Final - Sistema de Notificações de Campanhas

**Data**: 04/11/2025
**Versão do Sistema**: 3.0
**Usuário de Teste**: claud

## 🔄 Antes de Começar

### 1. Limpar Cache do Navegador

- [ ] Abrir DevTools (F12)
- [ ] Ir para Network/Rede
- [ ] Marcar "Disable cache"
- [ ] Fazer Hard Refresh: **Ctrl+F5** (Windows) ou **Cmd+Shift+R** (Mac)

### 2. Verificar Versão do JavaScript

- [ ] Na aba Network, procurar `reading-progress.js?v=3.0`
- [ ] Confirmar que foi baixado (não "from cache")
- [ ] Status deve ser 200

### 3. Verificar Servidor Django

- [ ] Servidor rodando: `python manage.py runserver`
- [ ] Sem erros no console
- [ ] `System check identified no issues (0 silenced).` ✓

---

## 📱 Testes no Frontend

### Teste 1: Visualização de Notificações

#### Ações:
1. [ ] Fazer login com usuário `claud`
2. [ ] Verificar badge do sininho (deve mostrar `1`)
3. [ ] Clicar no sininho para abrir painel

#### Resultado Esperado:
- [ ] Painel abre sem erros
- [ ] Mostra 2 notificações (1 reading + 1 campaign)
- [ ] Notificação de campanha tem:
  - [ ] Ícone de presente 🎁 (fas fa-gift)
  - [ ] Texto: "🎉 Parabéns! Você recebeu 30 dias de Premium..."
  - [ ] Botão "Ver Meu Premium"
  - [ ] Marcador de "não lida" (bolinha/destaque)

#### Log do Servidor:
```
"GET /api/notifications/unified/?page=1&unread_only=false&category=all HTTP/1.1" 200
```
✅ Status 200 (não 404)

---

### Teste 2: Marcar Notificação como Lida

#### Ações:
1. [ ] Com o painel aberto, identificar a notificação de campanha
2. [ ] Clicar no botão "Marcar como lida" ou no ícone de check

#### Resultado Esperado:
- [ ] Notificação muda visualmente (perde destaque)
- [ ] Botão "Marcar como lida" desaparece
- [ ] Badge do sininho atualiza (de 1 para 0)
- [ ] Toast de sucesso aparece

#### Log do Servidor:
```
"POST /api/notifications/unified/mark-read/ HTTP/1.1" 200
```
✅ Status 200 (não 404)
✅ URL correta: `/unified/mark-read/` (não `/mark-read-unified/`)

---

### Teste 3: Ação da Notificação (Ver Meu Premium)

#### Ações:
1. [ ] Recarregar página para restaurar notificação não lida
2. [ ] Abrir sininho
3. [ ] Clicar no botão "Ver Meu Premium"

#### Resultado Esperado:
- [ ] Redireciona para `/finance/subscription/status/`
- [ ] Página carrega sem erro 404
- [ ] Mostra status da assinatura Premium

#### Log do Servidor:
```
"GET /finance/subscription/status/ HTTP/1.1" 200
```
✅ Status 200 (não 404)
✅ URL correta: `/finance/subscription/status/` (não `/premium/`)

---

### Teste 4: Deletar Notificação

#### Ações:
1. [ ] Voltar para a home
2. [ ] Abrir sininho
3. [ ] Clicar no botão "Editar" (ícone de lápis)
4. [ ] Modo de edição ativa (checkboxes aparecem)
5. [ ] Selecionar a notificação de campanha
6. [ ] Clicar no botão "Deletar Selecionadas"
7. [ ] Confirmar no popup

#### Resultado Esperado:
- [ ] Popup de confirmação aparece
- [ ] Após confirmar:
  - [ ] Notificação desaparece da lista
  - [ ] Toast de sucesso: "X notificação(ões) deletada(s)"
  - [ ] Badge do sininho atualiza
  - [ ] Modo de edição desativa

#### Log do Servidor:
```
"POST /api/notifications/unified/delete-selected/ HTTP/1.1" 200
```
✅ Status 200 (não 404)
✅ URL correta: `/unified/delete-selected/` (não `/delete-unified/`)

---

### Teste 5: Marcar Todas como Lidas

#### Preparação:
1. [ ] Criar nova notificação para ter algo não lido:
   ```bash
   python scripts/create_campaign_for_user.py claud 7
   ```

#### Ações:
1. [ ] Abrir sininho (deve mostrar notificações não lidas)
2. [ ] Clicar no botão "Marcar Todas como Lidas"

#### Resultado Esperado:
- [ ] Todas as notificações mudam para "lida"
- [ ] Badge do sininho vai para 0
- [ ] Toast: "X notificação(ões) marcada(s) como lida(s)"
- [ ] Inclui notificações de TODAS as categorias (reading, system, campaign)

#### Log do Servidor:
```
"POST /api/notifications/unified/mark-all-read/ HTTP/1.1" 200
```
✅ Status 200 (não 404)
✅ URL correta: `/unified/mark-all-read/` (não `/mark-all-read/`)

---

### Teste 6: Filtro por Categoria

#### Ações:
1. [ ] Abrir sininho
2. [ ] Clicar no filtro de categorias (se disponível)
3. [ ] Selecionar "Campanhas"

#### Resultado Esperado:
- [ ] Mostra apenas notificações de campanhas
- [ ] Contador de categorias correto
- [ ] Paginação funciona

#### Log do Servidor:
```
"GET /api/notifications/unified/?page=1&category=campaign HTTP/1.1" 200
```

---

## 🔍 Verificações no DevTools

### Console do Navegador

Abrir DevTools (F12) → Console

#### Não deve haver erros como:
- ❌ `404 (Not Found)`
- ❌ `Failed to fetch`
- ❌ `Uncaught TypeError`

#### Pode haver avisos normais como:
- ⚠️ `Recommendation algorithm warnings` (normal)
- ⚠️ `CSRF token warnings` (se não estiver logado)

### Network Tab

#### Verificar chamadas corretas:
- [ ] `GET /api/notifications/unified/` → 200
- [ ] `GET /api/notifications/unread-count/` → 200
- [ ] `POST /api/notifications/unified/mark-read/` → 200
- [ ] `POST /api/notifications/unified/delete-selected/` → 200
- [ ] `POST /api/notifications/unified/mark-all-read/` → 200

#### Não deve aparecer:
- ❌ `/api/notifications/mark-read-unified/` → 404
- ❌ `/api/notifications/delete-unified/` → 404
- ❌ `/premium/` → 404

---

## 🗄️ Verificações no Backend

### 1. Banco de Dados

```bash
python manage.py shell
```

```python
from accounts.models import CampaignNotification
from django.contrib.auth.models import User

user = User.objects.get(username='claud')
notifs = CampaignNotification.objects.filter(user=user)

print(f"Total: {notifs.count()}")
for n in notifs:
    print(f"ID {n.id}: {n.notification_type} - {'Lida' if n.is_read else 'Não lida'}")
    print(f"  Action URL: {n.action_url}")
    print(f"  Action Text: {n.action_text}")
```

#### Resultado Esperado:
- [ ] action_url é `/finance/subscription/status/` (não `/premium/`)
- [ ] action_text é "Ver Meu Premium"

### 2. NotificationRegistry

```python
from accounts.models import NotificationRegistry

print(list(NotificationRegistry.get_all_types()))
# Deve incluir: ['reading', 'system', 'campaign']
```

- [ ] 'campaign' está na lista

### 3. API Unificada

```python
from accounts.models import NotificationRegistry
user = User.objects.get(username='claud')
notifs = NotificationRegistry.get_all_notifications(user)

print(f"Total via Registry: {len(notifs)}")
for n in notifs:
    print(f"  - {type(n).__name__}: {n.notification_type}")
```

- [ ] Inclui CampaignNotification

---

## 📊 Logs do Servidor - Checklist

### ✅ Deve Aparecer (Correto):
```
"GET /api/notifications/unified/?page=1&unread_only=false&category=all HTTP/1.1" 200
"GET /api/notifications/unread-count/ HTTP/1.1" 200
"POST /api/notifications/unified/mark-read/ HTTP/1.1" 200
"POST /api/notifications/unified/delete-selected/ HTTP/1.1" 200
"POST /api/notifications/unified/mark-all-read/ HTTP/1.1" 200
"GET /finance/subscription/status/ HTTP/1.1" 200
```

### ❌ Não Deve Aparecer (Erro):
```
Not Found: /api/notifications/mark-read-unified/
Not Found: /api/notifications/delete-unified/
Not Found: /premium/
```

---

## 🎯 Resultado Final

### Critérios de Sucesso:

- [ ] **Todos os testes passaram**
- [ ] **Nenhum erro 404 nos logs**
- [ ] **Badge de notificações funciona**
- [ ] **Notificações de campanha aparecem**
- [ ] **Operações CRUD funcionam**
- [ ] **URLs de ação são válidas**

### Se Algum Teste Falhar:

1. **Verificar cache do navegador**
   - Limpar cache manualmente
   - Fazer hard refresh (Ctrl+F5)
   - Verificar se está usando `reading-progress.js?v=3.0`

2. **Verificar arquivo JavaScript**
   ```bash
   grep -n "unified" static/js/reading-progress.js
   ```
   - Deve mostrar `/unified/mark-read/`
   - Deve mostrar `/unified/delete-selected/`
   - Deve mostrar `/unified/mark-all-read/`

3. **Verificar servidor Django**
   - Reiniciar servidor
   - Verificar logs de startup
   - Confirmar que não há erros de importação

4. **Verificar banco de dados**
   - Confirmar que notificações existem
   - Confirmar que action_url está correto

---

## 📝 Observações

- Emojis nas mensagens (🎉, ⚠️) podem não aparecer corretamente em terminais Windows
- Isso é apenas problema de encoding do terminal, não afeta funcionalidade
- No navegador, os emojis aparecem normalmente

---

## ✅ Status Final

Data do Teste: ___/___/_____

- [ ] **TODOS OS TESTES PASSARAM**
- [ ] **SISTEMA 100% FUNCIONAL**
- [ ] **PRONTO PARA PRODUÇÃO**

Testado por: _________________________

Assinatura: _________________________
