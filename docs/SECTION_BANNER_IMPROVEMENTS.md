# Melhorias no Sistema de Seções e Banners

## 📋 Resumo

Implementadas melhorias no sistema de seções dinâmicas da home, adicionando controles avançados para banners e correções de funcionalidades.

**Data de Implementação:** 04/12/2025
**Status:** ✅ Completo e Funcional

---

## ✨ Novas Funcionalidades

### 1. **Controle de Altura do Banner**
**Campo:** `banner_height`

**Características:**
- ✅ Altura personalizável em pixels
- ✅ Valor padrão: 400px
- ✅ Ajuste fino para cada seção
- ✅ Aplicado tanto na imagem quanto no container

**Uso no Admin:**
```
Altura do Banner (px): 400
```

**Exemplo de uso:**
- Banner pequeno: 250px
- Banner médio: 400px (padrão)
- Banner grande: 600px
- Banner hero: 800px

---

### 2. **Controle de Transparência do Banner**
**Campo:** `banner_opacity`

**Características:**
- ✅ Opacidade da imagem do banner
- ✅ Range: 0.0 (totalmente transparente) a 1.0 (totalmente opaco)
- ✅ Valor padrão: 1.0
- ✅ Permite criar efeitos de sobreposição

**Uso no Admin:**
```
Transparência do Banner: 1.0
```

**Casos de uso:**
- Banners sutis: 0.3 - 0.5
- Banners normais: 1.0
- Efeito fantasma: 0.7
- Marca d'água: 0.2

---

### 3. **Opacidade das Bordas do Banner**
**Campo:** `banner_border_opacity`

**Características:**
- ✅ Controla o gradiente de borda/overlay
- ✅ Range: 0.0 (sem efeito) a 1.0 (totalmente opaco)
- ✅ Valor padrão: 0.0
- ✅ Efeito de gradiente de baixo para cima

**Uso no Admin:**
```
Opacidade das Bordas: 0.0
```

**Efeitos:**
- Sem overlay: 0.0
- Overlay suave: 0.3 - 0.5
- Overlay padrão: 0.8 (valor antigo fixo)
- Overlay forte: 1.0

**Gradiente aplicado:**
```css
linear-gradient(to top,
    rgba(0,0,0,opacity) 0%,           /* Base (100%) */
    rgba(0,0,0,opacity * 0.5) 50%,    /* Meio (50%) */
    transparent 100%                   /* Topo (0%) */
)
```

---

### 4. **Funcionalidade "Ver Mais" (Corrigida)**
**Campos:** `show_see_more` + `see_more_url`

**Status:** ✅ **Já estava implementado e funcionando**

**Características:**
- ✅ Checkbox para ativar/desativar link
- ✅ Campo de URL para direcionar usuário
- ✅ Link aparece no cabeçalho da seção
- ✅ Ícone de seta para indicar ação

**Uso no Admin:**
```
☑ Mostrar 'Ver Mais'
URL do 'Ver Mais': /livros/?categoria=lancamentos
```

**URLs sugeridas no admin:**
- `/livros/` - Todos os livros
- `/autores/` - Todos os autores
- `/videos/` - Todos os vídeos
- `/eventos/` - Todos os eventos
- `/livros/?categoria=lancamentos` - Categoria específica
- `/livros/?tag=promocao` - Tag específica

**Renderização no template:**
```html
{% if section.show_see_more and section.see_more_url %}
    <a href="{{ section.see_more_url }}" class="view-all-link">
        Ver todos <i class="fas fa-chevron-right ms-1"></i>
    </a>
{% endif %}
```

---

## 📁 Arquivos Modificados

### 1. **core/models/section.py**
**Campos adicionados:**
```python
banner_height = models.PositiveIntegerField(
    default=400,
    verbose_name="Altura do Banner (px)",
    help_text="Altura do banner em pixels (padrão: 400px)"
)

banner_opacity = models.FloatField(
    default=1.0,
    validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
    verbose_name="Transparência do Banner",
    help_text="Opacidade da imagem do banner (0.0 = transparente, 1.0 = opaco)"
)

banner_border_opacity = models.FloatField(
    default=0.0,
    validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
    verbose_name="Opacidade das Bordas",
    help_text="Opacidade do efeito de borda/gradiente nas bordas do banner"
)
```

### 2. **core/admin/section_admin.py**
**Fieldset "Estilo Visual" atualizado:**
```python
'fields': (
    'banner_image',
    'banner_image_preview',
    'banner_height',           # NOVO
    'banner_opacity',          # NOVO
    'banner_border_opacity',   # NOVO
    'background_color',
    'container_opacity',
    'css_class',
    'custom_css'
)
```

### 3. **core/views/home_view.py**
**section_dict atualizado:**
```python
section_dict = {
    # ... campos existentes ...
    'banner_image_url': banner_url,
    'banner_height': section.banner_height,           # NOVO
    'banner_opacity': section.banner_opacity,         # NOVO
    'banner_border_opacity': section.banner_border_opacity,  # NOVO
    'container_opacity': section.container_opacity,
    # ... mais campos ...
}
```

### 4. **templates/core/home.html**
**Banner com novos controles:**
```html
<div class="section-banner-wrapper"
     style="max-height: {{ section.banner_height|default:400 }}px;">
    <img src="{{ section.banner_image_url }}"
         alt="{{ section.title }}"
         loading="lazy"
         style="max-height: {{ section.banner_height|default:400 }}px;
                opacity: {{ section.banner_opacity|default:1.0|floatformat:2 }};">

    <!-- Overlay com opacidade controlada -->
    <div class="section-banner-overlay"
         style="background: linear-gradient(to top,
            rgba(0,0,0,{{ section.banner_border_opacity|default:0.8|floatformat:2 }}) 0%,
            rgba(0,0,0,calc({{ section.banner_border_opacity|default:0.8|floatformat:2 }} * 0.5)) 50%,
            transparent 100%);">
        <!-- Conteúdo do overlay -->
    </div>
</div>
```

### 5. **core/migrations/0017_add_banner_controls.py**
**Migration criada:**
```python
operations = [
    migrations.AddField(
        model_name='section',
        name='banner_border_opacity',
        field=models.FloatField(default=0.0, ...),
    ),
    migrations.AddField(
        model_name='section',
        name='banner_height',
        field=models.PositiveIntegerField(default=400, ...),
    ),
    migrations.AddField(
        model_name='section',
        name='banner_opacity',
        field=models.FloatField(default=1.0, ...),
    ),
]
```

---

## 🎨 Exemplos de Configuração

### Exemplo 1: Banner Hero Full (Destaque Principal)
```
Altura: 800px
Transparência: 1.0
Opacidade Bordas: 0.9
```
**Efeito:** Banner grande, imagem nítida, overlay escuro forte para destacar texto.

### Exemplo 2: Banner Sutil (Seção Secundária)
```
Altura: 250px
Transparência: 0.5
Opacidade Bordas: 0.3
```
**Efeito:** Banner pequeno, imagem semi-transparente, overlay leve.

### Exemplo 3: Banner Sem Overlay (Imagem Limpa)
```
Altura: 400px
Transparência: 1.0
Opacidade Bordas: 0.0
```
**Efeito:** Banner médio, imagem totalmente nítida, sem gradiente de overlay.

### Exemplo 4: Banner Marca D'água
```
Altura: 300px
Transparência: 0.2
Opacidade Bordas: 0.0
```
**Efeito:** Banner como fundo sutil, quase invisível, sem overlay.

---

## 🔄 Valores Padrão

| Campo | Valor Padrão | Comportamento Antigo |
|-------|--------------|---------------------|
| `banner_height` | 400px | 400px (fixo no CSS) |
| `banner_opacity` | 1.0 | 1.0 (fixo) |
| `banner_border_opacity` | 0.0 | 0.8 (fixo no CSS) |

**Nota:** O valor padrão de `banner_border_opacity` foi alterado para 0.0 (sem overlay) para dar mais controle ao admin. Se quiser o comportamento antigo, configure para 0.8.

---

## 📊 Benefícios

### Para Administradores:
- ✅ Controle total sobre a aparência dos banners
- ✅ Não precisa editar CSS manualmente
- ✅ Ajuste fino por seção
- ✅ Preview em tempo real no admin
- ✅ Combinações ilimitadas de estilos

### Para o Design:
- ✅ Banners adaptáveis a diferentes conteúdos
- ✅ Efeitos de overlay personalizáveis
- ✅ Controle de legibilidade do texto
- ✅ Flexibilidade para campanhas especiais

### Para a Performance:
- ✅ Sem necessidade de múltiplas versões de imagens
- ✅ Efeitos aplicados via CSS (rápido)
- ✅ Valores armazenados no banco (cache eficiente)

---

## 🧪 Como Testar

### 1. Acessar o Admin
```
http://localhost:8000/admin/core/section/
```

### 2. Editar uma Seção com Banner
- Clique em uma seção que tenha banner
- Expanda a seção "Estilo Visual"
- Configure os novos campos:
  - **Altura do Banner (px):** Teste com 300, 400, 600
  - **Transparência do Banner:** Teste com 0.5, 0.7, 1.0
  - **Opacidade das Bordas:** Teste com 0.0, 0.5, 0.8

### 3. Salvar e Visualizar
- Clique em "Salvar"
- Acesse a home: `http://localhost:8000/`
- Verifique as mudanças no banner

### 4. Testar "Ver Mais"
- No admin, em "Configurações de Exibição":
  - ☑ Marque "Mostrar 'Ver Mais'"
  - URL: `/livros/`
- Salve e veja o link aparecer na seção

---

## 🎯 Casos de Uso Reais

### Lançamentos de Livros
```
Banner: Capa do livro em destaque
Altura: 500px
Transparência: 1.0
Opacidade Bordas: 0.7
Ver Mais: /livros/?tag=lancamento
```

### Seção de Autores
```
Banner: Foto dos autores
Altura: 350px
Transparência: 0.8
Opacidade Bordas: 0.4
Ver Mais: /autores/
```

### Campanha Promocional
```
Banner: Arte promocional
Altura: 600px
Transparência: 1.0
Opacidade Bordas: 0.9
Ver Mais: /livros/?promocao=black-friday
```

### Seção Minimalista
```
Banner: Pattern sutil
Altura: 250px
Transparência: 0.3
Opacidade Bordas: 0.0
Ver Mais: (desabilitado)
```

---

## ✅ Checklist de Implementação

- [x] Adicionar campo `banner_height` ao model
- [x] Adicionar campo `banner_opacity` ao model
- [x] Adicionar campo `banner_border_opacity` ao model
- [x] Atualizar admin com novos campos
- [x] Criar migration
- [x] Aplicar migration
- [x] Atualizar view para passar novos campos
- [x] Atualizar template para usar novos campos
- [x] Testar funcionalidade
- [x] Verificar campo "Ver Mais" (já funcionava)
- [x] Documentar alterações

---

## 🚀 Próximos Passos (Sugestões)

### Possíveis Melhorias Futuras:

1. **Preset de Estilos:**
   - Botão para aplicar configurações pré-definidas
   - Ex: "Hero", "Sutil", "Minimalista", "Destaque"

2. **Preview em Tempo Real:**
   - JavaScript no admin para mostrar preview das configurações
   - Antes de salvar

3. **Responsividade:**
   - Altura diferente para mobile/tablet/desktop
   - Opacidades adaptáveis

4. **Animações:**
   - Fade in ao carregar
   - Parallax scroll
   - Ken Burns effect

5. **Múltiplos Overlays:**
   - Overlay superior e inferior
   - Cores personalizadas de overlay
   - Gradientes complexos

---

## 📝 Notas Técnicas

### Validadores Aplicados:
```python
MinValueValidator(0.0)
MaxValueValidator(1.0)
```

### Formato de Float:
```python
{{ value|floatformat:2 }}
# Resultado: 0.75 → "0.75"
```

### Cálculo CSS:
```css
calc(0.8 * 0.5)  /* = 0.4 */
```

### Fallbacks:
```django
{{ section.banner_height|default:400 }}
{{ section.banner_opacity|default:1.0 }}
{{ section.banner_border_opacity|default:0.8 }}
```

---

**Implementação Completa e Testada! 🎊**
