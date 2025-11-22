# 🔧 Troubleshooting: Atualizações não aparecem no navegador

## 🎯 Problema
Você fez alterações no código, mas o navegador **ainda mostra a versão antiga** quando roda o servidor Django local. No entanto, as atualizações **funcionam no Render (produção)**.

## 🔍 Causa Raiz
**Cache do navegador!** O navegador armazena arquivos estáticos (JS, CSS, templates renderizados) para carregar páginas mais rápido. Quando você atualiza o código, o navegador continua usando os arquivos antigos do cache.

### Por que funciona no Render mas não localmente?
- **Render**: Usa URL diferente ou CDN que força novas versões
- **Local**: Mesmo `localhost:8000`, então navegador reutiliza cache antigo

---

## ✅ Soluções (em ordem de efetividade)

### 1️⃣ **Hard Refresh (Recarregamento Forçado)** ⚡ RECOMENDADO

Força o navegador a **ignorar o cache** e baixar tudo novamente:

| Sistema Operacional | Navegador | Teclas |
|---------------------|-----------|---------|
| **Windows/Linux** | Chrome, Edge, Brave | `Ctrl + Shift + R` |
| **Windows/Linux** | Firefox | `Ctrl + F5` |
| **Mac** | Chrome, Edge, Brave, Firefox | `Cmd + Shift + R` |
| **Mac** | Safari | `Cmd + Option + E` (limpa cache), depois `Cmd + R` |

---

### 2️⃣ **Limpar Cache do Navegador Manualmente**

#### Chrome/Edge/Brave:
1. Abra DevTools: `F12` ou `Ctrl + Shift + I`
2. Clique com botão direito no ícone de **Reload** (🔄)
3. Selecione **"Empty Cache and Hard Reload"**

**OU**

1. `Ctrl + Shift + Delete` (Windows) ou `Cmd + Shift + Delete` (Mac)
2. Selecione:
   - ✅ Cached images and files
   - ✅ Cookies and other site data
3. Time range: **Last hour** (ou **All time** se problema persistir)
4. Clique **Clear data**

#### Firefox:
1. `Ctrl + Shift + Delete` (Windows) ou `Cmd + Shift + Delete` (Mac)
2. Selecione:
   - ✅ Cache
   - ✅ Cookies
3. Time range: **Last hour**
4. Clique **Clear Now**

---

### 3️⃣ **Modo Anônimo / Privado** 🕵️

Abre o site em **modo anônimo** (não usa cache):

| Navegador | Teclas (Windows/Linux) | Teclas (Mac) |
|-----------|------------------------|--------------|
| Chrome, Edge | `Ctrl + Shift + N` | `Cmd + Shift + N` |
| Firefox | `Ctrl + Shift + P` | `Cmd + Shift + P` |
| Safari | - | `Cmd + Shift + N` |

---

### 4️⃣ **Desabilitar Cache Durante Desenvolvimento** (DevTools)

**MELHOR opção para desenvolvedores!**

#### Chrome/Edge/Brave:
1. Abra DevTools: `F12`
2. Vá em **Network** (Rede)
3. ✅ Marque **"Disable cache"**
4. **IMPORTANTE**: Deixe DevTools **aberto** enquanto desenvolve

#### Firefox:
1. Abra DevTools: `F12`
2. Clique no ⚙️ (Configurações) no canto superior direito
3. ✅ Marque **"Disable HTTP Cache (when toolbox is open)"**

---

### 5️⃣ **Script Automático: Limpar Todos os Caches** 🧹

Execute o script que criamos:

```bash
bash scripts/clear_all_caches.sh
```

Isso limpa:
- ✅ Cache do Redis
- ✅ Arquivos `.pyc` do Django
- ✅ Pasta `staticfiles/`

**Depois**:
1. Reinicie o servidor: `python manage.py runserver`
2. Faça **Hard Refresh** no navegador

---

### 6️⃣ **Reiniciar o Servidor Django** 🔄

Se você alterou **código Python** (`.py`), reinicie o servidor:

```bash
# Parar servidor: Ctrl + C no terminal
# Iniciar novamente:
python manage.py runserver
```

**Nota**: Django **detecta automaticamente** mudanças em arquivos `.py` e recarrega. Mas às vezes é necessário reiniciar manualmente.

---

## 🧪 Como Verificar se o Problema Foi Resolvido

### Verificar versão do template carregado:

1. Abra a página no navegador
2. Clique com botão direito → **View Page Source** (Ver código-fonte)
3. Procure por este comentário no início do HTML:

```html
<!--
    Seção de Recomendações Personalizadas
    Versão: 2.1 (Timeouts corrigidos: 30s IA, 10s outros)
    Última atualização: 2025-01-17
    Hash: 8285116469456800a37717f6d04b1420
-->
```

4. Se o **hash** for `8285116469456800a37717f6d04b1420` → ✅ Versão correta!
5. Se for diferente → ❌ Ainda está em cache, tente Hard Refresh novamente

### Verificar no console do navegador:

1. Abra DevTools: `F12`
2. Vá em **Console**
3. Procure logs das recomendações (se habilitados)

---

## 🚀 Solução Permanente: Cache Busting Automático

Para **prevenir** esse problema no futuro, adicione versão às URLs estáticas:

### Método 1: Timestamp no template
```django
{% load static %}
<script src="{% static 'js/recommendations.js' %}?v={{ timestamp }}"></script>
```

### Método 2: Git commit hash
```django
<script src="{% static 'js/recommendations.js' %}?v={{ GIT_COMMIT_HASH }}"></script>
```

### Método 3: Django-WhiteNoise (produção)
Já configurado em `settings.py` para produção:
```python
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

---

## 📊 Comparação: Local vs Produção

| Aspecto | Local (localhost) | Produção (Render) |
|---------|------------------|-------------------|
| Cache agressivo | ✅ SIM (problema comum) | ❌ NÃO (CDN/versioning) |
| WhiteNoise ativo | ❌ NÃO (DEBUG=True) | ✅ SIM (adiciona hash aos arquivos) |
| Cache do Redis | ⚠️ Opcional | ✅ SIM |
| URL muda a cada deploy | ❌ NÃO (sempre localhost) | ✅ SIM (render.com) |

---

## 🆘 Ainda não funciona?

Se tentou todas as soluções acima e **ainda** não funciona:

### 1. Verificar que servidor está rodando na porta correta:
```bash
python manage.py runserver
# Deve mostrar: "Starting development server at http://127.0.0.1:8000/"
```

### 2. Verificar que está acessando a URL certa:
- ✅ Correto: `http://localhost:8000/` ou `http://127.0.0.1:8000/`
- ❌ Errado: URL antiga salva em favoritos, IP diferente, etc.

### 3. Verificar logs do Django no terminal:
```
[17/Jan/2025 10:30:00] "GET /recommendations/api/recommendations/ HTTP/1.1" 200
```

### 4. Verificar no Network tab do DevTools:
1. Abra DevTools (`F12`)
2. Vá em **Network**
3. Recarregue a página
4. Clique na requisição `recommendations_section.html`
5. Veja a aba **Response** → deve mostrar HTML atualizado

### 5. Testar com CURL (sem cache):
```bash
curl http://localhost:8000/ | grep "Versão: 2.1"
```

Se aparecer "Versão: 2.1" → problema é cache do navegador
Se NÃO aparecer → problema é no servidor Django

---

## 📚 Recursos Adicionais

- [Django Caching Framework](https://docs.djangoproject.com/en/5.0/topics/cache/)
- [Browser Cache vs Server Cache](https://web.dev/http-cache/)
- [Django Debug Toolbar](https://django-debug-toolbar.readthedocs.io/) - mostra cache hits/misses

---

## ✅ Checklist Rápido

Antes de pedir ajuda, verifique:

- [ ] Fiz **Hard Refresh** (`Ctrl + Shift + R`)
- [ ] Limpei cache do navegador manualmente
- [ ] Testei em **modo anônimo**
- [ ] **DevTools aberto** com "Disable cache" marcado
- [ ] Servidor Django **reiniciado**
- [ ] Script `clear_all_caches.sh` executado
- [ ] Verificado **View Source** para confirmar versão
- [ ] Testado em **navegador diferente**
- [ ] Conferido que estou acessando `localhost:8000` (não outra URL)

Se marcou **todos** os itens acima e ainda não funciona, o problema pode ser outro (não cache).
