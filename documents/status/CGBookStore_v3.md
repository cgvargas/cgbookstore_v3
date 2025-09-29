# CGBookStore v3 - PROJETO EM DESENVOLVIMENTO ATIVO!

## 🎯 Status do Projeto

| Componente       | Status            | Descrição                                              |
|------------------|------------------|--------------------------------------------------------|
| Banco de Dados   | ✅ CONECTADO      | PostgreSQL 17.6 no Supabase                            |
| Ambiente Virtual | ✅ ATIVO          | Python com todas as dependências                       |
| Django Project   | ✅ CONFIGURADO    | cgbookstore configurado                                |
| Apps             | ✅ INSTALADOS     | core, chatbot_literario, accounts                      |
| Migrações        | ✅ APLICADAS      | Tabelas de core e auth criadas                         |
| Modelos          | ✅ IMPLEMENTADOS  | Book, Author, Category (em core)                       |
| Views & URLs     | ✅ IMPLEMENTADAS  | Mapeamento completo para core e accounts               |
| Formulários      | ✅ IMPLEMENTADOS  | Formulário de registro de usuário                      |
| Autenticação     | ✅ IMPLEMENTADA   | Ciclo de Registro, Login e Logout funcional            |
| Templates        | ✅ ESTRUTURADOS   | base.html + templates para core e accounts             |
| Admin            | ✅ CONFIGURADO    | Interface administrativa pronta                        |

---

## 📁 Estrutura do Projeto (Atualizada)

```bash
C:\Users\claud\OneDrive\ProjectsDjango\CGBookStore_v3\
├── 📁 cgbookstore/
│   ├── settings.py          # Configurado com apps, templates e redirects
│   └── urls.py              # URLs principais incluindo core, chatbot e accounts
├── 📁 core/
│   ├── models.py            # Modelos Book, Author, Category definidos
│   ├── views.py             # HomeView, BookListView, SearchView implementadas
│   ├── urls.py              # URLs de core definidas
│   └── admin.py
├── 📁 chatbot_literario/
│   ├── models.py
│   ├── views.py             # ChatbotView de placeholder criada
│   └── urls.py              # URL de placeholder criada
├── 📁 accounts/              # NOVO APP de autenticação
│   ├── forms.py             # UserRegisterForm customizado
│   ├── views.py             # register_view implementada
│   ├── urls.py              # URLs de login, logout e registro
│   └── admin.py
├── 📁 templates/
│   ├── 📁 core/              # Templates do app principal
│   │   ├── home.html
│   │   ├── book_list.html
│   │   └── search_results.html
│   ├── 📁 accounts/          # Templates de autenticação
│   │   ├── login.html
│   │   └── register.html
│   └── base.html            # Template base com Navbar dinâmica
├── 📁 static/
├── 📁 venv/
├── .env
├── manage.py
└── requirements.txt
```

---

## 🚀 Como Usar

### 1. Ativar Ambiente Virtual

```powershell
cd C:\Users\claud\OneDrive\ProjectsDjango\CGBookStore_v3
.\venv\Scripts\activate
```

### 2. Executar o Servidor

```powershell
python manage.py runserver
```

### 3. Acessar o Sistema

| URL                                   | Descrição                               |
|---------------------------------------|-----------------------------------------|
| http://localhost:8000                 | Página inicial                          |
| http://localhost:8000/livros          | Catálogo de livros                      |
| http://localhost:8000/buscar          | Busca avançada                          |
| http://localhost:8000/contas/registrar/ | Página de registro de novo usuário     |
| http://localhost:8000/contas/login/   | Página de login                         |
| http://localhost:8000/contas/logout/  | Ação de logout                          |
| http://localhost:8000/admin           | Painel administrativo                   |
| http://localhost:8000/chatbot         | Assistente literário (placeholder)       |

---

## 📝 Funcionalidades Implementadas

### Core (Livraria)
- ✅ Página Inicial com listagem dos últimos livros cadastrados.
- ✅ Catálogo de Livros para visualização de todos os produtos.
- ✅ Sistema de Busca funcional que pesquisa por título, autor e categoria.
- ✅ Modelos de Dados para Livros, Autores e Categorias.

### Autenticação & Contas
- ✅ Sistema de Registro de novos usuários com e-mail.
- ✅ Sistema de Login e Logout utilizando as views seguras do Django.
- ✅ Formulários customizados e estilizados para uma melhor experiência.
- ✅ Templates integrados ao design principal do site.
- ✅ Barra de Navegação Dinâmica que exibe o nome do usuário logado e links contextuais.

### Chatbot Literário
- ✅ Estrutura básica do app criada (views e urls de placeholder).

### Interface
- ✅ Template base responsivo com Bootstrap 5.
- ✅ Navbar com menu completo e links funcionais.
- ✅ Cards de livros para exibição dos produtos.

---

## 🎨 Próximas Melhorias Sugeridas
- Criar a View de Detalhes do Livro  
  *Permitir que o usuário clique em um livro para ver mais informações.*
- Popular o Banco de Dados  
  *Adicionar livros, autores e categorias através do painel Admin para testar a visualização.*
- Configurar Supabase Storage  
  *Criar os buckets (book-covers) e testar o upload de imagens de capa.*
- Implementar a Lógica do Chatbot  
  *Integrar com uma API como OpenAI/Ollama ou criar um sistema de respostas simples.*
- Segurança e Permissões  
  *Restringir o acesso a certas páginas (ex: "Minha Conta") apenas para usuários logados.*

---

🎉 **Projeto com funcionalidades básicas implementadas e pronto para evoluir!**  

📅 Última atualização: **28/09/2025**
