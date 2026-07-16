# Parceiros comerciais — configuração e operação segura

## Estado desta etapa

Esta etapa mantém integralmente os campos legados `purchase_partner_name` e
`purchase_partner_url`, o fluxo do Django Admin e o texto visual do CTA. O
`URLValidationService` e os diagnósticos do `AffiliateService` estão disponíveis,
mas a validação **ainda não bloqueia** o redirecionamento de produção. A ativação
fail-closed depende do saneamento dos dados indicado pelo comando de auditoria.

Não foram criados modelos, tabelas ou migrations.

## Cadastro administrativo do parceiro

O Tracking ID é segredo/configuração operacional e deve continuar no campo
`tracking_id` do `AffiliatePartner` no Django Admin. Ele não deve aparecer no
repositório, em documentação, em exemplos ou em logs.

Cadastro previsto para Amazon Brasil:

- Nome: `Amazon`
- Slug: `amazon`
- URL base: `https://www.amazon.com.br`
- Tracking ID: informado exclusivamente no ambiente administrativo
- Ativo: sim, após validação operacional
- Prioridade: `1`

O parceiro Skeelo e seus livros devem ser saneados manualmente; esta etapa não
altera dados automaticamente.

## Allowlist e parâmetro de tracking

A configuração declarativa usa a variável `PARTNER_COMMERCIAL_CONFIG`, indexada
pelo slug cadastrado no parceiro. Exemplo sem qualquer Tracking ID:

```dotenv
PARTNER_COMMERCIAL_CONFIG={"amazon":{"allowed_domains":["amazon.com.br","www.amazon.com.br"],"tracking_query_param":"tag"}}
```

O `.env.example` mantém somente `PARTNER_COMMERCIAL_CONFIG=` vazio. Em produção,
o valor deve ser definido no gerenciador de variáveis/segredos da infraestrutura.

Cada host é exato. Declarar `amazon.com.br` não autoriza automaticamente
subdomínios, hosts semelhantes ou `www.amazon.com.br`; ambos devem ser listados
quando necessários. Na ausência da configuração declarativa, o host exato de
`AffiliatePartner.url_base` funciona como compatibilidade mínima.

## Política central de validação

`partners.services.URLValidationService` aplica uma política reutilizável e sem
acesso à rede:

- exige URL absoluta HTTPS;
- normaliza scheme e hostname com IDNA;
- exige correspondência exata com a allowlist;
- rejeita credenciais embutidas, IPs literais e portas diferentes de `443`;
- rejeita portas inválidas, caracteres de controle e barras invertidas;
- rejeita hosts malformados, domínios semelhantes e encurtadores conhecidos;
- preserva caminho, query string e fragmento na normalização;
- oferece resultado estruturado e `validate_or_raise` para integrações futuras.

O serviço não segue respostas HTTP 3xx. Por isso, encurtadores são recusados e a
allowlist valida o destino cadastrado. Uma futura verificação de redirecionamentos
remotos deve ser assíncrona, ter limite de saltos, timeout e validação de cada host;
ela não deve ocorrer na requisição do usuário.

## Geração do link

Fluxo atual, preservado nesta etapa:

1. `Book` expõe a rota intermediária por suas propriedades legadas.
2. `partners.views.redirect_to_partner` resolve o livro e o parceiro.
3. `AffiliateService.generate_link` preserva parâmetros existentes e insere ou
   substitui o parâmetro de tracking configurado.
4. A view registra um `AffiliatePartnerClick` e redireciona.

O `AffiliateService` não contém regra específica da Amazon. O nome do parâmetro
vem da configuração do parceiro e o valor vem do cadastro administrativo. Os
métodos `resolve_partner_for_book`, `partner_matches_book`,
`validate_partner_url` e `inspect_link_for_book` preparam o bloqueio futuro, mas
não foram conectados à view nesta etapa.

## Auditoria somente leitura

Execução humana, sempre com código de saída zero se o comando conseguir ler os
dados:

```console
python manage.py audit_partner_links
```

Resumo sem detalhes por livro:

```console
python manage.py audit_partner_links --summary-only
```

Uso em CI/deploy gate:

```console
python manage.py audit_partner_links --fail-on-findings
```

Códigos de saída:

- `0`: comando executado; com `--fail-on-findings`, nenhum achado;
- `1`: achados encontrados quando `--fail-on-findings` está ativo;
- código não zero do Django: erro de configuração, conexão ou execução.

O relatório apresenta resumo executivo, severidades, categorias, contagens,
detalhes sem revelar Tracking IDs e sugestões de correção. O comando não chama
`save`, `update`, `delete`, `bulk_create` ou qualquer outra operação de escrita.

## Checklist antes do fail-closed

- [ ] Amazon cadastrada no Admin com slug, URL base, Tracking ID e status corretos.
- [ ] Allowlist de todos os parceiros configurada explicitamente.
- [ ] Skeelo e demais nomes legados resolvidos manualmente.
- [ ] Nenhum livro com parceiro sem URL ou URL sem parceiro.
- [ ] Nenhuma URL HTTP, encurtada, malformada ou fora da allowlist.
- [ ] Nenhuma divergência de Tracking ID no relatório.
- [ ] `audit_partner_links --fail-on-findings` retorna `0` no banco de produção.
- [ ] Testes da view atual e dos novos cenários de bloqueio aprovados.
- [ ] Mensagem amigável para parceiro inativo/inconsistência aprovada pelo produto.
- [ ] Logs e métricas usam clique/redirecionamento, nunca compra/conversão.

## Evolução conceitual para BookOffer

Sem implementar estrutura de banco nesta etapa, a próxima evolução pode separar:

- `Book`: identidade e metadados editoriais;
- `AffiliatePartner`: política, apresentação e credenciais de integração;
- `BookOffer`: associação entre livro e parceiro, URL original, preço exibido,
  disponibilidade, formato e vigência;
- serviço de resolução: escolhe ofertas elegíveis sem acoplar o domínio de livros;
- evento de clique: registra interesse/redirecionamento, não compra ou conversão.

A migração deve ser aditiva: criar ofertas a partir dos campos legados, operar em
leitura dupla por período controlado, comparar resultados e só depois alterar a
fonte primária. A remoção dos campos legados pertence a uma fase posterior.
