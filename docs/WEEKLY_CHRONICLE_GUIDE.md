# 📰 Guia da Crônica Semanal

## 📋 Visão Geral

A **Crônica Semanal** é uma funcionalidade que permite criar e publicar crônicas personalizadas no estilo de jornal tradicional. O superusuário pode editar todo o conteúdo (textos e imagens) mantendo a estrutura da página sempre consistente.

## 🎨 Características

### Layout de Jornal Tradicional
- Design inspirado em jornais clássicos
- Fonte serifada (Merriweather) para títulos
- Fonte sans-serif (Open Sans) para corpo do texto
- Grid responsivo de 2 colunas (principal + sidebar)
- Suporte total a dark mode

### Estrutura da Página

1. **Cabeçalho do Jornal**
   - Título: "A CRÔNICA SEMANAL"
   - Tagline: "Sua Semana em Revista"
   - Período da semana
   - Volume e edição

2. **Artigo Principal** (coluna esquerda)
   - Título em destaque
   - Subtítulo
   - Byline (autor e data)
   - Introdução
   - Imagem principal
   - Conteúdo
   - Conclusão

3. **Destaques da Semana** (sidebar direita)
   - Realização
   - Social
   - Saúde
   - Aprendizado
   - Pessoal

4. **Seções Adicionais**
   - Casa & Família
   - Saúde & Bem-Estar
   - Entretenimento & Cultura
   - Perspectivas (citações)

## 📝 Como Usar

### Acessando o Admin

1. Faça login como superusuário
2. Acesse: `/admin/core/weeklychronicle/`
3. Clique em "Adicionar Crônica Semanal"

### Preenchendo a Crônica

#### 📰 Informações da Edição
- **Volume e Edição**: Números sequenciais (ex: Vol. 1, Ed. 1)
- **Datas**: Início e fim da semana
- **Publicação**: Data e hora de publicação
- **Status**: Marque "Publicado" para tornar visível

#### 📝 Artigo Principal
- **Título**: Título principal da crônica (obrigatório)
- **Subtítulo**: Chamada complementar (opcional)
- **Autor**: Nome do autor (padrão: "Equipe CG.BookStore")
- **Introdução**: Primeiro parágrafo em destaque
- **Conteúdo Principal**: Corpo principal do texto
- **Conclusão**: Parágrafo final (opcional)

#### 🖼️ Imagem do Artigo Principal
- **Imagem**: Upload da foto principal
- **Proporção**: Escolha entre:
  - **1:1** - Quadrado
  - **4:5** - Vertical (Instagram)
  - **16:9** - Horizontal (widescreen)

#### ⭐ Destaques da Semana
Preencha até 5 destaques curtos que aparecem na sidebar:
- Realização
- Social
- Saúde
- Aprendizado
- Pessoal

#### 💬 Citações
- **Citação Principal**: Aparece na seção de Saúde & Bem-Estar
- **Autor da Citação**: Nome do autor
- **Citação Secundária**: Aparece na seção Perspectivas
- **Autor**: Nome do autor da segunda citação

#### 🏠 Seções Opcionais

**Casa & Família**
- Título do artigo
- Conteúdo
- Imagem secundária (opcional)

**Saúde & Bem-Estar**
- Título do artigo
- Conteúdo
- Imagem da galeria 1 (opcional)

**Entretenimento & Cultura**
- Título do artigo
- Conteúdo
- Imagens da galeria 2 e 3 (opcional)

#### 🎨 Galeria de Imagens
Adicione até 3 imagens extras:
- Galeria 1, 2 e 3
- Cada uma com proporção independente

## 🖼️ Proporções de Imagem Recomendadas

| Proporção | Uso Ideal | Dimensões Sugeridas |
|-----------|-----------|---------------------|
| **1:1** | Imagens quadradas, retratos | 800x800px |
| **4:5** | Fotos verticais estilo Instagram | 800x1000px |
| **16:9** | Paisagens, fotos horizontais | 1200x675px |

## 📖 Exemplo de Uso

```python
# Criar crônica via shell
from core.models import WeeklyChronicle
from django.utils import timezone

chronicle = WeeklyChronicle.objects.create(
    volume_number=1,
    issue_number=1,
    title="Minha Semana Literária",
    author_name="Carolina Vargas",
    introduction="Esta semana foi marcada por descobertas...",
    main_content="Segunda-feira começou com...",
    highlights_accomplishment="Li 3 livros",
    is_published=True,
)
```

## 🌐 Acessando a Crônica

- **URL Pública**: `/cronica-semanal/`
- **Link no Navbar**: "Crônica Semanal" (com ícone de pena)

## 💡 Dicas de Redação

### Para o Artigo Principal
1. Use a introdução para capturar a atenção
2. Desenvolva o tema no conteúdo principal
3. Finalize com reflexão ou convite à ação

### Para os Destaques
- Seja breve e direto (máx. 300 caracteres)
- Use linguagem positiva
- Destaque realizações concretas

### Para as Seções
- **Casa & Família**: Histórias pessoais, projetos domésticos
- **Saúde**: Dicas, rotinas, bem-estar
- **Entretenimento**: Filmes, livros, eventos culturais

## 🎯 Boas Práticas

### Conteúdo
✅ Escreva em português do Brasil
✅ Use parágrafos curtos (3-4 linhas)
✅ Varie o ritmo com citações
✅ Seja autêntico e pessoal

### Imagens
✅ Use imagens de alta qualidade
✅ Escolha a proporção adequada ao conteúdo
✅ Adicione imagens que complementam o texto
✅ Formatos aceitos: JPG, JPEG, PNG, WEBP

### Periodicidade
✅ Mantenha regularidade (semanal, quinzenal)
✅ Incremente o número da edição a cada publicação
✅ Atualize as datas da semana

## 🔧 Administração

### Listagem de Crônicas
O admin mostra:
- Título
- Autor
- Período da semana
- Volume/Edição
- Status (publicado/rascunho)
- Botão de visualização
- Data de atualização

### Pré-visualização
- Cada seção de imagem tem preview no admin
- Botão "Visualizar" abre a crônica em nova aba
- Preview mostra proporção escolhida

### SEO
- Meta descrição gerada automaticamente da introdução
- Pode ser customizada manualmente
- Limite: 160 caracteres

## 🎨 Personalização

### Cores (pode ser editado no CSS)
- Bordas: `#333` (preto)
- Sidebar: `#f9f9f9` (cinza claro)
- Quote box: `#f5f5f5` (cinza muito claro)

### Fontes
- Títulos: `Merriweather` (serifada)
- Corpo: `Open Sans` (sans-serif)

## 📱 Responsividade

- Desktop: Layout em 2 colunas
- Tablet/Mobile: Layout em 1 coluna
- Imagens adaptam automaticamente
- Fonte reduz em telas pequenas

## 🚀 Próximos Passos

1. Crie sua primeira crônica
2. Adicione imagens de qualidade
3. Preencha todos os campos
4. Marque como "Publicado"
5. Acesse `/cronica-semanal/` para ver o resultado

## 📞 Suporte

Para dúvidas ou sugestões:
- Email: contato@cgbookstore.com
- Admin: Acesse o painel administrativo

---

**Desenvolvido com ❤️ pela Equipe CG.BookStore**
