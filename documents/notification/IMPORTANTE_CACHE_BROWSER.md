# IMPORTANTE: Cache do Navegador

**Data**: 04/11/2025
**Problema**: Erros 404 persistindo após correções no JavaScript

## Problema Identificado

Após corrigir os endpoints no arquivo `static/js/reading-progress.js`, os erros 404 continuavam aparecendo no log:

```
[04/Nov/2025 19:04:34] "POST /api/notifications/mark-read-unified/ HTTP/1.1" 404
[04/Nov/2025 19:04:54] "POST /api/notifications/delete-unified/ HTTP/1.1" 404
```

## Causa

O **navegador estava usando a versão antiga do JavaScript armazenada em cache**. Mesmo após reiniciar o servidor Django, o navegador continuava usando o arquivo antigo.

## Solução

### 1. Cache Busting - Atualização da Versão

**Arquivo**: `templates/base.html` (linha 322)

**Antes:**
```html
<script src="{% static 'js/reading-progress.js' %}?v=2.2"></script>
```

**Depois:**
```html
<script src="{% static 'js/reading-progress.js' %}?v=3.0"></script>
```

O parâmetro `?v=3.0` força o navegador a reconhecer como um arquivo diferente e baixar a nova versão.

### 2. Como Funciona

Quando o navegador vê:
- `reading-progress.js?v=2.2` → Usa o cache (versão antiga) ❌
- `reading-progress.js?v=3.0` → Baixa nova versão (versão corrigida) ✅

## Como Confirmar que Funcionou

### No Navegador

1. Abra as **DevTools** (F12)
2. Vá para a aba **Network/Rede**
3. Marque "Disable cache" (desabilitar cache)
4. Recarregue a página (Ctrl+F5 ou Cmd+Shift+R)
5. Procure por `reading-progress.js?v=3.0`
6. Deve mostrar `Status: 200` e `Size: [tamanho real]` (não "from cache")

### No Console do Navegador

Execute no console:
```javascript
// Verificar se as URLs estão corretas
console.log('Testando endpoints...');

// Deve mostrar URLs com /unified/
fetch('/api/notifications/unified/mark-read/', {
  method: 'POST',
  headers: { 'X-CSRFToken': 'test' }
}).then(r => console.log('Mark read:', r.status));

fetch('/api/notifications/unified/delete-selected/', {
  method: 'POST',
  headers: { 'X-CSRFToken': 'test' }
}).then(r => console.log('Delete:', r.status));
```

### No Log do Servidor

Após recarregar com a nova versão, você deve ver:

✅ **CORRETO:**
```
"POST /api/notifications/unified/mark-read/ HTTP/1.1" 200
"POST /api/notifications/unified/delete-selected/ HTTP/1.1" 200
```

❌ **INCORRETO (cache antigo):**
```
"POST /api/notifications/mark-read-unified/ HTTP/1.1" 404
"POST /api/notifications/delete-unified/ HTTP/1.1" 404
```

## Limpeza Manual do Cache (Alternativa)

Se ainda persistir, limpe o cache manualmente:

### Chrome/Edge
1. Pressione `Ctrl+Shift+Delete`
2. Selecione "Imagens e arquivos em cache"
3. Clique em "Limpar dados"

### Firefox
1. Pressione `Ctrl+Shift+Delete`
2. Selecione "Cache"
3. Clique em "Limpar agora"

### Safari
1. Menu Safari → Preferências → Avançado
2. Marque "Mostrar menu Desenvolver"
3. Menu Desenvolver → Esvaziar Caches

### Modo Hard Refresh (Todos os navegadores)
- **Windows**: `Ctrl+F5` ou `Ctrl+Shift+R`
- **Mac**: `Cmd+Shift+R`

## Boas Práticas para Desenvolvimento

### Durante Desenvolvimento

**Sempre desabilite o cache nas DevTools:**

1. Abra DevTools (F12)
2. Vá para Settings (⚙️ ou F1)
3. Em "Network", marque:
   - ☑ Disable cache (while DevTools is open)

Isso evita problemas de cache durante o desenvolvimento.

### Para Produção

**Sempre incremente a versão quando modificar arquivos estáticos:**

```html
<!-- Após modificar reading-progress.js -->
<script src="{% static 'js/reading-progress.js' %}?v=3.1"></script>

<!-- Após modificar library-manager.js -->
<script src="{% static 'js/library-manager.js' %}?v=2.1"></script>
```

## Versionamento Automático (Opcional)

Para evitar esquecer de atualizar versões, você pode usar:

### Django-Compressor ou WhiteNoise

Adicionar hash automático aos arquivos:
```html
<script src="{% static 'js/reading-progress.abc123.js' %}"></script>
```

### Template Tag Customizado

Criar um template tag que adiciona timestamp:
```python
# templatetags/cache_bust.py
import os
from django import template
from django.templatetags.static import static

register = template.Library()

@register.simple_tag
def static_versioned(path):
    file_path = os.path.join(settings.STATIC_ROOT, path)
    if os.path.exists(file_path):
        timestamp = os.path.getmtime(file_path)
        return f"{static(path)}?v={timestamp}"
    return static(path)
```

Uso:
```html
<script src="{% static_versioned 'js/reading-progress.js' %}"></script>
```

## Resumo

- ✅ Versão do JS atualizada para `v=3.0`
- ✅ Navegador baixará nova versão automaticamente
- ✅ Endpoints corrigidos estarão ativos
- ✅ Erros 404 devem desaparecer

## Teste Final

Após recarregar a página com `Ctrl+F5`:

1. Abrir sininho de notificações
2. Clicar em "Marcar como lida" → **200 OK** ✅
3. Selecionar e deletar notificação → **200 OK** ✅
4. Clicar em "Marcar todas como lidas" → **200 OK** ✅

Se ainda houver 404, verifique se o arquivo `reading-progress.js` realmente tem as alterações:

```bash
# Verificar conteúdo do arquivo
grep -n "unified/mark-read" static/js/reading-progress.js
# Deve retornar a linha com o endpoint correto
```

---

**Lição Aprendida**: Sempre incremente versões de arquivos JavaScript quando fizer alterações, especialmente em produção!
