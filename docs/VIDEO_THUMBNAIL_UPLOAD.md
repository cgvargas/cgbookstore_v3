# 🎬 Sistema de Upload de Thumbnails para Vídeos

## 📋 Visão Geral

O sistema de vídeos agora suporta **upload de thumbnails customizadas** para vídeos de plataformas como Instagram, Vimeo, TikTok e outras que não geram thumbnails automaticamente.

## 🎯 Funcionalidades

### YouTube
- ✅ **Thumbnail Automática**: Gerada automaticamente ao salvar o vídeo
- 📸 **URL Auto**: `https://img.youtube.com/vi/{VIDEO_ID}/maxresdefault.jpg`
- 🔄 **Sem Upload**: Não é necessário fazer upload manual

### Instagram, Vimeo, TikTok
- 📤 **Upload Manual**: Faça upload de uma imagem customizada
- 🎨 **Formatos**: JPG, JPEG, PNG, WEBP
- 📏 **Proporção Recomendada**: 16:9 (1280x720px ou similar)

## 🛠️ Como Usar no Admin

### 1. Acessar Admin de Vídeos
```
URL: /admin/core/video/
```

### 2. Adicionar/Editar Vídeo

#### Para YouTube:
1. Preencha o campo **"URL do Vídeo"** com a URL do YouTube
2. A thumbnail será gerada **automaticamente**
3. Você verá o preview da thumbnail na seção "Thumbnail"

#### Para Instagram/Vimeo/TikTok:
1. Selecione a **Plataforma** (Instagram, Vimeo, TikTok)
2. Preencha o campo **"URL do Vídeo"**
3. Na seção **"Thumbnail"**, clique em **"Escolher arquivo"**
4. Faça upload da imagem da thumbnail
5. O preview aparecerá automaticamente

### 3. Preview no Admin

#### Na Listagem:
- Coluna **"Thumb"**: Miniatura 80x45px da thumbnail
- Mostra tanto thumbnails do YouTube quanto uploads customizados

#### No Formulário:
- Seção **"Thumbnail"** com preview grande (até 400x300px)
- Indica se é **"Upload Customizado"** ou **"YouTube (Auto)"**

## 🔧 Campos do Modelo

### `thumbnail_image`
- **Tipo**: ImageField
- **Upload Path**: `videos/thumbnails/`
- **Obrigatório**: Não (blank=True, null=True)
- **Uso**: Upload manual de thumbnail

### `thumbnail_url`
- **Tipo**: URLField
- **Obrigatório**: Não (blank=True)
- **Uso**: URL da thumbnail do YouTube (gerada automaticamente)

## 📊 Prioridade de Exibição

O método `get_thumbnail()` retorna a thumbnail seguindo esta ordem:

1. **Prioridade 1**: `thumbnail_image` (upload customizado)
2. **Prioridade 2**: `thumbnail_url` (YouTube automático)
3. **Fallback**: `None` (nenhuma thumbnail)

```python
# Exemplo de uso no código
video = Video.objects.get(pk=1)
thumbnail_url = video.get_thumbnail()  # Retorna a melhor thumbnail disponível
```

## 🎨 Especificações Técnicas

### Tamanhos Recomendados

| Plataforma | Proporção | Dimensões Recomendadas |
|------------|-----------|------------------------|
| YouTube | 16:9 | 1280x720px (Auto) |
| Instagram | 16:9 ou 1:1 | 1080x1080px ou 1920x1080px |
| Vimeo | 16:9 | 1280x720px |
| TikTok | 9:16 | 1080x1920px |

### Formatos Aceitos
- ✅ JPG / JPEG
- ✅ PNG
- ✅ WEBP

### Tamanho Máximo
- Recomendado: **2 MB**
- Máximo permitido: Configurado em `settings.py`

## 📝 Exemplos de Uso

### Exemplo 1: Vídeo do YouTube
```python
video = Video.objects.create(
    title="Book Trailer - Meu Livro",
    platform="youtube",
    video_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    video_type="trailer"
)
# Thumbnail será gerada automaticamente ao salvar
```

### Exemplo 2: Vídeo do Instagram com Upload
```python
from django.core.files import File

video = Video.objects.create(
    title="Resenha no Instagram",
    platform="instagram",
    video_url="https://www.instagram.com/reel/...",
    video_type="review"
)

# Upload de thumbnail customizada
with open('path/to/thumbnail.jpg', 'rb') as f:
    video.thumbnail_image.save('instagram_thumb.jpg', File(f))
```

### Exemplo 3: Obter Thumbnail
```python
# Em um template
<img src="{{ video.get_thumbnail }}" alt="{{ video.title }}">

# Em uma view
thumbnail_url = video.get_thumbnail()
if thumbnail_url:
    context['video_thumbnail'] = thumbnail_url
```

## 🎬 Seção Thumbnail no Admin

A seção "Thumbnail" no admin possui:

### Campos:
1. **Thumbnail Customizada** (upload de arquivo)
2. **URL da Thumbnail** (gerada automaticamente para YouTube)
3. **Preview da Thumbnail** (readonly - mostra a imagem)

### Descrição:
```
Para YouTube: a thumbnail é gerada automaticamente.
Para Instagram, Vimeo, TikTok: faça upload de uma imagem customizada.
```

## 🔍 Listagem no Admin

A listagem de vídeos agora inclui:
- ✅ Coluna "Thumb" com miniatura visual
- ✅ Preview automático de YouTube e uploads
- ✅ Indicador visual quando não há thumbnail

## 💡 Boas Práticas

### Para YouTube:
- ✅ Deixe o sistema gerar a thumbnail automaticamente
- ✅ Não é necessário fazer upload
- ⚠️ Se fizer upload, ele terá prioridade sobre a thumbnail do YouTube

### Para Outras Plataformas:
- ✅ Sempre faça upload de uma thumbnail customizada
- ✅ Use imagens de alta qualidade
- ✅ Mantenha proporção 16:9 quando possível
- ✅ Otimize as imagens antes do upload (max 2 MB)

### Nomes de Arquivo:
- ✅ Use nomes descritivos: `book-trailer-meu-livro.jpg`
- ✅ Evite caracteres especiais
- ✅ Use apenas letras, números e hífens

## 🚨 Troubleshooting

### Thumbnail não aparece:
1. Verifique se o arquivo foi carregado corretamente
2. Confirme que o formato é suportado (JPG, PNG, WEBP)
3. Verifique permissões da pasta `media/videos/thumbnails/`

### Thumbnail do YouTube não gera:
1. Verifique se a URL está correta
2. Confirme que o vídeo é público
3. Alguns vídeos antigos podem não ter `maxresdefault.jpg`

### Preview não carrega:
1. Verifique as configurações de MEDIA_URL e MEDIA_ROOT
2. Confirme que o servidor está servindo arquivos de media corretamente
3. Verifique logs de erro no Django

## 📁 Estrutura de Arquivos

```
media/
└── videos/
    └── thumbnails/
        ├── instagram_resenha_123.jpg
        ├── vimeo_entrevista_456.png
        └── tiktok_trailer_789.webp
```

## 🔄 Migração de Dados Antigos

Se você já tem vídeos sem thumbnail:
1. Os vídeos do YouTube continuarão funcionando (thumbnail automática)
2. Vídeos de outras plataformas: faça upload manual das thumbnails
3. Use o admin para adicionar thumbnails em massa

## 📅 Data de Implementação

**Data**: 05/12/2024
**Migration**: `0020_add_video_thumbnail_image.py`
**Status**: ✅ Implementado e Testado

---

**Desenvolvido por**: Equipe CG.BookStore
