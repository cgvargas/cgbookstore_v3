# Guia de Teste do Módulo de Pagamento Premium

## 🎯 Implementações Realizadas

### ✅ 1. Webhook Completo do Mercado Pago
- ✅ Busca informações de pagamento via API
- ✅ Valida e processa todos os status (approved, pending, rejected, cancelled, refunded)
- ✅ Ativa assinatura automaticamente quando aprovado
- ✅ Cria logs de transação para auditoria
- ✅ Sincroniza com UserProfile
- ✅ Envia emails de confirmação

### ✅ 2. Sistema de Notificações por Email
- ✅ Email de pagamento aprovado (com template HTML)
- ✅ Email de assinatura expirando (7, 3, 1 dias)
- ✅ Email de assinatura expirada
- ✅ Email de pagamento falhou
- ✅ Templates profissionais com design responsivo

### ✅ 3. Gerenciamento Automático de Assinaturas
- ✅ Command `check_subscriptions` para verificar expirações
- ✅ Notificações automáticas antes de expirar
- ✅ Desativação automática de assinaturas expiradas
- ✅ Sincronização com UserProfile

### ✅ 4. Histórico de Transações
- ✅ View para listar todos os pagamentos
- ✅ Template com cards informativos
- ✅ Filtro por status e método de pagamento
- ✅ Links na página de status da assinatura

---

## 🧪 CHECKLIST DE TESTE

### Fase 1: Configuração Inicial (Ambiente Sandbox)

- [ ] **1.1 Configurar credenciais de teste no Render**
  ```bash
  # No painel do Render, adicionar:
  MERCADOPAGO_ACCESS_TOKEN=TEST-xxxxxxxxxxxxx
  MERCADOPAGO_PUBLIC_KEY=TEST-xxxxxxxxxxxxx
  SITE_URL=https://cgbookstore-v3.onrender.com
  ```

- [ ] **1.2 Verificar webhook URL no painel do Mercado Pago**
  - URL: `https://cgbookstore-v3.onrender.com/finance/webhook/mercadopago/`
  - Tipo: Pagamentos (payments)
  - Status: Ativo

- [ ] **1.3 Deploy das alterações**
  ```bash
  git add .
  git commit -m "Feat: Implementar webhook completo e sistema de notificações"
  git push origin claude/analyze-library-restrictions-011CV2kppFs3GWrWtvj4h1Bg
  ```

---

### Fase 2: Teste de Pagamento PIX (Sandbox)

- [ ] **2.1 Acessar checkout**
  - URL: https://cgbookstore-v3.onrender.com/finance/subscription/checkout/
  - Verificar se email está confirmado
  - Selecionar método: PIX
  - Clicar em "Assinar Agora"

- [ ] **2.2 Página do Mercado Pago**
  - Deve redirecionar para página de pagamento
  - Mostrar QR Code do PIX (sandbox)
  - Usar dados de teste do MP

- [ ] **2.3 Simular pagamento aprovado**
  - No sandbox, aprovar pagamento
  - Aguardar webhook (pode levar alguns segundos)

- [ ] **2.4 Verificar processamento**
  - Verificar logs do Render: `Webhook recebido`
  - Verificar: `Pagamento XXX aprovado - Ativando assinatura`
  - Verificar: `TransactionLog criado`

- [ ] **2.5 Confirmar ativação**
  - Acessar: `/finance/subscription/status/`
  - Status deve estar: ✅ **Ativa**
  - Data de expiração: 30 dias a partir de hoje
  - Método: PIX

- [ ] **2.6 Verificar email**
  - Checar inbox do usuário
  - Deve ter recebido: "✅ Pagamento Aprovado"
  - Template HTML profissional

- [ ] **2.7 Verificar histórico**
  - Acessar: `/finance/subscription/history/`
  - Deve aparecer transação com status "Aprovado"
  - Valor: R$ 9,90
  - Método: PIX

- [ ] **2.8 Verificar UserProfile**
  - No Django Admin: `/admin/accounts/userprofile/`
  - Campo `is_premium`: ✅ True
  - Campo `premium_expires_at`: Data correta

- [ ] **2.9 Testar recursos Premium**
  - Acessar chatbot: deve ter acesso ilimitado
  - Verificar se restrições de free foram removidas

---

### Fase 3: Teste de Cartão de Crédito (Sandbox)

- [ ] **3.1 Novo checkout com cartão**
  - Cancelar assinatura anterior (se houver)
  - Acessar checkout novamente
  - Selecionar: Cartão de Crédito

- [ ] **3.2 Preencher dados de teste**
  - Usar cartões de teste do MP:
    - Aprovado: 5031 4332 1540 6351
    - CVV: 123
    - Validade: qualquer futura
    - Titular: APRO (para aprovar)

- [ ] **3.3 Verificar webhook e ativação**
  - Repetir passos 2.4 a 2.9

---

### Fase 4: Teste de Pagamento Pendente

- [ ] **4.1 Simular pagamento pendente**
  - No checkout, usar cartão: OTHE (para pending)
  - Verificar webhook recebido
  - Status deve ficar: ⏳ **Pendente**

- [ ] **4.2 Verificar que não ativou**
  - Assinatura deve estar "pendente", não "ativa"
  - Premium não deve estar disponível
  - Histórico deve mostrar status "Pendente"

---

### Fase 5: Teste de Pagamento Rejeitado

- [ ] **5.1 Simular rejeição**
  - Cartão de teste: FAIL (para rejeitar)
  - Webhook deve processar
  - Status: ❌ **Cancelada**

- [ ] **5.2 Verificar tratamento**
  - Não deve ativar Premium
  - Histórico mostra "Rejeitado"

---

### Fase 6: Teste de Notificações de Expiração

- [ ] **6.1 Ajustar data de expiração manualmente**
  - No Django Admin, editar assinatura ativa
  - Mudar `expiration_date` para daqui 7 dias
  - Salvar

- [ ] **6.2 Rodar command de verificação**
  ```bash
  # Via shell do Render (se disponível) ou localmente:
  python manage.py check_subscriptions --dry-run --verbose
  ```

- [ ] **6.3 Verificar output**
  - Deve mostrar: "Encontradas: 1 assinatura(s) expirando em 7 dias"
  - Modo dry-run não deve enviar email

- [ ] **6.4 Executar comando real**
  ```bash
  python manage.py check_subscriptions --notify-days 7
  ```

- [ ] **6.5 Verificar email**
  - Usuário deve receber: "⚠️ Sua assinatura expira em 7 dias"
  - Template com contagem de dias

- [ ] **6.6 Repetir para 3 dias e 1 dia**
  - Ajustar data para 3 dias
  - Rodar: `--notify-days 3`
  - Verificar email

---

### Fase 7: Teste de Desativação Automática

- [ ] **7.1 Ajustar para expirada**
  - No Admin, mudar `expiration_date` para 1 dia atrás
  - Salvar

- [ ] **7.2 Rodar command**
  ```bash
  python manage.py check_subscriptions
  ```

- [ ] **7.3 Verificar desativação**
  - Status deve mudar para: "expirada"
  - UserProfile: `is_premium` = False
  - Email enviado: "❌ Sua assinatura expirou"

---

### Fase 8: Teste de Histórico de Transações

- [ ] **8.1 Criar múltiplas transações**
  - Fazer 3 pagamentos de teste (aprovado, pendente, rejeitado)
  - Verificar que todos aparecem no histórico

- [ ] **8.2 Validar exibição**
  - Cards com cores diferentes por status
  - Informações corretas (valor, data, método)
  - Ordenação (mais recente primeiro)

- [ ] **8.3 Teste com lista vazia**
  - Limpar transações de um usuário novo
  - Acessar histórico
  - Deve mostrar: "Nenhum histórico de pagamento"
  - Botão: "Assinar Premium Agora"

---

### Fase 9: Teste de Sincronização

- [ ] **9.1 Dessincronizar manualmente**
  - No Admin, ativar assinatura
  - No UserProfile do mesmo usuário, marcar `is_premium = False`

- [ ] **9.2 Rodar sincronização**
  ```bash
  python manage.py check_subscriptions
  ```

- [ ] **9.3 Verificar correção**
  - UserProfile deve voltar a ter `is_premium = True`

---

### Fase 10: Teste de TransactionLog

- [ ] **10.1 Verificar logs criados**
  - No Admin: `/admin/finance/transactionlog/`
  - Deve ter log para cada webhook recebido

- [ ] **10.2 Validar dados salvos**
  - `mp_payment_id`: ID do MP
  - `mp_status`: approved/pending/rejected
  - `amount`: R$ 9,90
  - `payment_method`: pix/credit_card/boleto
  - `raw_data`: JSON completo do webhook

---

## 🐛 Troubleshooting

### Webhook não está sendo recebido
1. Verificar URL no painel do MP: https://seusite.com/finance/webhook/mercadopago/
2. Verificar logs do Render: "Webhook recebido"
3. Testar localmente com ngrok:
   ```bash
   ngrok http 8000
   # Usar URL do ngrok no MP
   ```

### Pagamento não ativa assinatura
1. Verificar logs: "Pagamento XXX aprovado"
2. Verificar se `external_reference` está correto: `subscription_X`
3. Verificar se assinatura existe no banco
4. Verificar credenciais do MP (devem ser de teste para sandbox)

### Emails não estão sendo enviados
1. Verificar configurações de email no `settings.py`
2. Verificar logs: "Email de confirmação enviado"
3. Verificar se `DEFAULT_FROM_EMAIL` está configurado
4. Testar com MailHog ou serviço de email real

### Command não executa
1. Verificar se está no ambiente correto
2. Verificar se finance está em INSTALLED_APPS
3. Rodar com `--verbose` para mais detalhes

---

## 📊 Métricas de Sucesso

- [ ] Webhook processa 100% dos pagamentos
- [ ] Assinatura ativa automaticamente em < 5 segundos
- [ ] Emails chegam em < 1 minuto
- [ ] Histórico mostra todas as transações
- [ ] Command de verificação roda sem erros
- [ ] Logs de transação criados corretamente

---

## 🚀 Próximos Passos Após Teste

1. **Colocar em produção**
   - Trocar credenciais de TEST para PROD
   - Atualizar webhook URL no MP

2. **Configurar Cron Job no Render**
   ```yaml
   # render.yaml
   - type: cron
     name: check-subscriptions
     schedule: "0 10 * * *"  # Diariamente às 10:00
     command: python manage.py check_subscriptions
   ```

3. **Monitorar primeiras semanas**
   - Acompanhar logs diários
   - Verificar taxa de conversão
   - Ajustar emails conforme feedback

4. **Implementações futuras**
   - Renovação automática recorrente
   - Cupons de desconto
   - Múltiplos planos (mensal, trimestral, anual)
   - Dashboard de métricas financeiras

---

## 📝 Notas Importantes

- **Sandbox vs Produção**: Sempre testar em sandbox primeiro
- **Credenciais**: Nunca commitar credenciais reais no código
- **Logs**: Manter logs por pelo menos 30 dias para auditoria
- **Emails**: Ter backup dos templates (já salvos em git)
- **Backup**: Fazer backup do banco antes de rodar commands

---

**Data de criação**: 13/11/2024
**Última atualização**: 13/11/2024
**Autor**: Claude Code Assistant
