# 📱 Guia Completo: Vídeos do Instagram na Home

Guia passo a passo para adicionar vídeos do Instagram na página inicial do CGBookStore.

---

## 📋 Índice

1. [Acessar o Admin](#passo-1-acessar-o-admin)
2. [Adicionar Vídeos do Instagram](#passo-2-adicionar-vídeos-do-instagram)
3. [Criar Seção na Home](#passo-3-criar-seção-na-home)
4. [Adicionar Vídeos à Seção](#passo-4-adicionar-vídeos-à-seção)
5. [Visualizar na Home](#passo-5-visualizar-na-home)
6. [Dicas e Troubleshooting](#dicas-e-troubleshooting)

---

## 🎯 Passo 1: Acessar o Admin

### 1.1 Fazer Login
1. Acesse: `https://seu-site.com/admin/`
2. Digite seu **usuário** e **senha** de administrador
3. Clique em **"Entrar"**

✅ Você deve ver o painel de administração do Django

---

## 📹 Passo 2: Adicionar Vídeos do Instagram

### 2.1 Navegar até Vídeos
1. No painel admin, procure a seção **"CORE"**
2. Clique em **"Vídeos"**
3. Clique no botão **"Adicionar Vídeo"** (canto superior direito)

### 2.2 Preencher Informações do Vídeo

#### 📝 Informações Básicas
- **Título**: Nome do vídeo
  - Exemplo: `Promoção Black Friday 2024`

- **Slug**: Deixe em branco (será gerado automaticamente)

- **Descrição**: Descreva o conteúdo
  - Exemplo: `Confira nossas ofertas imperdíveis de Black Friday! Até 70% de desconto em livros selecionados.`

- **Tipo de Vídeo**: Selecione **"Propaganda/Promocional"**
  - Outras opções: Book Trailer, Entrevista, Resenha, Tutorial, Discussão, Outro

#### 🎥 Vídeo
- **Plataforma**: Selecione **"Instagram"** ⭐ (IMPORTANTE!)

- **URL do Vídeo**: Cole a URL completa do Instagram
  - ✅ Formatos aceitos:
    - `https://www.instagram.com/p/ABC123/`
    - `https://www.instagram.com/reel/XYZ789/`
    - `https://instagram.com/p/DEF456/`

- **Código de Embed**: Deixe em branco (será extraído automaticamente)

- **URL da Thumbnail**: (Opcional) Cole a URL de uma imagem de preview
  - Se deixar em branco, aparecerá um ícone do Instagram

- **Duração**: (Opcional) Exemplo: `0:30` ou `1:15`

#### 🔗 Relacionamentos
- **Livro Relacionado**: (Opcional) Se o vídeo é sobre um livro específico
- **Autor Relacionado**: (Opcional) Se o vídeo é sobre um autor específico

#### ⚙️ Metadados
- **Visualizações**: Deixe em `0` ou adicione o número real
- **Data de Publicação**: (Opcional) Data do vídeo
- **Destacado**: ✅ Marque para dar destaque
- **Ativo**: ✅ Deixe marcado para publicar

### 2.3 Salvar o Vídeo
1. Clique em **"Salvar"** (canto inferior direito)
2. Verifique a mensagem de sucesso: "O vídeo ... foi adicionado com sucesso"

### 2.4 Adicionar Mais Vídeos
Repita os passos 2.1 a 2.3 para cada vídeo que quiser adicionar. **Recomendado: 4 a 8 vídeos** para uma boa seção.

---

## 🏠 Passo 3: Criar Seção na Home

### 3.1 Navegar até Seções
1. No painel admin, procure **"CORE"**
2. Clique em **"Seções"** (não confunda com "Vídeos")
3. Clique em **"Adicionar Seção"**

### 3.2 Configurar a Seção

#### 📝 Informações Básicas
- **Título**: Nome que aparecerá na home
  - ✨ Exemplo: `Nossos Vídeos no Instagram`
  - ✨ Exemplo: `Propaganda da Semana`
  - ✨ Exemplo: `Conteúdo Exclusivo Instagram`

- **Subtítulo**: (Opcional) Descrição complementar
  - Exemplo: `Confira nossos vídeos promocionais e fique por dentro das novidades`

- **Tipo de Conteúdo**: Selecione **"Vídeos"** ⭐ (IMPORTANTE!)

- **Layout**: Selecione **"Carrossel"**
  - Outras opções: Grid

#### 🎨 Estilo e Aparência
- **Classe CSS**: Deixe em branco (usará o padrão)

- **Cor de Fundo**: (Opcional) Exemplo: `#f8f9fa` para cinza claro

- **Número de Itens**: Digite quantos vídeos quer mostrar
  - Exemplo: `6` (mostrará os 6 vídeos que você adicionar na seção)

#### 🔗 Link "Ver Todos"
- **Mostrar "Ver Todos"**: ✅ Marque esta opção

- **URL do "Ver Todos"**: Digite `/videos/instagram/`
  - Isso levará para a página com todos os vídeos do Instagram

#### 📍 Ordenação
- **Ordem**: Número que define a posição na home
  - `10` = aparece primeiro
  - `20` = aparece depois
  - `30` = aparece depois ainda
  - **Recomendado**: Use `25` para aparecer entre outras seções

#### ✅ Status
- **Ativa**: ✅ Deixe marcado para publicar na home

### 3.3 Salvar a Seção
1. Clique em **"Salvar e continuar editando"** (canto inferior direito)
2. Verifique a mensagem de sucesso
3. **Importante**: Anote o ID da seção (aparece na URL, exemplo: `/admin/core/section/5/change/` → ID é **5**)

---

## ➕ Passo 4: Adicionar Vídeos à Seção

### 4.1 Navegar até Itens da Seção
1. Ainda na página de edição da seção, role para baixo
2. Procure a área **"ITENS DA SEÇÃO"** (geralmente no final da página)
3. Ou volte para o painel admin → **"CORE"** → **"Itens de seção"**

### 4.2 Adicionar Primeiro Vídeo
1. Clique em **"Adicionar Item de Seção"**
2. Preencha:
   - **Seção**: Selecione a seção que você criou (ex: "Nossos Vídeos no Instagram")
   - **Tipo de Conteúdo**: Selecione **"video"**
   - **ID do Objeto**: Digite o ID do vídeo que você quer adicionar
     - Para encontrar o ID:
       - Vá em CORE → Vídeos
       - Clique no vídeo
       - Olhe a URL: `/admin/core/video/3/change/` → ID é **3**
   - **Ordem**: `1` (primeiro vídeo)
   - **Título Personalizado**: (Opcional) Deixe em branco para usar o título do vídeo
3. Clique em **"Salvar e adicionar outro"**

### 4.3 Adicionar Mais Vídeos
Repita o passo 4.2 para cada vídeo, mudando:
- **ID do Objeto**: ID do próximo vídeo
- **Ordem**: `2`, `3`, `4`, etc. (na sequência que quer que apareçam)

### 4.4 Exemplo Prático

**Exemplo: Adicionar 4 vídeos à seção**

| Ordem | Tipo de Conteúdo | ID do Objeto | Vídeo                          |
|-------|------------------|--------------|--------------------------------|
| 1     | video            | 15           | Promoção Black Friday          |
| 2     | video            | 16           | Lançamentos de Dezembro        |
| 3     | video            | 17           | Depoimento Cliente             |
| 4     | video            | 18           | Tour pela Loja                 |

---

## 👀 Passo 5: Visualizar na Home

### 5.1 Abrir a Página Inicial
1. Abra uma nova aba
2. Acesse: `https://seu-site.com/`
3. Role a página para baixo

### 5.2 Localizar a Seção
- Procure pela seção com o título que você definiu
- Exemplo: **"Nossos Vídeos no Instagram"**
- Deve aparecer com ícone de vídeo vermelho 🎬

### 5.3 Verificar os Vídeos
✅ Você deve ver:
- Carrossel com os vídeos do Instagram
- Thumbnails (ou ícone do Instagram se não tiver thumbnail)
- Botão de play sobre cada vídeo
- Botão "Ver todos" no canto superior direito

### 5.4 Testar Funcionalidade
1. Clique em um vídeo → Deve abrir o Instagram em nova aba
2. Clique em "Ver todos" → Deve ir para `/videos/instagram/`
3. Navegue pelo carrossel usando as setas → Deve mostrar todos os vídeos

---

## 💡 Dicas e Troubleshooting

### ✅ Dicas de Uso

#### 🎨 Personalização
- Use thumbnails customizadas para melhor aparência visual
- Mantenha títulos curtos (máx. 50 caracteres) para ficarem bonitos nos cards
- Adicione 6-8 vídeos para um carrossel dinâmico

#### 📱 Boas Práticas
- Marque como "Destacado" apenas os vídeos mais importantes
- Use descrições claras e objetivas
- Mantenha a duração atualizada para informar os usuários
- Publique vídeos regularmente para manter a seção atualizada

#### 🎯 SEO e Engajamento
- Use palavras-chave relevantes no título
- Adicione descrições completas (ajuda no SEO)
- Link vídeos a livros ou autores quando possível
- Monitore visualizações e atualize o campo "Visualizações"

---

### ❌ Troubleshooting (Resolução de Problemas)

#### Problema 1: Vídeo não aparece na seção
**Possíveis causas:**
- ✅ Verificar se o vídeo está marcado como "Ativo"
- ✅ Verificar se a seção está marcada como "Ativa"
- ✅ Verificar se o item da seção foi criado corretamente
- ✅ Verificar se a plataforma está como "Instagram"

**Solução:**
1. Vá em CORE → Vídeos
2. Clique no vídeo
3. Certifique-se que "Ativo" está marcado
4. Salve novamente

---

#### Problema 2: Thumbnail não aparece
**Possíveis causas:**
- Instagram não fornece thumbnail automática (diferente do YouTube)

**Solução:**
1. Faça screenshot do vídeo no Instagram
2. Hospede a imagem (pode usar imgur.com ou similar)
3. Cole a URL no campo "URL da Thumbnail"

**Alternativa:** Deixe em branco, aparecerá um ícone bonito do Instagram

---

#### Problema 3: Seção não aparece na home
**Possíveis causas:**
- ✅ Seção não está marcada como "Ativa"
- ✅ Seção não tem itens adicionados
- ✅ Ordem muito alta (aparece muito abaixo)

**Solução:**
1. Vá em CORE → Seções
2. Clique na seção
3. Certifique-se:
   - "Ativa" está marcado ✅
   - "Ordem" é um número razoável (15-30)
   - Há itens adicionados na seção
4. Salve e recarregue a home

---

#### Problema 4: Link "Ver todos" não funciona
**Possíveis causas:**
- URL incorreta no campo "URL do Ver Todos"

**Solução:**
1. Vá em CORE → Seções
2. Clique na seção
3. No campo "URL do Ver Todos", digite exatamente: `/videos/instagram/`
4. Salve

---

#### Problema 5: Ordem dos vídeos está errada
**Solução:**
1. Vá em CORE → Itens de seção
2. Filtre pela sua seção
3. Edite cada item e ajuste o campo "Ordem":
   - 1 = primeiro
   - 2 = segundo
   - 3 = terceiro
   - etc.
4. Salve e recarregue a home

---

#### Problema 6: Código de embed não é extraído
**Possíveis causas:**
- URL do Instagram está incorreta ou incompleta

**Solução - URLs Corretas:**
```
✅ https://www.instagram.com/p/ABC123/
✅ https://www.instagram.com/reel/XYZ789/
✅ https://instagram.com/p/DEF456/

❌ instagram.com/p/ABC123 (falta https://)
❌ www.instagram.com/p/ (falta o código)
```

---

### 📊 Exemplo Completo de Seção

**Configuração Final de Exemplo:**

```
SEÇÃO:
- Título: 🎬 Nossos Vídeos no Instagram
- Subtítulo: Confira nossas propagandas e conteúdos exclusivos
- Tipo: Vídeos
- Layout: Carrossel
- Número de Itens: 6
- Mostrar Ver Todos: ✅
- URL Ver Todos: /videos/instagram/
- Ordem: 20
- Ativa: ✅

VÍDEOS NA SEÇÃO:
1. Promoção Black Friday (Ordem: 1)
2. Lançamentos Dezembro (Ordem: 2)
3. Depoimento de Cliente (Ordem: 3)
4. Tour pela Loja Virtual (Ordem: 4)
5. Novo Sistema de Recomendação (Ordem: 5)
6. Parceria com Editoras (Ordem: 6)
```

---

## 🚀 Resultado Final

Ao seguir todos os passos, você terá:

✅ Seção de vídeos do Instagram na página inicial
✅ Carrossel interativo e responsivo
✅ Design com cores do Instagram (gradiente rosa/roxo/laranja)
✅ Link "Ver todos" levando para `/videos/instagram/`
✅ Vídeos clicáveis que abrem no Instagram
✅ Sistema totalmente gerenciável pelo admin

---

## 📞 Suporte

Se tiver problemas:
1. Verifique todos os passos deste guia
2. Consulte a seção de Troubleshooting
3. Verifique os logs do Render para erros
4. Teste em modo anônimo (Ctrl+Shift+N) para descartar cache

---

**Última atualização:** Novembro 2024
**Versão:** 1.0
