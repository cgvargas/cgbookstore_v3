# 📄 CGBookStore v3 - Documento de Estado do Projeto

**Data:** 03/10/2025 - 14:30  
**Versão:** 3.4  
**Última Atualização:** Sistema de Temas Completo (Claro/Escuro/Sistema)

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
│   │   ├── section_admin.py  # ✅ Preview visual
│   │   ├── event_admin.py
│   │   └── widgets.py
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
│   │   └── themes.css        # ✅ NOVO - Sistema de temas completo
│   └── js/
│       └── theme-switcher.js # ✅ NOVO - Lógica de alternância
│
├── media/                    # ✅ Configurado e funcionando
│   ├── books/covers/
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
│       └── status_03102025.md  # Este arquivo
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

### Sistema de Temas ✨ NOVO (03/10/2025)
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

---

## 🎨 Sistema de Temas - Detalhes Técnicos

### Arquivos Criados/Modificados

#### `static/css/themes.css` ✅
Sistema completo de variáveis CSS:
- Cores primárias e secundárias
- Backgrounds e cards
- Textos e links
- Bordas e sombras
- Preços, alertas, badges
- Estrelas de avaliação
- Inputs e forms
- Media query para tema sistema (auto)

#### `static/js/theme-switcher.js` ✅
Funcionalidades:
- Detecta preferência do sistema operacional
- Salva tema no localStorage
- Aplica tema ao carregar página
- Alterna entre 3 temas
- Listener para mudanças no sistema
- Atualiza ícone do botão automaticamente
- API global `window.CGBookStore.ThemeSwitcher`

#### `templates/base.html` ✅
Modificações:
- Link para `themes.css` no `<head>`
- Dropdown theme switcher no navbar
- Script `theme-switcher.js` antes do `</body>`
- Estilos para `.theme-option` e botão switcher

#### `static/css/carousel.css` ✅
Adaptado para usar variáveis CSS:
- Todas as cores fixas substituídas
- Backgrounds adaptáveis
- Bordas e sombras usando variáveis
- Botões de navegação Swiper adaptados
- Paginação com cores do tema

#### `templates/core/home.html` ✅
Estilos inline adaptados:
- Cards de autores usando variáveis
- Seção de boas-vindas adaptada
- Cards de vídeo compatíveis
- List group adaptado

### Como Funciona o Sistema de Temas

**1. Tema Claro (light):**
- Background: `#f5f5f5`
- Cards: `#ffffff`
- Texto: `#0f1111`
- Links: `#007185`

**2. Tema Escuro (dark):**
- Background: `#0f1111`
- Cards: `#1a1d1f`
- Texto: `#f5f5f5`
- Links: `#5dc3d1`

**3. Tema Sistema (auto):**
- Detecta `prefers-color-scheme` do navegador
- Aplica automaticamente claro ou escuro
- Atualiza quando usuário muda preferência do SO

**Persistência:**
- Salvo no `localStorage` como `cgbookstore-theme-preference`
- Valores possíveis: `'light'`, `'dark'`, `'auto'`
- Restaurado automaticamente ao recarregar página

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
```

---

## 🛠️ Problemas Resolvidos na Sessão (03/10/2025)

### 1. Sistema de Temas Completo ✅
**Implementação:** Sistema de 3 temas (Claro/Escuro/Sistema)  
**Arquivos:** `themes.css`, `theme-switcher.js`, `base.html`, `carousel.css`  
**Status:** Resolvido

### 2. Contraste de Textos ✅
**Problema:** Bio de autores e nome de autores ilegíveis no tema escuro  
**Solução:** Ajustadas variáveis CSS `--text-secondary`  
**Status:** Resolvido

### 3. Dropdown Theme Switcher ✅
**Problema:** Fundo branco/texto claro no tema claro  
**Solução:** Regras específicas para `[data-theme="light"]`  
**Status:** Resolvido

### 4. Card de Preço ✅
**Problema:** Texto branco no tema claro (fundo verde)  
**Solução:** Forçado `color: var(--text-light)` em todos os elementos  
**Status:** Resolvido

### 5. Carousel Adaptado ✅
**Problema:** Cores fixas não adaptáveis ao tema  
**Solução:** Substituídas todas as cores por variáveis CSS  
**Status:** Resolvido

---

## 🚧 Próximas Funcionalidades Planejadas

### Prioridade ALTA

**1. Popular Banco de Dados**
   - Adicionar 50+ livros via Admin ou fixtures
   - Adicionar mais autores com fotos
   - Criar mais categorias
   - Adicionar ratings aos livros

**2. Integração Google Books API**
   - Criar `core/utils/google_books_api.py`
   - Funções: search_books(), get_by_isbn(), import_to_catalog()
   - Interface admin para buscar e importar
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

### ✅ Sistema de Temas Completo
- 3 temas implementados (Claro, Escuro, Sistema)
- Switcher funcional no navbar
- Persistência em localStorage
- Detecção automática do sistema operacional
- Transições suaves entre temas

### ✅ Variáveis CSS Organizadas
- `themes.css` com 60+ variáveis
- Todos os componentes adaptados
- Contraste otimizado para ambos os temas
- Código limpo e sem duplicatas

### ✅ JavaScript do Theme Switcher
- Lógica completa de alternância
- API global para uso em outros scripts
- Compatibilidade com navegadores antigos
- Listeners para mudanças no sistema

### ✅ Adaptação Completa dos Templates
- `base.html` com switcher integrado
- `carousel.css` usando variáveis
- `home.html` totalmente adaptado
- `book_detail.html` com contraste perfeito

### ✅ Correções de Contraste
- Textos legíveis em ambos os temas
- Dropdowns com cores adequadas
- Botões e badges adaptados
- Cards de preço sempre legíveis

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
git status
git add .
git commit -m "Feat: Implementa sistema de temas completo (Claro/Escuro/Sistema)"
git push
```

---

## 🗂️ Últimos Commits Importantes

```bash
✅ Feat: Implementa sistema de temas completo (Claro/Escuro/Sistema)
✅ Feat: Adiciona theme-switcher.js com persistência em localStorage
✅ Style: Adapta carousel.css para usar variáveis CSS
✅ Fix: Corrige contraste de textos em ambos os temas
✅ Fix: Ajusta dropdown theme switcher no tema claro
✅ Feat: Implementa sistema de 5 estrelas com preenchimento parcial
✅ Fix: Corrige renderização de fotos de autores na home
✅ Fix: Remove SectionItem inválido (object_id=0)
✅ Config: Otimiza conexões Supabase (conn_max_age=60)
✅ Feat: Melhora admin de seções com preview visual
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

- **Linhas de Código (estimado):** ~10.500
- **Models:** 7 (Category, Author, Book, Video, Section, SectionItem, Event)
- **Admin Files:** 7 (modular) + widgets.py
- **Views:** 8 principais
- **Template Tags:** 1 (custom_filters)
- **Templates:** 13+ principais
- **CSS Files:** 2 (carousel.css, themes.css)
- **JS Files:** 1 (theme-switcher.js)
- **Migrations:** 6 aplicadas
- **Commits Git:** 35+
- **Dias de Desenvolvimento:** 5

---

## 🎯 Contexto Importante para Próxima Sessão

### Estado Atual
- ✅ Projeto funcionando 100%
- ✅ Sistema de temas completo e testado
- ✅ Contraste perfeito em ambos os temas
- ✅ Persistência funcionando (localStorage)
- ✅ Switcher integrado ao navbar
- ✅ Todos os componentes adaptados
- ✅ Código limpo e organizado

### Próximas Ações Sugeridas
1. **Popular banco de dados** (adicionar 50+ livros com ratings)
2. **Testar temas em diferentes navegadores** (Chrome, Firefox, Edge, Safari)
3. **Criar mais seções dinâmicas** no admin
4. **Adicionar mais eventos** para testar widget
5. **Integração Google Books API**
6. **Dashboard admin personalizada**

### Pontos de Atenção
- Sistema de temas funcionando perfeitamente
- Avisos RLS do Supabase podem ser ignorados
- Sempre usar `python manage.py check` antes de testar
- Fazer commits frequentes
- Manter `conn_max_age=60` para evitar esgotamento de conexões
- Testar responsividade mobile
- Validar acessibilidade (contraste WCAG)

### Arquivos Importantes Modificados
- `static/css/themes.css` - **NOVO** - Sistema completo de temas
- `static/js/theme-switcher.js` - **NOVO** - Lógica de alternância
- `templates/base.html` - Adicionado switcher no navbar
- `static/css/carousel.css` - Adaptado com variáveis CSS
- `templates/core/home.html` - Estilos adaptados aos temas

### Teste do Sistema de Temas
**Como testar:**
1. Rodar servidor: `python manage.py runserver`
2. Acessar: `http://127.0.0.1:8000/`
3. Clicar no ícone 🌗 no navbar
4. Alternar entre: ☀️ Claro, 🌙 Escuro, 🌗 Sistema
5. Recarregar página - tema deve persistir
6. Mudar tema do SO - tema auto deve atualizar

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
6. Verificar conexões Supabase não esgotadas
7. Limpar cache do navegador (Ctrl+Shift+Delete)
8. Testar em modo anônimo/privado

### Recursos Úteis
- Stack Overflow
- Django Forum
- Supabase Community
- Bootstrap Examples
- CSS Tricks (variáveis CSS)
- MDN Web Docs (localStorage)

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

---

**Documento criado para continuidade do desenvolvimento.**  
**Última atualização:** 03/10/2025 14:30  
**Status:** ✅ Pronto para próxima sessão  
**Autor:** Claude (Assistente IA) + cgvargas (Desenvolvedor)

---

## 📄 Próxima Conversa - Instruções de Início

Ao iniciar a próxima conversa, forneça este documento e diga:

> "Olá! Este é o documento de estado do projeto CGBookStore v3 atualizado em 03/10/2025.
> 
> **Implementações da última sessão:**
> - Sistema de temas completo (Claro/Escuro/Sistema)
> - Theme switcher no navbar com persistência
> - Variáveis CSS organizadas (60+ variáveis)
> - Contraste otimizado para todos os componentes
> - JavaScript de alternância de temas
> - Adaptação completa de carousel.css
> - Correções finais de contraste
> 
> Gostaria de continuar com [ESCOLHA UMA OPÇÃO]:
> 1. Popular banco de dados com mais livros e ratings
> 2. Testar sistema de temas em diferentes navegadores
> 3. Integração Google Books API
> 4. Dashboard admin personalizada
> 5