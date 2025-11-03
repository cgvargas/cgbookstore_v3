# Guia Rápido - Módulo Finance

## Configuração em 5 Passos

### 1. Instalar Dependências
```bash
pip install mercadopago django-environ
```

### 2. Configurar .env
```env
MERCADOPAGO_ACCESS_TOKEN=TEST-seu_token_aqui
MERCADOPAGO_PUBLIC_KEY=TEST-sua_chave_aqui
SITE_URL=http://localhost:8000
```

### 3. Atualizar settings.py
```python
# Em INSTALLED_APPS
INSTALLED_APPS = [
    # ...
    'finance',
]

# Adicionar configurações
MERCADOPAGO_ACCESS_TOKEN = env('MERCADOPAGO_ACCESS_TOKEN')
MERCADOPAGO_PUBLIC_KEY = env('MERCADOPAGO_PUBLIC_KEY')
SITE_URL = env('SITE_URL', default='http://localhost:8000')
```

### 4. Atualizar URLs principais
```python
# cgbookstore_v3/urls.py
urlpatterns = [
    # ...
    path('finance/', include('finance.urls')),
]
```

### 5. Executar Migrações
```bash
python manage.py makemigrations finance
python manage.py migrate
python manage.py runserver
```

## URLs Disponíveis

- `/finance/subscription/checkout/` - Checkout de assinatura
- `/finance/subscription/status/` - Status da assinatura
- `/admin/finance/` - Painel administrativo

## Testar o Módulo

1. Acesse: http://localhost:8000/finance/subscription/checkout/
2. Escolha PIX como método de pagamento
3. Você será redirecionado para o Mercado Pago (sandbox)
4. Use as credenciais de teste do MP

## Obter Credenciais de Teste

1. Acesse: https://www.mercadopago.com.br/developers/panel/app
2. Clique em "Suas aplicações" > "Criar aplicação"
3. Vá em "Credenciais" > "Credenciais de teste"
4. Copie:
   - Access Token (começa com TEST-)
   - Public Key (começa com TEST-)

## Próximos Passos

- Configure webhooks (necessário domínio público ou ngrok)
- Personalize os templates em `finance/templates/finance/`
- Adicione produtos para e-commerce em `/admin/finance/product/`
