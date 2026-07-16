# Auditoria Arquitetural da CG.BookStore

## Preparação para integração escalável com parceiros comerciais e Amazon Associados

**Data da auditoria:** 16/07/2026
**Escopo:** análise estática do repositório local `cgbookstore_v3`
**Natureza:** somente arquitetura; nenhum código, model ou migration foi alterado
**Observação:** o banco de produção e o painel da Amazon não foram inspecionados. Conformidade jurídica e com as regras vigentes do Programa de Associados deve ser validada separadamente antes da entrada em produção.

---

## 1. Sumário executivo

A CG.BookStore é hoje um **monólito modular Django**. Os domínios estão separados em apps, mas dentro de cada app predomina uma arquitetura Django tradicional/Active Record: models concentram estado e parte das regras, views orquestram casos de uso, templates contêm lógica de apresentação e JavaScript, e services são usados de forma seletiva. Não é Clean Architecture estrita, embora haja uma base modular útil e reaproveitável.

Já existe um app `partners`, instalado e roteado, contendo:

- `AffiliatePartner`, para configuração de parceiros;
- `AffiliatePartnerClick`, para telemetria de cliques;
- `AffiliateService`, para resolver o parceiro e montar o link com tracking;
- uma view intermediária de registro e redirecionamento;
- administração e gráficos de cliques;
- testes básicos de resolução, geração de link e rastreamento.

Portanto, a integração não parte do zero. O problema central é que o novo app foi acoplado ao modelo legado: `Book` ainda armazena `purchase_partner_name` e `purchase_partner_url` como strings, e o parceiro é descoberto por comparação textual. O resultado é uma implementação funcional para um parceiro por livro, mas ainda frágil para múltiplos parceiros, múltiplos formatos/ofertas, automação, governança, segurança de domínio e evolução incremental.

### Conclusão arquitetural

A direção recomendada é **preservar o monólito modular e evoluir o app `partners`**, sem microserviços nesta fase. O núcleo da próxima implementação deve ser uma entidade de oferta comercial vinculando `Book` a `AffiliatePartner`, acompanhada por serviços de aplicação para resolver oferta, construir link e registrar clique. Os campos legados de `Book` devem permanecer temporariamente como fallback durante uma migração em etapas.

### Principais riscos

1. **Alto — parceiro ligado ao livro por texto**, sem FK ou entidade de oferta.
2. **Alto — importação de livros duplicada e não transacional**, com criação direta de entidades em duas views.
3. **Alto — ausência de validação do domínio de destino**, apesar do redirecionamento externo e da inserção de tracking.
4. **Alto — coleta de IP, sessão, usuário, User-Agent, referer e idioma sem governança técnica explícita de consentimento, retenção e anonimização.**
5. **Alto — ISBN, autores e categorias perdem fidelidade de edição:** apenas um ISBN, um autor e uma categoria são persistidos.
6. **Médio — CTA de compra e seu JavaScript estão duplicados** em dois templates extensos.
7. **Médio — regras de afiliado estão expostas como propriedades de `Book`**, invertendo a dependência entre catálogo e parceiros e gerando consultas repetidas.

Não foi identificado um defeito arquitetural que, isoladamente e com as evidências disponíveis, deva ser classificado como **Crítico**. Há, contudo, vários riscos Altos que devem bloquear a ampliação da monetização até serem endereçados.

---

## 2. Método e limites

Foram inspecionados:

- configuração Django, apps instalados, middleware, banco, cache, storage e rotas;
- models e migrations relevantes;
- Django Admin e templates customizados;
- integração Google Books e assistente administrativo por IA;
- fluxo user-facing de importação;
- detalhe do livro, página de resenhas, cards e consumidor do chatbot;
- app `partners`, serviço, redirect, tracking, admin e testes;
- modelos de usuário, biblioteca, gamificação e eventos;
- services, helpers, signals e management commands.

Não foram executadas migrations nem realizadas escritas no banco. Dados reais de produção, qualidade do catálogo em Supabase, credenciais, métricas reais e configuração da conta Amazon ficaram fora do escopo.

---

## 3. Mapa completo da arquitetura atual

### 3.1 Estilo arquitetural

**Classificação:** monólito modular Django, com Active Record e camadas informais.

```text
Browser / Django Admin
        |
        v
URLs -> Views / DRF endpoints
        |
        +--> Services e utils (uso seletivo)
        |
        +--> Models Django com regras de domínio
        |
        v
Templates + JavaScript
        |
        v
PostgreSQL/Supabase ou SQLite local
Redis/Celery | Supabase/R2 Storage | APIs externas
```

Os apps são registrados em [settings.py](../cgbookstore/settings.py#L40), o middleware em [settings.py](../cgbookstore/settings.py#L81), o banco em [settings.py](../cgbookstore/settings.py#L116) e as rotas de topo em [urls.py](../cgbookstore/urls.py#L1).

Pontos positivos:

- separação por domínio em apps Django;
- `core` e `accounts` já modularizam models, views e admin em arquivos menores;
- existência de services para IA, recomendações, pagamento e afiliados;
- Redis, Celery e storage abstrato já disponíveis;
- templates e rotas com namespaces;
- índices e `select_related` em pontos de alto uso;
- signals centralizados por app e commands operacionais existentes.

Limitações:

- casos de uso escrevem diretamente via ORM nas views;
- regras residem simultaneamente em models, views, templates, JS, signals e services;
- dependências cruzadas entre apps são frequentes e geralmente concretas;
- não há camada formal de aplicação/repositórios/ports;
- alguns templates e admins misturam HTML, CSS, JS e orquestração em arquivos extensos.

### 3.2 Apps Django e responsabilidades

| App | Responsabilidade observada | Estrutura predominante |
|---|---|---|
| `core` | Catálogo, livros, autores, categorias, home dinâmica, vídeos/adaptações, eventos, banners, universos, dashboards e ferramentas admin | models/views/admin modularizados, services, utils, signals, tasks e muitos commands |
| `accounts` | Perfil, biblioteca pessoal, progresso, resenhas, notificações, gamificação e exclusão de conta | pacote de models, views/forms, signals, admin e commands |
| `partners` | Parceiros afiliados, geração de links, redirect e tracking de cliques | models, service, view, admin, URLs e testes |
| `recommendations` | Interações, similaridade, recomendações e perfil de leitor por IA | models, services, tasks, API/views |
| `chatbot_literario` | Assistente literário e suporte, sessões, conhecimento e provedores de IA | services grandes, models, DRF views, commands |
| `news` | Notícias, artigos, tags, quizzes, newsletter e agente RSS/IA | models monolítico, services, tasks/scheduler, signals e commands |
| `debates` | Tópicos, posts e votos em debates | models, views, URLs e admin |
| `new_authors` | Autores emergentes, obras, capítulos, editoras e planos | models monolítico, views, services e pagamentos |
| `finance` | Assinaturas, produtos, pedidos, Mercado Pago e campanhas | models, services, signals, tasks, admin e commands |
| `ereader` | E-books, biblioteca digital, progresso, bookmarks, highlights e conversão | models, services externos, signals e commands |
| `monitoring` | Atividades suspeitas, alertas de IA e WhatsApp | models, detector, tasks e command |

### 3.3 Camadas e componentes transversais

#### Models

- `core/models/`: 13 arquivos/modelos exportados por [core/models/__init__.py](../core/models/__init__.py#L6).
- `accounts/models/`: perfil, biblioteca, progresso, resenhas, notificações e gamificação exportados por [accounts/models/__init__.py](../accounts/models/__init__.py#L5).
- Demais apps mantêm models concentrados em `models.py`.

#### Views

- `core/views/` está dividido por caso de tela/endpoint e reexportado por `core/views/__init__.py`.
- Outros apps usam views monolíticas ou poucos arquivos.
- Há views baseadas em classe para páginas e funções/DRF para APIs e ações.

#### Services

- `core/services`: provedores de IA, assistente de cadastro, resenhas, notificações, verificação e geradores de formulário.
- `partners/services`: geração/resolução de links afiliados.
- `recommendations/services`: recomendação e perfil do leitor.
- `news/services`: RSS, Gemini, imagem e storage.
- `new_authors/services`: pagamentos e manuscritos.
- `ereader/services`: Gutenberg e Open Library.
- `finance/services.py`: Mercado Pago e campanhas.

#### Helpers/utilitários

- [core/utils/google_books_api.py](../core/utils/google_books_api.py#L18): busca, extração, download de capa, datas e atualização.
- `core/utils/supabase_storage.py`: acesso específico ao Supabase Storage.
- helpers adicionais estão distribuídos em services, templatetags e scripts operacionais.

#### Middleware

- `RateLimitMiddleware`: converte `Ratelimited` em resposta 429.
- `PerformanceMonitoringMiddleware`: adiciona `Server-Timing` e registra requests acima de 1,5 s.
- Ambos estão em [core/middleware.py](../core/middleware.py#L10) e registrados globalmente.

#### Signals

- `accounts`: cria/salva `UserProfile` junto ao `User` e cria notificação inicial.
- `core`: invalidação de cache, limpeza assíncrona de mídias de livros e timeout de conexão PostgreSQL.
- `news`: insere artigos publicados nas seções da home.
- `finance`: sincroniza assinaturas/pedidos/campanhas.
- `ereader`: conversão de arquivos Kindle no `pre_save`.

#### Management commands

| App | Commands observados |
|---|---|
| `accounts` | `check_reading_deadlines`, `fix_missing_progress`, `populate_achievements` |
| `core` | `add_book_covers`, `check_books`, `clean_book_descriptions`, `cleanup_socialapps`, `create_tolkien_universe`, `download_book_covers`, `fix_book_covers`, `fix_duplicates`, `fix_section_contenttypes`, `health_check`, `import_author_books`, `migrate_from_supabase`, `migrate_media_to_supabase`, `migrate_supabase_to_r2`, `populate_child_shelves`, `populate_db`, `populate_sections`, `populate_shelf`, `setup_initial_data`, `setup_supabase`, `sync_media_paths`, `test_google_books`, `update_author_books`, `update_covers_google`, `upload_local_media_to_r2`, `verify_news_impl` |
| `chatbot_literario` | `add_navigation_knowledge`, `generate_knowledge_keywords`, `test_gemini`, `update_debate_knowledge` |
| `ereader` | `import_popular_books` |
| `finance` | `check_expiring_premium`, `process_campaigns` |
| `monitoring` | `test_monitoring` |
| `new_authors` | `populate_plans` |
| `news` | `generate_news_posts`, `setup_news_sources` |

Scripts fora da convenção de management command também são numerosos em `scripts/`. Eles devem ser considerados ferramentas operacionais, não uma camada de aplicação estável.

### 3.4 Infraestrutura e dependências externas

- Banco: `DATABASE_URL`, com SQLite local e PostgreSQL/Supabase em produção.
- Cache e broker: Redis; Celery já configurado.
- Mídia: Cloudflare R2, Supabase Storage ou filesystem conforme settings.
- APIs: Google Books, Gemini, Groq, OpenAI/Claude via abstração, Open Library, Gutenberg, Mercado Pago, serviços de e-mail.
- Frontend: Django Templates, Bootstrap, Font Awesome e JavaScript próprio.

Esses componentes permitem implementar processamento assíncrono, cache e observabilidade de parceiros sem introduzir nova infraestrutura.

---

## 4. Modelos principais e relacionamentos

### 4.1 Livro (`core.Book`)

O model [Book](../core/models/book.py#L13) reúne quatro responsabilidades:

1. identidade e catálogo (`title`, slug, autor, categoria, descrição);
2. dados editoriais/de edição (`publication_date`, ISBN, editora, páginas, idioma);
3. metadados externos Google (`google_books_id`, ratings e links);
4. apresentação/comércio (`price`, parceiro, URL, formatos e pré-venda).

Relacionamentos atuais:

- `Book -> Author`: FK opcional com `SET_NULL` ([book.py](../core/models/book.py#L31));
- `Book -> Category`: FK opcional com `SET_NULL` ([book.py](../core/models/book.py#L39));
- `Book <- Event`: M2M de eventos;
- `Book <- BookShelf`, `ReadingProgress`, `BookReview`, recomendações e interações;
- `Book <- AffiliatePartnerClick`: FK do log de cliques;
- não existe relação persistida `Book -> AffiliatePartner`.

Pontos positivos:

- IDs Google e ISBN possuem unicidade;
- campos Google relevantes são preservados;
- metadados de criação/alteração e índices existem;
- slug possui fallback de unicidade quando deixado vazio;
- o model já fornece URL canônica da página.

Pontos de melhoria:

- um livro só pode ter um autor e uma categoria, embora Google retorne listas;
- ISBN-10 e ISBN-13 não são armazenados separadamente;
- `price` não possui moeda, fonte nem data de aferição;
- formato e disponibilidade são propriedades de edição/oferta, não necessariamente da obra abstrata;
- o model acumula regras comerciais e importa `partners` em propriedades ([book.py](../core/models/book.py#L297));
- índices explícitos de `isbn` e `google_books_id` são redundantes com `unique=True`;
- `purchase_partner_name` e `purchase_partner_url` duplicam o novo domínio de parceiros.

### 4.2 Categoria (`core.Category`)

[Category](../core/models/category.py#L10) contém nome único, slug único, destaque e criação. É simples e coeso. A importação usa apenas a primeira categoria retornada pelo Google. Há uma `news.Category` separada, o que é aceitável como contexto distinto, desde que não sejam tratadas como a mesma taxonomia.

### 4.3 Autor (`core.Author`)

[Author](../core/models/author.py#L10) contém identidade, biografia, foto e redes. O vínculo com `Book` é 1:N, portanto coautoria não é representável. A importação guarda apenas o primeiro autor retornado. `AuthorWork` mantém ainda uma lista editorial de obras separada do catálogo, criando sobreposição conceitual que deve ser documentada, mas não precisa ser eliminada para a integração Amazon.

### 4.4 Usuário

O projeto usa `django.contrib.auth.models.User`, sem custom user model. [UserProfile](../accounts/models/user_profile.py#L39) estende o usuário por OneToOne e agrega personalização, premium, preferências, estatísticas e gamificação.

Redundâncias relevantes:

- `UserProfile.badges` em JSON convive com `UserBadge` relacional;
- `custom_shelves_list` em JSON convive com linhas `BookShelf` de tipo `custom`;
- `books_read_count` e `total_pages_read` são contadores desnormalizados derivados de progresso/prateleiras.

São otimizações possíveis, mas atualmente existem múltiplas fontes de verdade e atualização distribuída.

### 4.5 Biblioteca

[BookShelf](../accounts/models/book_shelf.py#L12) materializa a relação usuário-livro por tipo de prateleira. Possui restrição composta, índices e datas de início/fim. O `save()` também concede XP, incrementa contadores e streak ([book_shelf.py](../accounts/models/book_shelf.py#L115)), misturando persistência da biblioteca com gamificação.

[ReadingProgress](../accounts/models/reading_progress.py#L15) mantém progresso único por usuário/livro, verificação, prazos e abandono. Ao concluir, chama métodos que atualizam prateleira e XP. A biblioteca é funcional e reaproveitável no modal anterior à compra, mas suas regras deveriam ser chamadas por um caso de uso, não duplicadas nos models/views.

### 4.6 Gamificação

Modelos principais:

- `UserProfile`: XP total, nível, streak e contadores;
- `Achievement` / `UserAchievement`;
- `Badge` / `UserBadge`;
- `MonthlyRanking`;
- `XPMultiplier`.

A importação user-facing concede 15 XP diretamente na view. A navegação por recomendação/categoria também concede XP nas views. Conclusão de leitura concede XP em `ReadingProgress` e `BookShelf`. Essa dispersão dificulta idempotência, auditoria e evolução futura da monetização.

Foi identificado também acesso a `progress.book.num_pages` em `MonthlyRanking`, enquanto `Book` define `page_count`; o fallback é inconsistente e pode falhar quando acionado.

### 4.7 Eventos

[Event](../core/models/event.py#L9) relaciona livros e autores por M2M e guarda preço/inscrição. `is_free` é redundante com `price`. O `status` é recalculado somente no `save()`, logo pode ficar temporalmente desatualizado. Não afeta o primeiro rollout Amazon, mas é relevante para monetização futura de eventos.

### 4.8 Parceiros

[AffiliatePartner](../partners/models.py#L7) contém nome, slug, tracking ID, URL base, aparência, ativo e prioridade.

[AffiliatePartnerClick](../partners/models.py#L91) registra:

- usuário ou sessão;
- livro e parceiro;
- URL final;
- IP, User-Agent, browser, sistema, device, referer e idioma;
- timestamp e índices analíticos.

Não existe entidade de oferta/link que conecte um livro a um parceiro. `prioridade` e `url_base` não participam da resolução atual.

---

## 5. Fluxo completo de cadastro e importação de livros

Há três caminhos relevantes, não apenas um.

### 5.1 Caminho A — importação pelo Django Admin / Google Books

```text
Staff
  -> /admin/google-books/search/
  -> google_books_search
  -> core.utils.google_books_api.search_books
  -> template de resultados
  -> POST /admin/google-books/import/<google_id>/
  -> get_book_by_id
  -> busca/cria Author e Category
  -> cria Book diretamente
  -> baixa capa e salva no storage
  -> redireciona para changelist de Book
  -> administrador edita campos faltantes/comerciais
```

Arquivos envolvidos:

- patch de URLs do admin: [core/admin/__init__.py](../core/admin/__init__.py#L34);
- views: [google_books_views.py](../core/views/google_books_views.py#L14);
- cliente/normalização: [google_books_api.py](../core/utils/google_books_api.py#L22);
- tela: [google_books_search.html](../templates/admin/core/book/google_books_search.html#L406);
- formulário/admin: [book_admin.py](../core/admin/book_admin.py#L75) e [change_form.html](../templates/admin/core/book/change_form.html#L356).

Etapas exatas da importação:

1. staff pesquisa por título, autor, ISBN, editora ou texto;
2. Google Books é chamado com `langRestrict=pt` e paginação;
3. o resultado é normalizado;
4. no POST, duplicidade é verificada somente por ISBN;
5. apenas o primeiro autor é procurado/criado;
6. apenas a primeira categoria é procurada/criada;
7. `Book.objects.create()` persiste os campos retornados;
8. capa é baixada de forma síncrona e associada em um segundo `save()`;
9. preço Google é usado quando disponível;
10. parceiro e URL não são preenchidos por esse importador; ficam para edição posterior.

### 5.2 Caminho B — assistente administrativo por IA no formulário de Book

O formulário de Book possui um painel de IA. Staff pode fornecer texto/arquivo; o endpoint usa Open Library/Google Books e Gemini, devolvendo metadados e preenchendo o formulário no navegador.

O assistente:

- preenche ISBN, preço, autor/categoria sugeridos, ratings e formatos;
- baixa capa temporária;
- força `purchase_partner_name = Amazon`;
- constrói `https://www.amazon.com.br/dp/<isbn10>` quando consegue converter ISBN para ISBN-10 ([ai_book_assistant.py](../core/services/ai_book_assistant.py#L280));
- o JavaScript preenche diretamente os campos legados de parceiro no form ([change_form.html](../templates/admin/core/book/change_form.html#L558));
- `BookAdmin.save_model()` move a capa temporária para o campo definitivo ([book_admin.py](../core/admin/book_admin.py#L232)).

Esse caminho reduz o preenchimento manual, mas introduz hardcode de Amazon e mantém a regra comercial dentro do assistente de catálogo.

### 5.3 Caminho C — importação por usuário autenticado

```text
Usuário autenticado
  -> modal global/adicionar livro
  -> busca local + Google em paralelo
  -> POST /api/books/import-google/<google_id>/
  -> validação mínima para não-superuser
  -> busca/cria Author e Category
  -> cria Book diretamente
  -> baixa capa de forma síncrona
  -> concede 15 XP
```

Arquivos envolvidos:

- endpoints: [core/urls.py](../core/urls.py#L147);
- view: [book_search_views.py](../core/views/book_search_views.py#L22);
- JS: `static/js/book-search.js` e `static/js/global-search.js`;
- modais: `templates/core/modals/add_book_modal.html` e `global_search_modal.html`;
- testes de qualidade: [core/test_import.py](../core/test_import.py#L7).

Para usuários comuns, são exigidos capa, autor, ISBN, descrição mínima e páginas. Superusers ignoram essa política. O comentário afirma que a capa é assíncrona, mas `download_cover()` é chamado na própria request antes da resposta ([book_search_views.py](../core/views/book_search_views.py#L264)).

### 5.4 Informações Google preservadas

Preservadas atualmente:

- Google Books ID;
- título e subtítulo;
- primeiro autor;
- editora;
- data normalizada;
- um ISBN, priorizando ISBN-13 e usando ISBN-10 como fallback;
- páginas;
- primeira categoria;
- idioma;
- capa baixada para storage próprio;
- preview/info link;
- rating e contagem;
- preço, quando a API fornece.

Não preservadas adequadamente:

- ambos ISBN-10 e ISBN-13;
- lista completa de autores;
- lista completa de categorias;
- identificadores de edição além de Google ID/ISBN escolhido;
- origem e instante de cada metadado;
- `saleability`, moeda, formato de venda e demais dados de oferta;
- URL original da capa e variante/tamanho escolhido;
- payload bruto ou versão de sincronização.

### 5.5 Fragilidades dos fluxos de importação

- lógica duplicada entre admin e usuário;
- criação direta de `Author`, `Category` e `Book` nas views;
- ausência de `transaction.atomic()` para a unidade de importação;
- `slugify(title)` é passado explicitamente, impedindo o fallback de unicidade do `Book.save()`;
- duplicidade não é verificada de forma uniforme por Google ID, ISBN-10, ISBN-13 e edição;
- chamadas simultâneas podem criar corrida entre o check e o insert;
- data ausente/inválida vira `2000-01-01`, criando dado aparentemente real;
- string vazia é gravada em campos únicos anuláveis em alguns caminhos;
- capa e banco podem ficar parcialmente sincronizados quando uma etapa falha;
- erros são devolvidos com detalhes de exceção em alguns endpoints;
- criação por qualquer usuário autenticado altera o catálogo global e concede XP, ampliando o risco de abuso e dados ruins.

---

## 6. Fluxo completo do botão de compra

### 6.1 Fluxo atual

```text
Book.purchase_partner_name + Book.purchase_partner_url
        |
        v
Propriedades affiliate_* de Book
        |
        +--> AffiliateService.get_partner_for_book()
        |      compara nome/slug com AffiliatePartner ativo
        |
        v
Template monta CTA
        |
        +--> usuário não autenticado/preferência skip: abre rota de redirect
        |
        +--> usuário autenticado: modal opcional para adicionar à biblioteca
                  |
                  v
             rota de redirect
                  |
                  v
partners.views.redirect_to_partner
        |
        +--> carrega Book e Partner
        +--> lê URL legada do Book
        +--> acrescenta/substitui ?tag=<tracking_id>
        +--> cria sessão se necessário
        +--> evita duplicata por 10 segundos
        +--> registra AffiliatePartnerClick
        +--> HTTP redirect para URL externa
```

### 6.2 Onde o botão é construído

O botão é construído no template, não na view:

- detalhe: [book_detail.html](../templates/core/book_detail.html#L493);
- resenhas: [book_reviews.html](../templates/core/book_reviews.html#L47).

As propriedades de apresentação e URL são montadas em [Book](../core/models/book.py#L297):

- `affiliate_partner`;
- `affiliate_url`;
- `affiliate_button_class`;
- `affiliate_icon_class`;
- `affiliate_display_name`.

### 6.3 Onde ocorre o redirecionamento

- rotas: [partners/urls.py](../partners/urls.py#L6);
- controller: [partners/views.py](../partners/views.py#L76);
- construção de link: [affiliate_service.py](../partners/services/affiliate_service.py#L13).

A view registra o clique e retorna `redirect(url_final)`. O `partner_id` da URL é aceito se o parceiro estiver ativo, sem validar se corresponde ao parceiro textual do livro.

### 6.4 Comportamento do modal de biblioteca

Usuários autenticados podem adicionar o livro a uma prateleira antes de prosseguir. A preferência `skip_quick_add_modal` fica em `localStorage`. A implementação do modal e de suas funções está duplicada no detalhe e na página de resenhas ([book_detail.html](../templates/core/book_detail.html#L2065), [book_reviews.html](../templates/core/book_reviews.html#L509)).

### 6.5 Outros consumidores

O chatbot serializa `affiliate_display_name` e `affiliate_url` em [knowledge_retrieval.py](../chatbot_literario/knowledge_retrieval.py#L290). Assim, qualquer alteração do contrato precisa considerar não apenas os templates, mas também as respostas da IA.

### 6.6 Semântica incorreta observada

`BookDetailView` chama a existência de um clique de `has_purchased_before` e exibe “já demonstrou interesse nesta compra” ([book_detail_view.py](../core/views/book_detail_view.py#L33)). Um clique não comprova compra/conversão. O nome de contexto deve representar “clicou/visitou oferta anteriormente”, e métricas de conversão precisam de fonte própria.

---

## 7. Administração atual

### Livros

O admin de Book já oferece:

- busca e filtros;
- `select_related` de autor/categoria;
- autocomplete de autor/categoria;
- fieldsets separados;
- Google Books ID e metadados;
- preço, nome e URL do parceiro no fieldset “Compra e Imagens”;
- assistente de IA;
- capa temporária;
- artigos e vídeos relacionados.

É uma boa base operacional, mas o parceiro é texto livre. Não há inline/select de ofertas por parceiro, validação de host, ASIN ou preview do link afiliado final.

### Autores e categorias

O admin de autor possui busca, inline de livros/obras e ferramentas de associação/importação. Categorias têm administração simples e autocomplete no livro. A infraestrutura pode ser reaproveitada.

### Parceiros e cliques

O admin de parceiros permite ativar/desativar e ordenar. O admin de cliques é read-only para criação, possui filtros e gráficos por dia, mês, parceiro, categoria, autor, livro e dispositivo ([partners/admin.py](../partners/admin.py#L52)).

Limitações:

- `prioridade` não influencia o CTA;
- `url_base` não valida nem constrói o destino;
- desativar um parceiro não desativa o link legado: ocorre fallback para a URL direta do livro;
- os gráficos calculam tudo na request do changelist;
- “visitante único” é aproximação por `(session_key, user)`;
- exclusão de livro ou parceiro apaga cliques por `CASCADE`, perdendo histórico analítico.

---

## 8. Banco de dados: normalização, redundâncias e refatorações

### 8.1 Redundâncias atuais

| Dado | Fontes concorrentes | Avaliação |
|---|---|---|
| Parceiro do livro | strings em `Book` + `AffiliatePartner` | fonte textual frágil, sem integridade referencial |
| Link de compra | `Book.purchase_partner_url` + URL final no clique | snapshot no clique é útil; origem deveria ser uma oferta |
| Badges | `UserProfile.badges` JSON + `UserBadge` | duas fontes de verdade |
| Prateleiras customizadas | JSON no perfil + linhas `BookShelf` | duas fontes de verdade |
| Livros/páginas lidos | contadores no perfil + progresso/prateleiras | desnormalização sem ledger central |
| Evento gratuito | `is_free` + `price` nulo/zero | possível inconsistência |
| Clique/device | User-Agent bruto + browser/OS/device derivados | denormalização válida para analytics, exige versão do parser/governança |
| Índices | unique de ISBN/Google ID + índices explícitos; `created_at` do clique com `db_index` + índice explícito | custo de escrita/armazenamento desnecessário |

### 8.2 Conceitos ausentes

- edição/identificadores múltiplos de livro;
- oferta comercial por livro/parceiro/formato;
- ASIN ou identificador de produto do parceiro;
- moeda, fonte e atualização de preço;
- status/validade de oferta;
- estratégia/tipo do programa afiliado;
- domínios permitidos por parceiro;
- placement/source/campaign do clique;
- consentimento/base de processamento e política de retenção;
- evento de conversão separado de clique.

### 8.3 Deleção e histórico

`AffiliatePartnerClick.book` e `.partner` usam `CASCADE`. Para analytics, auditoria e reconciliação, é preferível preservar snapshot e usar `SET_NULL`/proteção conforme a política de retenção, evitando que a remoção editorial apague o histórico comercial.

---

## 9. Pontos de acoplamento e dependências fortes

1. `Book` conhece `AffiliateService`, URLs de `partners` e propriedades de UI.
2. `partners.models` importa `Book` concretamente; o catálogo e parceiros dependem um do outro.
3. Parceiro é resolvido por igualdade de nome ou slug gerado.
4. O assistente de catálogo contém regra específica da Amazon e gera URL de compra.
5. A view de redirect lê diretamente o campo legado do livro.
6. Templates chamam repetidamente propriedades que consultam o banco.
7. CTA, modal e JavaScript estão duplicados.
8. Admin customiza `admin.site.get_urls` por monkey patch global em duas etapas, em vez de `AdminSite`/`ModelAdmin.get_urls` com `admin_view`.
9. Importadores Google duplicam normalização e persistência.
10. Gamificação é chamada por imports, navegação, models e views.
11. URLs `/admin-tools/...` aparecem hardcoded dentro de HTML/JS do admin de autor.
12. A recomendação/chatbot depende das propriedades comerciais do model `Book`.

---

## 10. Problemas arquiteturais classificados

| ID | Severidade | Problema | Evidência/impacto | Direção recomendada |
|---|---|---|---|---|
| ARQ-01 | Alto | Relação livro-parceiro por texto | `purchase_partner_name` é comparado com nome/slug; renomear causa quebra e não há integridade | criar entidade de oferta com FKs |
| ARQ-02 | Alto | Apenas uma URL/parceiro por livro | não suporta Amazon + outros parceiros, formatos, prioridade real ou histórico | `BookOffer`/`PurchaseOffer` 1:N |
| ARQ-03 | Alto | Destino sem allowlist de host | qualquer URL válida armazenada recebe tracking e é redirecionada | validar esquema HTTPS e domínios do parceiro |
| ARQ-04 | Alto | `partner_id` pode não corresponder ao livro | rota aceita qualquer parceiro ativo e aplica seu tracking à URL do Book | redirect deve receber oferta opaca e resolver tudo server-side |
| ARQ-05 | Alto | Parceiro inativo não desliga a oferta | fallback envia à URL direta e ainda registra clique “direto” | política explícita de desativação/fallback |
| ARQ-06 | Alto | Coleta analítica sem governança técnica explícita | IP, usuário, sessão, UA, referer e idioma; banner diz “nenhum analytics no momento” | consentimento, minimização, retenção, anonimização e revisão jurídica |
| ARQ-07 | Alto | Importação duplicada e não transacional | duas views criam autor/categoria/livro e capa diretamente | caso de uso único, transação e idempotência |
| ARQ-08 | Alto | Risco de duplicidade/colisão | checks inconsistentes; slug explícito; Google ID nem sempre verificado; corrida check-insert | normalização e constraints por identificador/edição |
| ARQ-09 | Alto | Perda de fidelidade bibliográfica | somente primeiro autor/categoria e um ISBN | autores M2M e identificadores de edição incrementais |
| ARQ-10 | Alto | Data artificial `2000-01-01` | ausência/erro vira data real aparente | data anulável ou precisão/origem explícita |
| ARQ-11 | Alto | Catálogo global alterável por qualquer autenticado | importação pública cria entidades e concede XP | fila de curadoria ou limites/idempotência/moderação |
| ARQ-12 | Alto | Histórico de cliques apagado por CASCADE | exclusão editorial remove analytics | política de preservação e snapshots |
| ARQ-13 | Médio | Regras de parceiro dentro de `Book` | inversão de dependência e Active Record inchado | presenter/query service/use case |
| ARQ-14 | Médio | Consultas repetidas ao renderizar CTA | quatro propriedades podem resolver o mesmo parceiro várias vezes | resolver uma vez na view/query e montar view model |
| ARQ-15 | Médio | Estratégia “genérica” usa sempre `tag` | não é extensível para parceiros com regras diferentes | registry/strategy por programa |
| ARQ-16 | Médio | `url_base` e `prioridade` sem efeito | configuração sugere comportamento inexistente | remover intenção ambígua ou implementar via oferta/resolver |
| ARQ-17 | Médio | Tracking não é atomicamente deduplicado | `exists()` seguido de `create()` permite corrida | chave/evento idempotente ou constraint adequada |
| ARQ-18 | Médio | IP confia cegamente em `X-Forwarded-For` | header pode ser forjado fora de proxy confiável | configurar proxy confiável ou biblioteca apropriada |
| ARQ-19 | Médio | Clique chamado de compra | métricas/UI confundem interesse com conversão | nomenclatura e funil separados |
| ARQ-20 | Médio | CTA/modal/JS duplicados | detalhe e resenhas repetem o bloco inteiro | partial/inclusion tag + JS único |
| ARQ-21 | Médio | Template de detalhe monolítico | HTML/CSS/JS e múltiplos domínios em mais de 2 mil linhas | extração incremental de componentes |
| ARQ-22 | Médio | Hardcode Amazon no assistente de IA | catálogo depende de parceiro específico e de ISBN-10 como caminho para URL | assistente retorna metadados; oferta é caso de uso separado |
| ARQ-23 | Médio | Preço sem proveniência | exibe “estimado” e filtra, mas não há moeda/fonte/data | price snapshot na oferta, com validade |
| ARQ-24 | Médio | Signals/models concentram efeitos de gamificação | risco de duplicidade e difícil auditoria | serviço/ledger idempotente de XP |
| ARQ-25 | Médio | Fontes duplicadas em gamificação/biblioteca | JSON e tabelas relacionais coexistem | escolher fonte canônica e migrar gradualmente |
| ARQ-26 | Médio | Parser de User-Agent artesanal | classificação incompleta e difícil evolução | minimizar dado ou usar parser testado/versionado |
| ARQ-27 | Médio | Admin global monkey-patched | ordem de importação e wrapping de segurança ficam frágeis | `AdminSite` ou `get_urls` oficial com `admin_view` |
| ARQ-28 | Baixo | Índices redundantes | custo extra de storage/escrita | revisar plano de índices em migration futura |
| ARQ-29 | Baixo | Campo CSS livre no parceiro | hexadecimal não funciona como classe e configuração pode quebrar layout | choices/tokens de tema/presenter |
| ARQ-30 | Baixo | Imports/exceções/logs inconsistentes | `print`, mensagens cruas e imports locais espalhados | logging e erros de aplicação padronizados |
| ARQ-31 | Baixo | Status de evento recalculado só ao salvar | valor persistido pode ficar defasado | calcular ou atualizar por tarefa |

---

## 11. Componentes que podem ser reaproveitados

### Reaproveitar diretamente

- app `partners` como bounded context de monetização;
- `AffiliatePartner` como ponto inicial da entidade de parceiro;
- rota intermediária server-side de redirect;
- estrutura do admin de cliques e seus filtros;
- integração de sessão/usuário para contexto analítico, após governança;
- configuração Redis/Celery para tarefas e agregações;
- storage abstrato e cliente Google Books;
- autocomplete/admin modular de livros, autores e categorias;
- modal de biblioteca como comportamento de produto;
- namespaces de URL e testes existentes.

### Reaproveitar após ajuste

- `AffiliateService`: separar em construtor de link, resolver de oferta e recorder;
- `AffiliatePartnerClick`: migrar referência para oferta e aplicar retenção/snapshots;
- propriedades de `Book`: manter apenas como adapter de compatibilidade durante transição;
- dashboard de cliques: mover agregações pesadas para queries/rollups quando o volume crescer;
- importador Google: manter cliente e extração, centralizar persistência;
- `BookAdmin`: substituir campos de texto por inline de ofertas sem perder o fluxo atual;
- CTA: extrair para partial/inclusion tag e view model.

### Não reaproveitar como base definitiva

- resolução do parceiro por nome/slug do campo textual;
- `purchase_partner_url` como única fonte do destino;
- hardcode Amazon dentro do assistente IA;
- “estratégia genérica” que sempre adiciona `tag`;
- duplicação do modal/JS;
- denominação `has_purchased_before` baseada em clique.

---

## 12. Arquitetura alvo incremental

### 12.1 Princípio

Manter um **monólito modular**, com `partners` responsável por monetização e `core` responsável pelo catálogo. A dependência deve apontar do domínio de parceiros para uma referência de livro, enquanto `core.Book` não deve conhecer services, URLs ou apresentação de afiliados.

```text
core (catálogo)
  Book
    ^
    |
partners (monetização)
  AffiliatePartner
  PartnerProgram / regras
  BookOffer
  AffiliateClickEvent

application services
  ResolveBestOffer
  BuildAffiliateLink
  RecordAffiliateClick

adapters
  AmazonLinkStrategy
  GenericPartnerStrategy
  Django ORM repositories/query services
```

### 12.2 Modelo conceitual proposto

#### `AffiliatePartner` — evoluir o existente

- identidade, nome, slug, logo, status;
- domínios permitidos;
- configuração visual por tokens válidos;
- sem regra específica de livro.

#### `PartnerProgram` ou configuração equivalente

- parceiro, país/marketplace e tipo de programa;
- tracking ID;
- estratégia de link (`amazon_associates`, `generic_passthrough`, etc.);
- status, prioridade global e configuração validada.

Para o primeiro incremento, essa configuração pode permanecer em `AffiliatePartner` se houver somente um programa por parceiro. Separar a tabela só quando houver necessidade real de múltiplos países/programas.

#### `BookOffer`

- FK `book`;
- FK `partner`/programa;
- URL canônica de destino;
- identificador externo/ASIN;
- formato (`print`, `kindle`, `audiobook`, etc.);
- moeda e preço opcional;
- fonte e `price_checked_at`;
- status/validade;
- prioridade por livro;
- timestamps;
- constraints de unicidade coerentes.

Essa entidade resolve simultaneamente múltiplos parceiros, formatos, prioridade, automação e histórico.

#### `AffiliateClickEvent`

- FK para oferta, não combinação solta de Book e Partner;
- `event_id`/UUID idempotente;
- usuário/sessão opcionais;
- placement (`book_detail`, `reviews`, `chatbot`, `recommendation`);
- campaign/ref opcional;
- URL/partner/book em snapshot quando necessário;
- consentimento/base/versão de política, conforme decisão jurídica;
- retenção e anonimização definidas.

### 12.3 Serviços de aplicação

1. **`ResolveBookOffers`**: retorna ofertas elegíveis e ordenadas.
2. **`ResolveBestOffer`**: escolhe a oferta padrão conforme status, prioridade e formato.
3. **`BuildAffiliateLink`**: delega à strategy do programa e valida host/esquema.
4. **`RecordAffiliateClick`**: grava evento idempotente e minimizado.
5. **`ImportBookFromProvider`**: normaliza Google/Open Library e cria/atualiza o catálogo transacionalmente.

Interfaces/ports só devem ser introduzidas onde há variação real: provedor bibliográfico, estratégia de link e storage/telemetria. Não é necessário encapsular todo o ORM em repositórios genéricos.

### 12.4 Presenter/CTA

A view/query service deve entregar um objeto simples ao template:

- `available`;
- `display_name`;
- `redirect_url`;
- `button_class`/theme token;
- `icon_class`;
- `price` e `format`, se válidos;
- disclosure de link afiliado.

O template parcial renderiza o CTA, e um único arquivo JS controla o modal de biblioteca. O chatbot deve usar o mesmo serviço de aplicação, não propriedades do `Book`.

---

## 13. Plano técnico de implementação futura — sem código nesta fase

### Fase 0 — Governança e baseline

1. confirmar regras vigentes da conta Amazon Brasil e requisitos de disclosure/link/preço;
2. definir nomenclatura: clique, redirecionamento, oferta e conversão;
3. definir retenção, anonimização e base legal para analytics;
4. inventariar no banco de produção todos os valores distintos de `purchase_partner_name`, hosts e URLs inválidas;
5. registrar métricas de baseline e testes de regressão do fluxo atual.

**Saída:** decisão arquitetural (ADR), matriz de dados e política de tracking.

### Fase 1 — Fortalecer o fluxo atual

1. validar HTTPS e allowlist de domínios;
2. impedir mismatch entre parceiro e livro;
3. tornar “parceiro inativo” semanticamente efetivo;
4. corrigir nomenclatura de clique versus compra;
5. centralizar a estratégia Amazon e remover regra do assistente IA;
6. adicionar testes de segurança, fallback, consentimento e idempotência.

**Objetivo:** reduzir risco antes de ampliar o modelo.

### Fase 2 — Introduzir ofertas sem remover legado

1. criar conceitualmente `BookOffer` e constraints;
2. manter campos legados intactos;
3. fazer backfill: cada par nome/URL legado vira uma oferta;
4. gerar relatório de livros sem correspondência, hosts divergentes e duplicatas;
5. leitura preferencial da nova oferta com fallback legado;
6. observar divergências em logs/métricas.

**Estratégia:** expand-and-contract, sem big bang.

### Fase 3 — Admin e automação

1. adicionar ofertas como inline no `BookAdmin`;
2. selecionar parceiro por FK, não texto;
3. validar/extrair ASIN e gerar preview seguro;
4. permitir múltiplas ofertas e prioridade;
5. fazer o importador de metadados chamar um caso de uso único;
6. separar importação bibliográfica de criação/atualização de oferta.

### Fase 4 — CTA compartilhado e consumidores

1. criar um partial/inclusion component de compra;
2. extrair JS do modal para arquivo único;
3. adaptar detalhe e resenhas;
4. adaptar chatbot/recomendações ao resolver de ofertas;
5. manter adapter de compatibilidade temporário para `Book.affiliate_*`.

### Fase 5 — Tracking escalável

1. registrar placement/campaign/event ID;
2. aplicar minimização e retenção;
3. preservar histórico ao excluir livro/parceiro;
4. criar agregações periódicas se o volume justificar;
5. monitorar taxa de redirect, erros, hosts rejeitados e latência;
6. distinguir explicitamente clique de conversão.

### Fase 6 — Contração do legado

Somente após backfill completo, dual-read estável e observabilidade:

1. impedir novas escritas em `purchase_partner_name/url`;
2. remover dependência de templates/chatbot nas propriedades de `Book`;
3. retirar fallback legado;
4. em migration futura e separada, remover campos redundantes;
5. atualizar documentação e runbooks.

---

## 14. Estratégia de testes recomendada para a implementação

### Unidade

- normalização/validação de ISBN e ASIN;
- strategy Amazon com query params existentes;
- rejeição de host não permitido, HTTP, credenciais na URL e esquemas inválidos;
- ordenação e elegibilidade de ofertas;
- parceiro/oferta inativos;
- idempotência de clique;
- política de retenção/anonimização.

### Integração

- Book -> oferta -> redirect -> click event;
- múltiplas ofertas/formats;
- usuário autenticado e anônimo;
- modal de biblioteca e redirect;
- chatbot usando oferta resolvida;
- importador Google transacional e idempotente;
- backfill e fallback legado.

### Segurança e operação

- tentativa de mismatch de partner/offer;
- open redirect e URLs manipuladas;
- spoof de headers de proxy;
- concorrência de cliques e imports;
- deleção de livro/parceiro preservando histórico definido;
- volume e performance do dashboard.

---

## 15. Decisões recomendadas

1. **Manter o monólito modular.** Não há justificativa atual para microserviço de afiliados.
2. **Evoluir `partners`, não criar outro app comercial.** O bounded context já existe.
3. **Adicionar oferta como associação explícita.** Não colocar FK simples de parceiro em `Book`, pois isso ainda limitaria a uma oferta.
4. **Tratar ASIN separadamente de ISBN.** ISBN identifica edição bibliográfica; ASIN identifica produto/listagem Amazon e nem sempre é derivável com segurança.
5. **Gerar link server-side e validar host.** O browser recebe somente a URL local de redirect.
6. **Separar catálogo de monetização.** Google/IA importam metadados; parceiros administram ofertas.
7. **Migrar por expand-and-contract.** Preservar campos e rotas antigas até comprovar a nova leitura.
8. **Usar um único CTA compartilhado.** Detalhe, resenhas e chatbot devem compartilhar o mesmo resolver.
9. **Tratar tracking como dado pessoal/analítico sujeito a governança.** A implementação técnica deve seguir decisão jurídica explícita.
10. **Não chamar clique de compra.** Conversão futura deve ser outro evento/fonte.

---

## 16. Checklist de prontidão para iniciar a implementação

- [ ] inventário de URLs/parceiros em produção concluído;
- [ ] tracking ID Amazon e marketplace confirmados fora do código;
- [ ] domínios permitidos definidos;
- [ ] requisitos de disclosure e preço validados;
- [ ] política de dados/consentimento/retenção aprovada;
- [ ] modelo `BookOffer` e constraints aprovados em ADR;
- [ ] estratégia de backfill e rollback definida;
- [ ] contrato do CTA/presenter aprovado;
- [ ] critérios de aceite e testes de segurança definidos;
- [ ] métricas de sucesso e alertas definidos.

---

## 17. Parecer final

A arquitetura atual é suficientemente modular para receber a integração Amazon sem reescrita estrutural. O app `partners`, a rota de redirect, o tracking básico, o admin e a infraestrutura de cache/tasks constituem uma base real de reaproveitamento.

Entretanto, **o modelo atual ainda não deve ser considerado a arquitetura definitiva de parceiros**. Ele funciona como uma camada de compatibilidade sobre dois campos textuais em `Book`. Antes de escalar monetização, é necessário estabelecer integridade entre livro, oferta e parceiro; validar destinos; governar os dados de tracking; e centralizar os casos de uso de importação e compra.

A evolução recomendada é incremental: primeiro endurecer o fluxo existente, depois introduzir ofertas em paralelo, migrar dados, compartilhar o CTA e somente então retirar o legado. Essa abordagem preserva o sistema atual, reduz risco operacional e cria base para Amazon, outros parceiros, múltiplos formatos, campanhas, IA e monetização futura.
