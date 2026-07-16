# Investigação separada — falha de `settings_test.py`

## Resultado

A falha ocorre antes da execução dos testes de parceiros e é independente das
alterações comerciais. Nenhuma correção foi aplicada neste conjunto.

## Causa raiz

`cgbookstore/settings_test.py` remove `new_authors` de `INSTALLED_APPS`. Durante
`django.setup()`, a descoberta do Admin importa `core.admin`. Esse módulo importa
o pacote agregado `core.views`, cujo `__init__.py` importa `dashboard_view`.
`dashboard_view.py`, por sua vez, importa modelos de `new_authors`.

Como os modelos são carregados quando o app já foi removido, o Django levanta
`RuntimeError` (modelo sem `app_label` pertencente a app instalado). O bloco atual
captura apenas `ImportError`, portanto não intercepta — nem deveria mascarar — a
inconsistência do registro de apps.

Fluxo de importação observado:

```text
settings_test remove new_authors
  -> django.contrib.admin autodiscover
  -> core.admin.__init__
  -> core.views.__init__
  -> core.views.dashboard_view
  -> new_authors.models
  -> RuntimeError durante django.setup()
```

## Arquivos envolvidos

- `cgbookstore/settings_test.py`: remove o app nas linhas de configuração de teste;
- `core/admin/__init__.py`: importa o pacote agregado `core.views` e a dashboard;
- `core/views/__init__.py`: importa muitas views eagerly, inclusive a dashboard;
- `core/views/dashboard_view.py`: importa modelos opcionais no carregamento do módulo;
- `new_authors/models.py`: modelos carregados fora de um app instalado.

## Impacto

- nenhum teste chega a ser coletado com `--settings=cgbookstore.settings_test`;
- o problema afeta qualquer suíte, não apenas `partners`;
- tentativas de esconder a exceção podem deixar a dashboard parcialmente definida;
- a suíte com settings normais pode depender de infraestrutura/migrations mais lentas.

## Correção mínima recomendada, em conjunto independente

Primeiro decidir qual garantia o settings de teste deve oferecer:

1. Se `new_authors` precisa coexistir com `core`, mantê-lo em `INSTALLED_APPS` e
   tratar separadamente a compatibilidade de suas migrations com SQLite.
2. Se o app deve realmente ser opcional, evitar imports eager: importar diretamente
   a view necessária no Admin e carregar estatísticas opcionais somente quando
   `apps.is_installed('new_authors')` for verdadeiro.

A segunda opção melhora o desacoplamento, mas ultrapassa uma correção de uma linha.
A primeira é a menor mudança de configuração, porém deve ser validada contra as
migrations que motivaram a exclusão. Em ambos os casos, a correção deve ter testes
próprios de inicialização do Django e não fazer parte do deploy de parceiros.
