# 📄 CGBookStore v3 - Documento de Estado do Projeto

**Data:** 30/09/2025 - 19:30  
**Versão:** 3.2  
**Última Atualização:** Sistema de Eventos + Admin Modular implementados

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
C:\ProjectsDjango\CGBookStore_v3\
├── cgbookstore/              # Configurações do projeto
│   ├── settings.py           # ✅ Supabase configurado
│   ├── urls.py               # ✅ Static/Media configurado
│   └── wsgi.py
│
├── core/                     # App principal (livraria)
│   ├── models/               # ✅ MODULAR
│   │   ├── __init__.py
│   │   ├── category.py       # Model Category
│   │   ├── author.py         # Model Author (✅ COM FOTO + REDES SOCIAIS)
│   │   ├── book.py           # Model Book + Google Books
│   │   ├── video.py          # Model Video (YouTube, etc) ✅ NOVO
│   │   ├── section.py        # Model Section (seções dinâmicas) ✅ NOVO
│   │   ├── section_item.py   # Model SectionItem ✅ NOVO
│   │   └── event.py          # Model Event (eventos literários) ✅ NOVO
│   │
│   ├── admin/                # ✅ ADMIN MODULAR (NOVO)
│   │   ├── __init__.py
│   │   ├── category_admin.py
│   │   ├── author_admin.py   # ✅ Com inline de livros + preview foto
│   │   ├── book_admin.py     # ✅ Autocomplete para author/category
│   │   ├── video_admin.py
│   │   ├── section_admin.py  # ✅ Com inline de itens
│   │   └── event_admin.py    # ✅ NOVO - Admin completo de eventos
│   │
│   ├── views/                # ✅ Modular
│   │   ├── __init__.py
│   │   ├── home_view.py      # ✅ Com seções dinâmicas + widget evento
│   │   ├── book_views.py
│   │   ├── book_detail_view.py
│   │   ├── search_view.py
│   │   ├── about_view.py
│   │   ├── contact_view.py
│   │   ├── library_view.py
│   │   └── event_views.py    # ✅ NOVO - Lista de eventos
│   │
│   ├── migrations/
│   │   ├── 0001_initial.py
│   │   ├── 0002_*.py
│   │   ├── 0003_*.py
│   │   ├── 0004_video_section_sectionitem.py  # ✅ Seções dinâmicas
│   │   ├── 0005_author_photo_*.py             # ✅ Foto do autor
│   │   └── 0006_event.py                      # ✅ NOVO - Eventos
│   │
│   └── urls.py               # ✅ URLs atualizadas com eventos
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
│   ├── base.html             # ✅ Swiper integrado, Admin no dropdown
│   ├── core/
│   │   ├── home.html         # ✅ Seções dinâmicas + widget evento
│   │   ├── book_list.html    # ✅ Links de detalhes
│   │   ├── book_detail.html  # ✅ Página completa
│   │   ├── search_results.html
│   │   ├── about.html
│   │   ├── contact.html
│   │   ├── library.html      # Placeholder
│   │   ├── events.html       # ✅ NOVO - Página de eventos
│   │   └── widgets/
│   │       └── event_widget.html  # ✅ NOVO - Widget na home
│   └── accounts/
│       ├── login.html
│       └── register.html
│
├── static/
│   └── css/
│       └── carousel.css      # ✅ Estilos do carrossel
│
├── media/                    # ✅ Configurado e funcionando
│   ├── books/covers/
│   ├── authors/photos/       # ✅ NOVO - Fotos de autores
│   └── events/               # ✅ NOVO - Imagens de eventos
│       ├── banners/
│       └── thumbnails/
│
├── documents/
│   └── status/
│       ├── status_29092025.md
│       ├── status_30092025.md
│       └── status_30092025_final.md  # Este arquivo
│
├── .venv/                    # Ambiente virtual
├── .gitignore
├── requirements.txt
├── manage.py
└── .env                      # ✅ Credenciais Supabase
```

---

## ✅ Funcionalidades Implementadas

### Core (Livraria)
- ✅ Página inicial com seções dinâmicas gerenciáveis pelo admin
- ✅ **Widget de evento** na home (último evento em destaque)
- ✅ **Página de eventos** (`/eventos/`) com lista completa
- ✅ Catálogo de livros com paginação (12 por página)
- ✅ **BookDetailView** completa com todos os campos
- ✅ Sistema de busca (título, autor, categoria)
- ✅ Página "Sobre" institucional
- ✅ Formulário de contato (visual, preparado para email)
- ✅ Página de biblioteca pessoal (placeholder estruturado)
- ✅ Upload de imagens funcionando (MEDIA configurado)
- ✅ Navegação com breadcrumbs
- ✅ Livros relacionados por categoria
- ✅ Sistema de avaliação com estrelas (quando disponível)

### Sistema de Seções Dinâmicas ✅ NOVO
- ✅ **Model Section** - criar seções personalizadas
- ✅ **Model SectionItem** - associar conteúdo (livros, autores, vídeos)
- ✅ **3 tipos de layout:** carrossel, grid, lista
- ✅ **3 tipos de conteúdo:** livros, autores, vídeos
- ✅ **Admin com inline** para gerenciar itens
- ✅ **Ordenação** de seções e itens
- ✅ **Ativar/Desativar** seções

### Sistema de Vídeos ✅ NOVO
- ✅ **Model Video** - YouTube, Vimeo, Instagram, TikTok
- ✅ **Tipos:** trailer, entrevista, resenha, tutorial
- ✅ **Relacionamentos:** livros e autores
- ✅ **Extração automática** de embed code e thumbnail (YouTube)
- ✅ **Admin completo** com autocomplete

### Sistema de Eventos Literários ✅ NOVO
- ✅ **Model Event** completo com:
  - Título, descrição, tipo de evento
  - Datas de início/fim
  - Local (nome, endereço, cidade, estado)
  - Evento online (flag)
  - Banner e thumbnail
  - Link do evento
  - Link de inscrição
  - Preço / Gratuito
  - Capacidade
  - Relacionamento com livros e autores
- ✅ **Status automático:** próximo, acontecendo, finalizado, cancelado
- ✅ **Widget na home** - exibe evento em destaque
- ✅ **Página `/eventos/`** - lista completa
- ✅ **Eventos finalizados** somem automaticamente da home
- ✅ **Admin avançado** com:
  - Preview de imagens
  - Badges coloridas de status
  - Filtros por tipo, status, data
  - Autocomplete para livros e autores
  - Ações em massa (destacar, ativar, desativar)

### Autenticação
- ✅ Registro de usuários
- ✅ Login/Logout
- ✅ Proteção de rotas (biblioteca requer login)
- ✅ Navbar dinâmica (mostra usuário logado)
- ✅ Link Admin no dropdown para staff/superuser

### Models Completos

#### **Category**
```python
- name (CharField, unique)
- slug (SlugField, auto-gerado)
- featured (BooleanField)
- created_at (DateTimeField)
```

#### **Author** ✅ ATUALIZADO
```python
- name (CharField)
- slug (SlugField, auto-gerado)
- bio (TextField, nullable)
- photo (ImageField) ✅ NOVO
- website (URLField) ✅ NOVO
- twitter (CharField) ✅ NOVO
- instagram (CharField) ✅ NOVO
- created_at (DateTimeField)
```

#### **Book**
```python
# Campos locais
- title, slug, author (FK), category (FK)
- description, publication_date, isbn, publisher, price
- cover_image (ImageField)

# Campos Google Books API
- google_books_id, subtitle, page_count
- average_rating, ratings_count
- preview_link, info_link, language

# Metadados
- created_at, updated_at
```

#### **Video** ✅ NOVO
```python
- title, slug, description, video_type
- platform (youtube, vimeo, instagram, tiktok)
- video_url, embed_code, thumbnail_url
- related_book (FK), related_author (FK)
- duration, views_count, published_date
- featured, active
- created_at, updated_at
```

#### **Section** ✅ NOVO
```python
- title, subtitle
- content_type (books, authors, videos, mixed)
- layout (carousel, grid, list, featured)
- active, order
- background_color, css_class
- items_per_row, show_see_more, see_more_url
- created_at, updated_at
```

#### **SectionItem** ✅ NOVO
```python
- section (FK)
- content_type (GenericForeignKey)
- object_id
- content_object (GenericForeignKey)
- active, order
- custom_title, custom_description
- created_at
```

#### **Event** ✅ NOVO
```python
- title, slug, description, short_description
- event_type (launch, fair, meetup, workshop, lecture, signing, reading)
- banner_image, thumbnail_image
- start_date, end_date
- location_name, location_address, location_city, location_state
- is_online, event_url, registration_url
- related_books (M2M), related_authors (M2M)
- capacity, price, is_free
- featured, active, status
- created_at, updated_at

# Métodos:
- is_finished(), is_ongoing(), is_upcoming()
- days_until_event(), get_location_display()
```

### Admin Modular ✅ NOVO

Estrutura organizada em arquivos separados:

#### **CategoryAdmin**
- Lista com contador de livros
- Filtros por destaque e data
- Edição inline do campo featured

#### **AuthorAdmin** ✅ MELHORADO
- **Preview circular da foto**
- **Inline de livros** (mostra todos os livros do autor)
- Link direto para editar livros
- Contador visual de livros
- Indicador de redes sociais
- Fieldsets organizados

#### **BookAdmin** ✅ MELHORADO
- **Autocomplete para Author** (busca rápida digitando)
- **Autocomplete para Category**
- **Botão "+" verde** para adicionar autor/categoria rapidamente
- Fieldsets organizados
- Preview de Google Books

#### **VideoAdmin** ✅ NOVO
- Autocomplete para livros e autores
- Preview de thumbnail
- Filtros por plataforma e tipo
- Edição inline de featured/active

#### **SectionAdmin** ✅ NOVO
- **Inline de itens** (SectionItemInline)
- Contador de itens ativos
- Ordenação de seções
- Ativar/desativar inline

#### **EventAdmin** ✅ NOVO
- **Preview de banner**
- **Badges coloridas de status**
- **Autocomplete** para livros e autores
- **Filter_horizontal** para M2M
- **Ações em massa:**
  - Marcar/Remover destaque
  - Ativar/Desativar eventos
- Fieldsets bem organizados
- Filtros completos

### UI/UX
- ✅ Carrossel Swiper.js responsivo (múltiplos por página)
- ✅ Efeitos hover nos cards
- ✅ Design profissional estilo e-commerce
- ✅ Navegação intuitiva
- ✅ Responsividade completa (mobile/tablet/desktop)
- ✅ Widget de evento com animações
- ✅ Badges de status coloridas

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
| `/eventos/` | **EventListView** | `core:events` | Não ✅ NOVO |
| `/contas/login/` | LoginView | `accounts:login` | Não |
| `/contas/registrar/` | RegisterView | `accounts:register` | Não |
| `/contas/logout/` | LogoutView | `accounts:logout` | Sim |
| `/chatbot/` | ChatbotView | `chatbot:chat` | Não |
| `/admin/` | Admin | `admin:index` | Sim (staff) |

---

## 🔧 Configurações Importantes

### Banco de Dados (settings.py)
```python
# ✅ SUPABASE POSTGRESQL (MIGRADO)
import dj_database_url
from decouple import config

DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL'),
        conn_max_age=600,
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
# Django
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
```

---

## 🚧 Próximas Funcionalidades Planejadas

### Prioridade CRÍTICA
✅ ~~Migrar para PostgreSQL (Supabase)~~ **CONCLUÍDO**

### Prioridade ALTA
✅ ~~Sistema de Seções e Prateleiras Dinâmicas~~ **CONCLUÍDO**
✅ ~~Sistema de Eventos Literários~~ **CONCLUÍDO**

**Próximos:**
1. **Popular Banco de Dados**
   - Adicionar 50+ livros via Admin ou fixtures
   - Adicionar mais autores com fotos
   - Criar mais categorias

2. **Integração Google Books API**
   - Criar `core/utils/google_books_api.py`
   - Funções: search_books(), get_by_isbn(), import_to_catalog()
   - Interface admin para buscar e importar
   - Sincronização automática de dados

3. **Dashboard Admin Personalizada**
   - Estatísticas gerais (livros, autores, eventos)
   - Gráficos (Chart.js)
   - Ações rápidas
   - Atalhos para seções mais usadas

### Prioridade MÉDIA
4. **Sistema de Biblioteca Pessoal (Backend)**
   - Models: UserProfile, BookShelf, ReadingProgress, BookReview
   - CRUD de prateleiras personalizadas
   - Progresso de leitura (%)
   - Sistema de avaliações privadas

5. **Sistema de Carrinho de Compras**
   - Models: Cart, CartItem, Order
   - Checkout básico
   - Integração com pagamento (futuro)

6. **Filtros Avançados no Catálogo**
   - Filtro por categoria
   - Filtro por faixa de preço
   - Ordenação (preço, data, título, avaliação)
   - Busca avançada

7. **Sistema de Reviews Público**
   - Comentários públicos nos livros
   - Sistema de likes/dislikes
   - Moderação

### Prioridade BAIXA
8. **Chatbot Literário Funcional**
   - Integração com API (OpenAI/Ollama)
   - Recomendações personalizadas
   - Conversação sobre livros

9. **Gamificação**
   - Sistema de pontos por leitura
   - Conquistas (badges)
   - Ranking de leitores
   - Desafios de leitura

10. **Sistema de Usuários Avançado**
    - Models: UserActivity, Subscription, Partnership
    - Planos (Free, Premium)
    - Rastreamento de comportamento
    - Analytics

---

## 🎯 Conquistas Recentes (30/09/2025)

### ✅ Migração Supabase PostgreSQL
- Banco de dados migrado com sucesso
- Dados preservados (usuários + livros)
- Conexão estável e funcionando

### ✅ Sistema de Seções Dinâmicas
- 3 novos models (Section, SectionItem, Video)
- Admin com inlines
- Home renderizando dinamicamente
- 3 layouts (carrossel, grid, lista)

### ✅ Melhorias no Author
- Campo photo adicionado
- Campos de redes sociais
- Preview da foto no admin
- Inline de livros

### ✅ Admin Modular
- Estrutura organizada em pasta `core/admin/`
- 7 arquivos separados
- Autocomplete funcionando
- Inlines implementados

### ✅ Sistema de Eventos Literários
- Model Event completo
- Status automático
- Widget na home
- Página `/eventos/` funcionando
- Admin avançado com badges e ações

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
```

### Git
```powershell
# Status
git status

# Adicionar arquivos
git add .

# Commit
git commit -m "Mensagem"

# Push
git push

# Pull
git pull

# Ver histórico
git log --oneline
```

---

## 🗂️ Últimos Commits Importantes

```bash
✅ Feat: Implementa sistema de eventos + Admin modular + Widget na home
✅ Feat: Adiciona foto e redes sociais em Author + Admin avançado com autocomplete e inlines
✅ Feat: Implementa sistema de seções e prateleiras dinâmicas
✅ Feat: Implementa BookDetailView com suporte Google Books API
✅ Feat: Implementa carrossel de livros estilo Amazon na home
✅ Config: Migra banco de dados SQLite para Supabase PostgreSQL
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

### Supabase
- **Dashboard:** https://supabase.com/dashboard
- **Project:** uomjbcuowfgcwhsejatn

---

## 🔐 Credenciais de Acesso

### Admin Django
- **URL:** http://127.0.0.1:8000/admin/
- **User:** admin
- **Password:** Oa023568910@

### Supabase
- **URL:** https://uomjbcuowfgcwhsejatn.supabase.co
- **Database:** PostgreSQL via pooler
- **Connection String:** postgresql://postgres.uomjbcuowfgcwhsejatn:Oa023568910@@aws-1-sa-east-1.pooler.supabase.com:5432/postgres

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

### Organização de Models
- Um arquivo por model
- `__init__.py` exporta todos
- Ordenação alfabética

### Organização de Admin
- Um arquivo por model admin
- Pasta `core/admin/`
- Inlines quando necessário

---

## 📊 Estatísticas do Projeto

- **Linhas de Código (estimado):** ~8.000
- **Models:** 7 (Category, Author, Book, Video, Section, SectionItem, Event)
- **Admin Files:** 7 (modular)
- **Views:** 8 (Home, BookList, BookDetail, Search, About, Contact, Library, Events)
- **Templates:** 12+ principais
- **Migrations:** 6 aplicadas
- **Commits Git:** 25+
- **Dias de Desenvolvimento:** 2

---

## 🎯 Contexto Importante para Próxima Sessão

### Estado Atual
- ✅ Projeto funcionando 100%
- ✅ Supabase conectado e estável
- ✅ Admin modular e organizado
- ✅ Sistema de eventos completo
- ✅ Seções dinâmicas funcionando
- ✅ Imagens de autores e eventos configuradas

### Próximas Ações Sugeridas
1. **Popular banco de dados** (adicionar 50+ livros)
2. **Criar mais seções dinâmicas** no admin
3. **Adicionar mais eventos** para testar widget
4. **Integração Google Books API**
5. **Dashboard admin personalizada**

### Pontos de Atenção
- Avisos RLS do Supabase podem ser ignorados (Django tem segurança própria)
- Sempre usar `python manage.py check` antes de testar
- Fazer commits frequentes
- Testar em diferentes navegadores
- Validar responsividade mobile

### Arquivos Importantes
- `.env` - **NUNCA** versionar no Git
- `requirements.txt` - atualizar quando adicionar dependências
- `documents/status/` - manter documentos atualizados

---

## 🚀 Como Continuar o Desenvolvimento

### Setup em Novo Computador
```powershell
# 1. Clonar
cd C:\ProjectDjango
git clone https://github.com/cgvargas/cgbookstore_v3.git
cd cgbookstore_v3

# 2. Ambiente virtual
python -m venv .venv
.\.venv\Scripts\activate

# 3. Dependências
pip install -r requirements.txt

# 4. Criar .env (copiar credenciais deste documento)

# 5. Rodar
python manage.py runserver
```

### Workflow Diário
```powershell
# Início
git pull
.\.venv\Scripts\activate
python manage.py runserver

# Durante
# - Fazer alterações
# - Testar frequentemente
# - Commit após cada funcionalidade

# Fim
git add .
git commit -m "Tipo: Descrição"
git push
```

---

## 📞 Suporte e Referências

### Em Caso de Erro
1. Verificar `.env` está correto
2. Verificar ambiente virtual ativo
3. Verificar migrations aplicadas: `python manage.py migrate`
4. Verificar problemas: `python manage.py check`
5. Ver logs do servidor

### Recursos Úteis
- Stack Overflow
- Django Forum
- Supabase Community
- Bootstrap Examples

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

---

**Documento criado para continuidade do desenvolvimento.**  
**Última atualização:** 30/09/2025 19:30  
**Status:** ✅ Pronto para próxima sessão  
**Autor:** Claude (Assistente IA) + cgvargas (Desenvolvedor)

---

## 🔄 Próxima Conversa - Instruções de Início

Ao iniciar a próxima conversa, forneça este documento e diga:

> "Olá! Este é o documento de estado do projeto CGBookStore v3. Já temos:
> - Supabase PostgreSQL funcionando
> - Admin modular completo
> - Sistema de eventos implementado
> - Seções dinâmicas funcionando
> 
> Gostaria de continuar com [ESCOLHA UMA OPÇÃO]:
> 1. Popular banco de dados com mais livros
> 2. Integração Google Books API
> 3. Dashboard admin personalizada
> 4. Sistema de biblioteca pessoal (backend)
> 5. Outra funcionalidade"

Isso permitirá que eu retome exatamente de onde paramos! 🚀
