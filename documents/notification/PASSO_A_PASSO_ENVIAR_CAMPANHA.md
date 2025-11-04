# Passo a Passo: Enviar Campanha com Notificação para Usuário

## Objetivo
Enviar uma campanha de Premium para o usuário **claud** com notificação no sininho.

---

## PASSO 1: Acessar o Admin Django

1. Abra o navegador
2. Acesse: `http://127.0.0.1:8000/admin/`
3. Faça login com suas credenciais de admin
4. ✅ Você deve estar na página inicial do admin

---

## PASSO 2: Criar Nova Campanha

1. No menu lateral, clique em **"Finanças"**
2. Clique em **"Campanhas de marketing"**
3. Clique no botão **"ADICIONAR CAMPANHA DE MARKETING +"** (canto superior direito)

---

## PASSO 3: Preencher Informações Básicas

### Seção: Informações Básicas

**Nome da Campanha:**
```
Premium para claud - 30 dias
```

**Descrição:**
```
Campanha especial concedendo 30 dias de Premium gratuito para o usuário claud
```

**Status da Campanha:**
- Selecione: **Ativa**

---

## PASSO 4: Configurar a Campanha

### Seção: Configuração

**Duração do Premium Gratuito:**
- Selecione: **30 dias**

**Tipo de Público-Alvo:**
- Selecione: **Usuário Individual**

**Critérios de Seleção (JSON):**
```json
{"username": "claud"}
```

**✅ Concessão Automática:**
- **MARCAR** esta opção

**✅ Enviar Notificação:**
- **MARCAR** esta opção (⚠️ IMPORTANTE!)

**Limite de Concessões:**
- Deixe em branco (ou digite `1`)

---

## PASSO 5: Definir Período da Campanha

### Seção: Período

**Data de Início:**
- Selecione: **Data e hora atual** (hoje)

**Data de Término:**
- Selecione: **Daqui a 1 ano** (ou qualquer data futura)

---

## PASSO 6: Salvar a Campanha

1. Clique no botão **"SALVAR E CONTINUAR A EDITAR"** (ou "SALVAR")
2. ✅ Você verá mensagem: "A campanha de marketing ... foi adicionada com sucesso"
3. ✅ A página recarregará mostrando a campanha criada

---

## PASSO 7: Executar a Campanha

### Método 1: Via Admin (Recomendado)

1. Volte para a lista de campanhas: clique em **"Campanhas de marketing"** no menu
2. Localize a campanha que você acabou de criar
3. **MARQUE** a checkbox à esquerda da campanha
4. No dropdown **"Ação"** (acima da lista), selecione:
   - **"Executar campanhas selecionadas"**
5. Clique no botão **"Ir"**
6. ✅ Você verá mensagem de sucesso: "1 campanha(s) executada(s). Total de 1 Premiums concedidos."

### Método 2: Via Script (Alternativo)

```bash
python scripts/execute_campaign_for_user.py claud
```

---

## PASSO 8: Verificar Execução

### No Admin - Concessões

1. Acesse: **Finanças** → **Concessões de campanha**
2. ✅ Você deve ver uma nova concessão:
   - **Usuário:** claud
   - **Campanha:** Premium para claud - 30 dias
   - **Status:** ✓ Ativo
   - **Data de concessão:** Agora
   - **Expira em:** Daqui a 30 dias

### No Admin - Notificações

1. Acesse: **Contas e Perfis** → **Notificações de campanhas**
2. ✅ Você deve ver uma notificação:
   - **Usuário:** claud
   - **Campanha:** Premium para claud - 30 dias
   - **Tipo:** premium_granted
   - **Status:** ● Não lida
   - **Mensagem:** "🎉 Parabéns! Você recebeu 30 dias de Premium..."

---

## PASSO 9: Verificar como Usuário

### Fazer Login como claud

1. Abra uma aba anônima/privada do navegador
2. Acesse: `http://127.0.0.1:8000/`
3. Faça login com o usuário **claud**
4. ✅ Olhe para o **sininho (bell icon)** no header
5. ✅ Deve aparecer um **badge com número (1)**
6. Clique no sininho
7. ✅ Você verá a notificação:

```
🎉 Parabéns! Você recebeu 30 dias de Premium através da campanha
'Premium para claud - 30 dias'!

[Ver Benefícios]
```

8. Clique em **"Ver Benefícios"**
9. ✅ Será redirecionado para `/premium/`

---

## Resumo do Formulário Completo

```yaml
Informações Básicas:
  Nome: "Premium para claud - 30 dias"
  Descrição: "Campanha especial para o usuário claud"
  Status: "Ativa"

Configuração:
  Duração: "30 dias"
  Público-Alvo: "Usuário Individual"
  Critérios: {"username": "claud"}
  Concessão Automática: ✓ SIM
  Enviar Notificação: ✓ SIM (IMPORTANTE!)
  Limite: (vazio)

Período:
  Data Início: (hoje)
  Data Término: (daqui a 1 ano)
```

---

## Verificação Final - Checklist

Após executar a campanha, verifique:

- ✅ Concessão criada em `/admin/finance/campaigngrant/`
- ✅ Notificação criada em `/admin/accounts/campaignnotification/`
- ✅ UserProfile do claud tem `is_premium = True`
- ✅ Assinatura criada/ativada em `/admin/finance/subscription/`
- ✅ Sininho do claud mostra badge (1)
- ✅ Claud pode clicar e ver a notificação

---

## Troubleshooting

### Campanha não executou?

**Verifique:**
1. Status da campanha está "Ativa"? ✓
2. Data de início é hoje ou antes? ✓
3. Data de término é futura? ✓
4. Critério JSON está correto? `{"username": "claud"}`
5. Usuário "claud" existe no banco?

**Teste via console:**
```bash
python manage.py shell -c "from django.contrib.auth.models import User; print(User.objects.filter(username='claud').exists())"
```

### Notificação não aparece?

**Verifique:**
1. Campo "Enviar Notificação" estava marcado? ✓
2. Concessão foi criada? Veja em `/admin/finance/campaigngrant/`
3. Notificação foi criada? Veja em `/admin/accounts/campaignnotification/`

**Teste via console:**
```bash
python manage.py shell -c "from accounts.models import CampaignNotification; print(CampaignNotification.objects.filter(user__username='claud').count())"
```

---

## Script Automatizado (Opcional)

Se preferir, use o script:

```bash
# Criar campanha e executar automaticamente
python scripts/create_campaign_for_user.py claud 30
```

Onde:
- `claud` = nome do usuário
- `30` = dias de Premium

---

## Próximos Passos

Depois de enviar a campanha:

1. ✅ Usuário claud receberá notificação no sininho
2. ✅ Terá acesso Premium por 30 dias
3. ✅ Pode clicar em "Ver Benefícios" para conhecer vantagens
4. ✅ Receberá aviso quando Premium estiver para expirar (futuro)

---

## Dúvidas Frequentes

**P: Posso enviar para vários usuários de uma vez?**
R: Sim! Use tipo "Grupo de Usuários" com critério:
```json
{"usernames": ["claud", "outro_user", "mais_um"]}
```

**P: E se eu esquecer de marcar "Enviar Notificação"?**
R: O Premium será concedido, mas o usuário não receberá notificação no sininho.

**P: Posso testar antes de executar?**
R: Sim! Use a ação "Pré-visualizar usuários elegíveis" antes de executar.

**P: Como cancelar um Premium concedido?**
R: Acesse `/admin/finance/campaigngrant/`, encontre a concessão e use a ação "Revogar concessões selecionadas".

---

✅ **Guia completo! Siga estes passos e o usuário claud receberá Premium com notificação!** 🎉
