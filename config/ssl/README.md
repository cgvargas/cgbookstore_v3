# Certificados SSL

Este diretório contém certificados SSL para desenvolvimento local com HTTPS.

## Arquivos

- **cert.crt** - Certificado SSL
- **cert.key** - Chave privada do certificado

## Uso

Estes certificados são utilizados para:
- Desenvolvimento local com HTTPS
- Teste de funcionalidades que requerem conexão segura
- Integração com serviços que exigem SSL

## Geração de Novos Certificados

Para gerar novos certificados auto-assinados:

```bash
openssl req -x509 -newkey rsa:4096 -nodes \
  -out config/ssl/cert.crt \
  -keyout config/ssl/cert.key \
  -days 365 \
  -subj "/CN=localhost"
```

## Configuração no Django

Para usar com django-extensions:

```python
# settings.py
INSTALLED_APPS = [
    ...
    'django_extensions',
]
```

Executar servidor:
```bash
python manage.py runserver_plus --cert-file config/ssl/cert.crt --key-file config/ssl/cert.key
```

## Notas Importantes

⚠️ **NÃO versionar certificados de produção**
⚠️ Certificados auto-assinados são apenas para desenvolvimento
⚠️ Em produção, use certificados válidos (Let's Encrypt, etc.)
⚠️ Os arquivos `.crt` e `.key` estão no `.gitignore`

## Segurança

- Nunca compartilhe chaves privadas
- Use certificados válidos em produção
- Mantenha permissões restritas nos arquivos de chave
