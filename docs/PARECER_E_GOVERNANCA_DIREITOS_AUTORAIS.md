# Parecer Jurídico & Governança de Ativos Visuais e Direitos Autorais

## 1. Contexto e Enquadramento Legal da CG.BookStore

A plataforma **CG.BookStore** opera como uma comunidade literária interativa, portal de notícias, acervo de resenhas e espaço para debate de leitores. A utilização de ativos visuais (capas de livros, logos de editoras, fotografias de autores, banners de eventos e artes de adaptações literárias) obedece rigorosamente às diretrizes de proteção e conformidade jurídica previstas na legislação brasileira e nos padrões internacionais de *Fair Use*.

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
- A indicação de compra é realizada por meio de links do **Programa de Afiliados Amazon**, direcionando os leitores diretamente às páginas oficiais de venda. A remuneração recebida é uma comissão por indicação de tráfego concedida pela varejista parceira.

### 2.4 Fundamentação na Lei de Direitos Autorais (Lei nº 9.610/1998)
A reprodução de imagens e capas na plataforma enquadra-se nas **Limitações aos Direitos Autorais** estipuladas no **Artigo 46 da Lei nº 9.610/1998**:
- **Art. 46, III**: É livre a citação em livros, jornais, revistas ou qualquer outro meio de comunicação, de passagens de qualquer obra, para fins de estudo, crítica ou debate, na medida justificada para o fim a atingir, indicando-se o nome do autor e a origem da obra.
- **Art. 46, VIII**: É livre a reprodução, em quaisquer obras, de pequenos trechos de obras preexistentes, de artes plásticas ou fotográficas, sempre que a reprodução em si não seja o objeto principal da obra nova e que não prejudique a exploração normal da obra reproduzida nem cause um prejuízo injustificado aos legítimos interesses dos autores.

### 2.5 Princípio da Proporcionalidade e Limitação de Resolução
- Todas as imagens exibidas na interface do usuário passam por um processo de otimização e thumbnailing, mantendo as **dimensões e resolução adequadas exclusivamente para pré-visualização** (*preview/card*).
- O sistema registra e audita automaticamente as dimensões (`width`, `height`) e o peso em KB dos arquivos para comprovar a proporcionalidade do uso.

---

## 3. Matriz de Categorização e Finalidade dos Ativos Visuais

| Categoria do Ativo | Finalidade do Uso (`usage_purpose`) | Fundamento Jurídico (`legal_basis`) | Beneficiários Principais |
| :--- | :--- | :--- | :--- |
| **Capa de Livro** | Resenha & Debate Literário (`review_debate`) / Indicação Afiliada (`affiliate_promotion`) | Art. 46 LDA / Termos de Afiliados (`fair_use_art46`) | Editoras e Autores (Vendas via Amazon) |
| **Foto do Autor** | Biografia & Perfil de Autor (`author_bio`) | Citação Informativa / Art. 46 LDA (`fair_use_art46`) | Autor (Divulgação de Carreira) |
| **Banner de Evento** | Divulgação Gratuita de Eventos (`event_publicity`) | Divulgação Institucional / Autorização (`express_consent`) | Organizadores do Evento |
| **Adaptação Literária** | Informação Cultural (`adaptation_info`) | Citação / Divulgação Cultural (`fair_use_art46`) | Estúdios e Produtoras |
| **Banner da Plataforma** | Identidade & Layout (`institutional`) | Produção Própria / Licenciada (`own_production`) | CG.BookStore |

---

## 4. Política de Notice & Takedown (Notificação e Remoção)

Em conformidade com o **Artigo 19 do Marco Civil da Internet (Lei nº 12.965/2014)** e os padrões internacionais (DMCA), a plataforma disponibiliza um canal direto para que titulares de direitos autorais solicitem a atualização de créditos ou a remoção imediata de qualquer ativo visual, através dos Termos de Uso e do e-mail oficial de contato da equipe.

---

## 5. Rastreamento e Auditoria Interna via Django Admin

A governança corporativa de imagens é mantida através do modelo `ImageRightsRecord`, permitindo:
1. Identificação precisa do modelo e objeto vinculado via `GenericForeignKey`.
2. Verificação de integridade via **SHA-256 Checksum** do arquivo para detectar trocas não auditadas.
3. Rastreamento da finalidade do uso, enquadramento legal, dimensões físicas e créditos TASL (*Title, Author, Source, License*).
4. Monitoramento percentual das taxas de conformidade da aplicação através do Mapa de Conformidade e Dashboard de Auditoria em `/admin/audit/image-copyright/`.
