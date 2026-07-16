# Relatório de implementação — consolidação de parceiros comerciais

## Resultado

A camada interna de parceiros foi consolidada sem migrations, novas tabelas,
`BookOffer`, alteração do fluxo administrativo ou ativação de fail-closed. O CTA,
layout e templates permaneceram visualmente e estruturalmente inalterados.

O redirecionamento de produção continua com o comportamento legado até o
saneamento dos dados. A nova política pode ser auditada e testada sem bloquear
usuários.

## Arquivos da entrega

| Arquivo | Justificativa |
|---|---|
| `.env.example` | Declara somente a chave vazia da configuração comercial. |
| `cgbookstore/settings.py` | Lê allowlists/parâmetros por slug e mantém encurtadores conhecidos centralizados. |
| `partners/services/url_validation_service.py` | Encapsula toda a política estrutural, HTTPS, host e allowlist. |
| `partners/services/affiliate_service.py` | Remove regra específica de Amazon e centraliza resolução, diagnóstico e tracking. |
| `partners/services/__init__.py` | Expõe a API pública do pacote de serviços. |
| `partners/management/commands/audit_partner_links.py` | Auditoria permanente, somente leitura, com categorias, severidades e modo CI. |
| `partners/management/__init__.py` | Estrutura de management commands do app. |
| `partners/management/commands/__init__.py` | Estrutura de descoberta do comando. |
| `partners/test_partner_security.py` | Cobertura unitária de segurança, tracking, manipulação e auditoria. |
| `core/services/ai_book_assistant.py` | Remove exclusivamente a criação de parceiro/URL Amazon pela IA. |
| `chatbot_literario/gemini_service.py` | Remove exclusivamente a regra comercial fixa da Amazon. |
| `chatbot_literario/groq_service.py` | Remove exclusivamente a regra comercial fixa da Amazon. |
| `docs/PARCEIROS_COMERCIAIS_CONFIGURACAO.md` | Operação, política, fluxo, auditoria e checklist fail-closed. |
| `docs/INVESTIGACAO_SETTINGS_TEST.md` | Diagnóstico independente da configuração de testes; nenhuma correção misturada. |
| `docs/AUDITORIA_ARQUITETURAL_PARCEIROS_AMAZON.md` | Auditoria arquitetural que fundamentou esta etapa. |

## Validações executadas

- Segurança e serviços: **19/19** testes aprovados, sem banco.
- Suíte completa `partners`: **46/46** testes aprovados.
- Chatbot: **19/19** testes aprovados.
- Livros e importação administrativa: **22/22** testes aprovados.
- `manage.py check`: nenhum problema.
- `makemigrations --check --dry-run`: `No changes detected`.
- Busca global: nenhuma construção de link afiliado de produção fora do
  `AffiliateService`; chatbot e assistente não geram URL/tracking manualmente.

O conjunto combinado de `core` + chatbot excedeu 304 segundos sem produzir
resultado no limite do processo. Os mesmos grupos foram então executados
isoladamente e todos passaram. O startup também emite o aviso preexistente
`No module named 'imghdr'` ao importar `mobi`, sem afetar os testes.

O baseline com `cgbookstore.settings_test` não coleta testes devido à remoção de
`new_authors` seguida de import eager de seus modelos. A causa e a correção mínima
proposta estão no documento de investigação separado.

## Resultado da auditoria local

- Parceiros cadastrados: **0**
- Livros examinados: **184**
- Livros com dados comerciais: **4**
- Ocorrências: **4 de severidade alta**
- Parceiro não cadastrado: **3**
- Parceiro informado sem URL: **1**

Registros identificados:

- Livro `#96`, *A Roda do Tempo: O Dragão Renascido*: parceiro `skeelo`, sem URL;
- Livro `#213`, *O Último Desejo*: parceiro `Amazon` não cadastrado;
- Livro `#219`, *A guerra da papoula*: parceiro `Amazon` não cadastrado;
- Livro `#220`, *O Ultimo Desejo - Serie The Witcher - A Saga do Bruxo Geralt de Rivia - Vol. 1*: parceiro `Amazon` não cadastrado.

Nenhum registro foi modificado. Esses achados mantêm o gate fail-closed fechado.

## Pendências administrativas

1. Cadastrar Amazon no Admin com nome `Amazon`, slug `amazon`, URL base
   `https://www.amazon.com.br`, prioridade `1`, status apropriado e Tracking ID
   real informado apenas no Admin.
2. Configurar `PARTNER_COMMERCIAL_CONFIG` no ambiente com os hosts explícitos
   `amazon.com.br` e `www.amazon.com.br`, sem Tracking ID.
3. Corrigir manualmente o livro Skeelo e revisar o cadastro do parceiro.
4. Executar a auditoria contra uma cópia segura e depois contra produção.

## Riscos residuais

- **Alto, aceito temporariamente:** a view de produção ainda preserva fallback de
  URL quando não resolve parceiro e ainda não bloqueia Partner ID inconsistente.
- **Alto, aceito temporariamente:** o novo validador não é aplicado ao
  redirecionamento até o gate de dados retornar limpo.
- **Médio:** redirecionamentos HTTP remotos não são seguidos; encurtadores
  conhecidos são recusados, mas a verificação online deve ser assíncrona no futuro.
- **Médio:** variáveis JavaScript/contexto legadas com termo `purchase` continuam
  nos templates; não foram alteradas por proibição expressa de modificar templates.
- **Baixo:** o parâmetro de tracking tem fallback genérico `tag`; cada parceiro não
  compatível deve declarar seu parâmetro explicitamente.
- **Baixo:** a suíte global é lenta por migrations, sinais e esperas de cache; isso
  aumenta o tempo do pipeline, mas não muda a funcionalidade comercial.

## Deploy incremental

1. Fazer backup das variáveis atuais e confirmar que não há migration pendente.
2. Publicar os arquivos desta etapa; não executar migration específica da entrega.
3. Definir `PARTNER_COMMERCIAL_CONFIG` no gerenciador de ambiente.
4. Reiniciar processos para recarregar settings.
5. Cadastrar/revisar os parceiros no Admin sem alterar os livros automaticamente.
6. Executar `audit_partner_links` e registrar o relatório.
7. Após saneamento, usar `audit_partner_links --fail-on-findings` como gate de CI.

## Rollback

Como não há mudança de schema nem escrita automática, o rollback é somente de
código/configuração:

1. restaurar a versão anterior dos arquivos da entrega;
2. remover ou restaurar `PARTNER_COMMERCIAL_CONFIG` no ambiente;
3. reiniciar os processos;
4. manter os cadastros administrativos válidos ou revertê-los manualmente apenas
   se a operação assim decidir.

Não há migration reversa nem conversão de dados a executar.

## Próxima fase: ativação segura e BookOffer

Antes de qualquer `BookOffer`, concluir o checklist fail-closed documentado,
conectar `inspect_link_for_book` à view com mensagem amigável e logs sem dados
sensíveis, e adicionar testes de integração para parceiro inativo, ID manipulado e
domínio divergente.

Depois, introduzir `BookOffer` de forma aditiva: criar ofertas a partir dos campos
legados, operar leitura dupla, comparar decisões, tornar a nova resolução primária
e só em fase posterior descontinuar os campos antigos. Clique continuará sendo
evento de interesse/redirecionamento, nunca compra, pedido ou conversão.
