## 📋 **DOCUMENTO DE CONTEXTO - Sistema de Temas Personalizados**

```markdown
# CGBookStore v3 - Contexto: Sistema de Temas da Biblioteca Pessoal

**Data:** 13/10/2025
**Sessão:** Implementação de Temas Personalizados
**Status:** 🟡 Em Desenvolvimento - Conflito de CSS Identificado

---

## 🎯 OBJETIVO DA IMPLEMENTAÇÃO

Criar um sistema de temas visuais personalizados para a página de Biblioteca Pessoal do usuário, onde cada tema (Fantasy, Horror, Romance, etc.) aplica:

- **Paletas de cores** específicas (roxo/dourado para Fantasy, vermelho/preto para Horror)
- **Tipografia temática** (fontes serif elegantes, góticas, etc.)
- **Efeitos visuais** (bordas, sombras, partículas animadas)
- **Backgrounds temáticos** (cores de fundo, gradientes)
- **Ícones personalizados** por categoria

**Requisitos:**
- Suporte para modo claro E escuro por tema
- CSS externo (não inline) para manutenibilidade
- Compatibilidade com sistema de tema global (claro/escuro)
- Performance otimizada (system fonts, sem bibliotecas externas)

---

## 📂 ESTRUTURA DO PROJETO

### **Arquivos Principais:**

```
cgbookstore_v3/
├── accounts/
│   ├── models/
│   │   └── user_profile.py         # Campo: theme_preference
│   ├── forms.py                     # UserProfileForm
│   └── views.py                     # edit_profile view
│
├── core/
│   └── views/
│       └── library_view.py          # LibraryView (passa selected_theme)
│
├── templates/
│   ├── base.html                    # Template base (CONFLITO AQUI)
│   └── core/
│       └── library.html             # Biblioteca pessoal (tema aplicado)
│
└── static/
    ├── css/
    │   ├── themes.css               # Sistema global claro/escuro
    │   └── library-profile.css      # Temas personalizados (Fantasy, etc)
    └── js/
        ├── theme-switcher.js        # Toggle claro/escuro global
        └── library-manager.js       # Gerenciamento da biblioteca
```

---

## ⚙️ CONFIGURAÇÃO ATUAL

### **1. Model - UserProfile**
```python
# accounts/models/user_profile.py

THEME_CHOICES = [
    # FREE (3 temas)
    ('fantasy', '✨ Fantasia (Roxo/Dourado)'),
    ('classic', '📚 Clássicos (Marrom/Bege)'),
    ('romance', '💕 Romance (Rosa/Vermelho)'),
    # PREMIUM (12 temas)
    ('scifi', '🚀 Ficção Científica'),
    ('horror', '🎃 Terror'),
    # ... mais 10 temas
]

class UserProfile(models.Model):
    theme_preference = models.CharField(
        max_length=20,
        choices=THEME_CHOICES,
        default='fantasy',
        verbose_name="Tema Visual"
    )
```

### **2. View - Library**
```python
# core/views/library_view.py

class LibraryView(LoginRequiredMixin, TemplateView):
    template_name = 'core/library.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = getattr(self.request.user, 'profile', None)
        context['profile'] = profile

        # ✅ ADICIONADO: Passa o tema selecionado
        context['selected_theme'] = profile.theme_preference if profile else 'fantasy'

        # ... resto do context
        return context
```

### **3. Template - Library.html**
```html
{% extends 'base.html' %}
{% load static %}

{% block extra_css %}
<link rel="stylesheet" href="{% static 'css/library-profile.css' %}">
{% endblock %}

{% block content %}
<!-- ✅ CLASSE APLICADA -->
<div class="theme-{{ selected_theme }}" style="width: 100%;">
    <div class="container-fluid px-md-4">

        {% if profile %}
            {% include 'core/widgets/profile_hero.html' %}
        {% endif %}

        <div class="library-container theme-{{ selected_theme }}">
            <!-- Sidebar e conteúdo da biblioteca -->
        </div>
    </div>
</div>
{% endblock %}
```

---

## 🐛 PROBLEMA IDENTIFICADO

### **Conflito entre Dois Sistemas de Temas**

**Sistema 1: Theme Switcher Global** (`theme-switcher.js`)
- Controla modo claro/escuro do site inteiro
- Aplica: `data-bs-theme="dark"` ou `"light"` no `<html>`

**Sistema 2: Temas Personalizados** (`library-profile.css`)
- Controla estilo temático da biblioteca
- Aplica: classe `.theme-fantasy`, `.theme-horror`, etc.

### **Causa do Problema:**

Os seletores CSS dependem de AMBOS os sistemas:

```css
/* ❌ ATUAL: Requer data-bs-theme E classe do tema */
[data-bs-theme="dark"] .theme-fantasy .library-sidebar {
    background-color: #1f0f3a;
}

[data-bs-theme="light"] .theme-fantasy .library-sidebar {
    background-color: #ede9fe;
}
```

**Resultado:**
- ✅ Classe `.theme-fantasy` está aplicada no HTML
- ⚠️ CSS não funciona porque depende também do `[data-bs-theme]`
- ❌ Temas não são visíveis para o usuário

---

## 🔍 DIAGNÓSTICO TÉCNICO

### **Template base.html - Influências:**

```html
<!-- base.html carrega: -->
<link rel="stylesheet" href="{% static 'css/themes.css' %}">
<script src="{% static 'js/theme-switcher.js' %}"></script>

<!-- theme-switcher.js aplica: -->
<html data-bs-theme="dark"> <!-- ou "light" ou "auto" -->
```

### **Verificação via Console:**

```javascript
// Estado atual no navegador:
document.documentElement.getAttribute('data-bs-theme'); // "dark"
document.querySelector('.theme-fantasy'); // <div class="theme-fantasy">...</div>

// CSS esperado:
// [data-bs-theme="dark"] .theme-fantasy .library-sidebar
// ✅ Ambos presentes, mas CSS ainda não aplica
```

---

## 📝 TENTATIVAS ANTERIORES

### **✅ Tentativa 1: CSS Inline no Template**
- **Ação:** Colocar estilos direto no `<style>` do `library.html`
- **Resultado:** ❌ Funcionou, mas péssima prática
- **Problema:** Não é manutenível, mistura estrutura e estilo

### **✅ Tentativa 2: CSS Externo com !important**
- **Ação:** Adicionar `!important` em todas as regras
- **Resultado:** ❌ Não funcionou
- **Problema:** Estilos inline do template têm precedência

### **✅ Tentativa 3: Limpeza do Template**
- **Ação:** Remover TODO CSS inline do `library.html`
- **Resultado:** ✅ Template limpo, mas tema ainda não aplica
- **Status:** Arquivo `library.html` agora correto (sem CSS inline)

### **✅ Tentativa 4: CSS Completo Externo**
- **Ação:** Criar `library-profile.css` completo com todos estilos base + temas
- **Resultado:** ❌ Não funciona devido ao conflito de seletores
- **Status:** Arquivo CSS correto, problema é de arquitetura

---

## 🎯 SOLUÇÕES PROPOSTAS

### **Opção A: Simplificar Seletores (RECOMENDADO)**

**Remover dependência do `[data-bs-theme]`:**

```css
/* ✅ NOVO: Independente do theme-switcher */
.theme-fantasy .library-sidebar {
    background-color: #1f0f3a;
}

/* Variação por tema global via variáveis CSS */
.theme-fantasy {
    --theme-bg-sidebar: #1f0f3a; /* escuro */
}

@media (prefers-color-scheme: light) {
    .theme-fantasy {
        --theme-bg-sidebar: #ede9fe; /* claro */
    }
}

.theme-fantasy .library-sidebar {
    background-color: var(--theme-bg-sidebar);
}
```

**Vantagens:**
- ✅ Funciona independente do theme-switcher
- ✅ Suporta modo claro/escuro via media query
- ✅ Mais simples de manter

**Desvantagens:**
- ⚠️ Não respeita escolha manual do usuário (botão claro/escuro)

---

### **Opção B: Integração com Theme-Switcher**

**Adicionar lógica JavaScript para sincronizar:**

```javascript
// Detectar tema da biblioteca e forçar modo correspondente
if (document.querySelector('.theme-fantasy')) {
    // Tema Fantasy usa modo escuro por padrão
    ThemeSwitcher.setTheme('dark');
}
```

**Ou criar variação nos seletores:**

```css
/* Aceitar QUALQUER modo quando tema está ativo */
.theme-fantasy .library-sidebar {
    background-color: var(--fantasy-bg-sidebar);
}

:root[data-bs-theme="dark"] {
    --fantasy-bg-sidebar: #1f0f3a;
}

:root[data-bs-theme="light"] {
    --fantasy-bg-sidebar: #ede9fe;
}
```

**Vantagens:**
- ✅ Respeita escolha do usuário
- ✅ Integração perfeita entre sistemas

**Desvantagens:**
- ⚠️ Mais complexo
- ⚠️ Requer mudanças em 2 arquivos (CSS + JS)

---

### **Opção C: Sistema Único Unificado**

**Migrar tudo para variáveis CSS:**

```css
/* themes.css - Define variáveis base */
:root[data-bs-theme="dark"] {
    --theme-color: var(--fantasy-primary, #9333ea);
    --theme-bg: var(--fantasy-bg, #1a0b2e);
}

/* library-profile.css - Define valores por tema */
.theme-fantasy {
    --fantasy-primary: #9333ea;
    --fantasy-bg: #1a0b2e;
}

/* Aplicação direta */
.library-sidebar {
    background-color: var(--theme-bg);
}
```

**Vantagens:**
- ✅ Sistema mais elegante
- ✅ Fácil adicionar novos temas

**Desvantagens:**
- ⚠️ Requer refatoração completa
- ⚠️ Maior tempo de implementação

---

## 📊 RECOMENDAÇÃO

### **🎯 SOLUÇÃO HÍBRIDA (Melhor custo-benefício):**

1. **Manter** estrutura de classes atual (`.theme-fantasy`)
2. **Remover** seletor `[data-bs-theme]` dos temas personalizados
3. **Usar** variáveis CSS para suportar claro/escuro
4. **Adicionar** detecção automática do tema global quando necessário

**Implementação:**

```css
/* Tema Fantasy - Adaptável */
.theme-fantasy {
    /* Cores base (escuro) */
    --theme-primary: #9333ea;
    --theme-bg-sidebar: #1f0f3a;
    --theme-bg-content: #1a0b2e;
}

/* Adaptação para modo claro */
[data-bs-theme="light"] .theme-fantasy {
    --theme-bg-sidebar: #ede9fe;
    --theme-bg-content: #faf5ff;
}

/* Aplicação */
.theme-fantasy .library-sidebar {
    background-color: var(--theme-bg-sidebar);
    border-right: 2px solid var(--theme-primary);
}
```

---

## 🔧 PRÓXIMOS PASSOS

### **Fase 1: Correção Imediata (15 min)**
1. Atualizar `library-profile.css` com seletores corrigidos
2. Testar tema Fantasy em modo escuro e claro
3. Validar que mudanças não afetam outras páginas

### **Fase 2: Expansão (1h)**
4. Aplicar mesma lógica para temas Classic e Romance
5. Criar estrutura base para 12 temas PREMIUM
6. Documentar padrão para futuros temas

### **Fase 3: Refinamento (30 min)**
7. Ajustar contrastes para acessibilidade
8. Adicionar transições suaves entre temas
9. Testar em diferentes navegadores

---

## 🎨 ESPECIFICAÇÃO DO TEMA FANTASY

### **Paleta de Cores:**

**Modo Escuro:**
- Primária: `#9333ea` (roxo místico)
- Secundária: `#fbbf24` (dourado mágico)
- Background Sidebar: `#1f0f3a` (roxo muito escuro)
- Background Content: `#1a0b2e` (quase preto)
- Texto: `#e9d5ff` (lavanda claro)

**Modo Claro:**
- Primária: `#7c3aed` (roxo vibrante)
- Secundária: `#f59e0b` (dourado solar)
- Background Sidebar: `#ede9fe` (lavanda claro)
- Background Content: `#faf5ff` (lavanda muito claro)
- Texto: `#581c87` (roxo escuro)

### **Tipografia:**
- Display: `Georgia, 'Times New Roman', serif`
- Body: `-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif`

### **Efeitos Especiais:**
- ✨ Partículas flutuantes (emoji ✨)
- 💫 Brilho nos ícones (`text-shadow`, `filter: drop-shadow`)
- 🌟 Bordas animadas (gradiente rotativo no avatar)
- ⭐ Hover com elevação e brilho

---

## ✅ CHECKLIST DE VALIDAÇÃO

Após implementar a correção, verificar:

- [ ] Avatar tem borda roxa (não azul)
- [ ] Sidebar tem fundo roxo escuro
- [ ] Títulos usam fonte Georgia
- [ ] Stats cards têm bordas roxas
- [ ] Book cards têm bordas roxas ao hover
- [ ] Partículas ✨ aparecem e animam
- [ ] Tema funciona em modo claro
- [ ] Tema funciona em modo escuro
- [ ] Toggle claro/escuro não quebra o tema
- [ ] Outros temas (Classic, Romance) não afetados

---

## 📚 ARQUIVOS PARA REVISAR

### **Críticos (precisam de modificação):**
1. `static/css/library-profile.css` - **PRINCIPAL**
2. `core/views/library_view.py` - Verificar context
3. `templates/core/library.html` - Verificar classes aplicadas

### **Referência (não modificar):**
4. `templates/base.html` - Entender theme-switcher
5. `static/js/theme-switcher.js` - Lógica global
6. `accounts/models/user_profile.py` - THEME_CHOICES

---

## 💡 OBSERVAÇÕES IMPORTANTES

1. **System Fonts:** Usar apenas fontes do sistema (Georgia, serif) - sem Google Fonts
2. **Performance:** CSS externo para cache - NUNCA inline
3. **Manutenibilidade:** Um tema = um bloco CSS modular
4. **Escalabilidade:** Preparar estrutura para 15 temas total
5. **Acessibilidade:** Garantir contraste mínimo WCAG AA

---

## 🔗 LINKS ÚTEIS

- Projeto GitHub: `https://github.com/cgvargas/cgbookstore_v3`
- Branch: `main`
- Último commit antes do problema: `a010177`

---

**Este documento contém TODO o contexto necessário para retomar o trabalho.**

```

---

## 💾 **SALVE ESTE DOCUMENTO COMO:**

`documents/status/CONTEXTO_TEMAS_PERSONALIZADOS_13102025.md`

---

**Com este documento, qualquer desenvolvedor (ou nova sessão de IA) pode retomar de onde paramos!** 📋✅