# Fix: Erro de Cursor PostgreSQL no Admin de Campanhas

## Erro Original

```
psycopg.errors.InvalidCursorName: cursor "_django_curs_18520_sync_2" does not exist
```

Este erro ocorria ao tentar editar uma campanha no admin Django (`/admin/finance/campaign/4/change/`).

## Causa Raiz

O erro era causado pelo `CampaignGrantInline` tentando carregar muitos registros de uma vez. Quando há muitas concessões de campanha (CampaignGrant), o PostgreSQL cria um cursor de servidor que pode expirar ou ser fechado prematuramente, causando o erro.

## Solução Implementada

Modificamos o `CampaignGrantInline` em [finance/admin.py:52-68](finance/admin.py:52-68) para:

### 1. Limitar Quantidade de Registros

```python
def get_queryset(self, request):
    """Limita queryset para evitar problemas de cursor"""
    qs = super().get_queryset(request)
    # Limita a 10 registros mais recentes e otimiza com select_related
    return qs.select_related('user', 'subscription').order_by('-granted_at')[:10]
```

### 2. Otimizar Queries

- Usamos `select_related('user', 'subscription')` para reduzir queries N+1
- Ordenamos por `-granted_at` para mostrar os mais recentes primeiro
- Limitamos a exatamente 10 registros com slice `[:10]`

### 3. Melhorar UX

```python
verbose_name = 'Concessão Recente'
verbose_name_plural = 'Concessões Recentes (últimas 10)'
```

Isso deixa claro para o admin que está vendo apenas as últimas 10 concessões.

## Como Funciona Agora

Ao editar uma campanha:

1. ✅ Carrega apenas as 10 concessões mais recentes
2. ✅ Otimiza queries com select_related
3. ✅ Evita problema de cursor do PostgreSQL
4. ✅ Interface clara indicando limitação

## Visualizando Todas as Concessões

Se precisar ver TODAS as concessões de uma campanha, acesse:

**Opção 1: Admin de CampaignGrant**
```
/admin/finance/campaigngrant/
```
- Filtre por campanha
- Veja lista completa paginada

**Opção 2: Query Direta**
```python
from finance.models import Campaign, CampaignGrant

campaign = Campaign.objects.get(id=4)
grants = CampaignGrant.objects.filter(campaign=campaign)
print(f"Total: {grants.count()}")
```

## Benefícios da Solução

✅ **Performance**: Carrega apenas 10 registros ao invés de centenas/milhares

✅ **Estabilidade**: Evita timeout de cursores do PostgreSQL

✅ **UX**: Interface mais rápida e responsiva

✅ **Clareza**: Admin sabe que está vendo apenas últimas 10

## Configurações Aplicadas

```python
class CampaignGrantInline(admin.TabularInline):
    model = CampaignGrant
    extra = 0
    readonly_fields = ['user', 'granted_at', 'expires_at', 'is_active', 'was_notified']
    can_delete = False
    max_num = 10  # Limite máximo
    verbose_name = 'Concessão Recente'
    verbose_name_plural = 'Concessões Recentes (últimas 10)'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user', 'subscription').order_by('-granted_at')[:10]
```

## Testando a Correção

1. Reinicie o servidor Django
2. Acesse `/admin/finance/campaign/`
3. Clique em editar qualquer campanha
4. ✅ Deve carregar sem erros
5. ✅ Veja seção "Concessões Recentes (últimas 10)"

## Próximos Passos (Opcional)

Se quiser melhorar ainda mais:

1. **Paginação no Inline**: Adicionar paginação customizada
2. **Link para Ver Todas**: Adicionar botão "Ver todas as concessões"
3. **Estatísticas no Topo**: Mostrar contadores (Total, Ativas, Expiradas)

## Referências

- [Django Docs: ModelAdmin.get_queryset](https://docs.djangoproject.com/en/5.0/ref/contrib/admin/#django.contrib.admin.ModelAdmin.get_queryset)
- [PostgreSQL Cursor Naming](https://www.postgresql.org/docs/current/sql-declare.html)
- [Django select_related](https://docs.djangoproject.com/en/5.0/ref/models/querysets/#select-related)
