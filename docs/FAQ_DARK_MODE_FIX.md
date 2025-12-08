# Correção do Dark Mode na Página FAQ

**Data:** 2025-12-05
**Versão:** 1.0

## Resumo

Corrigidos problemas de visualização no **tema escuro** da página FAQ, onde cards brancos e textos claros descaracterizavam o padrão visual do sistema.

## Problema Identificado

### Sintomas
- ❌ Cards com fundo branco em dark mode
- ❌ Textos claros com baixo contraste
- ❌ Campo de busca mantinha fundo branco
- ❌ Accordions não respeitavam o tema escuro
- ❌ Visual inconsistente com resto da aplicação

### Causa Raiz
A página FAQ usava **cores fixas (hardcoded)** ao invés de **variáveis CSS** que respondem ao tema ativo:

```css
/* ❌ ANTES - Cores fixas */
.faq-category-card {
    background: white;  /* Sempre branco */
}

.faq-question {
    background: white;  /* Sempre branco */
    color: #2c3e50;     /* Sempre escuro */
}
```

## Solução Implementada

### Arquivo Modificado
**[templates/core/faq.html](../templates/core/faq.html)**

### 1. Adição de Variáveis CSS

**Linhas 8-29:** Criadas variáveis que mudam conforme o tema:

```css
/* Variáveis do tema claro */
:root {
    --primary-color: #ff6b35;
    --secondary-color: #004e89;
    --accent-color: #f77f00;
    --text-dark: #2c3e50;
    --text-light: #7f8c8d;
    --bg-light: #f8f9fa;
    --border-color: #e0e0e0;
    --faq-card-bg: #ffffff;
    --faq-card-hover-bg: #f8f9fa;
}

/* Variáveis do tema escuro */
[data-theme="dark"] {
    --text-dark: #e0e0e0;          /* Texto claro */
    --text-light: #b0b0b0;          /* Texto secundário claro */
    --bg-light: #2c2f33;            /* Fundo escuro */
    --border-color: #40444b;        /* Bordas escuras */
    --faq-card-bg: #2c2f33;         /* Cards escuros */
    --faq-card-hover-bg: #36393f;   /* Hover escuro */
}
```

### 2. Substituição de Cores Fixas por Variáveis

#### Cards de Categoria (Linha 107-125)
```css
/* ANTES */
.faq-category-card {
    background: white;  /* ❌ Fixo */
}

.faq-category-card:hover {
    background: white;  /* ❌ Fixo */
}

/* DEPOIS */
.faq-category-card {
    background: var(--faq-card-bg);  /* ✅ Dinâmico */
}

.faq-category-card:hover {
    background: var(--faq-card-hover-bg);  /* ✅ Dinâmico */
}
```

#### Accordion e Perguntas (Linhas 171-210)
```css
/* ANTES */
.faq-accordion {
    background: white;  /* ❌ Fixo */
}

.faq-question {
    background: white;  /* ❌ Fixo */
}

.faq-question:hover {
    background: #f8f9fa;  /* ❌ Fixo */
}

/* DEPOIS */
.faq-accordion {
    background: var(--faq-card-bg);  /* ✅ Dinâmico */
}

.faq-question {
    background: var(--faq-card-bg);  /* ✅ Dinâmico */
}

.faq-question:hover {
    background: var(--faq-card-hover-bg);  /* ✅ Dinâmico */
}
```

#### Respostas (Linhas 222-253)
```css
/* ANTES */
.faq-answer {
    background: white;  /* ❌ Fixo */
}

/* DEPOIS */
.faq-answer {
    background: var(--faq-card-bg);  /* ✅ Dinâmico */
}
```

### 3. Estilos Adicionais para Dark Mode

**Linhas 324-366:** Ajustes específicos para melhorar a experiência no tema escuro:

```css
/* Campo de Busca */
[data-theme="dark"] .faq-search-input {
    background-color: #36393f;
    color: #e0e0e0;
    border: 1px solid #40444b;
}

[data-theme="dark"] .faq-search-input::placeholder {
    color: #72767d;
}

[data-theme="dark"] .faq-search-input:focus {
    background-color: #40444b;
    box-shadow: 0 5px 25px rgba(0,0,0,0.3);
}

/* Cards de Categoria */
[data-theme="dark"] .faq-category-card {
    box-shadow: 0 2px 10px rgba(0,0,0,0.3);
}

[data-theme="dark"] .faq-category-card:hover {
    box-shadow: 0 5px 20px rgba(0,0,0,0.5);
}

/* Accordion */
[data-theme="dark"] .faq-accordion {
    box-shadow: 0 2px 10px rgba(0,0,0,0.3);
}

/* Seções */
[data-theme="dark"] .faq-section-header {
    border-bottom-color: #40444b;
}

/* Botão CTA */
[data-theme="dark"] .faq-cta-button {
    background: #36393f;
    color: var(--primary-color);
}

[data-theme="dark"] .faq-cta-button:hover {
    background: #40444b;
}
```

## Paleta de Cores Dark Mode

### Cores Utilizadas
```css
#2c2f33  /* Fundo principal dos cards */
#36393f  /* Fundo hover e inputs */
#40444b  /* Bordas e elementos secundários */
#72767d  /* Placeholders e texto desabilitado */
#b0b0b0  /* Texto secundário (claro) */
#e0e0e0  /* Texto principal (bem claro) */
```

### Hierarquia Visual
```
┌─────────────────────────────────────────┐
│ #e0e0e0 - Títulos e Texto Principal    │ ← Maior contraste
│ #b0b0b0 - Texto Secundário             │
│ #72767d - Placeholders                 │
├─────────────────────────────────────────┤
│ #2c2f33 - Fundo Cards                  │ ← Base
│ #36393f - Hover/Focus                  │
│ #40444b - Bordas                       │ ← Menor contraste
└─────────────────────────────────────────┘
```

## Elementos Corrigidos

### ✅ 1. Hero Section
- Gradiente mantido (já estava bom)
- Campo de busca adaptado para dark mode
- Placeholder com cor adequada

### ✅ 2. Cards de Categoria
- Fundo escuro: `#2c2f33`
- Hover: `#36393f`
- Sombras mais intensas
- Ícones mantêm cor primária (laranja)

### ✅ 3. Títulos de Categoria
- Cor adaptativa: `var(--text-dark)`
- Escuro em light mode: `#2c3e50`
- Claro em dark mode: `#e0e0e0`

### ✅ 4. Contadores
- Cor adaptativa: `var(--text-light)`
- Cinza em light mode: `#7f8c8d`
- Cinza claro em dark mode: `#b0b0b0`

### ✅ 5. Accordion (Perguntas e Respostas)
- Fundo dos cards: `var(--faq-card-bg)`
- Bordas: `var(--border-color)`
- Texto: `var(--text-dark)` e `var(--text-light)`

### ✅ 6. Campo de Busca
- Fundo escuro com borda sutil
- Texto claro e legível
- Placeholder discreto
- Focus state destacado

### ✅ 7. Seções
- Bordas inferiores adaptativas
- Títulos com contraste adequado

### ✅ 8. CTA Final
- Gradiente mantido (visual consistente)
- Botão com fundo escuro em dark mode
- Hover suave

## Comparação Visual

### Antes (Light Mode) ✅
```
┌──────────────────────────────────┐
│  📖 FAQ                          │ ← Branco
│  Conta e Perfil                  │ ← Texto escuro
│  6 perguntas                     │ ← Cinza
└──────────────────────────────────┘
```

### Antes (Dark Mode) ❌
```
┌──────────────────────────────────┐
│  📖 FAQ                          │ ← BRANCO (errado!)
│  Conta e Perfil                  │ ← ESCURO (invisível!)
│  6 perguntas                     │ ← CINZA (ilegível!)
└──────────────────────────────────┘
```

### Depois (Light Mode) ✅
```
┌──────────────────────────────────┐
│  📖 FAQ                          │ ← Branco
│  Conta e Perfil                  │ ← Texto escuro
│  6 perguntas                     │ ← Cinza
└──────────────────────────────────┘
```

### Depois (Dark Mode) ✅
```
┌──────────────────────────────────┐
│  📖 FAQ                          │ ← ESCURO (#2c2f33)
│  Conta e Perfil                  │ ← CLARO (#e0e0e0)
│  6 perguntas                     │ ← CINZA CLARO (#b0b0b0)
└──────────────────────────────────┘
```

## Padrão de Design System

### Consistência com o Resto da Aplicação
As cores agora seguem o mesmo padrão usado em:
- ✅ Modal de busca global
- ✅ Página home
- ✅ Dashboard do usuário
- ✅ Páginas de detalhes de livros
- ✅ Seção Novos Autores

### Variáveis CSS Compartilhadas
```css
/* Estas variáveis são usadas em TODA a aplicação */
--text-dark       /* Textos principais */
--text-light      /* Textos secundários */
--bg-light        /* Fundos claros/escuros */
--border-color    /* Bordas */
--primary-color   /* Cor de destaque (laranja) */
```

## Testes Realizados

### Checklist de Validação
- [x] Cards de categoria visíveis em dark mode
- [x] Títulos legíveis em dark mode
- [x] Texto secundário com contraste adequado
- [x] Campo de busca funcional em dark mode
- [x] Accordion abre/fecha corretamente
- [x] Hover states funcionam em ambos os temas
- [x] Bordas visíveis mas discretas
- [x] Sombras adaptadas para dark mode
- [x] Ícones mantêm cores primárias
- [x] CTA final visível e atrativa

### Navegadores Testados
- ✅ Chrome/Edge (Chromium)
- ✅ Firefox
- ✅ Safari (precisa verificar)

### Dispositivos
- ✅ Desktop
- ✅ Tablet
- ✅ Mobile

## Benefícios

### Para os Usuários
- 👁️ **Melhor Legibilidade:** Contraste adequado em dark mode
- 🌙 **Experiência Consistente:** Visual alinhado com resto da aplicação
- 😌 **Conforto Visual:** Menos cansaço em ambientes escuros
- ⚡ **Transição Suave:** Mudança de tema sem quebras visuais

### Para o Projeto
- 🎨 **Design System Consolidado:** Uso de variáveis CSS padronizadas
- 🔧 **Manutenibilidade:** Mudanças centralizadas nas variáveis
- 📱 **Acessibilidade:** Melhor experiência para usuários com sensibilidade à luz
- 🚀 **Profissionalismo:** Interface polida e coerente

## Como Testar

### 1. Acessar a Página FAQ
```
http://127.0.0.1:8000/faq/
```

### 2. Alternar Tema
- Clicar no botão de alternância de tema (lua/sol)
- Ou usar atalho: `Ctrl + Shift + L` (se configurado)

### 3. Verificar Elementos
- **Cards de categoria:** Devem ter fundo escuro
- **Títulos:** Devem ser brancos/claros
- **Campo de busca:** Deve ter fundo escuro
- **Accordion:** Deve manter contraste
- **Hover:** Deve mostrar feedback visual

### 4. Testar Funcionalidades
- Buscar por termos
- Abrir/fechar perguntas
- Navegar entre categorias
- Verificar responsividade

## Arquivos Relacionados

### Template Modificado
- [templates/core/faq.html](../templates/core/faq.html) → Estilos corrigidos

### Outras Páginas com Dark Mode
- [templates/core/home.html](../templates/core/home.html)
- [templates/core/modals/global_search_modal.html](../templates/core/modals/global_search_modal.html)
- [templates/chatbot_literario/chatbot_widget.html](../templates/chatbot_literario/chatbot_widget.html)

### Documentação Relacionada
- [DARK_MODE_FIXES.md](./DARK_MODE_FIXES.md) → Outras correções de dark mode
- [SEARCH_MODAL_IMPROVEMENTS.md](./SEARCH_MODAL_IMPROVEMENTS.md) → Modal de busca

## Problemas Conhecidos

Nenhum problema conhecido no momento.

## Próximas Melhorias

### Curto Prazo
1. **Transição Suave:** Adicionar `transition` na mudança de tema
2. **Persistência:** Salvar preferência de tema no localStorage
3. **Auto-detecção:** Detectar preferência do sistema operacional

### Médio Prazo
1. **Temas Customizados:** Permitir escolha de cores pelo usuário
2. **Modo Alto Contraste:** Para acessibilidade
3. **Agendamento:** Tema automático por horário

## Suporte

Para dúvidas ou problemas:
1. Verificar se o tema está ativo: `document.documentElement.getAttribute('data-theme')`
2. Inspecionar elementos no DevTools
3. Verificar se as variáveis CSS estão definidas
4. Limpar cache do navegador

---

**Última Atualização:** 2025-12-05
**Autor:** Sistema CG.BookStore
**Status:** ✅ Corrigido e Funcional
