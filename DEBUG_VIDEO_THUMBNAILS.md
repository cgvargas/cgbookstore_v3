# Debug - Extração de Thumbnails do Instagram

## 🔍 Como Debugar

### 1. Verificar se Deploy Funcionou

**No Render Dashboard → Logs**, procure por:
```
✓ Installing dependencies
✓ Collecting requests==2.32.3
✓ Build succeeded
✓ Deploy live
```

### 2. Testar com YouTube (Caso Base)

1. Acesse: https://cgbookstore-v3.onrender.com/admin/core/video/add/
2. Adicione:
   - **Título:** Teste YouTube
   - **Plataforma:** YouTube
   - **URL:** https://www.youtube.com/watch?v=dQw4w9WgXcQ
3. Clique em **Salvar**
4. **Verifique:**
   - Thumbnail apareceu automaticamente?
   - Preview está visível?

**Se YouTube funcionar:** ✅ Código básico está OK
**Se YouTube NÃO funcionar:** ❌ Problema no deploy ou importação

### 3. Ver Logs do Django

**No Render → Logs (aba superior):**

Procure por mensagens como:
```
✅ INFO Thumbnail extraída para youtube: https://img.youtube.com/vi/...
✅ INFO Embed code extraído para youtube: dQw4w9WgXcQ

⚠️  WARNING Erro ao tentar oEmbed do Instagram: ...
❌ ERROR Erro ao extrair informações do vídeo (instagram): ...
```

### 4. Testar Instagram

Use URLs reais e públicas:

**Exemplo de URLs válidas:**
```
https://www.instagram.com/p/C0aBC1234/
https://www.instagram.com/reel/ABC123xyz/
```

⚠️ **Importante:**
- Substitua pelos códigos reais de posts públicos
- Vídeos privados NÃO funcionarão
- Stories NÃO são suportados

### 5. Problemas Comuns

#### A. Thumbnail não aparece

**Causas possíveis:**
1. Instagram bloqueou a requisição
2. URL inválida ou vídeo privado
3. Timeout (Instagram demorou para responder)
4. Rate limiting

**Solução:**
- Tente outra URL
- Adicione manualmente (campo "URL da Thumbnail")
- Veja logs para erro específico

#### B. Erro "ModuleNotFoundError"

```
ModuleNotFoundError: No module named 'core.utils.video_utils'
```

**Causa:** Arquivo não foi deployado
**Solução:** Limpar cache e redeploy

#### C. Erro "requests.exceptions.Timeout"

```
ERROR Erro ao extrair thumbnail: HTTPConnectionPool timeout
```

**Causa:** Instagram demorou para responder
**Solução:** Normal, use outra URL ou adicione manualmente

#### D. Erro "ConnectionError"

```
ERROR Erro ao extrair thumbnail: Connection refused
```

**Causa:** Instagram bloqueou IP do Render
**Solução:** Adicione thumbnail manualmente

### 6. Adicionar Thumbnail Manualmente

Se extração automática falhar:

1. Abra a URL do Instagram no navegador
2. Clique com botão direito → **Inspecionar**
3. Procure por: `<meta property="og:image" content="..."/>`
4. Copie a URL da imagem
5. Cole no campo **"URL da Thumbnail"** no admin
6. Salve

### 7. Comandos de Debug (Para Desenvolvedores)

**No servidor (via SSH ou Django shell no Render):**

```python
from core.utils.video_utils import extract_instagram_thumbnail

# Testar URL específica
url = "https://www.instagram.com/p/ABC123/"
result = extract_instagram_thumbnail(url)
print(f"Resultado: {result}")
```

---

## 📊 Matriz de Testes

| Plataforma | Status Esperado | Como Testar |
|------------|----------------|-------------|
| **YouTube** | ✅ Deve funcionar | URL: youtube.com/watch?v=... |
| **Instagram** | ⚠️ Pode falhar | URL pública, não privada |
| **Vimeo** | ✅ Deve funcionar | URL: vimeo.com/123456 |
| **TikTok** | ⚠️ Pode falhar | URL: tiktok.com/@user/video/... |

---

## 🆘 Se Nada Funcionar

1. **Verifique logs do Render** - pode haver erro de importação
2. **Teste localmente** - rode o código no seu ambiente
3. **Me avise** - posso criar versão alternativa sem requests externos
4. **Solução temporária** - adicione thumbnails manualmente

---

## ✅ Sucesso Esperado

**YouTube:**
```
✓ Thumbnail extraída automaticamente
✓ Preview aparece no admin
✓ URL: https://img.youtube.com/vi/{video_id}/maxresdefault.jpg
```

**Instagram (quando funcionar):**
```
✓ Thumbnail extraída via oEmbed ou HTML
✓ Preview aparece no admin
✓ URL: https://scontent.cdninstagram.com/...
```

---

**Data:** 2025-11-15
**Versão:** 1.0
