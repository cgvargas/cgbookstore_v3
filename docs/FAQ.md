# ❓ FAQ - CGBookStore - Perguntas Frequentes

**Última atualização:** 24 de Maio de 2026
**Versão do Sistema:** 3.0

---

## 📋 Índice

### 🚀 [Começando](#começando)
1. [O que é o CGBookStore?](#1-o-que-é-o-cgbookstore)
2. [Como faço o setup inicial?](#2-como-faço-o-setup-inicial)
3. [Quais são os requisitos do sistema?](#3-quais-são-os-requisitos-do-sistema)
4. [Como configurar em um segundo computador?](#4-como-configurar-em-um-segundo-computador)

### 🤖 [Chatbot Literário](#chatbot-literário)
5. [Como funciona o Chatbot Literário?](#5-como-funciona-o-chatbot-literário)
6. [O que é RAG?](#6-o-que-é-rag)
7. [O que é a Knowledge Base?](#7-o-que-é-a-knowledge-base)
8. [Como corrigir respostas erradas do chatbot?](#8-como-corrigir-respostas-erradas-do-chatbot)
9. [Como o chatbot aprende com as correções?](#9-como-o-chatbot-aprende-com-as-correções)
10. [Como configurar a API Groq?](#10-como-configurar-a-api-groq)

### 📚 [Livros e Catálogo](#livros-e-catálogo)
11. [Como adicionar um novo livro?](#11-como-adicionar-um-novo-livro)
12. [Como a integração com Google Books funciona?](#12-como-a-integração-com-google-books-funciona)
13. [Como categorizar livros?](#13-como-categorizar-livros)
14. [Como fazer upload de capas de livros?](#14-como-fazer-upload-de-capas-de-livros)

### 👥 [Usuários e Autenticação](#usuários-e-autenticação)
15. [Como criar um superusuário?](#15-como-criar-um-superusuário)
16. [Como configurar login social (Google/Facebook)?](#16-como-configurar-login-social-googlefacebook)
17. [O que fazer quando há perfis de usuário duplicados?](#17-o-que-fazer-quando-há-perfis-de-usuário-duplicados)

### 💰 [Sistema Financeiro](#sistema-financeiro)
18. [Como funcionam as assinaturas Premium?](#18-como-funcionam-as-assinaturas-premium)
19. [Como criar campanhas de acesso gratuito?](#19-como-criar-campanhas-de-acesso-gratuito)
20. [Como configurar o MercadoPago?](#20-como-configurar-o-mercadopago)

### 🌐 [Deploy e Produção](#deploy-e-produção)
21. [Como fazer deploy no Render.com?](#21-como-fazer-deploy-no-rendercom)
22. [Como otimizar performance no plano Free do Render?](#22-como-otimizar-performance-no-plano-free-do-render)
23. [Como configurar variáveis de ambiente?](#23-como-configurar-variáveis-de-ambiente)
24. [Como acessar o shell no Render Free?](#24-como-acessar-o-shell-no-render-free)

### 🔧 [Manutenção e Troubleshooting](#manutenção-e-troubleshooting)
25. [Como limpar o cache do sistema?](#25-como-limpar-o-cache-do-sistema)
26. [O que fazer quando o site está lento?](#26-o-que-fazer-quando-o-site-está-lento)
27. [Erro 404 ao clicar em "Ver Detalhes" de um livro](#27-erro-404-ao-clicar-em-ver-detalhes-de-um-livro)
28. [Como fazer backup do banco de dados?](#28-como-fazer-backup-do-banco-de-dados)
29. [Como verificar logs de erro?](#29-como-verificar-logs-de-erro)

### 📊 [Dashboard e Administração](#dashboard-e-administração)
30. [Como acessar a dashboard administrativa?](#30-como-acessar-a-dashboard-administrativa)
31. [O que cada card da dashboard mostra?](#31-o-que-cada-card-da-dashboard-mostra)
32. [Como monitorar o chatbot via dashboard?](#32-como-monitorar-o-chatbot-via-dashboard)

### 🧪 [Desenvolvimento e Testes](#desenvolvimento-e-testes)
33. [Como executar os testes?](#33-como-executar-os-testes)
34. [Como testar o sistema RAG?](#34-como-testar-o-sistema-rag)
35. [Como debugar problemas no chatbot?](#35-como-debugar-problemas-no-chatbot)

### 📧 [Email e Notificações](#email-e-notificações)
36. [Como configurar envio de emails?](#36-como-configurar-envio-de-emails)
37. [Como usar SendGrid?](#37-como-usar-sendgrid)

### 💬 [Debates Literários](#debates-literários)
40. [O que são os Debates Literários?](#40-o-que-são-os-debates-literários)
41. [Como criar um tópico de debate?](#41-como-criar-um-tópico-de-debate)
42. [Como participar de um debate (responder)?](#42-como-participar-de-um-debate-responder)
43. [Como funciona o sistema de votos?](#43-como-funciona-o-sistema-de-votos)
44. [Como editar ou deletar meu post/tópico?](#44-como-editar-ou-deletar-meu-posttópico)
45. [Quais são as limitações por plano (Free vs Premium)?](#45-quais-são-as-limitações-por-plano-free-vs-premium)
46. [Como administrar debates pelo painel Admin?](#46-como-administrar-debates-pelo-painel-admin)

### 📖 [Documentação](#documentação)
38. [Onde encontro a documentação completa?](#38-onde-encontro-a-documentação-completa)
39. [Como está organizada a estrutura do projeto?](#39-como-está-organizada-a-estrutura-do-projeto)

---

## 🚀 Começando

### 1. O que é o CGBookStore?

**R:** CGBookStore é uma **plataforma completa de livraria virtual** com recursos avançados de IA, incluindo:

- 📚 **Catálogo de Livros** com integração Google Books API
- 🤖 **Chatbot Literário** com IA (Groq/LLaMA 3.1 70B)
- 🎯 **Sistema RAG** (Retrieval-Augmented Generation)
- 🧠 **Knowledge Base** com aprendizado contínuo
- 💡 **Recomendações Inteligentes** por IA
- 💰 **Módulo Financeiro** com MercadoPago
- 👥 **Autenticação Social** (Google/Facebook)
- ✨ **Autores Emergentes** - Plataforma para novos escritores
- 💬 **Debates Literários** - Comunidade de leitores

**Stack Tecnológica:**
- Django 5.1.1
- PostgreSQL
- Redis
- Groq API (IA)
- Google Books API

---

### 2. Como faço o setup inicial?

**R:** Siga estes passos:

```bash
# 1. Clone o repositório
git clone <repository-url>
cd cgbookstore_v3

# 2. Crie ambiente virtual
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. Instale dependências
pip install -r requirements.txt

# 4. Configure variáveis de ambiente
cp .env.example .env
# Edite .env com suas credenciais

# 5. Execute migrações
python manage.py migrate

# 6. Crie superusuário
python manage.py createsuperuser

# 7. Inicie o servidor
python manage.py runserver
```

**Acesse:**
- Site: http://localhost:8000/
- Admin: http://localhost:8000/admin/
- Dashboard: http://localhost:8000/admin/dashboard/

📖 **Documentação completa:** [docs/GUIA_CONFIGURACAO_LOCAL.md](docs/GUIA_CONFIGURACAO_LOCAL.md)

---

### 3. Quais são os requisitos do sistema?

**R:** Requisitos mínimos:

**Software:**
- Python 3.11 ou superior
- PostgreSQL 13+
- Redis (opcional, para cache)
- Git

**APIs Externas (opcionais):**
- Groq API Key (para chatbot IA)
- Google Books API Key
- MercadoPago Access Token (para pagamentos)
- SendGrid API Key (para emails)
- Google/Facebook OAuth (para login social)

**Hardware (desenvolvimento):**
- RAM: 4GB mínimo (8GB recomendado)
- Espaço: 2GB
- Processador: Dual-core

**Produção (Render Free):**
- Funciona perfeitamente no plano gratuito
- Database: Supabase Free Tier
- Storage: Pode usar Supabase Storage

---

### 4. Como configurar em um segundo computador?

**R:** Processo simplificado:

```bash
# 1. Clone o repo
git clone <repository-url>
cd cgbookstore_v3

# 2. Ambiente virtual e dependências
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 3. Copie o .env do primeiro computador
# OU configure novo .env a partir do .env.example

# 4. Migrações e servidor
python manage.py migrate
python manage.py runserver
```

**Importante:**
- ✅ Use o mesmo `.env` (mesmas credenciais de banco)
- ✅ Não precisa criar superusuário novamente
- ✅ Banco de dados já está populado

📖 **Documentação completa:** [docs/setup/SETUP_SEGUNDO_COMPUTADOR.md](docs/setup/SETUP_SEGUNDO_COMPUTADOR.md)

---

## 🤖 Chatbot Literário

### 5. Como funciona o Chatbot Literário?

**R:** O chatbot usa uma arquitetura em **3 camadas** para garantir respostas precisas:

```
┌─────────────────────────────────────────────────┐
│  1. KNOWLEDGE BASE (Prioridade Máxima)         │
│     ↓ Se não encontrar...                       │
│  2. RAG - Consulta Banco de Dados               │
│     ↓ Se não encontrar...                       │
│  3. IA (Groq LLaMA 3.1 70B)                     │
└─────────────────────────────────────────────────┘
```

**Fluxo completo:**

1. **Usuário faz pergunta** sobre livros/autores
2. **Knowledge Base verifica** se existe correção prévia
3. **RAG detecta intenção** e busca dados no banco
4. **IA processa** com contexto enriquecido
5. **Resposta entregue** ao usuário
6. **Admin pode corrigir** se necessário
7. **Correção armazenada** para futuro uso

**Vantagens:**
- ✅ Respostas baseadas em dados reais
- ✅ Não alucina informações
- ✅ Aprende com correções
- ✅ Melhora continuamente

---

### 6. O que é RAG?

**R:** **RAG** significa **Retrieval-Augmented Generation** (Geração Aumentada por Recuperação).

**Como funciona:**

```python
# Antes (IA pura - pode alucinar)
IA: "Quem escreveu Quarta Asa?"
Resposta: [IA inventa baseado no que 'acha']

# Com RAG (IA + Database)
1. Detecta intenção: "author_query"
2. Busca no banco: SELECT author FROM books WHERE title='Quarta Asa'
3. Encontra: "Brandon Sanderson"
4. IA usa dado real: "Quarta Asa foi escrito por Brandon Sanderson"
```

**Benefícios:**
- ✅ **100% de precisão** em dados existentes no banco
- ✅ **Zero alucinações** sobre livros cadastrados
- ✅ **Respostas verificáveis**
- ✅ **Performance otimizada** (~50ms overhead)

**Intents Detectados:**
- `author_query` - Perguntas sobre autores
- `book_info` - Informações sobre livros
- `recommendation` - Pedidos de recomendação
- `series_info` - Informações sobre séries
- `category_search` - Busca por categoria

📖 **Documentação completa:** [docs/features/RAG_IMPLEMENTATION.md](docs/features/RAG_IMPLEMENTATION.md)

---

### 7. O que é a Knowledge Base?

**R:** A **Knowledge Base** é um sistema de **aprendizado contínuo** que permite ao chatbot aprender com seus erros.

**Como funciona:**

```
1. Chatbot dá resposta errada
   ↓
2. Admin acessa Django Admin
   ↓
3. Admin corrige a resposta
   ↓
4. Sistema cria entrada em ChatbotKnowledge
   ↓
5. Extrai keywords automaticamente
   ↓
6. Próxima pergunta similar → Usa correção
```

**Exemplo prático:**

```
❌ Erro original:
User: "Quem escreveu Quarta Asa?"
Bot: "Não sei informar"

✅ Admin corrige:
Original: "Não sei informar"
Correção: "Quarta Asa foi escrito por Brandon Sanderson"

✅ Próxima vez:
User: "Quem é o autor de Quarta Asa?"
Bot: [Usa correção] "Quarta Asa foi escrito por Brandon Sanderson"
```

**Busca Inteligente (3 estratégias):**
1. **Match exato** - Pergunta idêntica
2. **Fuzzy match** - Similaridade de keywords (Jaccard)
3. **Substring match** - Parte da pergunta

**Estatísticas:**
- Rastreamento de uso (quantas vezes foi usado)
- Confidence score (0.0 a 1.0)
- Data de última utilização
- Admin que criou a correção

📖 **Documentação completa:** [docs/features/KNOWLEDGE_BASE_SYSTEM.md](docs/features/KNOWLEDGE_BASE_SYSTEM.md)

---

### 8. Como corrigir respostas erradas do chatbot?

**R:** Via Django Admin (interface visual):

**Passo a Passo:**

1. **Acesse o Admin:**
   - URL: `/admin/`
   - Login com superusuário

2. **Navegue até Chatbot Literário:**
   - Clique em "Chat messages" ou "Mensagens de chat"

3. **Encontre a conversa:**
   - Use filtros ou busca
   - Identifique a mensagem errada (role=assistant)

4. **Edite a mensagem:**
   - Clique na mensagem
   - Marque "Has correction" (Tem correção)
   - Preencha "Corrected content" com resposta correta
   - Salve

5. **Crie Knowledge Base (opcional mas recomendado):**
   - Selecione a mensagem corrigida
   - Action: "Create knowledge from correction"
   - Execute

**Pronto!** A correção será usada automaticamente em perguntas similares futuras.

**Atalho via Dashboard:**
- `/admin/dashboard/` → Card "Chatbot Literário" → "Ver todas conversas"

---

### 9. Como o chatbot aprende com as correções?

**R:** O sistema usa **Jaccard Similarity** para detectar perguntas similares.

**Algoritmo:**

```python
# Extração de keywords
def extract_keywords(question):
    # Remove stop words (o, a, de, para, etc.)
    # Mantém apenas palavras significativas
    # Exemplo: "Quem escreveu Quarta Asa?" → ['quem', 'escreveu', 'quarta', 'asa']
    return keywords

# Cálculo de similaridade
def jaccard_similarity(set1, set2):
    intersection = len(set1 & set2)  # Palavras em comum
    union = len(set1 | set2)         # Total de palavras únicas
    return intersection / union       # Score de 0.0 a 1.0

# Exemplo:
Q1: "Quem escreveu Quarta Asa?"
    Keywords: {quem, escreveu, quarta, asa}

Q2: "Quem é o autor de Quarta Asa?"
    Keywords: {quem, autor, quarta, asa}

Intersection: {quem, quarta, asa} = 3
Union: {quem, escreveu, autor, quarta, asa} = 5
Similarity: 3/5 = 0.6 (60%)

✅ Se > 50% → Usa a mesma correção
```

**Threshold:** 50% de similaridade (configurável)

---

### 10. Como configurar a API Groq?

**R:** A API Groq é gratuita e fácil de configurar:

**1. Obter API Key:**
```
1. Acesse: https://console.groq.com/
2. Crie uma conta (gratuita)
3. Vá em "API Keys"
4. Clique em "Create API Key"
5. Copie a key gerada
```

**2. Configure no .env:**
```env
GROQ_API_KEY=gsk_sua_chave_aqui
```

**3. Teste:**
```bash
python scripts/testing/test_chatbot_fix.py
```

**Modelos disponíveis:**
- `llama-3.1-70b-versatile` (padrão - melhor custo/benefício)
- `llama-3.1-8b-instant` (mais rápido)
- `mixtral-8x7b-32768` (alternativa)

**Limites do plano gratuito:**
- 30 requisições/minuto
- 14.400 tokens/minuto
- Suficiente para uso normal

📖 **Documentação completa:** [docs/setup/GROQ_SETUP.md](docs/setup/GROQ_SETUP.md)

---

## 📚 Livros e Catálogo

### 11. Como adicionar um novo livro?

**R:** Duas formas: **Manual** ou **via Google Books API**

**Forma 1: Manual (Django Admin)**

```
1. Acesse /admin/
2. Core → Books → Add Book
3. Preencha:
   - Title (obrigatório)
   - Author (selecione ou crie)
   - Category (selecione)
   - Description
   - ISBN (opcional)
   - Cover image (upload opcional)
4. Salve
```

**Forma 2: Google Books API (automático)**

```python
# No admin, ao criar livro:
1. Preencha apenas o ISBN
2. Sistema busca automaticamente:
   - Título
   - Autor
   - Descrição
   - Capa
   - Editora
   - Ano de publicação
3. Revise e salve
```

**Bulk Import:**
```bash
# Via comando Django (se implementado)
python manage.py import_books books.csv
```

---

### 12. Como a integração com Google Books funciona?

**R:** Integração automática via API:

**Configuração:**
```env
# No .env (opcional - funciona sem key também)
GOOGLE_BOOKS_API_KEY=sua_chave_aqui
```

**Funcionalidades:**

1. **Busca por ISBN:**
   ```python
   GET https://www.googleapis.com/books/v1/volumes?q=isbn:9788576573443
   ```

2. **Dados extraídos:**
   - Título
   - Autor(es)
   - Descrição
   - Capa (thumbnail e alta resolução)
   - Editora
   - Data de publicação
   - Número de páginas
   - Categorias

3. **Fallback:**
   - Se API falhar → Usa placeholder
   - Capa padrão se não houver imagem

**Obter API Key (gratuito):**
```
1. https://console.cloud.google.com/
2. Create Project
3. Enable "Google Books API"
4. Create Credentials → API Key
```

**Limites:** 1.000 requisições/dia (plano gratuito)

---

### 13. Como categorizar livros?

**R:** Sistema de categorias pré-definidas:

**Categorias Padrão (20):**
- Ficção
- Romance
- Suspense/Thriller
- Fantasia
- Ficção Científica
- Terror
- Mistério/Policial
- Aventura
- Não-ficção
- Biografia
- História
- Autoajuda
- Negócios
- Ciência
- Tecnologia
- Artes
- Poesia
- Infantil
- Jovem Adulto
- Clássicos

**Gerenciar categorias:**
```
1. Admin → Core → Categories
2. Add/Edit/Delete conforme necessário
3. Cada categoria tem:
   - Name (nome)
   - Slug (URL-friendly)
   - Description (opcional)
```

**Múltiplas categorias por livro:**
- Não suportado nativamente (ForeignKey único)
- Solução: Use tag system ou ManyToManyField customizado

---

### 14. Como fazer upload de capas de livros?

**R:** Três opções disponíveis:

**Opção 1: Upload Manual (Admin)**
```
1. Admin → Books → Edit book
2. Campo "Cover image"
3. Choose file → Upload
4. Save
```

**Opção 2: Google Books API (Automático)**
```
- Sistema baixa automaticamente ao cadastrar ISBN
- Prioriza alta resolução quando disponível
```

**Opção 3: Supabase Storage (Produção)**
```env
# Configure no .env
USE_SUPABASE_STORAGE=true
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_ANON_KEY=sua_key
SUPABASE_SERVICE_KEY=sua_service_key
```

**Formatos suportados:**
- JPG/JPEG
- PNG
- GIF
- WebP

**Limites:**
- Tamanho máximo: 5MB por imagem
- Resolução recomendada: 600x900px

**Armazenamento:**
- Local: `media/books/covers/`
- Supabase: Bucket `book-covers`

---

## 👥 Usuários e Autenticação

### 15. Como criar um superusuário?

**R:** Depende do ambiente:

**Desenvolvimento Local:**
```bash
python manage.py createsuperuser
# Preencha: username, email, password
```

**Produção (Render Free - via variáveis de ambiente):**
```env
# No dashboard Render, em Environment:
CREATE_SUPERUSER=true
SUPERUSER_USERNAME=admin
SUPERUSER_EMAIL=seu@email.com
SUPERUSER_PASSWORD=SuaSenhaSegura123
```

Depois: **Manual Deploy → Deploy latest commit**

**Produção (Render Free - via Web Tools):**
```
1. Acesse: https://seu-app.onrender.com/admin-tools/setup/
2. Faça login como superusuário existente
3. Use formulário para criar novo admin
```

**IMPORTANTE:**
- ⚠️ Remova `CREATE_SUPERUSER=true` após criação
- 🔒 Use senhas fortes em produção
- 📧 Use email válido para recuperação

---

### 16. Como configurar login social (Google/Facebook)?

**R:** Via Django-Allauth:

**1. Obter Credenciais:**

**Google:**
```
1. https://console.cloud.google.com/
2. Create Project
3. APIs & Services → Credentials
4. Create OAuth 2.0 Client ID
5. Authorized redirect URIs:
   - http://localhost:8000/accounts/google/login/callback/
   - https://seu-dominio.com/accounts/google/login/callback/
6. Copie Client ID e Client Secret
```

**Facebook:**
```
1. https://developers.facebook.com/
2. Create App
3. Add Facebook Login
4. Settings → Basic
5. Valid OAuth Redirect URIs:
   - http://localhost:8000/accounts/facebook/login/callback/
   - https://seu-dominio.com/accounts/facebook/login/callback/
6. Copie App ID e App Secret
```

**2. Configure no .env:**
```env
GOOGLE_CLIENT_ID=seu_client_id
GOOGLE_CLIENT_SECRET=seu_secret

FACEBOOK_APP_ID=seu_app_id
FACEBOOK_APP_SECRET=seu_secret
```

**3. Configure no Admin:**
```
1. Admin → Sites → django.contrib.sites
2. Certifique-se que Domain está correto

3. Admin → Social applications → Add
4. Provider: Google (ou Facebook)
5. Name: Google Login
6. Client id: [cole do .env]
7. Secret key: [cole do .env]
8. Sites: Selecione seu site
9. Save
```

**4. Teste:**
```
1. Logout do admin
2. Acesse /accounts/login/
3. Clique em "Login with Google"
4. Autorize
5. ✅ Deve criar usuário automaticamente
```

📖 **Documentação:** Procure por `CONFIGURAR_LOGIN_SOCIAL.md` em docs/

---

### 17. O que fazer quando há perfis de usuário duplicados?

**R:** Execute o script de correção:

**Diagnóstico:**
```bash
python scripts/maintenance/database/verify_userprofiles.py
```

**Output esperado:**
```
✅ Usuários sem perfil: 0
✅ Usuários com múltiplos perfis: 0
✅ Sistema OK
```

**Se houver duplicados:**
```bash
python scripts/maintenance/database/fix_userprofile_duplicate.py
```

**O script faz:**
1. Identifica usuários com múltiplos perfis
2. Mantém o perfil mais recente
3. Remove duplicados
4. Gera relatório

**Prevenção:**
```python
# O sistema usa signals para prevenir duplicação:
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)
```

📖 **Documentação:** [docs/USERPROFILE_DUPLICATE_FIX.md](docs/USERPROFILE_DUPLICATE_FIX.md)

---

## 💰 Sistema Financeiro

### 18. Como funcionam as assinaturas Premium?

**R:** Sistema completo de assinaturas com MercadoPago:

**Tipos de Assinatura:**
```python
PLANOS = {
    'mensal': {
        'price': 19.90,
        'duration_days': 30,
        'features': ['Acesso ilimitado', 'Sem anúncios', 'Download de livros']
    },
    'trimestral': {
        'price': 49.90,
        'duration_days': 90,
        'features': [...]
    },
    'anual': {
        'price': 149.90,
        'duration_days': 365,
        'features': [...]
    }
}
```

**Fluxo de Compra:**
```
1. Usuário escolhe plano
   ↓
2. Redirect para MercadoPago
   ↓
3. Usuário paga
   ↓
4. Webhook recebe confirmação
   ↓
5. Sistema ativa Premium
   ↓
6. Email de confirmação enviado
```

**Gerenciar Assinaturas (Admin):**
```
1. Admin → Finance → Subscriptions
2. Lista todas assinaturas
3. Status: ativa | expirada | cancelada
4. Ações:
   - Ativar/Desativar manualmente
   - Estender prazo
   - Cancelar
   - Ver histórico de pagamentos
```

**Monitoramento:**
- Dashboard mostra assinaturas ativas
- Notificações de expiração (7 dias antes)
- Renovação automática (se configurado)

---

### 19. Como criar campanhas de acesso gratuito?

**R:** Via Admin:

**Criar Campanha:**
```
1. Admin → Finance → Campaigns → Add Campaign
2. Preencha:
   - Name: "Promo Natal 2025"
   - Duration days: 30
   - Start date: 2025-12-01
   - End date: 2025-12-31
   - Target type: all_users | new_users | specific_users
   - Is active: ✓
3. Save
```

**Tipos de Campanha:**

- **all_users**: Todos os usuários existentes
- **new_users**: Apenas usuários que se cadastrarem durante a campanha
- **specific_users**: Lista específica de emails

**Aplicar Campanha:**
```
1. Selecione campanha
2. Action: "Grant access to users"
3. Execute
```

**Sistema cria automaticamente:**
- `CampaignGrant` para cada usuário
- Premium ativo por X dias
- Notificação por email
- Registro de auditoria

**Dashboard:**
- Card mostra campanhas ativas
- Total de premiums concedidos
- Taxa de conversão

---

### 20. Como configurar o MercadoPago?

**R:** Obtenha credenciais:

**1. Criar Conta:**
```
1. https://www.mercadopago.com.br/developers
2. Crie aplicação
3. Credentials → Production/Test
4. Copie Access Token
```

**2. Configure no .env:**
```env
# Teste
MERCADOPAGO_ACCESS_TOKEN=TEST-xxxxx
MERCADOPAGO_PUBLIC_KEY=TEST-xxxxx

# Produção
MERCADOPAGO_ACCESS_TOKEN=APP-xxxxx
MERCADOPAGO_PUBLIC_KEY=APP-xxxxx
```

**3. Configure Webhooks:**
```
1. MercadoPago Dashboard
2. Webhooks → Add
3. URL: https://seu-dominio.com/finance/webhook/mercadopago/
4. Events: payment.created, payment.updated
```

**4. Teste:**
```bash
python scripts/testing/test_mercadopago_credentials.py
```

**Cartões de Teste:**
```
Aprovado: 5031 4332 1540 6351
Rejeitado: 5031 4332 1540 6351
CVV: 123
Validade: 11/25
```

---

## 🌐 Deploy e Produção

### 21. Como fazer deploy no Render.com?

**R:** Deploy automático via `render.yaml`:

**1. Criar conta:**
```
1. https://render.com/
2. Sign up (gratuito)
3. Connect GitHub
```

**2. Novo Web Service:**
```
1. New → Web Service
2. Connect repository
3. Render detecta render.yaml automaticamente
4. Build command: bash config/deployment/build.sh
5. Start command: gunicorn cgbookstore.wsgi:application --config config/deployment/gunicorn_config.py
```

**3. Configurar Database:**
```
1. New → PostgreSQL
2. Name: cgbookstore-db
3. Plan: Free
4. Create
5. Copie External Database URL
```

**4. Variáveis de Ambiente:**
```
Environment:
  DATABASE_URL: [cole URL do Postgres]
  SECRET_KEY: [gere: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"]
  DEBUG: False
  ALLOWED_HOSTS: seu-app.onrender.com
  CSRF_TRUSTED_ORIGINS: https://seu-app.onrender.com

  # Opcionais:
  GROQ_API_KEY: [sua key]
  GOOGLE_BOOKS_API_KEY: [sua key]
  MERCADOPAGO_ACCESS_TOKEN: [sua key]
```

**5. Deploy:**
```
- Manual Deploy → Deploy latest commit
- Aguarde ~5-10 minutos
- ✅ App disponível em: https://seu-app.onrender.com
```

**Render.yaml já configura:**
- ✅ Build automático
- ✅ Collectstatic
- ✅ Migrações
- ✅ Gunicorn workers
- ✅ Health checks

📖 **Documentação:** [docs/deployment/RENDER_PERFORMANCE_FIXES.md](docs/deployment/RENDER_PERFORMANCE_FIXES.md)

---

### 22. Como otimizar performance no plano Free do Render?

**R:** Otimizações implementadas:

**1. Database Connection Pooling:**
```python
# cgbookstore/settings.py
DATABASES = {
    'default': {
        'CONN_MAX_AGE': 600,  # 10 minutos
        'OPTIONS': {
            'pool': True,
            'pool_size': 10,
        }
    }
}
```

**2. Cache (Redis):**
```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.getenv('REDIS_URL'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

**3. Static Files (Whitenoise):**
```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # ← Serve estáticos
    ...
]
```

**4. Query Optimization:**
```python
# Use select_related para ForeignKey
books = Book.objects.select_related('author', 'category').all()

# Use prefetch_related para ManyToMany
users = User.objects.prefetch_related('reading_lists').all()
```

**5. Pagination:**
```python
# Sempre pagine listas grandes
paginator = Paginator(books, 20)  # 20 por página
```

**Resultado:**
- ⚡ Tempo de resposta: ~200ms (média)
- 💾 Uso de RAM: ~500MB
- 🔋 Spin-down: ~15min de inatividade (plano free)

📖 **Documentação:** [docs/deployment/RENDER_PERFORMANCE_FIXES.md](docs/deployment/RENDER_PERFORMANCE_FIXES.md)

---

### 23. Como configurar variáveis de ambiente?

**R:** Variáveis obrigatórias e opcionais:

**Arquivo .env (desenvolvimento):**
```env
# ===== OBRIGATÓRIAS =====
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=postgresql://user:password@localhost:5432/cgbookstore
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost:8000

# ===== OPCIONAIS (APIs) =====
# Chatbot IA
GROQ_API_KEY=gsk_xxxxx

# Google Books
GOOGLE_BOOKS_API_KEY=AIzaSyxxxxx

# MercadoPago
MERCADOPAGO_ACCESS_TOKEN=APP-xxxxx
MERCADOPAGO_PUBLIC_KEY=APP-xxxxx

# SendGrid (Email)
SENDGRID_API_KEY=SG.xxxxx
DEFAULT_FROM_EMAIL=noreply@cgbookstore.com

# OAuth Social
GOOGLE_CLIENT_ID=xxxxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=xxxxx
FACEBOOK_APP_ID=xxxxx
FACEBOOK_APP_SECRET=xxxxx

# Redis (Cache)
REDIS_URL=redis://localhost:6379/0

# Supabase Storage
USE_SUPABASE_STORAGE=true
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_ANON_KEY=eyJxxxxx
SUPABASE_SERVICE_KEY=eyJxxxxx
```

**Produção (Render):**
- Mesmas variáveis
- DEBUG=False
- ALLOWED_HOSTS=seu-app.onrender.com
- CSRF_TRUSTED_ORIGINS=https://seu-app.onrender.com

📖 **Template completo:** [.env.example](.env.example)

---

### 24. Como acessar o shell no Render Free?

**R:** Plano Free não tem shell, mas temos alternativas:

**Opção 1: Web Tools (Admin)**
```
URL: /admin-tools/health/
Funcionalidades:
- Health check completo
- Status do banco de dados
- Configurações do site
- Dados cadastrados
```

```
URL: /admin-tools/setup/
Funcionalidades:
- Popular banco automaticamente
- Criar categorias
- Criar livros de exemplo
- Configurar OAuth apps
```

**Opção 2: Django Admin**
```
- Todas as operações via interface visual
- CRUD completo de todos os models
- Actions customizadas
```

**Opção 3: Management Commands (deploy):**
```python
# Adicione em config/deployment/build.sh
python manage.py seu_comando
```

**Opção 4: Logs (diagnóstico):**
```
Render Dashboard → Logs
- Ver erros em tempo real
- Buscar por texto
- Download de logs
```

---

## 🔧 Manutenção e Troubleshooting

### 25. Como limpar o cache do sistema?

**R:** Três opções:

**Opção 1: Script de Manutenção**
```bash
python scripts/maintenance/clear_cache.py
```

**Opção 2: Cache da Home**
```bash
python scripts/maintenance/clear_home_cache.py
```

**Opção 3: Django Management**
```bash
# Limpar todo o cache
python manage.py clear_cache

# Limpar cache específico
from django.core.cache import cache
cache.delete('chave_especifica')
cache.clear()  # Limpa tudo
```

**Opção 4: Redis CLI (se usando Redis)**
```bash
redis-cli FLUSHDB
```

**Quando limpar cache:**
- ✅ Após atualizar dados importantes
- ✅ Após deploy
- ✅ Quando dados parecem desatualizados
- ✅ Problemas de performance inexplicáveis

📖 **Documentação:** [docs/troubleshooting/TROUBLESHOOTING_CACHE.md](docs/troubleshooting/TROUBLESHOOTING_CACHE.md)

---

### 26. O que fazer quando o site está lento?

**R:** Checklist de diagnóstico:

**1. Verificar Health:**
```
Acesse: /admin-tools/health/
Verifique:
- ✅ Database: OK
- ✅ Redis: OK
- ✅ Configurações: OK
```

**2. Verificar Queries N+1:**
```bash
# Ative query logging
DEBUG=True python manage.py runserver

# Ou use Django Debug Toolbar
pip install django-debug-toolbar
```

**3. Verificar Cache:**
```bash
# Limpe cache
python scripts/maintenance/clear_cache.py

# Verifique hit rate
python manage.py cache_stats
```

**4. Verificar Database:**
```sql
-- Queries lentas (PostgreSQL)
SELECT pid, now() - pg_stat_activity.query_start AS duration, query
FROM pg_stat_activity
WHERE state = 'active' AND now() - pg_stat_activity.query_start > interval '2 seconds';

-- Índices faltantes
SELECT schemaname, tablename, attname
FROM pg_stats
WHERE tablename NOT IN (SELECT tablename FROM pg_indexes);
```

**5. Profile de Performance:**
```bash
python scripts/maintenance/diagnose_performance.py
```

**Causas comuns:**
- ❌ Queries N+1
- ❌ Cache desativado
- ❌ Índices faltantes
- ❌ Muitas chamadas de API externa
- ❌ Render Free spin-down (~15min inatividade)

---

### 27. Erro 404 ao clicar em "Ver Detalhes" de um livro

**R:** Problema: URLs usando ID em vez de SLUG

**Causa:**
```javascript
// ❌ Errado (antigo)
url = '/livros/' + book.id + '/'  // /livros/69/

// ✅ Correto (atual)
url = '/livros/' + book.slug + '/'  // /livros/quarta-asa/
```

**Solução (já implementada):**

Commit: `fix: Corrigir URLs do modal de busca para usar slug em vez de ID`

**Se ainda ocorrer:**
```bash
# 1. Limpe cache
python scripts/maintenance/clear_cache.py

# 2. Verifique que livro tem slug
python manage.py shell
>>> from core.models import Book
>>> book = Book.objects.get(id=69)
>>> print(book.slug)  # Deve ter valor
>>> if not book.slug:
...     book.slug = slugify(book.title)
...     book.save()
```

**Prevenir:** Todos os livros devem ter slug gerado automaticamente

📖 **Documentação:** [docs/features/BUG_FIX_SUMMARY.md](docs/features/BUG_FIX_SUMMARY.md)

---

### 28. Como fazer backup do banco de dados?

**R:** Depende do database:

**PostgreSQL (Supabase/Render):**
```bash
# Backup
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql

# Com compressão
pg_dump $DATABASE_URL | gzip > backup_$(date +%Y%m%d).sql.gz

# Restore
psql $DATABASE_URL < backup.sql
```

**Django Fixtures:**
```bash
# Backup (JSON)
python manage.py dumpdata > backup.json

# Backup específico (apenas livros)
python manage.py dumpdata core.Book > books_backup.json

# Restore
python manage.py loaddata backup.json
```

**Automático (Supabase):**
- Dashboard → Database → Backups
- Backups diários automáticos (plano free)
- Point-in-time recovery (planos pagos)

**Armazenar backups:**
```bash
# Local
cp backup.sql backups/

# Cloud (via rclone ou aws cli)
aws s3 cp backup.sql s3://my-bucket/backups/
```

---

### 29. Como verificar logs de erro?

**R:** Múltiplas formas:

**Desenvolvimento (local):**
```bash
# Console do runserver mostra todos os erros
python manage.py runserver

# Arquivo de log (se configurado)
tail -f logs/django.log
```

**Produção (Render):**
```
1. Render Dashboard
2. Selecione seu Web Service
3. Logs tab
4. Filtros:
   - Error
   - Warning
   - Info
5. Search box para buscar texto específico
```

**Django Admin:**
```
- Admin → Admin Logs
- Mostra ações administrativas
- Filtra por usuário, tipo, data
```

**Sentry (opcional - monitoramento):**
```bash
pip install sentry-sdk
```

```python
# settings.py
import sentry_sdk
sentry_sdk.init(dsn="https://...@sentry.io/...")
```

**Tipos de log:**
```python
import logging
logger = logging.getLogger(__name__)

logger.debug("Debug info")
logger.info("Informação")
logger.warning("Aviso")
logger.error("Erro")
logger.critical("Erro crítico")
```

---

## 📊 Dashboard e Administração

### 30. Como acessar a dashboard administrativa?

**R:** Via URL ou Admin:

**Acesso Direto:**
```
URL: /admin/dashboard/
Requisito: Estar logado como superusuário
```

**Via Admin:**
```
1. /admin/
2. Header: "Dashboard CGBookStore"
3. Ou link "Voltar ao Site"
```

**O que a dashboard mostra:**
- 📚 Total de livros, autores, categorias
- 📅 Próximos eventos
- 💎 Assinaturas ativas (Finance)
- 🎁 Campanhas ativas
- ✨ Autores emergentes
- 🤖 Chatbot Literário (conversas e Knowledge Base)
- 📊 Gráficos: livros por categoria, eventos, capas

**Ações rápidas:**
- Adicionar livro, autor, evento, seção, vídeo
- Criar campanha
- Adicionar conhecimento ao chatbot
- Publicar livro de autor emergente

---

### 31. O que cada card da dashboard mostra?

**R:** Descrição completa:

**Total de Livros:**
- Número total de livros cadastrados
- Barra de progresso: % com capa
- Link: Lista de livros no admin

**Autores:**
- Total de autores cadastrados
- Link: Lista de autores

**Categorias:**
- Total de categorias ativas
- Link: Gerenciar categorias

**Eventos:**
- Próximos eventos (não finalizados)
- Status: upcoming | happening | finished
- Link: Lista de eventos

**Seções Ativas:**
- Seções visíveis na home
- Link: Gerenciar seções

**Vídeos:**
- Total de vídeos cadastrados
- Link: Lista de vídeos

**Autores Emergentes:**
- Total de livros publicados
- Total de autores e capítulos
- Link: Gerenciar autores emergentes

**Chatbot Literário 🆕:**
- Total de mensagens
- Total de conversas
- Correções ativas na Knowledge Base
- Link: Conversas do chatbot

**Assinaturas Ativas (Finance):**
- Total de premiums ativos
- Link: Gerenciar assinaturas

**Campanhas Ativas (Finance):**
- Total de campanhas em andamento
- Link: Gerenciar campanhas

**Premiums Concedidos:**
- Total de premiums via campanhas
- Link: Ver grants

📖 **Documentação:** [docs/features/DASHBOARD_CHATBOT_CARD.md](docs/features/DASHBOARD_CHATBOT_CARD.md)

---

### 32. Como monitorar o chatbot via dashboard?

**R:** Seção dedicada na dashboard:

**Card Principal:**
```
🤖 Chatbot Literário
   1,234 mensagens
   89 conversas • 15 correções ativas
```

**Seção Detalhada:**

**Coluna 1: Conversas Recentes**
- Lista das últimas 5 conversas
- Para cada conversa:
  - Título (truncado em 60 caracteres)
  - Usuário
  - Status: ⚡ Ativa ou 🔒 Encerrada
  - Número de mensagens
  - Data/hora da última atualização
- Link: "Ver todas →"

**Coluna 2: Base de Conhecimento**

Mini Stats:
- **Correções Ativas:** Número de correções na KB
- **Vezes Usado:** Total de consultas à KB

Painel de Atividade:
- 📊 Total de Conversas
- 💬 Mensagens (últimos 7 dias)
- ✏️ Respostas Corrigidas
- 🏆 Conhecimento Mais Usado:
  - Mostra a pergunta mais consultada
  - Quantas vezes foi usada

**Ações Rápidas:**
- 🧠 Adicionar Conhecimento ao Chatbot
- 🤖 Acessar módulo Chatbot Literário

**Exemplo Visual:**
```
┌─────────────────────────────────────────────────┐
│ 🤖 CONVERSAS RECENTES      [Ver todas →]        │
├─────────────────────────────────────────────────┤
│ Quem escreveu Cem Anos de Solidão?              │
│ 👤 joao_silva • ⚡ Ativa • 12 msg • 03/12/25    │
├─────────────────────────────────────────────────┤
│ Recomende livros de ficção científica           │
│ 👤 maria_costa • 🔒 Encerrada • 8 msg • 02/12   │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ 🧠 BASE DE CONHECIMENTO    [Ver tudo →]         │
├─────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐            │
│  │     15       │  │     42       │            │
│  │  Correções   │  │ Vezes Usado  │            │
│  └──────────────┘  └──────────────┘            │
│                                                  │
│ 📊 Total de Conversas:                    89    │
│ 💬 Mensagens (últimos 7 dias):           234    │
│ ✏️ Respostas Corrigidas:                  15    │
│ ─────────────────────────────────────────────   │
│ 🏆 Conhecimento Mais Usado:                     │
│    "Quem é o autor de Quarta Asa?"              │
│    ✓ Usado 8 vezes                              │
└─────────────────────────────────────────────────┘
```

---

## 🧪 Desenvolvimento e Testes

### 33. Como executar os testes?

**R:** Scripts organizados em `scripts/testing/`:

**Testes Gerais:**
```bash
# Todos os testes
python scripts/testing/test_all_improvements.py

# Testes Django padrão
python manage.py test

# Testes específicos de app
python manage.py test chatbot_literario
python manage.py test core
python manage.py test recommendations
```

**Testes do Chatbot:**
```bash
# Teste completo do chatbot
python scripts/testing/test_chatbot_fix.py

# Teste do sistema RAG
python scripts/testing/test_rag.py

# Teste de integração RAG completo
python scripts/testing/test_rag_integration_complete.py

# Teste de variações de perguntas
python scripts/testing/test_quero_saber_variation.py

# Teste específico do bug "Quarta Asa"
python scripts/testing/test_quarta_asa_final.py
```

**Testes de Recomendações:**
```bash
# Teste simples
python scripts/testing/test_recommendations_simple.py

# Teste de lógica
python scripts/testing/test_rec_logic.py
```

**Testes de Debug:**
```bash
# Debug de extração de dados
python scripts/testing/test_extraction_debug.py
```

**Coverage (opcional):**
```bash
pip install coverage
coverage run manage.py test
coverage report
coverage html  # Gera relatório HTML
```

---

### 34. Como testar o sistema RAG?

**R:** Testes automatizados disponíveis:

**Teste Completo:**
```bash
python scripts/testing/test_rag_integration_complete.py
```

**O que testa:**
1. ✅ Detecção de intenção (author_query, book_info, etc.)
2. ✅ Extração de entidades (nomes de livros, autores)
3. ✅ Busca no banco de dados
4. ✅ Enrichment do prompt
5. ✅ Resposta da IA com contexto
6. ✅ Anti-alucinação

**Teste Manual (Django Shell):**
```python
python manage.py shell

from chatbot_literario.groq_service import GroqService

service = GroqService()

# Teste 1: Pergunta sobre autor
response = service.send_message(
    message="Quem escreveu Quarta Asa?",
    session_id="test-session"
)
print(response)

# Teste 2: Pergunta sobre livro
response = service.send_message(
    message="Me fale sobre O Nome do Vento",
    session_id="test-session"
)
print(response)

# Teste 3: Recomendação
response = service.send_message(
    message="Recomende livros de fantasia",
    session_id="test-session"
)
print(response)
```

**Verificar Logs:**
```python
# Logs mostram:
# ✅ Intent detectado
# ✅ Dados extraídos do banco
# ✅ Prompt enriquecido
# ✅ Resposta gerada

# Exemplo de log:
# [INFO] 🎯 RAG INTENT: author_query
# [INFO] 📚 RAG DATA: {'author': 'Brandon Sanderson', 'book': 'Quarta Asa'}
# [INFO] ✅ PROMPT ENRICHED with verified data
```

---

### 35. Como debugar problemas no chatbot?

**R:** Ferramentas de debug:

**1. Django Admin (ver conversas):**
```
1. Admin → Chatbot Literário → Chat sessions
2. Clique na sessão
3. Veja todas as mensagens
4. Verifique:
   - RAG intent detected
   - RAG data used
   - Knowledge base used
   - Has correction
```

**2. Logs (ativar verbosidade):**
```python
# settings.py
LOGGING = {
    'loggers': {
        'chatbot_literario': {
            'level': 'DEBUG',
        }
    }
}
```

**3. Debug Scripts:**
```bash
# Debug completo
python scripts/debug/debug_banner.py

# Debug simplificado
python scripts/debug/debug_banner_simple.py
```

**4. Django Shell (interativo):**
```python
python manage.py shell

from chatbot_literario.groq_service import GroqService
from chatbot_literario.knowledge_base_service import get_knowledge_service

# Teste Knowledge Base
kb = get_knowledge_service()
result = kb.search_knowledge("Quem escreveu Quarta Asa?")
print(result)

# Teste RAG
service = GroqService()
# Adicione breakpoints com pdb
import pdb; pdb.set_trace()
response = service.send_message("Test", "session-id")
```

**5. API Diretamente (Groq):**
```python
import os
from groq import Groq

client = Groq(api_key=os.getenv('GROQ_API_KEY'))

response = client.chat.completions.create(
    model="llama-3.1-70b-versatile",
    messages=[{"role": "user", "content": "Test"}]
)
print(response)
```

**Problemas comuns:**
- ❌ API Key inválida → Verifique .env
- ❌ Rate limit → Aguarde 60s
- ❌ Intent não detectado → Melhore regex
- ❌ Dados não encontrados → Verifique banco

---

## 📧 Email e Notificações

### 36. Como configurar envio de emails?

**R:** Duas opções: SMTP ou SendGrid

**Opção 1: SMTP (Gmail exemplo):**
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-app  # Não é senha normal!
DEFAULT_FROM_EMAIL=seu-email@gmail.com
```

**Obter senha de app (Gmail):**
```
1. Conta Google → Segurança
2. Verificação em duas etapas (ativar)
3. Senhas de app
4. Selecione: Mail + Outro (Django)
5. Gere senha
6. Use no EMAIL_HOST_PASSWORD
```

**Opção 2: SendGrid (recomendado produção):**
```env
EMAIL_BACKEND=sendgrid_backend.SendgridBackend
SENDGRID_API_KEY=SG.xxxxx
DEFAULT_FROM_EMAIL=noreply@cgbookstore.com
```

**Testar:**
```python
python manage.py shell

from django.core.mail import send_mail

send_mail(
    'Assunto teste',
    'Mensagem de teste',
    'from@example.com',
    ['to@example.com'],
    fail_silently=False,
)
```

📖 **Documentação:** [docs/CONFIGURAR_EMAIL.md](docs/CONFIGURAR_EMAIL.md)

---

### 37. Como usar SendGrid?

**R:** Configuração completa:

**1. Criar conta:**
```
1. https://sendgrid.com/
2. Sign Up (gratuito - 100 emails/dia)
3. Verify email
```

**2. Criar API Key:**
```
1. Settings → API Keys
2. Create API Key
3. Name: Django CGBookStore
4. Full Access
5. Copie a key (só aparece uma vez!)
```

**3. Configure .env:**
```env
EMAIL_BACKEND=sendgrid_backend.SendgridBackend
SENDGRID_API_KEY=SG.xxxxxxxxx
DEFAULT_FROM_EMAIL=noreply@cgbookstore.com
```

**4. Instale biblioteca:**
```bash
pip install sendgrid-django
```

**5. Verifique sender:**
```
SendGrid Dashboard → Sender Authentication
- Single Sender Verification
- Ou Domain Authentication (melhor)
```

**6. Teste:**
```bash
python manage.py shell
from django.core.mail import send_mail
send_mail('Test', 'Message', 'from@domain.com', ['to@domain.com'])
```

**Monitorar:**
- SendGrid Dashboard → Activity
- Ver emails enviados, abertos, clicados
- Bounces, spam reports

📖 **Documentação:** [docs/SENDGRID_SETUP.md](docs/SENDGRID_SETUP.md)

---

## 💬 Debates Literários

### 40. O que são os Debates Literários?

**R:** O módulo **Debates Literários** é um espaço comunitário integrado à plataforma onde leitores podem criar e participar de discussões aprofundadas sobre qualquer livro do catálogo.

**Funcionalidades principais:**
- 📌 **Tópicos de debate** vinculados a livros específicos
- 💬 **Posts e respostas** em thread (comentários aninhados)
- 👍👎 **Sistema de votos** (upvote/downvote) em cada post
- 📌 **Tópicos fixados** pelo administrador para discussões importantes
- 🔒 **Tópicos bloqueados** para encerrar discussões encerradas
- 🔍 **Busca** por título, descrição ou nome do livro
- 📊 **Contadores** de posts e visualizações por tópico

**Onde acessar:**
```
Lista geral de debates:  /debates/
Debate de um livro:      /debates/criar/<book_id>/  (via página do livro)
Detalhe de um tópico:   /debates/topico/<slug>/
```

**Como navegar:**
1. Acesse a página de detalhes de qualquer livro
2. Role até a seção "Debates Literários"
3. Clique em um tópico existente para participar
4. Ou clique em "Novo Debate" para criar um tópico

**Modelos do sistema:**

| Modelo | Descrição |
|---|---|
| `DebateTopic` | Tópico de debate vinculado a um livro |
| `DebatePost` | Mensagem/resposta dentro de um tópico |
| `DebateVote` | Voto (positivo ou negativo) em um post |

---

### 41. Como criar um tópico de debate?

**R:** Para criar um tópico você deve estar logado.

**Passo a Passo:**

1. **Acesse a página do livro** que deseja debater
   - URL: `/catalogo/<slug-do-livro>/`

2. **Clique em "Novo Debate"** (ou "Criar Debate")
   - O botão aparece na seção de Debates na página do livro
   - Redireciona para: `/debates/criar/<book_id>/`

3. **Preencha o formulário:**
   ```
   Título:      Título do tópico (obrigatório, max 200 caracteres)
   Descrição:   Contexto inicial do debate (obrigatório)
   ```

4. **Submeta** e você será redirecionado ao tópico criado

**Regras ao criar tópico:**
- ✅ Título e descrição são **obrigatórios**
- ✅ O sistema gera um **slug automático** a partir do título
- ✅ Você se torna o **criador/dono** do tópico
- ⚠️ Usuários **Free** podem criar apenas **1 tópico por livro**
- ✅ Usuários **Premium** podem criar **tópicos ilimitados** por livro

**Exemplo:**
```
Título:     "A magia do sistema de Sanderson em Mistborn"
Descrição:  "Quero discutir como o sistema de Allomancy foi desenvolvido..."
```

**Rate limiting (Produção):**
- Máximo de **10 tópicos criados por hora** por usuário

---

### 42. Como participar de um debate (responder)?

**R:** Qualquer usuário logado pode responder em qualquer tópico não bloqueado.

**Para responder em um tópico:**

1. **Acesse o tópico** clicando nele na lista de debates
2. **Leia as mensagens existentes** (exibidas em ordem cronológica)
3. **Use o formulário de resposta** ao final da página
4. **Escreva seu conteúdo** e clique em "Publicar"

**Para responder a um post específico (resposta aninhada):**

1. Clique no botão **"Responder"** abaixo do post desejado
2. Um formulário inline aparece abaixo do post
3. Escreva sua resposta e publique
4. A resposta ficará **indentada** sob o post original

**Visualização de um tópico:**
```
┌─────────────────────────────────────────────────────┐
│ 📖 TÍTULO DO TÓPICO                                  │
│ Descrição inicial do debate...                       │
├─────────────────────────────────────────────────────┤
│ 👤 usuario_a  •  01/01/2025 10:00                    │
│ Primeiro comentário do debate...                     │
│ 👍 +5  👎  [Responder] [Editar] [Deletar]            │
│   └─ 👤 usuario_b  •  01/01/2025 10:30              │
│      Resposta ao primeiro comentário...              │
│      👍 +2  👎  [Responder]                          │
├─────────────────────────────────────────────────────┤
│ 📝 Adicione sua resposta:                            │
│ [________________________]                           │
│                           [Publicar]                 │
└─────────────────────────────────────────────────────┘
```

**Rate limiting (Produção):**
- Máximo de **60 posts por hora** por usuário

**Restrições:**
- ❌ Tópicos **bloqueados** não aceitam novos posts
- ❌ Usuários **não autenticados** não podem postar
- ✅ Respostas são **ilimitadas** para todos os usuários (Free e Premium)

---

### 43. Como funciona o sistema de votos?

**R:** Cada post pode receber votos positivos (👍 upvote) ou negativos (👎 downvote) de outros usuários logados.

**Como votar:**

1. Acesse o tópico com o post que deseja avaliar
2. Clique em 👍 para votar **positivamente** ou 👎 para votar **negativamente**
3. O **score** do post é atualizado instantaneamente via AJAX

**Comportamento dos votos:**

| Ação | Resultado |
|---|---|
| Clicar 👍 (sem voto anterior) | Adiciona voto positivo, score +1 |
| Clicar 👎 (sem voto anterior) | Adiciona voto negativo, score -1 |
| Clicar 👍 novamente (já votou 👍) | **Remove** o voto, score volta ao anterior |
| Clicar 👎 após ter votado 👍 | **Troca** o voto, score -2 |
| Clicar 👍 após ter votado 👎 | **Troca** o voto, score +2 |

**Cálculo do score:**
```python
score = upvotes - downvotes
```

**Regras:**
- ✅ Cada usuário pode dar **apenas 1 voto** por post
- ✅ Votos podem ser **removidos ou trocados**
- ❌ Não é possível votar no **próprio post**
- ❌ Usuários **não autenticados** não podem votar

**Rate limiting (Produção):**
- Máximo de **100 votos por hora** por usuário

---

### 44. Como editar ou deletar meu post/tópico?

**R:** Você pode editar e deletar seus próprios posts e tópicos.

**Editar um Post:**

1. Localize seu post no tópico
2. Clique no botão **"Editar"** (aparece apenas para o autor do post)
3. O conteúdo vira um campo de texto editável
4. Faça as alterações e clique em **"Salvar"**
5. O post exibe a data/hora da edição: `(editado em dd/mm/YYYY HH:MM)`

**Deletar um Post:**

1. Localize seu post
2. Clique em **"Deletar"** (aparece para autor do post e staff)
3. Confirme a ação
4. O post é **removido da visualização** (soft delete — fica no banco)
5. O contador de posts do tópico é atualizado automaticamente

**Editar um Tópico:**

1. Acesse o tópico que você criou
2. Clique em **"Editar Tópico"** (aparece apenas para o criador)
3. Altere o título e/ou a descrição
4. Clique em **"Salvar"**

**Deletar um Tópico:**

1. Acesse seu tópico
2. Clique em **"Deletar Tópico"**
3. Confirme a ação
4. **Todos os posts** do tópico são deletados junto
5. Você é redirecionado para a página do livro

**Permissões:**

| Ação | Quem pode fazer |
|---|---|
| Editar post | Somente o **autor** do post |
| Deletar post | Autor do post **ou staff** |
| Editar tópico | Somente o **criador** do tópico |
| Deletar tópico | Criador do tópico **ou staff** |

> ⚠️ **Atenção:** Tópicos e posts deletados não podem ser recuperados pela interface. Posts usam soft-delete (marcados como `is_deleted=True`), mas tópicos são deletados permanentemente.

---

### 45. Quais são as limitações por plano (Free vs Premium)?

**R:** O sistema de debates tem diferenciação de recursos por plano de assinatura:

**Comparativo de Planos:**

| Recurso | Free | Premium |
|---|---|---|
| Visualizar debates | ✅ Ilimitado | ✅ Ilimitado |
| Criar tópicos por livro | ⚠️ **1 tópico** | ✅ **Ilimitado** |
| Responder em tópicos | ✅ Ilimitado | ✅ Ilimitado |
| Votar em posts | ✅ Ilimitado | ✅ Ilimitado |
| Editar próprios posts | ✅ Sim | ✅ Sim |
| Deletar próprios posts | ✅ Sim | ✅ Sim |

**Mensagem ao atingir o limite (usuário Free):**
```
⚠️ "Usuários gratuitos podem criar apenas 1 tópico por livro.
    Para criar mais tópicos, assine o plano Premium!
    (Você ainda pode responder ilimitadamente a outros tópicos)"
```

**Como fazer upgrade para Premium:**
1. Acesse `/finance/planos/` ou o botão "Seja Premium"
2. Escolha o plano (mensal, trimestral ou anual)
3. Efetue o pagamento via MercadoPago
4. O acesso ilimitado aos debates é liberado imediatamente

**Rate Limiting em Produção (todos os planos):**

| Operação | Limite |
|---|---|
| Visualizar lista de debates | 200 requisições/hora por IP |
| Criar tópicos | 10 tópicos/hora por usuário |
| Criar posts/respostas | 60 posts/hora por usuário |
| Votar | 100 votos/hora por usuário |

> 💡 **Nota:** Os limites de rate são aplicados apenas em **produção** (DEBUG=False). Em ambiente de desenvolvimento local, são desativados automaticamente.

---

### 46. Como administrar debates pelo painel Admin?

**R:** O Django Admin oferece controle total sobre todos os debates.

**Acesso:**
```
URL: /admin/debates/
```

**Gerenciar Tópicos (`DebateTopic`):**
```
/admin/debates/debatetopic/

Colunas exibidas:
- Título
- Livro vinculado
- Criador
- Nº de posts
- Nº de visualizações
- Fixado (is_pinned)
- Bloqueado (is_locked)
- Data de criação

Filtros disponíveis:
- Por status (fixado / bloqueado)
- Por data de criação

Ações administrativas:
- Editar título e descrição
- Fixar/Desfixar tópico (is_pinned)
- Bloquear/Desbloquear tópico (is_locked)
- Deletar tópico
```

**Gerenciar Posts (`DebatePost`):**
```
/admin/debates/debatepost/

Colunas exibidas:
- Autor
- Tópico
- Score de votos
- Deletado (is_deleted)
- Data de criação

Filtros disponíveis:
- Por status de deleção
- Por data

Ações:
- Ver e editar conteúdo de qualquer post
- Marcar como deletado (soft delete)
- Restaurar posts deletados
```

**Gerenciar Votos (`DebateVote`):**
```
/admin/debates/debatevote/

Colunas exibidas:
- Usuário
- Post
- Tipo de voto (positivo / negativo)
- Data

Filtros:
- Por tipo de voto
- Por data
```

**Operações comuns de moderação:**

```
1. Fixar um tópico importante:
   Admin → Debates → Tópicos → Editar tópico → ☑ Fixado → Salvar

2. Bloquear debate encerrado:
   Admin → Debates → Tópicos → Editar tópico → ☑ Bloqueado → Salvar

3. Remover post inapropriado:
   Admin → Debates → Posts → Editar post → ☑ Deletado → Salvar

4. Ver todos os debates de um livro:
   Admin → Debates → Tópicos → Filtrar por livro
```

**Campos somente leitura (admin):**
- `created_at`, `updated_at` — datas automáticas
- `views_count` — contador incrementado automaticamente
- `posts_count` — calculado a partir dos posts ativos
- `votes_score` — calculado a partir dos votos

---

## 📖 Documentação

### 38. Onde encontro a documentação completa?

**R:** Documentação organizada em `docs/`:

**Índice Principal:**
📄 [docs/PROJECT_INDEX.md](docs/PROJECT_INDEX.md) - Navegação completa

**Por Categoria:**

**Setup e Configuração:**
- [docs/GUIA_CONFIGURACAO_LOCAL.md](docs/GUIA_CONFIGURACAO_LOCAL.md)
- [docs/setup/GROQ_SETUP.md](docs/setup/GROQ_SETUP.md)
- [docs/setup/SETUP_SEGUNDO_COMPUTADOR.md](docs/setup/SETUP_SEGUNDO_COMPUTADOR.md)
- [docs/SUPABASE_RENDER_SETUP.md](docs/SUPABASE_RENDER_SETUP.md)

**Funcionalidades:**
- [docs/features/KNOWLEDGE_BASE_SYSTEM.md](docs/features/KNOWLEDGE_BASE_SYSTEM.md)
- [docs/features/RAG_IMPLEMENTATION.md](docs/features/RAG_IMPLEMENTATION.md)
- [docs/features/DASHBOARD_CHATBOT_CARD.md](docs/features/DASHBOARD_CHATBOT_CARD.md)
- [docs/features/RECOMMENDATIONS_REFACTORING.md](docs/features/RECOMMENDATIONS_REFACTORING.md)

**Deploy:**
- [docs/deployment/RENDER_PERFORMANCE_FIXES.md](docs/deployment/RENDER_PERFORMANCE_FIXES.md)
- [docs/GUIA_ATUALIZACAO_RENDER.md](docs/GUIA_ATUALIZACAO_RENDER.md)
- [docs/INSTRUÇÕES_RENDER.md](docs/INSTRUÇÕES_RENDER.md)

**Troubleshooting:**
- [docs/troubleshooting/TROUBLESHOOTING_CACHE.md](docs/troubleshooting/TROUBLESHOOTING_CACHE.md)
- [docs/USERPROFILE_DUPLICATE_FIX.md](docs/USERPROFILE_DUPLICATE_FIX.md)

**Histórico:**
- [docs/REORGANIZACAO_2025.md](docs/REORGANIZACAO_2025.md) - Reorganização do projeto
- [docs/features/BUG_FIX_SUMMARY.md](docs/features/BUG_FIX_SUMMARY.md) - Correções de bugs
- [docs/features/IMPROVEMENTS_SUMMARY.md](docs/features/IMPROVEMENTS_SUMMARY.md) - Melhorias

**README:**
- [README.md](README.md) - Visão geral do projeto

---

### 39. Como está organizada a estrutura do projeto?

**R:** Estrutura organizada e profissional:

```
cgbookstore_v3/
├── 📄 Arquivos Essenciais (7 na raiz)
│   ├── manage.py
│   ├── requirements.txt
│   ├── README.md
│   ├── .env
│   ├── .env.example
│   └── .gitignore
│
├── 🏗️ Apps Django (8 aplicações)
│   ├── accounts/              # Autenticação
│   ├── cgbookstore/           # Settings
│   ├── chatbot_literario/     # Chatbot IA + RAG + KB
│   ├── core/                  # Livros, Autores, etc.
│   ├── debates/               # Sistema de debates
│   ├── finance/               # Assinaturas + Pagamentos
│   ├── new_authors/           # Autores emergentes
│   └── recommendations/       # Recomendações IA
│
├── 📖 docs/ (40+ documentos)
│   ├── features/              # Funcionalidades
│   ├── setup/                 # Configuração
│   ├── deployment/            # Deploy
│   ├── guides/                # Guias
│   ├── testing/               # Testes
│   ├── troubleshooting/       # Solução de problemas
│   ├── PROJECT_INDEX.md       # Índice completo
│   └── FAQ.md                 # Este arquivo
│
├── 🔧 scripts/ (35+ scripts)
│   ├── testing/               # Testes automatizados
│   ├── debug/                 # Scripts de debug
│   ├── maintenance/           # Manutenção
│   │   ├── clear_cache.py
│   │   └── database/          # Manutenção DB
│   ├── setup/                 # Setup automatizado
│   └── utils/                 # Utilitários
│
├── ⚙️ config/
│   ├── deployment/
│   │   ├── build.sh
│   │   ├── gunicorn_config.py
│   │   └── render.yaml
│   └── .env.example
│
├── 🎨 templates/              # Templates Django
├── 📦 static/                 # CSS, JS, Images
├── 📁 media/                  # Uploads
└── 💾 backups/                # Backups
```

**Convenções:**
- 📄 Raiz: Apenas arquivos essenciais (manage.py, README, .env)
- 📖 Docs: Organizados por categoria
- 🔧 Scripts: Por função (testing, debug, maintenance)
- ⚙️ Config: Isolado em config/deployment/

📖 **Documentação:** [docs/REORGANIZACAO_2025.md](docs/REORGANIZACAO_2025.md)

---

## 🆘 Suporte e Ajuda

### Não encontrou sua resposta?

1. **📖 Documentação Completa:** [docs/PROJECT_INDEX.md](docs/PROJECT_INDEX.md)
2. **🔧 Troubleshooting:** [docs/troubleshooting/](docs/troubleshooting/)
3. **💬 Issues:** Reporte problemas no repositório GitHub
4. **📧 Email:** Contate o time de desenvolvimento

---

## 📊 Estatísticas do FAQ

- **Total de Perguntas:** 46
- **Categorias:** 12
- **Última Atualização:** 24/05/2026
- **Versão:** 1.1

---

**🎉 Desenvolvido com ❤️ usando Django, PostgreSQL, Redis e IA**
