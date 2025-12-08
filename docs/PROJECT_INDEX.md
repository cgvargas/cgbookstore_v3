# 📚 CGBookStore - Índice de Documentação

**Última atualização:** 03 de Dezembro de 2025

Este documento fornece uma visão geral completa da estrutura de documentação do projeto CGBookStore.

---

## 📂 Estrutura de Diretórios

```
cgbookstore_v3/
├── 📖 docs/                          # Documentação completa
│   ├── features/                     # Documentação de funcionalidades
│   ├── setup/                        # Guias de configuração
│   ├── deployment/                   # Deployment e produção
│   ├── guides/                       # Guias gerais
│   ├── testing/                      # Testes
│   └── troubleshooting/              # Solução de problemas
│
├── 🔧 scripts/                       # Scripts utilitários
│   ├── testing/                      # Scripts de teste
│   ├── debug/                        # Scripts de debug
│   ├── maintenance/                  # Manutenção
│   │   └── database/                 # Manutenção de banco
│   ├── setup/                        # Setup inicial
│   └── utils/                        # Utilitários gerais
│
├── ⚙️ config/                        # Configurações
│   └── deployment/                   # Configurações de deploy
│
├── 🏗️ Apps Django                    # Aplicações do projeto
│   ├── accounts/                     # Autenticação e perfis
│   ├── chatbot_literario/            # Chatbot com IA
│   ├── core/                         # App principal
│   ├── debates/                      # Sistema de debates
│   ├── finance/                      # Assinaturas e pagamentos
│   ├── new_authors/                  # Autores emergentes
│   └── recommendations/              # Sistema de recomendações
│
└── 📦 Outros
    ├── media/                        # Arquivos de mídia
    ├── static/                       # Arquivos estáticos
    ├── staticfiles/                  # Arquivos coletados
    ├── templates/                    # Templates globais
    └── backups/                      # Backups do sistema
```

---

## 📖 Documentação por Categoria

### 🚀 **Configuração e Setup**

| Documento | Descrição | Localização |
|-----------|-----------|-------------|
| **GUIA_RAPIDO_ESTRUTURA.md** | Visão rápida da estrutura do projeto | `docs/` |
| **SETUP_SEGUNDO_COMPUTADOR.md** | Como configurar em outro computador | `docs/setup/` |
| **GROQ_SETUP.md** | Configuração da API Groq para chatbot | `docs/setup/` |
| **GUIA_CONFIGURACAO_LOCAL.md** | Setup completo do ambiente local | `docs/` |
| **SUPABASE_RENDER_SETUP.md** | Configuração Supabase + Render | `docs/` |

### 🎯 **Funcionalidades e Features**

| Documento | Descrição | Localização |
|-----------|-----------|-------------|
| **KNOWLEDGE_BASE_SYSTEM.md** | Sistema de aprendizado do chatbot | `docs/features/` |
| **RAG_IMPLEMENTATION.md** | Implementação RAG (Retrieval-Augmented Generation) | `docs/features/` |
| **DASHBOARD_CHATBOT_CARD.md** | Card do chatbot na dashboard admin | `docs/features/` |
| **RECOMMENDATIONS_REFACTORING.md** | Refatoração do sistema de recomendações | `docs/features/` |
| **IMPROVEMENTS_SUMMARY.md** | Resumo de melhorias implementadas | `docs/features/` |
| **BUG_FIX_SUMMARY.md** | Resumo de correções de bugs | `docs/features/` |

### 🌐 **Deployment e Produção**

| Documento | Descrição | Localização |
|-----------|-----------|-------------|
| **RENDER_PERFORMANCE_FIXES.md** | Otimizações para Render | `docs/deployment/` |
| **GUIA_ATUALIZACAO_RENDER.md** | Como atualizar no Render | `docs/` |
| **INSTRUÇÕES_RENDER.md** | Instruções gerais de deploy | `docs/` |
| **MIGRACAO_RAPIDA.md** | Migração rápida de ambientes | `docs/` |

### 📧 **Configuração de Email**

| Documento | Descrição | Localização |
|-----------|-----------|-------------|
| **CONFIGURAR_EMAIL.md** | Configuração geral de email | `docs/` |
| **CONFIGURAR_EMAIL_RENDER.md** | Email específico para Render | `docs/` |
| **SENDGRID_SETUP.md** | Setup do SendGrid | `docs/` |
| **STATUS_FINAL_EMAIL.md** | Status final da configuração | `docs/` |

### 🧪 **Testes**

| Documento | Descrição | Localização |
|-----------|-----------|-------------|
| **TESTING_GUIDE.md** | Guia completo de testes | `docs/` |
| **GUIA_TESTE_LOCAL.md** | Testes em ambiente local | `docs/` |

### 🔧 **Troubleshooting**

| Documento | Descrição | Localização |
|-----------|-----------|-------------|
| **TROUBLESHOOTING_CACHE.md** | Problemas com cache | `docs/troubleshooting/` |
| **USERPROFILE_DUPLICATE_FIX.md** | Correção de perfis duplicados | `docs/` |
| **FIX_MERGE_CONFLICT.md** | Resolução de conflitos de merge | `docs/` |

### 📊 **Estrutura e Organização**

| Documento | Descrição | Localização |
|-----------|-----------|-------------|
| **ESTRUTURA_PROJETO.md** | Estrutura detalhada do projeto | `docs/` |
| **ESTRUTURA_REORGANIZADA.md** | Histórico de reorganização | `docs/` |
| **REORGANIZACAO_COMPLETA.md** | Reorganização completa do projeto | `docs/` |

---

## 🔧 Scripts Disponíveis

### 🧪 **Testing** (`scripts/testing/`)

| Script | Descrição |
|--------|-----------|
| `test_all_improvements.py` | Testa todas as melhorias implementadas |
| `test_chatbot_fix.py` | Testa correções do chatbot |
| `test_rag.py` | Testa sistema RAG |
| `test_rag_integration_complete.py` | Teste completo de integração RAG |
| `test_recommendations_simple.py` | Testa sistema de recomendações |
| `test_quarta_asa_final.py` | Teste específico do bug "Quarta Asa" |
| `test_extraction_debug.py` | Debug de extração de dados |
| `test_quero_saber_variation.py` | Testa variações de perguntas |
| `test_rec_logic.py` | Testa lógica de recomendações |

### 🐛 **Debug** (`scripts/debug/`)

| Script | Descrição |
|--------|-----------|
| `debug_banner.py` | Debug completo de banners |
| `debug_banner_simple.py` | Debug simplificado de banners |

### 🔧 **Maintenance** (`scripts/maintenance/`)

| Script | Descrição |
|--------|-----------|
| `clear_cache.py` | Limpa cache do sistema |
| `clear_home_cache.py` | Limpa cache da home |

### 💾 **Database Maintenance** (`scripts/maintenance/database/`)

| Script | Descrição |
|--------|-----------|
| `fix_userprofile_duplicate.py` | Corrige perfis de usuário duplicados |
| `verify_userprofiles.py` | Verifica integridade de perfis |

### ⚙️ **Setup e Utilitários** (`scripts/`)

| Script | Descrição |
|--------|-----------|
| `setup_local_env.sh` | Setup automático de ambiente local |
| `start_local.sh` | Inicia servidor local |
| `quick_test.sh` | Testes rápidos |
| `diagnose_recommendations.sh` | Diagnóstico de recomendações |
| `check_recommendations_health.sh` | Verifica saúde do sistema |

---

## ⚙️ Configurações

### 📦 **Deployment** (`config/deployment/`)

| Arquivo | Descrição |
|---------|-----------|
| `build.sh` | Script de build para produção |
| `gunicorn_config.py` | Configuração do Gunicorn |
| `render.yaml` | Configuração do Render.com |

### 🔐 **Ambiente**

| Arquivo | Descrição | Localização |
|---------|-----------|-------------|
| `.env.example` | Template de variáveis de ambiente | Raiz |
| `.env` | Variáveis de ambiente (não versionado) | Raiz |
| `.env.backup_render_*` | Backups de configuração Render | Raiz |

---

## 🏗️ Aplicações Django

### 📱 **Aplicações Principais**

| App | Descrição | Principais Funcionalidades |
|-----|-----------|---------------------------|
| **core** | App principal | Livros, Autores, Categorias, Eventos, Seções, Vídeos |
| **accounts** | Autenticação | Perfis de usuário, Listas de leitura, Favoritos |
| **chatbot_literario** | Chatbot IA | Conversas, RAG, Knowledge Base, Groq API |
| **finance** | Financeiro | Assinaturas Premium, Campanhas, MercadoPago |
| **recommendations** | Recomendações | Sistema de sugestões de livros |
| **new_authors** | Autores Emergentes | Publicação de autores iniciantes |
| **debates** | Debates | Sistema de discussões sobre livros |

---

## 📝 Convenções do Projeto

### 🗂️ **Organização de Arquivos**

1. **Documentação (.md)** → `docs/` (subdividido por categoria)
2. **Scripts Python (.py)** → `scripts/` (subdividido por função)
3. **Configurações de deploy** → `config/deployment/`
4. **Templates HTML** → `templates/`
5. **Arquivos estáticos** → `static/`
6. **Media uploads** → `media/`
7. **Backups** → `backups/`

### 📋 **Nomenclatura**

- **Documentação:** `NOME_EM_MAIUSCULAS.md`
- **Scripts de teste:** `test_*.py`
- **Scripts de debug:** `debug_*.py`
- **Scripts de setup:** `setup_*.sh` ou `setup_*.py`
- **Configurações:** `*_config.py` ou `*.yaml`

---

## 🚀 Quick Start

### **1. Clone e Configure**
```bash
git clone <repository-url>
cd cgbookstore_v3
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### **2. Configure Ambiente**
```bash
cp .env.example .env
# Edite .env com suas credenciais
```

### **3. Prepare Database**
```bash
python manage.py migrate
python manage.py createsuperuser
```

### **4. Inicie Servidor**
```bash
python manage.py runserver
```

### **5. Acesse**
- **Site:** http://localhost:8000/
- **Admin:** http://localhost:8000/admin/
- **Dashboard:** http://localhost:8000/admin/dashboard/

---

## 🔗 Links Úteis

### **Documentação Externa**
- [Django Documentation](https://docs.djangoproject.com/)
- [Groq API Docs](https://console.groq.com/docs)
- [Render.com Docs](https://render.com/docs)
- [Supabase Docs](https://supabase.com/docs)
- [MercadoPago API](https://www.mercadopago.com.br/developers)

### **APIs Utilizadas**
- **Groq:** IA para chatbot literário
- **Google Books API:** Metadados e capas de livros
- **MercadoPago:** Pagamentos e assinaturas
- **SendGrid:** Envio de emails

---

## 📊 Estatísticas do Projeto

- **Aplicações Django:** 7 apps principais
- **Modelos de Dados:** ~30 models
- **Scripts de Teste:** 15+ scripts
- **Documentos:** 40+ arquivos .md
- **APIs Integradas:** 4 APIs externas
- **Features Principais:** Chatbot IA, RAG, Knowledge Base, Recomendações, Assinaturas

---

## 🆘 Precisa de Ajuda?

**📋 FAQ - Perguntas Frequentes:** [docs/FAQ.md](FAQ.md) ⭐ **NOVO!**
- 39 perguntas e respostas
- 11 categorias
- Exemplos práticos
- Troubleshooting passo a passo

**Problemas Específicos:**
1. **Problemas de Cache:** Ver `docs/troubleshooting/TROUBLESHOOTING_CACHE.md`
2. **Erro de Database:** Ver `docs/USERPROFILE_DUPLICATE_FIX.md`
3. **Deploy no Render:** Ver `docs/deployment/RENDER_PERFORMANCE_FIXES.md`
4. **Configurar Email:** Ver `docs/CONFIGURAR_EMAIL_RENDER.md`
5. **Chatbot não funciona:** Ver `docs/setup/GROQ_SETUP.md`

---

## 📌 Notas Importantes

⚠️ **Arquivos Sensíveis:**
- `.env` contém credenciais - NUNCA versionar
- Use `.env.example` como template
- Backups em `.env.backup_render_*` são apenas para referência

✅ **Antes de Deploy:**
- Execute testes: `python manage.py test`
- Colete estáticos: `python manage.py collectstatic`
- Verifique migrações: `python manage.py showmigrations`

🔄 **Atualizações:**
- Mantenha `requirements.txt` atualizado
- Documente mudanças importantes
- Faça backup antes de grandes alterações

---

**Última revisão:** 03/12/2025
**Versão do Projeto:** 3.0
**Python:** 3.11+
**Django:** 5.0+
