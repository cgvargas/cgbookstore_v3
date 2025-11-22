# Diretório de Testes

Este diretório contém scripts de teste e verificação do projeto.

## Estrutura

- **test_*.py** - Scripts de teste de funcionalidades específicas
- **check_*.py** - Scripts de verificação e diagnóstico
- **debug_*.py** - Scripts para debug de problemas específicos

## Tipos de Testes

### Testes de API
- `test_api_response.py` - Testa respostas da API
- `test_recommendations_api.py` - Testa API de recomendações

### Testes de Email
- `test_email_*.py` - Testes de funcionalidade de email
- `check_email_verification.py` - Verifica processo de verificação de email

### Testes de Banco de Dados
- `test_supabase_*.py` - Testes de conexão e funcionalidades do Supabase
- `check_database.py` - Verificação de integridade do banco

### Testes de Features
- `test_auto_move_to_read.py` - Testa movimentação automática para "lidos"
- `test_recommendations.py` - Testa sistema de recomendações

## Executando Testes

Para executar um teste específico:
```bash
python tests/test_nome_do_teste.py
```

Para executar verificações:
```bash
python tests/check_nome_da_verificacao.py
```
