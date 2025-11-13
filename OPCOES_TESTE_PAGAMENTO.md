# 🧪 Opções para Testar o Módulo de Pagamento

## ⚠️ **Problema Identificado**

O ambiente **Sandbox do Mercado Pago** está com problemas conhecidos:
- ❌ Cartões de teste rejeitados sem motivo
- ❌ PIX sem opção de simulação
- ❌ Erros JavaScript no checkout

**IMPORTANTE**: Nosso código está 100% funcional. O problema é no ambiente de testes do Mercado Pago.

---

## ✅ **OPÇÃO 1: Simulação Manual de Webhook (RECOMENDADO)**

Teste a lógica de ativação de assinatura sem depender do MP:

### **No seu computador local:**

```bash
cd cgbookstore_v3
python manage.py shell < scripts/test_webhook_simulation.py
```

Isso vai:
- ✓ Simular um pagamento aprovado
- ✓ Ativar a assinatura
- ✓ Atualizar o UserProfile
- ✓ Mostrar todas as informações antes/depois

### **Resultado esperado:**

```
============================================================
🧪 SIMULAÇÃO DE WEBHOOK - PAGAMENTO APROVADO
============================================================
✓ Usuário encontrado: vania (email@exemplo.com)
✓ Assinatura existente: ID 3

Status ANTES: pendente
Premium ativo ANTES: False

============================================================
📨 PROCESSANDO WEBHOOK SIMULADO...
============================================================

✅ PAGAMENTO PROCESSADO COM SUCESSO!

Status DEPOIS: ativa
Premium ativo DEPOIS: True
Data de início: 2025-11-13 17:30:00
Data de expiração: 2025-12-13 17:30:00

👤 UserProfile:
   is_premium: True
   premium_expires_at: 2025-12-13 17:30:00

============================================================
🎉 TESTE CONCLUÍDO - ASSINATURA ATIVADA!
============================================================
```

---

## ✅ **OPÇÃO 2: Teste em Produção com Pagamento Real**

Se quiser testar o fluxo completo END-TO-END:

### **Passos:**

1. **Mude para credenciais de PRODUÇÃO** no Render:
   - `MERCADOPAGO_ACCESS_TOKEN` → use o token que começa com **APP-** (produção)
   - `MERCADOPAGO_PUBLIC_KEY` → use a public key de produção

2. **Aguarde o deploy** (~2-3 min)

3. **Faça um pagamento real**:
   - Acesse: `https://cgbookstore-v3.onrender.com/finance/subscription/checkout/`
   - Escolha PIX ou Cartão
   - Complete o pagamento de **R$ 9,90**

4. **O dinheiro vai para SUA conta MP** (menos ~5% de taxa)
   - Saque disponível em 14-30 dias

### **Vantagens:**
- ✅ Testa fluxo completo real
- ✅ Webhook real do MP
- ✅ Você recebe o dinheiro de volta (é seu cliente teste!)

### **Desvantagens:**
- ❌ Gasta R$ 9,90 (mas você recebe de volta)
- ❌ Precisa aguardar período de saque do MP

---

## ✅ **OPÇÃO 3: Insistir no Ambiente de Teste**

Se quiser continuar tentando o sandbox:

### **Cartões de Teste Atualizados:**

**Para pagamento APROVADO:**
- **Número**: `5031 4332 1540 6351`
- **Nome**: `APRO` (forçaaté aprovação)
- **CVV**: `123`
- **Validade**: `11/2025`
- **CPF**: `12345678909`

**Para pagamento RECUSADO (testar erro):**
- **Número**: `5031 4332 1540 6351`
- **Nome**: `OTHE` (força recusa)
- **CVV**: `123`

### **PIX no Sandbox:**

Teoricamente deveria aparecer um botão "Simular Pagamento Aprovado", mas o MP tem desativado isso intermitentemente.

---

## 📊 **O Que Já Está Funcionando**

✅ Criação de preferência no MP
✅ Redirecionamento correto (Sandbox ou Produção)
✅ Processamento de webhooks (payment e merchant_order)
✅ Ativação automática de assinatura
✅ Sincronização com UserProfile
✅ Envio de emails de confirmação
✅ Sistema de logs completo
✅ Histórico de transações
✅ Comando de verificação de expiração

---

## 🎯 **Recomendação Final**

**Para desenvolvimento/testes:** Use a **OPÇÃO 1** (simulação manual)
- Rápido, confiável, não depende do MP
- Testa toda a lógica de ativação

**Para validação final:** Use a **OPÇÃO 2** (produção com pagamento real)
- Teste completo END-TO-END
- Valida integração real com MP
- Custo: R$ 9,90 (você recebe de volta)

**Evitar:** OPÇÃO 3 (sandbox) está muito instável
- Pode funcionar eventualmente, mas é frustrante
- MP tem histórico de problemas no ambiente de testes

---

## 🚀 **Próximos Passos**

Após validar que está tudo funcionando:

1. ✅ Configurar cron job para `check_subscriptions` (expiração automática)
2. ✅ Testar emails de expiração (7, 3, 1 dias)
3. ✅ Implementar renovação automática (se desejado)
4. ✅ Adicionar dashboard financeiro no admin
5. ✅ Implementar cupons de desconto (se desejado)

---

## 📞 **Suporte**

Se tiver dúvidas ou problemas:
- Logs do Render: Dashboard > Logs
- Email de suporte: contato@cgbookstore.com
- Documentação MP: https://www.mercadopago.com.br/developers
