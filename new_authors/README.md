# Plataforma de Autores Emergentes - CG.BookStore v3

## Visão Geral

A Plataforma de Autores Emergentes é um módulo completo do CG.BookStore v3 que oferece espaço para novos talentos literários publicarem suas obras, interagirem com leitores e conectarem-se com editoras.

## Funcionalidades Principais

### Para Autores
- **Perfil de Autor**: Criação de perfil com biografia, foto e redes sociais
- **Publicação de Livros**: Upload de capas, sinopses e descrições completas
- **Gestão de Capítulos**: Sistema de capítulos com visualizador de texto integrado
- **Dashboard**: Estatísticas de visualizações, avaliações e interações
- **Controle de Status**: Rascunho, em revisão, publicado ou arquivado

### Para Leitores
- **Exploração de Livros**: Busca e filtros por gênero, avaliação e popularidade
- **Visualizador de Capítulos**: Leitura em interface otimizada
- **Sistema de Avaliações**: Avalie obras com 1-5 estrelas e comentários
- **Seguir Livros**: Receba notificações de novos capítulos
- **Livros Relacionados**: Descubra obras similares

### Para Editoras
- **Dashboard de Talentos**: Visualize livros mais bem avaliados
- **Expressão de Interesse**: Contacte autores diretamente
- **Análise de Métricas**: Avaliações, visualizações e engajamento da comunidade
- **Sistema de Verificação**: Perfil verificado para editoras autênticas

## Estrutura do Banco de Dados

### Models Principais

1. **EmergingAuthor**: Perfil do autor emergente
   - Informações pessoais e biografia
   - Redes sociais
   - Estatísticas (visualizações, livros, seguidores)
   - Status de verificação

2. **AuthorBook**: Livros publicados
   - Título, sinopse e descrição
   - Capa (imagem)
   - Gênero e tags
   - Status de publicação
   - Métricas (views, avaliações, curtidas)

3. **Chapter**: Capítulos dos livros
   - Número e título
   - Conteúdo textual
   - Arquivo opcional (PDF, DOCX, TXT)
   - Controle de acesso (gratuito/pago)
   - Contagem de palavras e visualizações

4. **AuthorBookReview**: Avaliações dos leitores
   - Avaliação de 1-5 estrelas
   - Título e comentário
   - Sistema de "útil"
   - Moderação

5. **BookFollower**: Seguidores de livros
   - Preferências de notificação
   - Data de início do acompanhamento

6. **PublisherProfile**: Perfil de editoras
   - Informações da empresa
   - Contatos
   - Status de verificação

7. **PublisherInterest**: Interesse de editoras em autores
   - Mensagem personalizada
   - Status da negociação

## URLs e Rotas

Todas as rotas começam com `/novos-autores/`:

### Rotas Públicas
- `/novos-autores/` - Lista de todos os livros
- `/novos-autores/livro/<slug>/` - Detalhes do livro
- `/novos-autores/livro/<slug>/capitulo/<numero>/` - Visualizador de capítulo
- `/novos-autores/autor/<username>/` - Perfil público do autor
- `/novos-autores/buscar/` - Busca avançada
- `/novos-autores/em-alta/` - Livros em destaque

### Rotas de Autores (requer login)
- `/novos-autores/tornar-se-autor/` - Registro como autor
- `/novos-autores/dashboard/` - Dashboard do autor

### API Endpoints (requer login)
- `POST /novos-autores/api/seguir/<book_id>/` - Seguir/deixar de seguir livro
- `POST /novos-autores/api/avaliar/<book_id>/` - Submeter avaliação
- `POST /novos-autores/api/review/<review_id>/util/` - Marcar review como útil

### Rotas de Editoras (requer login e perfil verificado)
- `/novos-autores/editora/dashboard/` - Dashboard da editora
- `POST /novos-autores/api/interesse/<book_id>/` - Expressar interesse em autor

## Administração Django

Acesse em `/admin/` após login com credenciais de superusuário.

### Painéis Disponíveis

1. **Autores Emergentes**
   - Aprovar/verificar autores
   - Gerenciar perfis e estatísticas

2. **Livros**
   - Publicar/arquivar livros
   - Editar informações e capas
   - Ver estatísticas detalhadas

3. **Capítulos**
   - Publicar/despublicar capítulos
   - Editar conteúdo
   - Ver métricas de leitura

4. **Avaliações**
   - Moderar comentários
   - Aprovar/reprovar reviews
   - Destacar avaliações importantes

5. **Editoras**
   - Verificar editoras
   - Gerenciar interesses

## Como Usar

### Para se tornar um Autor

1. Crie uma conta ou faça login
2. Acesse `/novos-autores/tornar-se-autor/`
3. Preencha sua biografia
4. Submeta o formulário

### Para Publicar um Livro

1. Acesse o Django Admin (`/admin/`)
2. Vá em "Autores Emergentes" > "Livros de Autores Emergentes"
3. Clique em "Adicionar Livro"
4. Preencha:
   - Título, sinopse e descrição
   - Faça upload da capa (recomendado: 600x900px)
   - Selecione o gênero
   - Adicione tags (JSON: `["fantasia", "aventura"]`)
5. Altere o status para "Publicado"
6. Salve

### Para Adicionar Capítulos

1. No admin, acesse "Capítulos"
2. Adicione novo capítulo
3. Selecione o livro
4. Defina número e título
5. Cole ou escreva o conteúdo
6. Marque como "Publicado"
7. Salve

**Dica**: Você também pode adicionar capítulos diretamente na página de edição do livro usando a seção "Capítulos" inline.

### Para Editoras

1. Crie um perfil de editora no admin
2. Aguarde verificação pelo administrador
3. Acesse o dashboard em `/novos-autores/editora/dashboard/`
4. Explore talentos e expresse interesse

## Características Técnicas

### Otimizações
- Queries otimizadas com `select_related` e `prefetch_related`
- Índices de banco de dados para buscas rápidas
- Paginação em todas as listagens
- Cache de contadores e estatísticas

### Segurança
- Validação de permissões em todas as views
- Proteção CSRF em formulários
- Sanitização de entradas de usuário
- Moderação de conteúdo

### Responsividade
- As views retornam dados preparados para templates responsivos
- Sistema pronto para integração com frontend moderno (React, Vue, etc.)
- API endpoints para aplicativos móveis futuros

## Próximos Passos

### Templates (Não incluídos nesta versão)
Você precisará criar templates em `new_authors/templates/new_authors/`:

1. `books_list.html` - Lista de livros
2. `book_detail.html` - Detalhes do livro
3. `chapter_read.html` - Visualizador de capítulo
4. `author_profile.html` - Perfil do autor
5. `become_author.html` - Formulário para se tornar autor
6. `author_dashboard.html` - Dashboard do autor
7. `publisher_dashboard.html` - Dashboard da editora
8. `search_results.html` - Resultados de busca
9. `trending_books.html` - Livros em alta

### Sistema de Notificações
- Implementar notificações por email para novos capítulos
- Alertas para autores sobre novas avaliações
- Notificações para editoras sobre respostas de autores

### Monetização
- Sistema de capítulos premium
- Assinaturas para leitores
- Comissões para a plataforma em conexões autor-editora

## Integração com Sistema Existente

O módulo se integra perfeitamente com:
- Sistema de autenticação do Django (User)
- Sistema de upload de mídia (Supabase Storage)
- Sistema de emails (Brevo API)
- Django Admin

## Suporte e Contribuições

Para dúvidas ou sugestões, entre em contato ou abra uma issue no repositório.

---

**Desenvolvido com Django 5.1+**
**Versão: 1.0.0**
**Última atualização: Novembro 2025**
