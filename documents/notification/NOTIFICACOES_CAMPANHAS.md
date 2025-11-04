# Sistema de Notificações de Campanhas

## Visão Geral

Sistema completo de notificações que permite que usuários sejam avisados através do sininho (bell icon) quando receberem Premium via campanhas de marketing.

## Funcionalidades Implementadas

### 1. Novo Campo no Modelo Campaign

Foi adicionado o campo `send_notification` ao modelo `Campaign`:

```python
send_notification = models.BooleanField(
    default=True,
    verbose_name='Enviar Notificação',
    help_text='Se marcado, os usuários receberão uma notificação no sininho quando receberem Premium'
)
```

**Características:**
- ✅ Habilitado por padrão (`default=True`)
- ✅ Pode ser desabilitado para campanhas silenciosas
- ✅ Aparece no formulário de criação/edição de campanhas no admin

### 2. Modelo CampaignNotification

Novo modelo de notificação criado em `accounts/models/campaign_notification.py`:

**Campos principais:**
- `user`: Usuário que recebe a notificação
- `campaign`: Campanha que gerou a notificação
- `campaign_grant`: Concessão de Premium relacionada
- `notification_type`: Tipo de notificação (premium_granted, premium_expiring, etc.)
- `message`: Mensagem da notificação
- `is_read`: Status de leitura
- `priority`: Prioridade (Baixa, Média, Alta)
- `action_url`: URL para onde a notificação direciona
- `action_text`: Texto do botão de ação

**Herda de BaseNotification:**
- Sistema unificado de notificações
- Integração automática com o sininho
- Métodos prontos: `mark_as_read()`, `mark_as_unread()`
- Propriedades úteis: `formatted_time`, `age_in_hours`, `is_recent`

### 3. Tipos de Notificações

Três tipos implementados:

#### Premium Concedido (`premium_granted`)
```
🎉 Parabéns! Você recebeu 7 dias de Premium através da campanha 'Nome da Campanha'!
Ação: Ver Benefícios → /premium/
```

#### Premium Expirando (`premium_expiring`)
```
⚠️ Seu Premium da campanha 'Nome' expira em X dia(s). Aproveite os benefícios enquanto pode!
Ação: Assinar Premium → /premium/
```

#### Premium Expirado (`premium_expired`)
```
ℹ️ Seu Premium da campanha 'Nome' expirou. Assine para continuar aproveitando!
Ação: Assinar Premium → /premium/
```

### 4. Integração com CampaignService

O `CampaignService.grant_premium()` foi atualizado para enviar notificações automaticamente:

```python
# Enviar notificação se habilitado
if campaign.send_notification:
    try:
        from accounts.models import CampaignNotification
        notification = CampaignNotification.create_premium_granted_notification(
            user=user,
            campaign=campaign,
            grant=grant
        )
        logger.info(f"Notificação enviada para {user.username}: {notification.id}")
    except Exception as e:
        logger.warning(f"Erro ao enviar notificação para {user.username}: {str(e)}")
```

**Comportamento:**
- ✅ Verifica se `campaign.send_notification` está habilitado
- ✅ Cria notificação automaticamente ao conceder Premium
- ✅ Registra logs de sucesso ou erro
- ✅ Não interrompe a execução se houver erro na notificação

### 5. Interface Admin

#### Formulário de Campanha
O campo `send_notification` aparece na seção "Configuração":

```
Configuração:
  - Duração do Premium Gratuito
  - Tipo de Público-Alvo
  - Critérios de Seleção
  - Concessão Automática
  - ☑️ Enviar Notificação  ← NOVO!
  - Limite de Concessões
```

#### Admin de CampaignNotification

Novo admin em `/admin/accounts/campaignnotification/`:

**Colunas exibidas:**
- Usuário
- Campanha
- Tipo de notificação
- Status (Lida/Não lida) com ícones coloridos
- Prioridade
- Data de criação

**Filtros disponíveis:**
- Tipo de notificação
- Status de leitura
- Prioridade
- Data de criação

**Ações em massa:**
- Marcar como lida
- Marcar como não lida

**Campos somente leitura:**
- created_at, read_at
- campaign, campaign_grant
- user, notification_type, message

## Como Usar

### 1. Criar Campanha com Notificações

No admin Django:

1. Acesse `/admin/finance/campaign/add/`
2. Preencha os dados da campanha
3. Na seção "Configuração":
   - ✅ Marque "Enviar Notificação" (já vem marcado por padrão)
4. Salve a campanha

### 2. Executar Campanha

Quando a campanha for executada (manual ou automaticamente):

1. Sistema concede Premium aos usuários elegíveis
2. Se `send_notification = True`:
   - Cria automaticamente uma `CampaignNotification` para cada usuário
   - Notificação aparece no sininho do frontend
   - Usuário é avisado na próxima vez que acessar o site

### 3. Visualizar Notificações

**No Admin:**
- `/admin/accounts/campaignnotification/`
- Veja todas as notificações enviadas
- Filtre por usuário, campanha, status de leitura
- Marque manualmente como lida/não lida

**No Frontend (para usuários):**
- Clique no sininho (bell icon)
- Veja notificações não lidas
- Clique para marcar como lida
- Clique no botão de ação para ir para `/premium/`

### 4. Desabilitar Notificações (Campanha Silenciosa)

Se quiser conceder Premium sem notificar:

1. Edite a campanha
2. Desmarque "Enviar Notificação"
3. Salve
4. Ao executar, Premium será concedido mas sem notificação

## Scripts de Teste

### test_campaign_notifications.py

Testa o envio de notificações em campanhas existentes:

```bash
python scripts/test_campaign_notifications.py
```

**O que faz:**
- Busca campanhas ativas
- Verifica se têm notificações habilitadas
- Executa a campanha
- Conta notificações criadas
- Mostra estatísticas

### create_test_campaign_with_notification.py

Cria uma nova campanha de teste e executa:

```bash
python scripts/create_test_campaign_with_notification.py
```

**O que faz:**
- Cria campanha "Teste de Notificações - Premium 7 dias"
- Público-alvo: usuario_ativo_1, usuario_ativo_2
- Notificações habilitadas
- Executa automaticamente
- Mostra notificações criadas

### list_notifications.py

Lista todas as notificações existentes:

```bash
python scripts/list_notifications.py
```

**Saída:**
```
📬 Total: 2 notificação(ões)

🔔 Notificação #1
   Usuário: usuario_ativo_1
   Campanha: Teste de Notificações
   Tipo: premium_granted
   Mensagem: 🎉 Parabéns! Você recebeu 7 dias de Premium...
   Prioridade: Média
   Lida: Não ●
   Criada: 04/11/2025 11:08:44
   Ação: Ver Benefícios → /premium/
```

## Arquivos Modificados/Criados

### Models
- ✅ **`finance/models.py`** - Adicionado campo `send_notification`
- ✅ **`accounts/models/campaign_notification.py`** - Novo modelo criado
- ✅ **`accounts/models/__init__.py`** - Import adicionado

### Services
- ✅ **`finance/services.py`** - Lógica de envio de notificações em `grant_premium()`

### Admin
- ✅ **`finance/admin.py`** - Campo `send_notification` adicionado ao formulário
- ✅ **`accounts/admin.py`** - Admin completo para `CampaignNotification`

### Migrations
- ✅ **`finance/migrations/0004_campaign_send_notification.py`** - Campo send_notification
- ✅ **`accounts/migrations/0012_...campaignnotification.py`** - Modelo CampaignNotification

### Scripts
- ✅ **`scripts/test_campaign_notifications.py`** - Teste de notificações
- ✅ **`scripts/create_test_campaign_with_notification.py`** - Criar e testar
- ✅ **`scripts/list_notifications.py`** - Listar notificações

## Fluxo Completo

```
1. Admin cria Campanha
   └─> send_notification = True ✓

2. Admin executa Campanha
   └─> CampaignService.execute_campaign()

3. Para cada usuário elegível:
   └─> CampaignService.grant_premium()
       ├─> Cria Subscription
       ├─> Cria CampaignGrant
       ├─> Atualiza UserProfile
       └─> Se send_notification = True:
           └─> CampaignNotification.create_premium_granted_notification()
               ├─> Cria registro no banco
               ├─> Notificação aparece no sininho
               └─> Usuário é notificado

4. Usuário acessa o site
   ├─> Vê sininho com badge (1)
   ├─> Clica no sininho
   ├─> Vê: "🎉 Parabéns! Você recebeu 7 dias de Premium..."
   ├─> Clica em "Ver Benefícios"
   └─> Redirecionado para /premium/
```

## Estrutura da Notificação

```python
CampaignNotification {
    id: 1,
    user: User(usuario_ativo_1),
    campaign: Campaign("Teste de Notificações"),
    campaign_grant: CampaignGrant(#123),
    notification_type: "premium_granted",
    message: "🎉 Parabéns! Você recebeu 7 dias de Premium...",
    is_read: False,
    priority: 2,  # Média
    action_url: "/premium/",
    action_text: "Ver Benefícios",
    created_at: "2025-11-04 11:08:44",
    read_at: None,
    extra_data: {
        "campaign_id": 7,
        "campaign_name": "Teste de Notificações",
        "duration_days": 7,
        "expires_at": "2025-11-11T11:08:44"
    }
}
```

## Próximos Passos Sugeridos

1. ✅ Integrar com frontend (sininho já existente)
2. ✅ Testar visualização no navegador
3. ✅ Criar notificações de Premium expirando (scheduled task)
4. ✅ Adicionar email opcional além da notificação
5. ✅ Dashboard de notificações para admin
6. ✅ Estatísticas de taxa de abertura

## Vantagens

✅ **Engajamento**: Usuários são avisados imediatamente quando recebem Premium

✅ **Flexibilidade**: Pode ser habilitado/desabilitado por campanha

✅ **Rastreabilidade**: Todas as notificações ficam registradas no banco

✅ **Integração**: Usa sistema de notificações existente (BaseNotification)

✅ **Prioridades**: Suporta diferentes níveis de prioridade

✅ **Ações**: Botão de ação direciona para página de benefícios

✅ **Admin**: Interface completa para gerenciar notificações

✅ **Logs**: Sistema registra erros e sucessos

## Suporte

Para testar:
1. Execute `python scripts/create_test_campaign_with_notification.py`
2. Faça login como `usuario_ativo_1` (senha: `test123`)
3. Clique no sininho no header
4. Veja a notificação de Premium concedido!
