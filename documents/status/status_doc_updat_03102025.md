# 📄 CGBookStore v3 - Documento de Estado do Projeto

**Data:** 03/10/2025 - 18:45  
**Versão:** 3.5  
**Última Atualização:** Sistema de População de Dados e Seções Dinâmicas com Dropdown

---

## 🎯 Visão Geral do Projeto

**CGBookStore v3** é uma livraria online desenvolvida em Django 5.0.3 com PostgreSQL (Supabase), focada em proporcionar uma experiência completa de leitura com biblioteca pessoal gamificada, sistema de eventos literários e assistente literário inteligente.

### Tecnologias Principais
- **Backend:** Django 5.0.3
- **Banco de Dados:** PostgreSQL 17.6 (Supabase) ✅ **MIGRADO**
- **Python:** 3.13
- **Frontend:** Bootstrap 5, Font Awesome, Swiper.js
- **Controle de Versão:** Git + GitHub

---

## 📂 Estrutura Atual do Projeto

```
C:\ProjectDjango\cgbookstore_v3\
├── cgbookstore/              # Configurações do projeto
│   ├── settings.py           # ✅ Supabase configurado
│   ├── urls.py               # ✅ Static/Media configurado
│   └── wsgi.py
│
├── core/                     # App principal (livraria)
│   ├── models/               # ✅ MODULAR
│   │   ├── __init__.py
│   │   ├── category.py
│   │   ├── author.py         # ✅ COM FOTO + REDES SOCIAIS
│   │   ├── book.py
│   │   ├── video.py
│   │   ├── section.py
│   │   ├── section_item.py
│   │   └── event.py
│   │
│   ├── admin/                # ✅ ADMIN MODULAR
│   │   ├── __init__.py
│   │   ├── category_admin.py
│   │   ├── author_admin.py
│   │   ├── book_admin.py
│   │   ├── video_admin.py
│   │   ├── section_admin.py  # ✅ Dropdown dinâmico NOVO
│   │   ├── event_admin.py
│   │   └── widgets.py
│   │
│   ├── management/           # ✅ NOVO - Management Commands
│   │   ├── __init__.py
│   │   └── commands/
│   │       ├── __init__.py
│   │       ├── populate_db.py      # ✅ NOVO - Popular banco
│   │       └── add_book_covers.py  # ✅ NOVO - Adicionar capas
│   │
│   ├── views/                # ✅ Modular
│   │   ├── __init__.py
│   │   ├── home_view.py
│   │   ├── book_views.py
│   │   ├── book_detail_view.py
│   │   ├── search_view.py
│   │   ├── about_view.py
│   │   ├── contact_view.py
│   │   ├── library_view.py
│   │   └── event_views.py
│   │
│   ├── templatetags/         # ✅ Template tags customizados
│   │   ├── __init__.py
│   │   └── custom_filters.py # ✅ Sistema de 5 estrelas
│   │
│   ├── migrations/
│   │   ├── 0001_initial.py
│   │   ├── 0002_*.py
│   │   ├── 0003_*.py
│   │   ├── 0004_video_section_sectionitem.py
│   │   ├── 0005_author_photo_*.py
│   │   └── 0006_event.py
│   │
│   └── urls.py
│
├── accounts/                 # App de autenticação
│   ├── forms.py
│   ├── views.py
│   ├── urls.py
│   └── admin.py
│
├── chatbot_literario/        # App do chatbot (placeholder)
│   ├── views.py
│   └── urls.py
│
├── templates/
│   ├── base.html             # ✅ Theme switcher integrado
│   ├── core/
│   │   ├── home.html         # ✅ Adaptado aos temas
│   │   ├── book_list.html
│   │   ├── book_detail.html  # ✅ Adaptado aos temas
│   │   ├── search_results.html
│   │   ├── about.html
│   │   ├── contact.html
│   │   ├── library.html
│   │   ├── events.html
│   │   └── widgets/
│   │       └── event_widget.html
│   └── accounts/
│       ├── login.html
│       └── register.html
│
├── static/
│   ├── css/
│   │   ├── carousel.css      # ✅ Adaptado com variáveis CSS
│   │   └── themes.css        # ✅ Sistema de temas completo
│   └── js/
│       └── theme-switcher.js # ✅ Lógica de alternância
│
├── media/                    # ✅ Configurado e funcionando
│   ├── books/covers/         # ✅ NOVO - 47 capas placeholder
│   ├── authors/photos/
│   └── events/
│       ├── banners/
│       └── thumbnails/
│
├── documents/
│   └── status/
│       ├── status_29092025.md
│       ├── status_30092025.md
│       ├── status_02102025.md
│       ├── status_02102025_v2.md
│       └── status_03102025_v3.md  # Este arquivo
│
├── .venv/                    # Ambiente virtual
├── .gitignore
├── requirements.txt          # ✅ Atualizado com requests
├── manage.py
└── .env                      # ✅ Credenciais Supabase
```

---

## ✅ Funcionalidades Implementadas

### Core (Livraria)
- ✅ Página inicial com seções dinâmicas gerenciáveis pelo admin
- ✅ Widget de evento na home
- ✅ Página de eventos (`/eventos/`)
- ✅ Catálogo de livros com paginação (12 por página)
- ✅ BookDetailView completa
- ✅ Sistema de avaliação com 5 estrelas
- ✅ Sistema de busca (título, autor, categoria)
- ✅ Página "Sobre" institucional
- ✅ Formulário de contato
- ✅ Página de biblioteca pessoal (placeholder)
- ✅ Upload de imagens funcionando
- ✅ Navegação com breadcrumbs
- ✅ Livros relacionados por categoria

### Sistema de Temas ✨ (Implementado 03/10/2025)
- ✅ **3 Temas:** Claro, Escuro, Sistema (auto)
- ✅ **Variáveis CSS organizadas** para todas as cores
- ✅ **Persistência no localStorage** - tema salvo entre sessões
- ✅ **Detecção automática** de preferência do sistema operacional
- ✅ **Transições suaves** entre temas
- ✅ **Switcher visual** no navbar com dropdown
- ✅ **Contraste otimizado** em todos os componentes
- ✅ **Ícones adaptáveis** ao tema
- ✅ **Cards, botões, forms** totalmente adaptados
- ✅ **Breadcrumbs, dropdowns, modais** adaptados

### Sistema de Seções Dinâmicas
- ✅ Model Section - criar seções personalizadas
- ✅ Model SectionItem - associar conteúdo
- ✅ 3 tipos de layout: carrossel, grid, lista
- ✅ 3 tipos de conteúdo: livros, autores, vídeos
- ✅ Admin com preview visual dos itens
- ✅ Ordenação de seções e itens
- ✅ Ativar/Desativar seções

### Sistema de Avaliação com Estrelas
- ✅ Template tag customizado (`custom_filters.py`)
- ✅ Renderização de 5 estrelas baseada no rating
- ✅ Preenchimento parcial (cheia, meia, vazia)
- ✅ Tamanho reduzido das estrelas
- ✅ Valor numérico ao lado
- ✅ Fallback para livros sem avaliação
- ✅ Funciona em todos os layouts

### Sistema de Vídeos
- ✅ Model Video - YouTube, Vimeo, Instagram, TikTok
- ✅ Tipos: trailer, entrevista, resenha, tutorial
- ✅ Relacionamentos: livros e autores
- ✅ Extração automática de embed code e thumbnail
- ✅ Admin completo com autocomplete

### Sistema de Eventos Literários
- ✅ Model Event completo
- ✅ Status automático (próximo, acontecendo, finalizado)
- ✅ Widget na home
- ✅ Página `/eventos/`
- ✅ Admin avançado com badges e ações

### Autenticação
- ✅ Registro de usuários
- ✅ Login/Logout
- ✅ Proteção de rotas
- ✅ Navbar dinâmica
- ✅ Link Admin no dropdown para staff/superuser

### Admin Melhorado
- ✅ Preview visual em SectionItemInline
- ✅ Validação robusta de object_id e slugs
- ✅ Mensagens de erro claras
- ✅ Contador inteligente de itens (com cores)
- ✅ Interface organizada com fieldsets
- ✅ Autocomplete em BookAdmin e AuthorAdmin

### Management Commands ✨ NOVO (03/10/2025)

#### `populate_db.py`
- ✅ Popular banco de dados automaticamente
- ✅ **15 categorias** diversificadas criadas
- ✅ **22 autores** (brasileiros e internacionais) criados
- ✅ **47 livros** com ratings (3.5 a 5.0) e preços (R$ 25 a R$ 90) criados
- ✅ Validação de duplicatas
- ✅ Detecção de erros de relacionamento
- ✅ Argumentos: `--clear`, `--books=N`, `--verbose`
- ✅ Mensagens coloridas e informativas
- ✅ Transaction atomic para segurança
- ✅ Resumo final com estatísticas

**Uso:**
```bash
python manage.py populate_db
python manage.py populate_db --clear --verbose
python manage.py populate_db --books=30
```

#### `add_book_covers.py`
- ✅ Adicionar capas placeholder aos livros
- ✅ **47 capas** baixadas do Lorem Picsum (400x600)
- ✅ Seeds únicos baseados no ID do livro
- ✅ Tratamento robusto de erros (timeout, rede)
- ✅ Argumentos: `--force`, `--verbose`
- ✅ Resumo com estatísticas e cobertura
- ✅ Barra de progresso visual

**Uso:**
```bash
python manage.py add_book_covers
python manage.py add_book_covers --force --verbose
```

### Sistema de Dropdown Dinâmico ✨ NOVO (03/10/2025)

#### SectionItemAdminForm
- ✅ **Form customizado** para SectionItem
- ✅ **3 dropdowns separados** (Book, Author, Video)
- ✅ Exibição inteligente: "Título - Autor" para livros
- ✅ Ordenação alfabética
- ✅ Empty label descritivo
- ✅ Método `clean()` para validação
- ✅ Método `save()` customizado para setar `object_id`
- ✅ Preview visual após salvar
- ✅ Validação robusta com mensagens claras
- ✅ Funciona tanto em inline quanto em admin standalone

**Como usar:**
1. Selecionar Content Type (Book/Author/Video)
2. Escolher objeto do dropdown correspondente
3. object_id é setado automaticamente
4. Preview aparece após salvar

---

## 🗺️ URLs Mapeadas

| URL | View | Nome | Autenticação |
|-----|------|------|--------------|
| `/` | HomeView | `core:home` | Não |
| `/livros/` | BookListView | `core:book_list` | Não |
| `/livros/<slug>/` | BookDetailView | `core:book_detail` | Não |
| `/buscar/` | SearchView | `core:search` | Não |
| `/sobre/` | AboutView | `core:about` | Não |
| `/contato/` | ContactView | `core:contact` | Não |
| `/biblioteca/` | LibraryView | `core:library` | **Sim** |
| `/eventos/` | EventListView | `core:events` | Não |
| `/contas/login/` | LoginView | `accounts:login` | Não |
| `/contas/registrar/` | RegisterView | `accounts:register` | Não |
| `/contas/logout/` | LogoutView | `accounts:logout` | Sim |
| `/chatbot/` | ChatbotView | `chatbot:chat` | Não |
| `/admin/` | Admin | `admin:index` | Sim (staff) |

---

## 🔧 Configurações Importantes

### Banco de Dados (settings.py)
```python
import dj_database_url
from decouple import config

DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL'),
        conn_max_age=60,
        conn_health_checks=True,
    )
}
```

### Arquivos Estáticos e Media
```python
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

### Variáveis de Ambiente (.env)
```env
SECRET_KEY=Oa023568910@
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Supabase PostgreSQL
DATABASE_URL=postgresql://postgres.uomjbcuowfgcwhsejatn:Oa023568910@@aws-1-sa-east-1.pooler.supabase.com:5432/postgres

# Supabase API
SUPABASE_URL=https://uomjbcuowfgcwhsejatn.supabase.co
SUPABASE_ANON_KEY=eyJhbG...
SUPABASE_SERVICE_KEY=eyJhbG...
```

---

## 📦 Dependências (requirements.txt)

```txt
Django==5.0.3
django-environ==0.11.2
python-decouple==3.8
psycopg[binary]>=3.1.0
dj-database-url==2.1.0
supabase>=2.4.0
storage3>=0.7.3
gotrue>=2.4.1
postgrest>=0.16.0
realtime>=2.0.0
supafunc>=0.4.0
Pillow>=10.0.0
requests>=2.31.0
```

---

## 🛠️ Problemas Resolvidos na Sessão (03/10/2025)

### 1. População do Banco de Dados ✅
**Implementação:** Commands `populate_db` e `add_book_covers`  
**Status:** Resolvido - 47 livros, 22 autores, 15 categorias, 47 capas

### 2. Campo description em Category ✅
**Problema:** Campo não existia no model  
**Solução:** Removido do comando, usar apenas `name`  
**Status:** Resolvido

### 3. Campos rating e stock em Book ✅
**Problema:** Models usam `average_rating` (não `rating`) e não tem `stock`  
**Solução:** Mapeado corretamente no comando  
**Status:** Resolvido

### 4. Capas Placeholder ✅
**Problema:** Livros sem capa visual  
**Solução:** Comando para baixar do Lorem Picsum  
**Status:** Resolvido - 47 capas adicionadas

### 5. Dropdown Dinâmico no Admin ✅
**Problema:** Digitar ID manualmente era confuso  
**Solução:** Form customizado com dropdowns para Book/Author/Video  
**Status:** Resolvido

### 6. Erro object_id NULL ✅
**Problema:** object_id não estava sendo setado antes do save  
**Solução:** Método `save()` customizado no Form  
**Status:** Resolvido

---

## 🚧 Próximas Funcionalidades Planejadas

### Prioridade ALTA

**1. Criar Seções na Home**
   - Via Admin: criar seções manualmente
   - Sugestões: "Mais Vendidos", "Lançamentos", "Ficção Científica"
   - Testar diferentes layouts (carrossel, grid, lista)

**2. Integração Google Books API**
   - Criar `core/utils/google_books_api.py`
   - Funções: search_books(), get_by_isbn(), import_to_catalog()
   - Interface admin para buscar e importar
   - Substituir capas placeholder por capas reais
   - Sincronização automática de dados

**3. Dashboard Admin Personalizada**
   - Estatísticas gerais (livros, autores, eventos)
   - Gráficos (Chart.js)
   - Ações rápidas
   - Atalhos para seções mais usadas

### Prioridade MÉDIA

**4. Sistema de Biblioteca Pessoal (Backend)**
   - Models: UserProfile, BookShelf, ReadingProgress, BookReview
   - CRUD de prateleiras personalizadas
   - Progresso de leitura (%)
   - Sistema de avaliações privadas

**5. Sistema de Carrinho de Compras**
   - Models: Cart, CartItem, Order
   - Checkout básico
   - Integração com pagamento (futuro)

**6. Filtros Avançados no Catálogo**
   - Filtro por categoria
   - Filtro por faixa de preço
   - Ordenação (preço, data, título, avaliação)
   - Busca avançada

**7. Sistema de Reviews Público**
   - Comentários públicos nos livros
   - Sistema de likes/dislikes
   - Moderação

### Prioridade BAIXA

**8. Chatbot Literário Funcional**
   - Integração com API (OpenAI/Ollama)
   - Recomendações personalizadas
   - Conversação sobre livros

**9. Gamificação**
   - Sistema de pontos por leitura
   - Conquistas (badges)
   - Ranking de leitores
   - Desafios de leitura

**10. Sistema de Usuários Avançado**
    - Models: UserActivity, Subscription, Partnership
    - Planos (Free, Premium)
    - Rastreamento de comportamento
    - Analytics

---

## 🎯 Conquistas da Sessão (03/10/2025)

### ✅ Management Commands Implementados
- `populate_db.py` com 15 categorias, 22 autores, 47 livros
- `add_book_covers.py` com 47 capas placeholder
- Argumentos customizáveis (--clear, --force, --verbose)
- Mensagens coloridas e informativas
- Resumos estatísticos

### ✅ Sistema de Dropdown Dinâmico
- Form customizado para SectionItem
- 3 dropdowns separados (Book, Author, Video)
- Exibição inteligente com autor visível
- Preview visual dos itens
- Validação robusta

### ✅ Banco de Dados Populado
- 47 livros com dados completos
- 22 autores com biografias
- 15 categorias organizadas
- 47 capas placeholder (400x600)
- Ratings variados (3.5 a 5.0)
- Preços realistas (R$ 25 a R$ 90)

### ✅ Admin Profissional
- Interface intuitiva para gerenciar seções
- Dropdowns ao invés de IDs numéricos
- Preview visual imediato
- Mensagens de erro claras

---

## 📝 Comandos Úteis

### Ambiente Virtual
```powershell
# Ativar
.\.venv\Scripts\activate

# Desativar
deactivate
```

### Django
```powershell
# Rodar servidor
python manage.py runserver

# Criar migrations
python manage.py makemigrations

# Aplicar migrations
python manage.py migrate

# Criar superuser
python manage.py createsuperuser

# Shell interativo
python manage.py shell

# Verificar problemas
python manage.py check

# Popular banco de dados
python manage.py populate_db --verbose

# Adicionar capas
python manage.py add_book_covers --verbose
```

### Git
```powershell
git status
git add .
git commit -m "Feat: Descrição"
git push
```

---

## 🗂️ Últimos Commits Importantes

```bash
✅ Feat: Implementa população de dados e sistema de seções dinâmicas
✅ Feat: Adiciona populate_db.py (15 categorias, 22 autores, 47 livros)
✅ Feat: Adiciona add_book_covers.py (47 capas placeholder)
✅ Feat: Form customizado para SectionItem com dropdowns
✅ Fix: Corrige mapeamento de campos (rating → average_rating)
✅ Fix: Adiciona método save() para setar object_id corretamente
✅ Feat: Implementa sistema de temas completo (Claro/Escuro/Sistema)
✅ Feat: Adiciona theme-switcher.js com persistência em localStorage
✅ Style: Adapta carousel.css para usar variáveis CSS
✅ Fix: Corrige contraste de textos em ambos os temas
```

---

## 🌐 Links Importantes

### Repositório
- **GitHub:** https://github.com/cgvargas/cgbookstore_v3
- **Branch Principal:** main

### Documentação
- **Django Docs:** https://docs.djangoproject.com/en/5.0/
- **Bootstrap 5:** https://getbootstrap.com/docs/5.3/
- **Supabase Docs:** https://supabase.com/docs
- **Swiper.js:** https://swiperjs.com/
- **Font Awesome:** https://fontawesome.com/icons
- **Google Books API:** https://developers.google.com/books
- **Lorem Picsum:** https://picsum.photos/

### Supabase
- **Dashboard:** https://supabase.com/dashboard
- **Project:** uomjbcuowfgcwhsejatn

---

## 📋 Credenciais de Acesso

### Admin Django
- **URL:** http://127.0.0.1:8000/admin/
- **User:** admin
- **Password:** Oa023568910@

### Supabase
- **URL:** https://uomjbcuowfgcwhsejatn.supabase.co
- **Database:** PostgreSQL via pooler
- **Connection String:** (ver .env)

---

## 🎨 Design e Padrões

### Convenções de Código
- **PEP 8** para Python
- **Docstrings** em português
- **Models:** CamelCase
- **Views:** CamelCase + View suffix
- **URLs:** snake_case
- **Templates:** snake_case.html

### Estrutura de Commits
```
Tipo: Descrição curta

Tipos aceitos:
- Feat: Nova funcionalidade
- Fix: Correção de bug
- Docs: Documentação
- Style: Formatação, espaços
- Refactor: Refatoração de código
- Test: Testes
- Chore: Tarefas gerais
- Config: Configurações
```

---

## 📊 Estatísticas do Projeto

- **Linhas de Código (estimado):** ~12.000
- **Models:** 7 (Category, Author, Book, Video, Section, SectionItem, Event)
- **Admin Files:** 7 (modular) + widgets.py
- **Views:** 8 principais
- **Template Tags:** 1 (custom_filters)
- **Templates:** 13+ principais
- **CSS Files:** 2 (carousel.css, themes.css)
- **JS Files:** 1 (theme-switcher.js)
- **Management Commands:** 2 (populate_db, add_book_covers)
- **Migrations:** 6 aplicadas
- **Commits Git:** 40+
- **Dias de Desenvolvimento:** 5
- **Livros no Catálogo:** 47
- **Autores Cadastrados:** 22
- **Categorias:** 15

---

## 🎯 Contexto Importante para Próxima Sessão

### Estado Atual
- ✅ Projeto funcionando 100%
- ✅ Banco de dados populado (47 livros, 22 autores, 15 categorias)
- ✅ Sistema de temas completo e testado
- ✅ Sistema de dropdown para seções funcionando
- ✅ 47 capas placeholder adicionadas
- ✅ Admin profissional e intuitivo
- ✅ Management commands reutilizáveis

### Próximas Ações Sugeridas
1. **Criar seções na home** via Admin (Mais Vendidos, Lançamentos, etc.)
2. **Testar diferentes layouts** (carrossel, grid, lista)
3. **Integração Google Books API** para capas e dados reais
4. **Dashboard admin personalizada** com estatísticas
5. **Sistema de biblioteca pessoal** (backend)
6. **Adicionar eventos literários** para testar widget

### Pontos de Atenção
- Sistema de dropdown funcionando perfeitamente
- Capas são placeholder - substituir por reais no futuro
- Avisos RLS do Supabase podem ser ignorados
- Sempre usar `python manage.py check` antes de testar
- Fazer commits frequentes
- Manter `conn_max_age=60` para evitar esgotamento de conexões
- Testar responsividade mobile
- Validar acessibilidade (contraste WCAG)

### Arquivos Importantes Modificados/Criados
- `core/management/commands/populate_db.py` - **NOVO** - Popular banco
- `core/management/commands/add_book_covers.py` - **NOVO** - Adicionar capas
- `core/admin/section_admin.py` - Dropdown dinâmico implementado
- `requirements.txt` - Adicionado requests>=2.31.0
- `media/books/covers/` - 47 capas placeholder

### Testes Realizados
**Management Commands:**
- ✅ `populate_db` - Criou 47 livros, 22 autores, 15 categorias
- ✅ `populate_db --clear --verbose` - Limpou e recriou
- ✅ `add_book_covers` - Adicionou 47 capas
- ✅ `add_book_covers --force` - Substituiu capas existentes

**Admin:**
- ✅ Dropdown de livros funcionando
- ✅ Preview visual aparecendo corretamente
- ✅ Validação de object_id funcionando
- ✅ Salvamento correto sem erros NULL

---

## ✨ Visão de Longo Prazo

**CGBookStore v3** será uma plataforma completa que combina:
1. **E-commerce de Livros** (compra e venda)
2. **Biblioteca Pessoal Digital** (organização e tracking)
3. **Rede Social de Leitores** (reviews, recomendações)
4. **Assistente Literário IA** (chatbot inteligente)
5. **Gamificação** (conquistas, desafios, ranking)
6. **Integração Google Books** (catálogo massivo)
7. **Sistema de Vídeos** (entrevistas, book trailers, resenhas)
8. **Eventos Literários** (agenda completa)
9. **Dashboard Analytics** (métricas de negócio)
10. **Sistema de Assinaturas** (Free, Premium)
11. **Sistema de Temas** ✅ **IMPLEMENTADO** (Claro/Escuro/Sistema)
12. **Seções Dinâmicas** ✅ **IMPLEMENTADO** (Admin com dropdown)
13. **População Automatizada** ✅ **IMPLEMENTADO** (Management commands)

---

**Documento criado para continuidade do desenvolvimento.**  
**Última atualização:** 03/10/2025 18:45  
**Status:** ✅ Pronto para próxima sessão  
**Autor:** Claude (Assistente IA) + cgvargas (Desenvolvedor)


