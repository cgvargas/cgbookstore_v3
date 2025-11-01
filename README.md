#  CGBookStore v3 📚✨

Uma livraria online moderna e responsiva construída com Django e Python, utilizando Supabase para um banco de dados PostgreSQL robusto e escalável. O projeto inclui um sistema completo de autenticação de usuários e a base para um assistente literário inteligente.

![badge-python] ![badge-django] ![badge-license]

<!-- Futuramente, adicione um screenshot da aplicação aqui -->
<!-- <p align="center">
  <img src="link_para_seu_screenshot.png" alt="Screenshot da Home Page da CGBookStore">
</p> -->

## 🎯 Status do Projeto

**Em Desenvolvimento Ativo.** As funcionalidades principais de catálogo e autenticação estão implementadas e funcionais.

## ✅ Funcionalidades Implementadas

### 📖 Core (Livraria)
-   **Catálogo de Livros:** Visualização de todos os produtos em um layout de cards.
-   **Página Inicial Dinâmica:** Apresenta os últimos livros cadastrados.
-   **Sistema de Busca:** Pesquisa funcional por título, autor ou categoria.
-   **Estrutura de Modelos:** Modelos de dados para Livros, Autores e Categorias.

### 👤 Autenticação & Contas (`accounts`)
-   **Registro de Usuários:** Formulário completo para criação de novas contas com validação.
-   **Login & Logout:** Sistema seguro utilizando as views nativas do Django.
-   **Navbar Dinâmica:** A interface se adapta para usuários logados e visitantes.
-   **Templates Integrados:** Páginas de login e registro seguindo a identidade visual do site.

### 🤖 Chatbot Literário (`chatbot_literario`)
-   **Estrutura Básica:** App criado com URLs e views de placeholder, pronto para desenvolvimento.

## 🔧 Tecnologias Utilizadas

-   **Backend:** Python 3.11+, Django 5.x
-   **Banco de Dados:** PostgreSQL (gerenciado pelo Supabase)
-   **Frontend:** HTML5, CSS3, Bootstrap 5
-   **Controle de Versão:** Git & GitHub

## 📁 Estrutura do Projeto

```
cgbookstore_v3/
├── accounts/               # Sistema de autenticação e usuários
├── core/                   # Catálogo de livros (modelos, views)
├── recommendations/        # Sistema de recomendações ML + IA
├── chatbot_literario/      # Chatbot inteligente
├── notifications/          # Sistema de notificações
├── config/                 # Configurações do Django
├── templates/              # Templates HTML
├── static/                 # Arquivos estáticos (CSS, JS, imagens)
├── media/                  # Uploads (capas de livros)
│
├── docs/                   # 📚 Documentação
│   ├── guides/            # Guias de uso
│   ├── testing/           # Documentação de testes
│   └── integration/       # Guias de integração
│
├── scripts/                # 🔧 Scripts utilitários
│   ├── setup/             # Scripts de configuração
│   ├── testing/           # Scripts de teste
│   └── maintenance/       # Scripts de manutenção
│
├── documents/              # Documentação técnica detalhada
│   └── status/            # Status do projeto
│
├── manage.py               # CLI do Django
├── requirements.txt        # Dependências Python
└── README.md              # Este arquivo
```

### 📖 Documentação

- **[docs/](docs/)** - Documentação completa organizada
- **[scripts/](scripts/)** - Scripts para desenvolvimento e testes

O projeto é organizado em apps Django, seguindo as melhores práticas da comunidade: