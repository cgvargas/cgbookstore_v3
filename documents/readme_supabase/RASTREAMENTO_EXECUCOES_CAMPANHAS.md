# Rastreamento de Execuções de Campanhas

## Visão Geral

Sistema de rastreamento visual para identificar quais campanhas foram executadas, quantas vezes e quando foi a última execução.

## Funcionalidades Implementadas

### 1. Novos Campos no Model Campaign

Dois novos campos foram adicionados ao modelo `Campaign`:

```python
# Controle de execuções
last_execution_date = models.DateTimeField(
    null=True,
    blank=True,
    verbose_name='Última Execução',
    help_text='Data e hora da última vez que a campanha foi executada'
)

execution_count = models.IntegerField(
    default=0,
    verbose_name='Número de Execuções',
    help_text='Quantas vezes esta campanha foi executada manualmente'
)
```

### 2. Atualização Automática no CampaignService

Quando uma campanha é executada via `CampaignService.execute_campaign()`, os campos são atualizados automaticamente:

```python
# Atualiza controle de execuções
from django.db.models import F
campaign.last_execution_date = timezone.now()
campaign.execution_count = F('execution_count') + 1
campaign.save(update_fields=['last_execution_date', 'execution_count'])
```

### 3. Interface Admin com Indicadores Visuais

#### Colunas na Lista de Campanhas

Duas novas colunas foram adicionadas à lista do admin:

1. **Execuções** - Badge visual mostrando quantas vezes a campanha foi executada:
   - **Cinza**: "Nunca executada" (0 execuções)
   - **Verde**: "✓ 1 vez" (primeira execução)
   - **Azul**: "✓ X vezes" (múltiplas execuções)

2. **Última Execução** - Data formatada com cores baseadas em quão recente foi:
   - **Verde**: Executada hoje
   - **Azul**: Última semana (1-7 dias)
   - **Laranja**: Último mês (8-30 dias)
   - **Cinza**: Mais de 30 dias atrás
   - **Itálico cinza**: "Nunca" (nunca executada)

#### Exemplo Visual

```
| Execuções          | Última Execução              |
|--------------------|------------------------------|
| [Nunca executada]  | Nunca                        |
| [✓ 1 vez]         | 04/11/2025 10:49 (Hoje)      |
| [✓ 4 vezes]       | 28/10/2025 15:30 (Há 7 dias) |
```

### 4. Filtros no Admin

Novo filtro adicionado para facilitar a busca:
- **execution_count**: Permite filtrar por número de execuções

### 5. Seção no Formulário de Edição

Nova seção "Controle de Execuções" no formulário de edição da campanha (colapsada por padrão):
- execution_count (somente leitura)
- last_execution_date (somente leitura)

## Como Usar

### No Admin Django

1. Acesse `/admin/finance/campaign/`
2. Visualize as colunas "Execuções" e "Última Execução"
3. Use os filtros para encontrar campanhas:
   - Nunca executadas
   - Executadas 1 vez
   - Executadas múltiplas vezes

### Executar uma Campanha

1. Selecione a checkbox da campanha
2. No dropdown "Ações", escolha "Executar campanhas selecionadas"
3. Clique em "Ir"
4. O contador será incrementado automaticamente
5. A data/hora da execução será registrada

### Via Código Python

```python
from finance.models import Campaign
from finance.services import CampaignService

# Buscar campanha
campaign = Campaign.objects.get(name="Minha Campanha")

# Executar
result = CampaignService.execute_campaign(campaign, preview=False)

# Verificar resultado
print(f"Execuções: {campaign.execution_count}")
print(f"Última: {campaign.last_execution_date}")
```

## Scripts de Teste

Foram criados scripts para testar a funcionalidade:

### 1. test_execution_tracking.py

Testa a execução básica e verifica os campos:

```bash
python scripts/test_execution_tracking.py
```

**Saída esperada:**
- Lista campanhas ativas
- Mostra status antes da execução
- Executa uma campanha
- Mostra status após execução com contador incrementado

### 2. test_multiple_executions.py

Testa múltiplas execuções consecutivas:

```bash
python scripts/test_multiple_executions.py
```

**Saída esperada:**
- Executa a mesma campanha 3 vezes
- Mostra contador incrementando (1 → 2 → 3 → 4)
- Atualiza data/hora a cada execução

## Migração

A migração foi criada e aplicada automaticamente:

```bash
python manage.py makemigrations finance
# Cria: finance/migrations/0003_campaign_execution_count_and_more.py

python manage.py migrate finance
# Aplica: Add field execution_count to campaign
#        Add field last_execution_date to campaign
```

## Comportamento

### Quando uma campanha é executada:

1. ✅ `execution_count` é incrementado em +1
2. ✅ `last_execution_date` recebe a data/hora atual (timezone-aware)
3. ✅ Os valores são salvos no banco de dados
4. ✅ O admin mostra os badges visuais atualizados

### Quando uma campanha é executada em preview:

1. ❌ `execution_count` **NÃO** é incrementado
2. ❌ `last_execution_date` **NÃO** é atualizado
3. ℹ️ Preview apenas conta elegíveis sem fazer concessões

## Arquivos Modificados

### Models
- `finance/models.py` - Adicionados campos `execution_count` e `last_execution_date`

### Services
- `finance/services.py` - Atualização automática dos campos em `execute_campaign()`

### Admin
- `finance/admin.py` - Novos display methods com badges visuais

### Migrations
- `finance/migrations/0003_campaign_execution_count_and_more.py` - Migração dos novos campos

### Scripts de Teste
- `scripts/test_execution_tracking.py` - Teste básico
- `scripts/test_multiple_executions.py` - Teste de múltiplas execuções

## Vantagens

✅ **Visibilidade Instantânea**: Identifique campanhas executadas vs. não executadas com um olhar

✅ **Histórico de Execuções**: Saiba quantas vezes cada campanha foi executada

✅ **Rastreamento Temporal**: Veja quando foi a última execução e há quanto tempo

✅ **Filtros Eficientes**: Encontre rapidamente campanhas por número de execuções

✅ **Indicadores Visuais**: Cores e badges facilitam a interpretação

✅ **Automático**: Não requer ação manual - atualiza sozinho

## Exemplo de Uso Prático

### Cenário: Campanha Mensal de Reativação

1. Crie campanha "Volte para nós - Novembro 2025"
2. Configure para usuários inativos (60+ dias)
3. Execute no dia 1º de cada mês
4. No admin, você verá:
   - **Execuções**: `[✓ 1 vez]` (verde)
   - **Última Execução**: `01/11/2025 09:00 (Hoje)` (verde)

5. No dia 15, ao visualizar a lista:
   - **Execuções**: `[✓ 1 vez]` (verde)
   - **Última Execução**: `01/11/2025 09:00 (Há 14 dias)` (azul)

6. Execute novamente no dia 1º de dezembro:
   - **Execuções**: `[✓ 2 vezes]` (azul)
   - **Última Execução**: `01/12/2025 09:00 (Hoje)` (verde)

## Próximos Passos Sugeridos

1. ✅ Testar no ambiente de produção
2. ✅ Executar campanhas reais e verificar badges
3. ✅ Usar filtros para gerenciar campanhas
4. 📊 Criar relatórios baseados em execution_count
5. 📧 Configurar notificações para campanhas não executadas há X dias

## Suporte

Para dúvidas ou problemas:
- Verifique os logs de execução das campanhas
- Execute os scripts de teste para validar funcionamento
- Revise os campos no admin Django
