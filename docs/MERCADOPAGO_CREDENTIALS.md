# Como Obter Credenciais do MercadoPago

## Problema Atual

O erro que você está enfrentando:
```
ERROR: Erro na API do Mercado Pago: At least one policy returned UNAUTHORIZED. - Status: 403
```

Isso ocorre porque as credenciais do MercadoPago não estão configuradas no arquivo `.env`.

---

## Solução: Configurar Credenciais do MercadoPago

### Passo 1: Criar/Acessar Conta no MercadoPago

1. Acesse: https://www.mercadopago.com.br/
2. Faça login ou crie uma conta (se ainda não tiver)

### Passo 2: Acessar o Painel de Desenvolvedores

1. Acesse: https://www.mercadopago.com.br/developers/panel/app
2. Faça login com sua conta do MercadoPago

### Passo 3: Criar uma Aplicação (se não tiver)

1. No painel de desenvolvedores, clique em **"Suas integrações"**
2. Clique em **"Criar aplicação"**
3. Preencha os dados:
   - **Nome da aplicação**: "CG.BookStore" (ou o nome que preferir)
   - **Descrição**: "Sistema de assinatura para autores e editoras"
   - **Tipo de integração**: Checkout Pro
4. Clique em **"Criar aplicação"**

### Passo 4: Obter Credenciais de TESTE (Recomendado para Desenvolvimento)

1. No painel da sua aplicação, vá para **"Credenciais"**
2. Selecione **"Credenciais de teste"**
3. Você verá:
   - **Public Key (teste)**: Começa com `TEST-...`
   - **Access Token (teste)**: Começa com `TEST-...`

4. Copie ambas as credenciais

### Passo 5: Adicionar Credenciais no arquivo `.env`

Abra o arquivo `.env` na raiz do projeto e adicione as credenciais:

```bash
# ==============================================================================
# MERCADOPAGO - PAYMENT GATEWAY
# ==============================================================================
MERCADOPAGO_ACCESS_TOKEN=TEST-1234567890123456-123456-abcdef1234567890abcdef1234567890-123456789
MERCADOPAGO_PUBLIC_KEY=TEST-abcdef12-3456-7890-abcd-ef1234567890
```

**⚠️ IMPORTANTE:**
- Substitua os valores acima pelas suas credenciais reais
- Use credenciais de TESTE para desenvolvimento
- NUNCA commite credenciais de PRODUÇÃO no Git

### Passo 6: Reiniciar o Servidor Django

Após adicionar as credenciais, reinicie o servidor:

```bash
# Pare o servidor (Ctrl+C)
# Inicie novamente:
python manage.py runserver
```

---

## Testando a Integração

### Usando Credenciais de TESTE

Com credenciais de teste, você pode:

1. **Simular pagamentos sem cobrar dinheiro real**
2. **Usar cartões de teste do MercadoPago**

#### Cartões de Teste para Aprovar Pagamento:

- **VISA**: 4509 9535 6623 3704
- **Mastercard**: 5031 7557 3453 0604
- **Nome**: APRO
- **CVV**: 123
- **Validade**: Qualquer data futura (ex: 11/25)

#### Cartões de Teste para Recusar Pagamento:

- **Nome**: OTHE
- **CVV**: 123
- **Número**: 5031 4332 1540 6351

#### Outros Cenários de Teste:

- **Pagamento Pendente**: Use o nome "CONT" no cartão
- **Erro de Processamento**: Use o nome "CALL" no cartão

Documentação completa: https://www.mercadopago.com.br/developers/pt/docs/checkout-pro/additional-content/test-cards

---

## Credenciais de PRODUÇÃO (Apenas quando for ao ar)

### ⚠️ Use apenas quando o sistema estiver pronto para produção!

1. No painel da aplicação, vá para **"Credenciais"**
2. Selecione **"Credenciais de produção"**
3. Você verá:
   - **Public Key (produção)**: Começa com `APP_USR-...`
   - **Access Token (produção)**: Começa com `APP_USR-...`

4. **ATENÇÃO**: Com credenciais de produção, pagamentos reais serão processados!

### Configuração de Produção no `.env`:

```bash
MERCADOPAGO_ACCESS_TOKEN=APP_USR-1234567890123456-123456-abcdef1234567890abcdef1234567890-123456789
MERCADOPAGO_PUBLIC_KEY=APP_USR-abcdef12-3456-7890-abcd-ef1234567890
```

---

## Configurações Adicionais (Opcional)

### Webhook para Notificações de Pagamento

Para receber notificações automáticas quando um pagamento for aprovado/recusado:

1. No painel da aplicação, vá para **"Webhooks"**
2. Configure a URL de notificação:
   ```
   https://seudominio.com/novos-autores/webhook/mercadopago/
   ```

**⚠️ Importante**: O webhook só funciona em produção com HTTPS. Para desenvolvimento local, você pode usar:
- **ngrok**: https://ngrok.com/
- **localtunnel**: https://localtunnel.github.io/www/

---

## Verificando se as Credenciais Estão Corretas

Após configurar, teste fazendo uma assinatura:

1. Acesse: http://localhost:8000/novos-autores/planos/autores/
2. Clique em **"Assinar Agora"** em qualquer plano
3. Você será redirecionado para o checkout do MercadoPago
4. Use um cartão de teste para simular o pagamento

Se tudo estiver correto:
- ✅ Você será redirecionado para o checkout do MercadoPago
- ✅ Após pagar, será redirecionado para a página de sucesso
- ✅ Sua assinatura será ativada automaticamente

---

## Troubleshooting

### Erro 403 UNAUTHORIZED

**Problema**: Credenciais não configuradas ou inválidas

**Solução**:
1. Verifique se o `.env` tem as variáveis `MERCADOPAGO_ACCESS_TOKEN` e `MERCADOPAGO_PUBLIC_KEY`
2. Verifique se as credenciais estão corretas (copie novamente do painel)
3. Reinicie o servidor Django

### Erro 404 Not Found

**Problema**: Credenciais de teste não ativadas

**Solução**:
1. No painel do MercadoPago, vá para "Credenciais de teste"
2. Clique em "Ativar credenciais de teste"

### Checkout não abre

**Problema**: `init_point` não foi retornado

**Solução**:
1. Verifique os logs do Django
2. Certifique-se de que está usando credenciais válidas
3. Verifique se o MercadoPago SDK está instalado: `pip install mercadopago`

---

## Links Úteis

- **Painel de Desenvolvedores**: https://www.mercadopago.com.br/developers/panel/app
- **Documentação do Checkout Pro**: https://www.mercadopago.com.br/developers/pt/docs/checkout-pro/landing
- **Cartões de Teste**: https://www.mercadopago.com.br/developers/pt/docs/checkout-pro/additional-content/test-cards
- **Referência da API**: https://www.mercadopago.com.br/developers/pt/reference

---

## Status Atual da Integração

✅ **Código implementado e funcional**
- Service layer criado ([new_authors/services/payment_service.py](../new_authors/services/payment_service.py))
- Views de pagamento criadas ([new_authors/payment_views.py](../new_authors/payment_views.py))
- Templates de sucesso/falha/pendente criados
- Formulários de checkout adicionados aos planos

❌ **Faltando: Credenciais do MercadoPago**
- Adicione as credenciais no `.env` seguindo este guia
- Use credenciais de TESTE para desenvolvimento

🔄 **Após configurar credenciais**
- Reinicie o servidor
- Teste fazendo uma assinatura
- Use cartões de teste para simular pagamentos
