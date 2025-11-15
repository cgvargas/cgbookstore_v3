# Implementação de Thumbnails Automáticas para Instagram e outras plataformas

## 📋 Resumo da Implementação

Implementei extração automática de thumbnails para vídeos do **Instagram**, **Vimeo** e **TikTok**, além de melhorar a implementação existente do YouTube.

## ✨ O que foi implementado

### 1. **Utilitário de Extração de Thumbnails** (`core/utils/video_utils.py`)

Criado novo módulo com funções especializadas para cada plataforma:

#### Instagram (`extract_instagram_thumbnail`)
Usa **múltiplas estratégias** para extrair thumbnails:

1. **API oEmbed do Instagram** (funciona até outubro/2025)
   ```
   https://api.instagram.com/oembed/?url={instagram_url}
   ```

2. **Extração de metadados HTML** (Open Graph tags)
   - Extrai `og:image` do HTML da página
   - Extrai `og:video:thumbnail` como alternativa
   - Mais confiável quando a API falha

#### YouTube (`extract_youtube_thumbnail`)
- Suporta múltiplos formatos de URL:
  - `youtube.com/watch?v=VIDEO_ID`
  - `youtu.be/VIDEO_ID`
  - `youtube.com/shorts/VIDEO_ID`
  - `youtube.com/embed/VIDEO_ID`
- Usa `maxresdefault.jpg` para melhor qualidade

#### Vimeo (`extract_vimeo_thumbnail`)
- Usa API oEmbed do Vimeo
- Extrai thumbnail de alta qualidade

#### TikTok (`extract_tiktok_thumbnail`)
- Extrai metadados HTML (Open Graph)
- Suporta vídeos e links curtos

#### Função Unificada (`extract_video_thumbnail`)
```python
embed_code, thumbnail_url = extract_video_thumbnail(platform, video_url)
```

### 2. **Atualização do Model Video** (`core/models/video.py`)

**Método `save()` aprimorado:**
```python
def save(self, *args, **kwargs):
    # Extrai automaticamente embed_code e thumbnail_url
    # para TODAS as plataformas suportadas

    if self.video_url and self.platform:
        embed_code, thumbnail_url = extract_video_thumbnail(
            self.platform,
            self.video_url
        )

        # Atualiza apenas se campos estiverem vazios
        # (permite edição manual)
```

**Mudanças:**
- ✅ Extração automática para YouTube, Instagram, Vimeo e TikTok
- ✅ Mantém valores editados manualmente
- ✅ Logging de erros e sucessos
- ✅ Help text atualizado

### 3. **Melhorias no Django Admin** (`core/admin/video_admin.py`)

**Novos recursos:**

#### Preview de Thumbnail na Lista
- Miniatura 80x45px ao lado de cada vídeo
- Indicador visual "Sem thumbnail" quando não disponível

#### Preview Grande no Formulário
- Preview 400x225px no formulário de edição
- Aparece logo após o campo `thumbnail_url`
- Atualiza automaticamente ao salvar

#### Descrição Melhorada
Adicionada descrição no fieldset "Vídeo":
> "A thumbnail é extraída automaticamente ao salvar. Para Instagram, tenta múltiplas estratégias. Você pode editar manualmente se necessário."

## 🎯 Como Usar

### No Django Admin

1. **Acesse:** `/admin/core/video/add/`

2. **Preencha os campos:**
   - **Título:** Nome do vídeo
   - **Plataforma:** Selecione "Instagram" (ou YouTube, Vimeo, TikTok)
   - **URL do Vídeo:** Cole a URL completa do Instagram
     ```
     Exemplo: https://www.instagram.com/p/ABC123xyz/
     ou: https://www.instagram.com/reel/XYZ789abc/
     ```

3. **Salve o vídeo**
   - O sistema tentará extrair automaticamente:
     - ✅ `thumbnail_url` (se possível)
     - ✅ `embed_code` (para YouTube/Vimeo)

4. **Verifique o preview**
   - Logo após salvar, verá o preview da thumbnail
   - Se não extrair automaticamente, pode adicionar manualmente

### Adição Manual de Thumbnail

Se a extração automática falhar:

1. Encontre a thumbnail do Instagram:
   - Clique com botão direito no vídeo → "Inspecionar elemento"
   - Procure por tags `<meta property="og:image" content="..."/>`
   - Copie a URL da imagem

2. Cole no campo **"URL da Thumbnail"**

3. Salve e veja o preview

## 📊 Compatibilidade

### Plataformas Suportadas

| Plataforma | Extração Automática | Embed Code | Observações |
|------------|---------------------|------------|-------------|
| **YouTube** | ✅ Sim | ✅ Sim | Funciona 100% |
| **Instagram** | ⚠️ Parcial | ❌ Não | API sendo descontinuada em out/2025 |
| **Vimeo** | ✅ Sim | ✅ Sim | Via API oEmbed |
| **TikTok** | ⚠️ Parcial | ❌ Não | Via scraping HTML |

### Limitações do Instagram

**⚠️ IMPORTANTE:**
A API oEmbed do Instagram está sendo descontinuada:
- **Até outubro/2025:** Funciona parcialmente
- **Após outubro/2025:** Apenas scraping HTML funcionará

**Problemas conhecidos:**
- Alguns vídeos podem retornar erro 404
- Vídeos privados não funcionam
- Rate limiting pode ocorrer

**Solução:**
- O sistema tenta múltiplas estratégias automaticamente
- Se falhar, adicione manualmente

## 🧪 Testes

### Script de Teste Criado

Execute para testar todas as plataformas:
```bash
python test_video_thumbnails.py
```

### Testar no Django Shell

```python
from core.utils.video_utils import extract_video_thumbnail

# Testar Instagram
url = "https://www.instagram.com/p/ABC123/"
embed, thumb = extract_video_thumbnail('instagram', url)
print(f"Thumbnail: {thumb}")

# Testar YouTube
url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
embed, thumb = extract_video_thumbnail('youtube', url)
print(f"Embed: {embed}, Thumbnail: {thumb}")
```

### Testar Criando Vídeo

```python
from core.models import Video

video = Video.objects.create(
    title="Teste Instagram",
    platform="instagram",
    video_url="https://www.instagram.com/p/ABC123/",
)

print(f"Thumbnail: {video.thumbnail_url}")
```

## 📁 Arquivos Modificados/Criados

### Novos Arquivos
- ✅ `core/utils/video_utils.py` - Utilitários de extração
- ✅ `test_video_thumbnails.py` - Script de testes
- ✅ `IMPLEMENTACAO_THUMBNAILS_INSTAGRAM.md` - Esta documentação

### Arquivos Modificados
- ✅ `core/models/video.py` - Model atualizado
- ✅ `core/admin/video_admin.py` - Admin melhorado

## 🚀 Próximos Passos (Opcional)

### Melhorias Futuras

1. **Upload de Imagem como Alternativa**
   - Adicionar campo `ImageField` para upload manual
   - Útil quando extração automática falha

2. **Cache de Thumbnails**
   - Fazer download e armazenar localmente
   - Evita dependência de URLs externas

3. **Validação de Thumbnail**
   - Verificar se URL está acessível ao salvar
   - Notificar admin se thumbnail quebrou

4. **API do Instagram Graph**
   - Usar Instagram Graph API (requer token)
   - Mais confiável mas requer autenticação

5. **Atualização em Lote**
   - Action no admin para re-extrair thumbnails
   - Útil para vídeos antigos

## ⚠️ Troubleshooting

### Thumbnail não é extraída

**Possíveis causas:**
1. URL inválida ou vídeo privado
2. API do Instagram indisponível
3. Rate limiting
4. Vídeo foi removido

**Solução:**
- Adicione manualmente no campo "URL da Thumbnail"
- Verifique os logs do Django para erros específicos

### Preview não aparece

**Verifique:**
1. Campo `thumbnail_url` está preenchido?
2. URL da thumbnail está acessível?
3. CORS pode estar bloqueando (raro)

**Solução:**
- Recarregue a página do admin
- Verifique se a URL abre no navegador

### Erro ao salvar vídeo

**Verifique:**
1. Conexão com internet (para extração)
2. Logs do Django (`logger`)
3. URL do vídeo está correta?

## 📝 Logging

O sistema loga todas as operações:

```python
import logging
logger = logging.getLogger(__name__)

# Ver logs:
# - Extração bem-sucedida: INFO
# - Falha na extração: WARNING/ERROR
```

**Ver logs no console do Django:**
```bash
# Durante development
python manage.py runserver
# Logs aparecem no console
```

## 🎉 Conclusão

Agora o sistema suporta **extração automática de thumbnails** para:
- ✅ YouTube
- ✅ Instagram (com fallbacks)
- ✅ Vimeo
- ✅ TikTok

**Principais vantagens:**
- 🚀 Automação completa para YouTube e Vimeo
- ⚡ Múltiplas estratégias para Instagram
- 👁️ Preview visual no admin
- ✏️ Permite edição manual quando necessário
- 📊 Logging completo para debugging

**Para usar:**
1. Adicione vídeo no admin
2. Cole a URL do Instagram/YouTube/etc
3. Salve
4. ✨ Thumbnail extraída automaticamente!

---

**Desenvolvido em:** 2025-11-15
**Compatível com:** Django 5.1.1+
**Dependências:** requests (já instalado)
