# 📚 CG Bookstore - Livraria Virtual com IA

Sistema completo de livraria virtual com recomendações por IA, gamificação, debates literários e integrações avançadas.

## 🚀 Status do Projeto

- **Versão:** 3.0
- **Django:** 5.1.1
- **Python:** 3.11+
- **Produção:** [cgbookstore-v3.onrender.com](https://cgbookstore-v3.onrender.com)

---

## 📁 Estrutura do Projeto

```
cgbookstore_v3/
├── 📂 Apps Django             # Aplicações principais
│   ├── accounts/              # Autenticação e perfis
│   ├── cgbookstore/           # Configurações Django
│   ├── chatbot_literario/     # Chatbot IA com RAG + Knowledge Base
│   ├── core/                  # App principal (livros, autores, etc.)
│   ├── debates/               # Sistema de debates literários
│   ├── finance/               # Assinaturas e pagamentos
│   ├── new_authors/           # Autores emergentes
│   └── recommendations/       # Sistema de recomendações IA
│
├── 📂 config/                 # ⭐ Configurações
│   └── deployment/            # Configurações de deploy
│       ├── build.sh           # Script de build para produção
│       ├── gunicorn_config.py # Configuração do Gunicorn
│       └── render.yaml        # Configuração Render.com
│
├── 📂 docs/                   # ⭐ Documentação completa
│   ├── features/              # Documentação de funcionalidades
│   │   ├── KNOWLEDGE_BASE_SYSTEM.md
│   │   ├── RAG_IMPLEMENTATION.md
│   │   ├── DASHBOARD_CHATBOT_CARD.md
│   │   └── RECOMMENDATIONS_REFACTORING.md
│   ├── setup/                 # Guias de configuração
│   │   ├── GROQ_SETUP.md
│   │   └── SETUP_SEGUNDO_COMPUTADOR.md
│   ├── deployment/            # Deploy e produção
│   │   └── RENDER_PERFORMANCE_FIXES.md
│   ├── guides/                # Guias gerais
│   ├── testing/               # Documentação de testes
│   └── troubleshooting/       # Solução de problemas
│
├── 📂 scripts/                # ⭐ Scripts utilitários
│   ├── testing/               # Scripts de teste
│   │   ├── test_chatbot_fix.py
│   │   ├── test_rag_integration_complete.py
│   │   └── test_recommendations_simple.py
│   ├── debug/                 # Scripts de debug
│   │   ├── debug_banner.py
│   │   └── debug_banner_simple.py
│   ├── maintenance/           # Manutenção do sistema
│   │   ├── clear_cache.py
│   │   └── database/          # Manutenção de banco
│   │       ├── fix_userprofile_duplicate.py
│   │       └── verify_userprofiles.py
│   ├── setup/                 # Scripts de setup
│   └── utils/                 # Utilitários gerais
│
├── 📂 templates/              # Templates Django
├── 📂 static/                 # Arquivos estáticos (CSS, JS, images)
├── 📂 staticfiles/            # Arquivos estáticos coletados
├── 📂 media/                  # Uploads de usuários
├── 📂 backups/                # Backups do sistema
│
├── 📄 manage.py               # CLI do Django
├── 📄 requirements.txt        # Dependências Python
├── 📄 .env.example            # Template de variáveis de ambiente
├── 📄 .env                    # Variáveis de ambiente (não versionado)
└── 📄 .gitignore              # Arquivos ignorados pelo Git
```

> 📖 **Índice Completo:** Veja [docs/PROJECT_INDEX.md](docs/PROJECT_INDEX.md) para navegação detalhada.

---

## ⚡ Quick Start

### 1. Clonar e Instalar

```bash
git clone <repo-url>
cd cgbookstore_v3
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configurar Ambiente

```bash
cp .env.example .env
# Edite o .env com suas credenciais
```

### 3. Inicializar Banco

```bash
python manage.py migrate
python manage.py setup_initial_data
python manage.py createsuperuser
```

### 4. Executar

```bash
python manage.py runserver
```

Acesse: `http://localhost:8000`

---

## 🎯 Funcionalidades Principais

### 🤖 Recomendações por IA
- Algoritmo híbrido (colaborativo + conteúdo + tendências)
- Integração com Google Gemini AI
- Análise de preferências do usuário
- Cache inteligente de recomendações

### 📖 Catálogo de Livros
- Integração Google Books API
- Busca avançada e filtros
- Sistema de categorias
- Gestão de autores e editoras

### 💬 Chatbot Literário (com IA)
- Powered by Groq API (LLaMA 3.1 70B)
- **RAG (Retrieval-Augmented Generation)** - Consulta banco antes da IA
- **Knowledge Base com Aprendizado** - Correções administrativas reutilizadas
- Recomendações personalizadas via chat
- Processamento de linguagem natural
- Histórico de conversas
- Dashboard administrativa com estatísticas

### 🎮 Gamificação
- Sistema de pontos e badges
- Desafios de leitura
- Rankings e conquistas
- Progresso de leitura

### 💰 Módulo Financeiro
- Integração Mercado Pago
- Sistema de créditos
- Histórico de transações

### 🗣️ Debates Literários
- Fóruns por livro
- Sistema de comentários
- Moderação de conteúdo

### 🔐 Autenticação Social
- Login com Google
- Login com Facebook
- Gestão de perfis

---

## 📚 Documentação

### ❓ **FAQ - Perguntas Frequentes** ⭐ **NOVO!**

- **[FAQ Completo](docs/FAQ.md)** - 39 perguntas e respostas sobre o sistema
  - 🚀 Setup e configuração
  - 🤖 Chatbot e IA
  - 📚 Livros e catálogo
  - 💰 Sistema financeiro
  - 🌐 Deploy e produção
  - 🔧 Troubleshooting

### 📖 **Documentação Geral**

- **[Índice Completo](docs/PROJECT_INDEX.md)** - Navegação por toda documentação
- **[Estrutura do Projeto](docs/REORGANIZACAO_2025.md)** - Como está organizado

### 🚀 Deploy e Produção

- **[Guia Rápido - Plano Free](docs/production/GUIA_RAPIDO_FREE.md)** - Para quem usa Render Free
- **[Correções de Produção](docs/production/CORRECOES_PRODUCAO.md)** - Soluções rápidas
- **[Troubleshooting](docs/troubleshooting/TROUBLESHOOTING_PRODUCAO.md)** - Problemas comuns
- **[README Produção](docs/production/README_PRODUCAO.md)** - Visão geral

### 🛠️ Setup e Configuração

- **[Configurar Login Social](docs/setup/CONFIGURAR_LOGIN_SOCIAL.md)** - OAuth Google/Facebook
- **[Deploy no Render](docs/deployment/DEPLOY_RENDER.md)** - Guia completo
- **[Production Checklist](docs/deployment/PRODUCTION_CHECKLIST.md)** - Checklist pré-deploy

---

## 🛠️ Ferramentas Administrativas (Render Free)

Como o plano free do Render não tem Shell, use estas ferramentas web:

### 🏥 Health Check
**URL:** `/admin-tools/health/`

Diagnóstico completo da aplicação:
- Status do banco de dados
- Conexão Redis
- Configuração do Site
- Apps OAuth
- Dados cadastrados

### 🔄 Setup de Dados
**URL:** `/admin-tools/setup/`

Popular banco de dados automaticamente:
- Criar Site (django-allauth)
- 20 categorias de livros
- 3 livros de exemplo
- Apps OAuth configurados

**Requisito:** Estar logado como superusuário

---

## 🔧 Comandos Django Úteis

### Setup Inicial
```bash
# Popular dados iniciais
python manage.py setup_initial_data

# Apenas categorias
python manage.py setup_initial_data --skip-books

# Com superusuário customizado
python manage.py setup_initial_data --admin-email seu@email.com --admin-password senha123
```

### Health Check
```bash
# Diagnóstico completo
python manage.py health_check
```

### Migrações
```bash
# Criar migrações
python manage.py makemigrations

# Aplicar migrações
python manage.py migrate

# Ver status
python manage.py showmigrations
```

### Arquivos Estáticos
```bash
# Coletar arquivos estáticos
python manage.py collectstatic --no-input
```

---

## 🌍 Deploy no Render.com

### Opção 1: Deploy Automático (via Web)

1. Conecte seu repositório Git no Render
2. O `render.yaml` configura tudo automaticamente
3. Configure variáveis de ambiente opcionais (OAuth, APIs)

### Opção 2: Deploy Manual

Ver [docs/deployment/DEPLOY_RENDER.md](docs/deployment/DEPLOY_RENDER.md)

### Criar Superusuário em Produção (Render Free)

**No painel do Render, em Environment:**
```
CREATE_SUPERUSER=true
SUPERUSER_USERNAME=admin
SUPERUSER_EMAIL=seu@email.com
SUPERUSER_PASSWORD=SuaSenha123
```

Depois: Manual Deploy > Deploy latest commit

---

## 📋 Variáveis de Ambiente

### Essenciais

```env
SECRET_KEY=sua-chave-secreta
DEBUG=False
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
ALLOWED_HOSTS=seu-dominio.com
CSRF_TRUSTED_ORIGINS=https://seu-dominio.com
```

### OAuth (Opcional)

```env
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
FACEBOOK_APP_ID=...
FACEBOOK_APP_SECRET=...
```

### APIs (Opcional)

```env
GOOGLE_BOOKS_API_KEY=...
GEMINI_API_KEY=...
```

### Supabase Storage (Opcional)

```env
USE_SUPABASE_STORAGE=true
SUPABASE_URL=...
SUPABASE_ANON_KEY=...
SUPABASE_SERVICE_KEY=...
```

Ver [.env.example](.env.example) para lista completa.

---

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch: `git checkout -b feature/nova-funcionalidade`
3. Commit: `git commit -m 'Add nova funcionalidade'`
4. Push: `git push origin feature/nova-funcionalidade`
5. Abra um Pull Request

---

## 📄 Licença

Este projeto é proprietário e de uso exclusivo da CG Bookstore.

---

## 🆘 Suporte

### Problemas em Produção?

1. **Health Check:** Acesse `/admin-tools/health/`
2. **Logs:** Dashboard Render > Logs
3. **Documentação:** [docs/troubleshooting/](docs/troubleshooting/)

### Links Úteis

- 🏥 Health Check: `/admin-tools/health/`
- 🔄 Setup Dados: `/admin-tools/setup/`
- 🔐 Admin: `/admin/`
- 📊 Dashboard Render: https://dashboard.render.com

---

## 🗺️ Roadmap

- [ ] Sistema de notificações em tempo real
- [ ] App mobile (React Native)
- [ ] Integração com mais providers OAuth
- [ ] Sistema de cupons e descontos
- [ ] Analytics e relatórios avançados
- [ ] API REST completa
- [ ] Testes automatizados (coverage > 80%)

---

**Desenvolvido com ❤️ usando Django, PostgreSQL, Redis e IA**
