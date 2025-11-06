# ✅ Checklist de Produção - CGBookStore

## 📦 Preparação Concluída

### ✅ Configurações de Segurança
- [x] SECRET_KEY configurável via variável de ambiente
- [x] DEBUG=False por padrão
- [x] ALLOWED_HOSTS configurável
- [x] CSRF_TRUSTED_ORIGINS configurável
- [x] HTTPS/SSL redirect habilitado em produção
- [x] HSTS configurado (1 ano)
- [x] Headers de segurança (XSS, Content-Type, X-Frame)
- [x] WhiteNoise para servir arquivos estáticos
- [x] Cookies seguros (SECURE, HTTPONLY)

### ✅ Arquivos de Deploy
- [x] build.sh - Script de build do Render
- [x] render.yaml - Configuração de infraestrutura
- [x] .env.example - Template de variáveis de ambiente
- [x] DEPLOY_RENDER.md - Documentação completa
- [x] requirements.txt atualizado

### ✅ Configurações do Banco de Dados
- [x] PostgreSQL configurado via DATABASE_URL
- [x] Connection pooling (conn_max_age=600)
- [x] Health checks habilitados

### ✅ Cache e Background Tasks
- [x] Redis configurado para cache
- [x] Celery configurado para tarefas assíncronas
- [x] REDIS_URL configurável

## 🚀 Próximos Passos para Deploy

### 1. Render.com Setup

1. **Criar conta no Render**: https://render.com
2. **Conectar repositório Git**
3. **Criar Blueprint** usando render.yaml
4. **Configurar variáveis de ambiente**

### 2. Variáveis de Ambiente Essenciais

```bash
# Django
SECRET_KEY=<gerar-nova-chave>
DEBUG=False
ALLOWED_HOSTS=<seu-app>.onrender.com
CSRF_TRUSTED_ORIGINS=https://<seu-app>.onrender.com

# Supabase (OBRIGATÓRIO)
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_ANON_KEY=sua-anon-key
SUPABASE_SERVICE_KEY=sua-service-key

# Google Gemini AI (OBRIGATÓRIO)
GOOGLE_API_KEY=sua-google-api-key
```

### 3. Variáveis Opcionais

```bash
# Social Authentication
GOOGLE_CLIENT_ID=seu-google-client-id
GOOGLE_CLIENT_SECRET=seu-google-client-secret
FACEBOOK_APP_ID=seu-facebook-app-id
FACEBOOK_APP_SECRET=seu-facebook-app-secret

# Mercado Pago
MERCADOPAGO_ACCESS_TOKEN=seu-access-token
MERCADOPAGO_PUBLIC_KEY=sua-public-key
```

### 4. Após o Deploy

- [ ] Testar cadastro/login
- [ ] Testar upload de imagens (Supabase)
- [ ] Testar sistema de recomendações (Google Gemini)
- [ ] Configurar callbacks OAuth (se usar social auth)
- [ ] Configurar domínio customizado (opcional)
- [ ] Monitorar logs
- [ ] Configurar backups do PostgreSQL

## 📊 Monitoramento

### Métricas a Observar
- Response time
- Error rate
- Database connections
- Redis memory usage
- Celery tasks

### Logs
- Acessar via Render Dashboard → Logs
- Filtrar por nível (ERROR, WARNING, INFO)

## 🔄 Workflow de Atualização

1. Desenvolver localmente
2. Testar todas as funcionalidades
3. Commit e push para `main`
4. Render faz deploy automático
5. Monitorar logs durante deploy
6. Verificar funcionalidades em produção

## ⚠️ Avisos Importantes

1. **Plano Free do Render**:
   - Serviço hiberna após 15 min de inatividade
   - Primeiro acesso após hibernação é lento (~30s)
   - Considere upgrade para produção real

2. **Backups**:
   - PostgreSQL: backups automáticos (plano free = 7 dias)
   - Supabase: gerencia próprio backup

3. **Limites**:
   - PostgreSQL Free: 256MB
   - Redis Free: 25MB
   - Considere upgrade se necessário

## 📚 Documentação

- Guia completo: [DEPLOY_RENDER.md](./DEPLOY_RENDER.md)
- Variáveis de ambiente: [.env.example](./.env.example)
- Configuração do Render: [render.yaml](./render.yaml)

## 🆘 Suporte

Em caso de problemas:
1. Verificar logs no Render
2. Consultar [DEPLOY_RENDER.md](./DEPLOY_RENDER.md) → Troubleshooting
3. Documentação do Render: https://render.com/docs

---

**Status**: ✅ Pronto para Deploy  
**Última Atualização**: Novembro 2025
