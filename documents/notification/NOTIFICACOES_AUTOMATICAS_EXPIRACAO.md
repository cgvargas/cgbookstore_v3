# Sistema de Notificações Automáticas de Expiração

**Data**: 04/11/2025
**Versão**: 1.0
**Status**: ✅ Implementado e Testado

## 📋 Índice

1. [Vis ão Geral](#visão-geral)
2. [Como Funciona](#como-funciona)
3. [Comando Django](#comando-django)
4. [Mensagens Personalizadas](#mensagens-personalizadas)
5. [Configuração de Cron Job](#configuração-de-cron-job)
6. [Testes](#testes)
7. [Exemplos de Uso](#exemplos-de-uso)
8. [Troubleshooting](#troubleshooting)

---

## Visão Geral

O sistema envia **notificações automáticas** para usuários com Premium (via campanhas) que está próximo de expirar, incentivando a renovação.

### Momentos de Notificação

| Quando | Mensagem | Urgência |
|--------|----------|----------|
| **3 dias antes** | ⏰ "...expira em 3 dias. Garanta sua renovação!" | Média |
| **1 dia antes** | ⚠️ "...expira AMANHÃ! Não perca tempo, renove agora." | Alta |
| **No dia** | 🚨 "...expira HOJE! Renove agora para não perder o acesso." | Crítica |

### Benefícios

- ✅ **Aumenta retenção**: Usuários são lembrados de renovar
- ✅ **Automático**: Roda diariamente via cron sem intervenção manual
- ✅ **Não invasivo**: Máximo 1 notificação por dia por usuário
- ✅ **Personalizável**: Mensagens variam conforme urgência
- ✅ **Seguro**: Modo dry-run para testar sem enviar

---

## Como Funciona

### Fluxo de Execução

```
┌─────────────────────────────────────┐
│  Cron Job Diário (exemplo: 9h)     │
└──────────────┬──────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────┐
│  python manage.py check_expiring_premium     │
└──────────────┬───────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────┐
│  Busca CampaignGrants ativos expirando:     │
│  - Em 3 dias (00:00 a 23:59 do dia +3)      │
│  - Em 1 dia (00:00 a 23:59 do dia +1)       │
│  - Hoje (00:00 a 23:59 de hoje)             │
└──────────────┬───────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────┐
│  Para cada concessão encontrada:             │
│  1. Verifica se já foi notificado hoje       │
│  2. Se não, cria CampaignNotification        │
│  3. Usuário vê notificação no sininho        │
└──────────────────────────────────────────────┘
```

### Prevenção de Duplicatas

O sistema verifica se **já enviou notificação hoje** para aquela concessão específica:

```python
def _already_notified(self, grant, days_before):
    """Verifica se já foi enviada notificação hoje."""
    today = timezone.now().date()

    return CampaignNotification.objects.filter(
        user=grant.user,
        campaign_grant=grant,
        notification_type='premium_expiring',
        created_at__date=today
    ).exists()
```

**Resultado**: Usuário recebe **no máximo 1 notificação por dia**, mesmo que o comando seja executado múltiplas vezes.

---

## Comando Django

### Localização

```
finance/management/commands/check_expiring_premium.py
```

### Uso

#### 1. Execução Normal (Envia Notificações)

```bash
python manage.py check_expiring_premium
```

**Output:**
```
======================================================================
VERIFICAÇÃO DE PREMIUM EXPIRANDO
======================================================================

>> Verificando Premium expirando em 3 dias...
   Encontradas: 2 concessao(oes)
   [OK] joao_silva: Notificacao enviada (ID: 15)
   [OK] maria_souza: Notificacao enviada (ID: 16)
   Total notificado neste período: 2

>> Verificando Premium expirando em 1 dia...
   Encontradas: 1 concessao(oes)
   [OK] pedro_santos: Notificacao enviada (ID: 17)
   Total notificado neste período: 1

>> Verificando Premium expirando em hoje (último dia)...
   Encontradas: 0 concessao(oes)

======================================================================
RESUMO
======================================================================
Total de notificacoes enviadas: 3
[SUCCESS] Comando executado com sucesso!
```

#### 2. Dry-Run (Simula sem Enviar)

```bash
python manage.py check_expiring_premium --dry-run
```

**Uso**: Testar se o comando funciona sem criar notificações de verdade.

**Output:**
```
MODO DRY-RUN: Nenhuma notificação será enviada

>> Verificando Premium expirando em 3 dias...
   Encontradas: 2 concessao(oes)
   [NOTIFY] joao_silva: Seria notificado (DRY-RUN)
   [NOTIFY] maria_souza: Seria notificado (DRY-RUN)
   ...
```

#### 3. Verificar Apenas Um Período

```bash
# Apenas 3 dias
python manage.py check_expiring_premium --days 3

# Apenas 1 dia
python manage.py check_expiring_premium --days 1
```

**Uso**: Útil para debugging ou execuções customizadas.

---

## Mensagens Personalizadas

As mensagens variam automaticamente baseadas na urgência:

### Código (campaign_notification.py)

```python
days_left = (grant.expires_at - timezone.now()).days

if days_left <= 0:
    message = f"🚨 Seu Premium da campanha '{campaign_name}' expira HOJE! " \
              f"Renove agora para não perder o acesso."
elif days_left == 1:
    message = f"⚠️ Seu Premium da campanha '{campaign_name}' expira AMANHÃ! " \
              f"Não perca tempo, renove agora."
elif days_left <= 3:
    message = f"⏰ Seu Premium da campanha '{campaign_name}' expira em {days_left} dias. " \
              f"Garanta sua renovação!"
else:
    message = f"ℹ️ Seu Premium da campanha '{campaign_name}' expira em {days_left} dias. " \
              f"Aproveite os benefícios enquanto pode!"
```

### Exemplos Reais

| Dias Restantes | Mensagem no Sininho |
|----------------|---------------------|
| 3 | ⏰ Seu Premium da campanha 'Boas-vindas 2025' expira em 3 dias. Garanta sua renovação! |
| 2 | ⏰ Seu Premium da campanha 'Boas-vindas 2025' expira em 2 dias. Garanta sua renovação! |
| 1 | ⚠️ Seu Premium da campanha 'Boas-vindas 2025' expira AMANHÃ! Não perca tempo, renove agora. |
| 0 | 🚨 Seu Premium da campanha 'Boas-vindas 2025' expira HOJE! Renove agora para não perder o acesso. |

### Ação do Botão

Todas as notificações de expiração incluem botão:

```
[Renovar Premium] → /finance/subscription/checkout/
```

---

## Configuração de Cron Job

### Linux/Mac (crontab)

```bash
# Editar crontab
crontab -e
```

Adicionar linha:

```cron
# Executar todo dia às 9h
0 9 * * * cd /path/to/project && /path/to/venv/bin/python manage.py check_expiring_premium >> /var/log/premium_notifications.log 2>&1
```

**Explicação**:
- `0 9 * * *`: Todo dia às 9h
- `cd /path/to/project`: Vai para pasta do projeto
- `/path/to/venv/bin/python`: Usa Python do virtualenv
- `>> /var/log/...`: Salva logs
- `2>&1`: Inclui erros no log

### Windows (Task Scheduler)

1. Abrir **Task Scheduler**
2. **Create Basic Task**
3. Trigger: **Daily** at 9:00 AM
4. Action: **Start a Program**
   - Program: `C:\path\to\venv\Scripts\python.exe`
   - Arguments: `manage.py check_expiring_premium`
   - Start in: `C:\path\to\project\`

### Django-Cron (Alternativa Python)

Instalar:
```bash
pip install django-cron
```

Criar arquivo `finance/cron.py`:
```python
from django_cron import CronJobBase, Schedule

class CheckExpiringPremiumCronJob(CronJobBase):
    RUN_EVERY_MINS = 1440  # 24 horas

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'finance.check_expiring_premium'

    def do(self):
        from django.core.management import call_command
        call_command('check_expiring_premium')
```

Adicionar em `settings.py`:
```python
INSTALLED_APPS = [
    ...
    'django_cron',
]

CRON_CLASSES = [
    'finance.cron.CheckExpiringPremiumCronJob',
]
```

Rodar:
```bash
python manage.py runcrons
```

### Celery Beat (Produção Recomendado)

`celery.py`:
```python
from celery import Celery
from celery.schedules import crontab

app = Celery('cgbookstore')

app.conf.beat_schedule = {
    'check-expiring-premium-daily': {
        'task': 'finance.tasks.check_expiring_premium',
        'schedule': crontab(hour=9, minute=0),  # 9h todo dia
    },
}
```

`finance/tasks.py`:
```python
from celery import shared_task
from django.core.management import call_command

@shared_task
def check_expiring_premium():
    call_command('check_expiring_premium')
```

---

## Testes

### Teste Manual Rápido

1. **Ajustar data de uma concessão existente**:

```bash
python scripts/adjust_grant_for_testing.py
```

Isso ajusta a concessão do usuário `claud` para expirar em 3 dias.

2. **Executar dry-run**:

```bash
python manage.py check_expiring_premium --dry-run
```

**Esperado**: Deve encontrar 1 concessão e mostrar `[NOTIFY] claud: Seria notificado`

3. **Executar de verdade**:

```bash
python manage.py check_expiring_premium
```

**Esperado**: Deve mostrar `[OK] claud: Notificacao enviada (ID: X)`

4. **Verificar notificação criada**:

```bash
python scripts/list_notifications.py
```

**Esperado**: Deve mostrar a notificação nova com tipo `premium_expiring`

5. **Verificar no frontend**:
   - Login como `claud`
   - Abrir sininho
   - Ver notificação de expiração com ícone de presente

### Teste de Prevenção de Duplicatas

```bash
# Executar 2x seguidas
python manage.py check_expiring_premium
python manage.py check_expiring_premium
```

**Esperado**:
- 1ª execução: Envia notificação
- 2ª execução: Mostra `[SKIP] claud: Ja notificado`

### Teste com Diferentes Períodos

```bash
# Ajustar para 1 dia
python manage.py shell
>>> from finance.models import CampaignGrant
>>> from django.utils import timezone
>>> from datetime import timedelta
>>> grant = CampaignGrant.objects.get(id=13)
>>> grant.expires_at = timezone.now() + timedelta(days=1)
>>> grant.save()
>>> exit()

# Executar
python manage.py check_expiring_premium --days 1
```

**Esperado**: Notificação com mensagem "expira AMANHÃ!"

---

## Exemplos de Uso

### Cenário 1: Setup Inicial

```bash
# 1. Testar se funciona
python manage.py check_expiring_premium --dry-run

# 2. Se OK, configurar cron
crontab -e
# Adicionar: 0 9 * * * cd /projeto && python manage.py check_expiring_premium

# 3. Monitorar logs
tail -f /var/log/premium_notifications.log
```

### Cenário 2: Debugging

```bash
# Ver quais concessões estão expirando
python manage.py shell
>>> from finance.models import CampaignGrant
>>> from django.utils import timezone
>>> from datetime import timedelta
>>>
>>> now = timezone.now()
>>> expires_3_days = now + timedelta(days=3)
>>>
>>> grants = CampaignGrant.objects.filter(
...     is_active=True,
...     expires_at__date=expires_3_days.date()
... )
>>> for g in grants:
...     print(f"{g.user.username}: {g.expires_at}")
```

### Cenário 3: Forçar Notificação

```bash
# Deletar notificações antigas do usuário
python manage.py shell
>>> from accounts.models import CampaignNotification
>>> CampaignNotification.objects.filter(
...     user__username='claud',
...     notification_type='premium_expiring'
... ).delete()

# Executar novamente
python manage.py check_expiring_premium
```

---

## Troubleshooting

### Problema 1: Comando não encontra concessões

**Sintoma**: `Encontradas: 0 concessao(oes)` mesmo tendo Premium ativo

**Causas Possíveis**:
1. Premium já expirou ou expira em mais de 3 dias
2. Campo `is_active=False`
3. Data de expiração não está no timezone correto

**Solução**:
```bash
python manage.py shell
>>> from finance.models import CampaignGrant
>>> grants = CampaignGrant.objects.filter(is_active=True)
>>> for g in grants:
...     print(f"{g.user.username}: {g.expires_at} (ativo: {g.is_active})")
```

### Problema 2: Notificações duplicadas

**Sintoma**: Usuário recebe múltiplas notificações no mesmo dia

**Causa**: Comando executado múltiplas vezes e verificação de duplicatas não funcionou

**Solução**:
```bash
# Ver quantas notificações foram criadas hoje
python manage.py shell
>>> from accounts.models import CampaignNotification
>>> from django.utils import timezone
>>> today = timezone.now().date()
>>> notifs = CampaignNotification.objects.filter(
...     notification_type='premium_expiring',
...     created_at__date=today
... )
>>> print(f"Total hoje: {notifs.count()}")
>>> for n in notifs:
...     print(f"{n.user.username}: {n.created_at}")
```

### Problema 3: Erro de timezone

**Sintoma**: `RuntimeWarning: DateTimeField received a naive datetime`

**Causa**: Datas sem timezone

**Solução**: Sempre usar `timezone.now()` e `timezone.make_aware()`

```python
# ERRADO
from datetime import datetime
now = datetime.now()  # Naive

# CORRETO
from django.utils import timezone
now = timezone.now()  # Timezone-aware
```

### Problema 4: Encoding no Windows

**Sintoma**: `UnicodeEncodeError: 'charmap' codec can't encode character`

**Causa**: Terminal do Windows não suporta emojis

**Solução**: Os emojis são apenas visuais no terminal. A notificação no banco e no frontend funcionam normalmente. Ou rode:

```bash
# PowerShell
$OutputEncoding = [System.Text.Encoding]::UTF8
python manage.py check_expiring_premium
```

### Problema 5: Notificação não aparece no sininho

**Sintoma**: Comando diz que enviou, mas usuário não vê

**Causas**:
1. Cache do navegador
2. Usuário filtrou por categoria diferente

**Solução**:
1. Hard refresh: `Ctrl+F5`
2. Verificar filtro de categoria no painel de notificações
3. Verificar no banco:

```bash
python scripts/list_notifications.py
```

---

## Configurações Avançadas

### Alterar Períodos de Notificação

Editar `check_expiring_premium.py`:

```python
# PADRÃO: 3 dias, 1 dia, hoje
periods = [
    (3, '3 dias'),
    (1, '1 dia'),
    (0, 'hoje (último dia)'),
]

# CUSTOMIZADO: 7 dias, 3 dias, 1 dia, hoje
periods = [
    (7, '7 dias'),
    (3, '3 dias'),
    (1, '1 dia'),
    (0, 'hoje'),
]
```

### Alterar Horário de Execução

**Recomendação**: Executar de manhã (9h) para usuários terem o dia todo para renovar.

### Adicionar Logging Detalhado

```python
import logging
logger = logging.getLogger(__name__)

# Adicionar no comando
logger.info(f'Iniciando verificacao de expiracao: {timezone.now()}')
logger.info(f'Encontradas {count} concessoes expirando em {days_before} dias')
logger.info(f'Notificacao enviada: user={user.username}, grant={grant.id}')
```

Configurar em `settings.py`:
```python
LOGGING = {
    ...
    'loggers': {
        'finance.management.commands': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

---

## Métricas e Analytics

### Queries Úteis

```python
from accounts.models import CampaignNotification
from django.utils import timezone
from datetime import timedelta

# Notificações de expiração dos últimos 30 dias
last_30_days = timezone.now() - timedelta(days=30)
expiring_notifs = CampaignNotification.objects.filter(
    notification_type='premium_expiring',
    created_at__gte=last_30_days
)

# Taxa de abertura
total = expiring_notifs.count()
read = expiring_notifs.filter(is_read=True).count()
taxa_abertura = (read / total * 100) if total > 0 else 0
print(f"Taxa de abertura: {taxa_abertura:.1f}%")

# Taxa de conversão (clicou no botão)
# (Requer tracking adicional de cliques)
```

### Dashboard Admin

Adicionar em `finance/admin.py`:

```python
@admin.register(ExpiringPremiumStats)
class ExpiringPremiumStatsAdmin(admin.ModelAdmin):
    change_list_template = 'admin/expiring_premium_stats.html'

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context)

        # Calcular estatísticas
        notifs = CampaignNotification.objects.filter(
            notification_type='premium_expiring'
        )

        extra_context = {
            'total_notifs': notifs.count(),
            'total_lidas': notifs.filter(is_read=True).count(),
            'total_nao_lidas': notifs.filter(is_read=False).count(),
        }

        response.context_data.update(extra_context)
        return response
```

---

## Próximos Passos (Melhorias Futuras)

1. **Notificação por Email**
   - Além do sininho, enviar email
   - Template HTML bonito
   - Link direto para renovação

2. **Notificação Push (PWA)**
   - Push notifications no navegador
   - Funciona mesmo com app fechado

3. **SMS para Urgentes**
   - Premium expirando hoje = SMS
   - Integração com Twilio

4. **A/B Testing de Mensagens**
   - Testar diferentes textos
   - Medir qual tem maior taxa de conversão

5. **Desconto Progressivo**
   - 3 dias antes: 10% de desconto
   - 1 dia antes: 15% de desconto
   - Dia da expiração: 20% de desconto

6. **Relatório Semanal para Admins**
   - Email toda segunda-feira
   - "Esta semana: X usuários renovaram após notificação"
   - Taxa de conversão

---

## Arquivos Relacionados

| Arquivo | Descrição |
|---------|-----------|
| `finance/management/commands/check_expiring_premium.py` | Comando principal |
| `accounts/models/campaign_notification.py` | Modelo de notificações (método create_expiring_notification) |
| `scripts/adjust_grant_for_testing.py` | Script para ajustar datas para testes |
| `scripts/list_notifications.py` | Listar notificações criadas |
| `documents/notification/NOTIFICACOES_CAMPANHAS.md` | Doc geral de notificações |

---

## Changelog

### v1.0 (04/11/2025)
- ✅ Implementação inicial
- ✅ Comando Django com dry-run
- ✅ Mensagens personalizadas por urgência
- ✅ Prevenção de duplicatas
- ✅ Testes completos
- ✅ Documentação completa

---

**Desenvolvido por**: Claude Code
**Testado em**: Python 3.13, Django 5.x, PostgreSQL
