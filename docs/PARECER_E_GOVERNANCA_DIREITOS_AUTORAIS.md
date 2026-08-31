# Parecer Jurídico & Governança de Ativos Visuais e Direitos Autorais

## 1. Contexto e Enquadramento Legal da CG.BookStore

A plataforma **CG.BookStore** opera como uma comunidade literária interativa, portal de notícias, acervo de resenhas e espaço para debate de leitores. A utilização de ativos visuais (capas de livros, logos de editoras, fotografias de autores, banners de eventos e artes de adaptações literárias) obedece a uma governança corporativa prudente de conformidade jurídica, pautada na legislação brasileira de direitos autorais (Lei nº 9.610/1998), na distinção clara entre regimes de licenciamento e na avaliação caso a caso da procedência dos ativos.

> **Nota Doutrinária**: O conceito de *Fair Use* pertence estritamente ao direito norte-americano (*Copyright Act of 1976*) e não possui aplicação direta como fundamento autônomo no ordenamento jurídico brasileiro. No Brasil, eventuais utilizações sem autorização prévia devem se fundamentar estritamente nas hipóteses taxativas e restritivas de **Limitações aos Direitos Autorais** (Artigos 46 a 48 da Lei nº 9.610/1998) ou em regimes próprios de licenciamento (Creative Commons, Domínio Público, Autorizações Expressas e Termos Contratuais de Parceiros).

---

## 2. Pilares da Proteção Jurídica da Aplicação

### 2.1 Não Comercialização de Obras / Ausência de Concorrência Direta
- A plataforma **NÃO** comercializa arquivos de livros digitais (EPUB, PDF, MOBI) nem vende livros físicos diretamente aos leitores.
- As imagens das capas de livros e marcas de editoras são utilizadas unicamente como **elementos identificadores e ilustrativos** para orientar o leitor durante pesquisas, leitura de resenhas e participação em fóruns de debate.
- A exibição visual não substitui nem concorre com o produto principal oferecido pelos titulares dos direitos autorais.

### 2.2 Modelo de Monetização Restrito ao Plano Premium
- A sustentabilidade financeira da aplicação provém exclusivamente da assinatura do **Plano Premium**, cujos benefícios são estritamente funcionais e comunitários:
  - Maior limite de réplicas em debates e fóruns;
  - Personalização de temas visuais da biblioteca pessoal do leitor;
  - Conquistas, distintivos e *badges* de engajamento na comunidade.
- **Nenhum valor é cobrado pelo acesso, visualização ou download de capas ou ativos visuais de obras protegidas.**

### 2.3 Promoção Gratuita e Direcionamento via Afiliados (Amazon)
- Editoras, autores, livrarias e organizadores de eventos beneficiam-se de **divulgação e publicidade 100% gratuita** dentro da plataforma.
- A indicação de compra é realizada por meio de links do **Programa de Afiliados Amazon**, direcionando os leitores diretamente às páginas oficiais de venda. A remuneração recebida é uma comissão por indicação de tráfego concedida pela varejista parceira em conformidade com seus termos de operação.

### 2.4 Análise Criteriosa das Limitações da Lei de Direitos Autorais (Lei nº 9.610/1998)
O enquadramento no **Artigo 46 da Lei nº 9.610/1998** não é tratado pela CG.BookStore como uma autorização ampla ou automática para reprodução irrestrita de imagens, mas sim como uma **justificativa jurídica de limitação legal analisada**, exigindo conformidade rigorosa com seus requisitos legais:
- **Art. 46, III (Citação e Debate)**: Aplicado estritamente na medida justificada para fins de estudo, crítica ou debate literário em resenhas e fóruns da comunidade, sempre indicando-se o nome do autor e a origem da obra. Não constitui autorização automática de reprodução integral desvinculada de contexto crítico ou informativo.
- **Art. 46, VIII (Pequenos Trechos e Proporcionalidade)**: Aplicado a pequenos trechos e elementos visuais preexistentes quando a reprodução em si não seja o objeto principal da obra nova e não cause prejuízo injustificado aos legítimos interesses dos autores e titulares.

### 2.5 Princípio da Proporcionalidade e Limitação de Resolução
- Todas as imagens exibidas na interface do usuário passam por um processo de otimização e thumbnailing, mantendo as **dimensões e resolução adequadas exclusivamente para pré-visualização** (*preview/card*).
- O sistema registra e audita automaticamente as dimensões (`width`, `height`) e o peso em KB dos arquivos para comprovar a proporcionalidade do uso.

---

## 3. Matriz de Categorização e Finalidade dos Ativos Visuais

| Categoria do Ativo | Finalidade do Uso (`usage_purpose`) | Fundamento Jurídico (`legal_basis`) | Beneficiários Principais |
| :--- | :--- | :--- | :--- |
| **Capa de Livro** | Resenha & Debate Literário (`review_debate`) / Indicação Afiliada (`affiliate_promotion`) | Limitação Legal Analisada (Art. 46 LDA) / Termos de Afiliados (`fair_use_art46` / `amazon_affiliate_terms`) | Editoras e Autores (Divulgação e Vendas) |
| **Foto do Autor** | Biografia & Perfil de Autor (`author_bio`) | Divulgação Informativa / Limitação Legal Analisada (Art. 46 LDA) (`fair_use_art46`) | Autor (Divulgação de Carreira) |
| **Banner de Evento** | Divulgação Gratuita de Eventos (`event_publicity`) | Divulgação Institucional / Autorização Expressa (`express_consent`) | Organizadores do Evento |
| **Adaptação Literária** | Informação Cultural (`adaptation_info`) | Divulgação Cultural / Limitação Legal Analisada (`fair_use_art46`) | Estúdios e Produtoras |
| **Banner da Plataforma** | Identidade & Layout (`institutional`) | Produção Própria / Licença Adquirida (`own_production` / `licensed`) | CG.BookStore |

---

## 4. Política de Notice & Takedown (Notificação e Retirada de Boa-Fé)

Como prática ativa de integridade, boa-fé e governança corporativa, a plataforma disponibiliza canal permanente e direto para que titulares de direitos autorais solicitem atualização de créditos, complementação de informações ou a **remoção imediata de qualquer ativo visual**, através do e-mail oficial de contato (`suporte@cgbookstore.com.br`) e do procedimento detalhado na Seção 11 dos Termos de Uso.

---

## 5. Rastreamento e Auditoria Interna via Django Admin

A governança corporativa de imagens é mantida através do modelo `ImageRightsRecord`, permitindo:
1. Identificação precisa do modelo e objeto vinculado via `GenericForeignKey`.
2. Verificação de integridade via **SHA-256 Checksum** do arquivo para detectar trocas não auditadas.
3. Rastreamento da finalidade do uso, enquadramento legal, dimensões físicas e créditos TASL (*Title, Author, Source, License*).
4. Monitoramento percentual das taxas de conformidade da aplicação através do Mapa de Conformidade e Dashboard de Auditoria em `/admin/audit/image-copyright/`.

