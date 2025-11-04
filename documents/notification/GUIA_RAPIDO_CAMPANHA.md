# 📱 Guia Rápido: Enviar Campanha para Usuário "claud"

## ⚡ Método Rápido (Script Automatizado)

```bash
python scripts/create_campaign_for_user.py claud 30
```

✅ Pronto! A campanha será criada e executada automaticamente!

---

## 🖱️ Método Manual (Via Admin)

### 1️⃣ Criar Campanha
```
/admin/finance/campaign/add/
```

| Campo | Valor |
|-------|-------|
| **Nome** | Premium para claud - 30 dias |
| **Descrição** | Campanha especial para claud |
| **Status** | Ativa |
| **Duração** | 30 dias |
| **Público-Alvo** | Usuário Individual |
| **Critérios** | `{"username": "claud"}` |
| **✅ Concessão Automática** | MARCAR |
| **✅ Enviar Notificação** | MARCAR ⚠️ |
| **Data Início** | Hoje |
| **Data Término** | Daqui a 1 ano |

### 2️⃣ Executar Campanha
```
/admin/finance/campaign/
```

1. Marque a checkbox da campanha
2. Ação: **"Executar campanhas selecionadas"**
3. Clique em **"Ir"**

### 3️⃣ Verificar Notificação
```
/admin/accounts/campaignnotification/
```

✅ Deve aparecer notificação para o usuário "claud"

---

## 🔍 Verificação Rápida

### Via Console
```bash
# Verificar se usuário existe
python manage.py shell -c "from django.contrib.auth.models import User; print(User.objects.filter(username='claud').exists())"

# Verificar notificações criadas
python manage.py shell -c "from accounts.models import CampaignNotification; print(CampaignNotification.objects.filter(user__username='claud').count())"

# Listar todas as notificações do claud
python scripts/list_notifications.py
```

---

## 📊 O Que Acontece Quando Você Executa

```
1. Campanha é criada
   └─> Nome: "Premium para claud - 30 dias"
   └─> Status: Ativa
   └─> Notificação: ✓ Habilitada

2. Campanha é executada
   └─> Busca usuário "claud"
   └─> Cria CampaignGrant (concessão)
   └─> Ativa Subscription (assinatura)
   └─> Atualiza UserProfile (is_premium = True)
   └─> 🔔 Cria CampaignNotification

3. Usuário "claud" recebe
   └─> 30 dias de Premium
   └─> Notificação no sininho
   └─> Pode clicar e ver: "🎉 Parabéns! Você recebeu 30 dias..."
```

---

## 🎯 Checklist de Verificação

Após executar, verifique:

- [ ] Concessão criada em `/admin/finance/campaigngrant/`
- [ ] Notificação criada em `/admin/accounts/campaignnotification/`
- [ ] UserProfile tem `is_premium = True`
- [ ] Assinatura ativada em `/admin/finance/subscription/`
- [ ] Sininho do claud mostra badge (1)

---

## ⚠️ Importante!

**NÃO ESQUEÇA de marcar:**
- ✅ **Enviar Notificação** ← SEM ISSO, não haverá notificação no sininho!
- ✅ **Concessão Automática** ← Para conceder automaticamente

---

## 🆘 Problemas Comuns

### Usuário "claud" não existe?

```bash
# Criar usuário
python manage.py createsuperuser
# Username: claud
# Email: claud@example.com
# Password: (sua senha)
```

### Notificação não aparece?

1. Verifique se "Enviar Notificação" estava marcado
2. Verifique em `/admin/accounts/campaignnotification/`
3. Execute `python scripts/list_notifications.py`

### Campanha não executou?

1. Status = "Ativa" ✓
2. Data início ≤ hoje ✓
3. Data término > hoje ✓
4. Critério correto: `{"username": "claud"}` ✓

---

## 📞 Ajuda Rápida

```bash
# Ver usuários disponíveis
python manage.py shell -c "from django.contrib.auth.models import User; [print(u.username) for u in User.objects.all()[:10]]"

# Ver campanhas ativas
python manage.py shell -c "from finance.models import Campaign; [print(c.name) for c in Campaign.objects.filter(status='active')]"

# Ver notificações do claud
python scripts/list_notifications.py
```

---

✅ **Siga este guia e o usuário "claud" receberá Premium com notificação!**
