# Configuração Supabase + Render - Guia de Resolução de Problemas

## Problema: "Tenant or user not found" no Render

Este erro geralmente ocorre quando há problemas de conexão entre o Render e o Supabase, especialmente relacionados a IPv4/IPv6.

### Sintomas

```
django.db.utils.OperationalError: connection failed: connection to server at "44.208.221.186",
port 5432 failed: FATAL: Tenant or user not found
```

### Causas Comuns

1. **Formato incorreto da DATABASE_URL**
2. **Problemas de resolução IPv4/IPv6**
3. **Uso do pooler incorreto**
4. **Credenciais inválidas**

## Solução Implementada

### 1. Configuração Automática de IPv4

O arquivo `cgbookstore/settings.py` foi atualizado para:

- ✅ Detectar automaticamente quando está usando Supabase
- ✅ Forçar uso de IPv4 para evitar conflitos
- ✅ Configurar corretamente SSL para Supabase
- ✅ Adicionar timeouts apropriados

### 2. Como Configurar a DATABASE_URL no Render

#### Passo 1: Obter a Connection String no Supabase

1. Acesse o [Supabase Dashboard](https://app.supabase.com)
2. Selecione seu projeto
3. Vá em **Project Settings** > **Database**
4. Role até **Connection String**
5. Selecione a aba **URI**
6. **IMPORTANTE**: Copie a connection string **DIRETA** (não pooler)

A connection string terá o formato:
```
postgresql://postgres:[YOUR-PASSWORD]@db.XXXXXXXXXX.supabase.co:5432/postgres
```

**Exemplo real:**
```
postgresql://postgres:SuaSenha123@db.uomjbcuowfgcwhsejatn.supabase.co:5432/postgres
```

#### Passo 2: Configurar no Render

1. Acesse o [Render Dashboard](https://dashboard.render.com)
2. Selecione seu serviço web
3. Vá em **Environment**
4. Adicione/edite a variável `DATABASE_URL` com a connection string do Supabase
5. **Importante**:
   - Substitua `[YOUR-PASSWORD]` pela sua senha real do banco
   - Use a conexão DIRETA (`db.*.supabase.co`) - **NÃO use pooler!**
   - Porta: `5432`

### 3. Conexão Direta vs Pooler

| Tipo | Host | Porta | Uso Recomendado |
|------|------|-------|-----------------|
| **Direta** | `db.XXXXXXXXXX.supabase.co` | 5432 | ✅ **Render, migrations, deploy** |
| **Pooler (Session)** | `aws-0-us-east-1.pooler.supabase.co` | 6543 | ❌ Pode causar erro "Tenant not found" |
| **Pooler (Transaction)** | `aws-0-us-east-1.pooler.supabase.com` | 5432 | ❌ Apenas serverless |

**⚠️ Para o Render, use SEMPRE a conexão DIRETA!**

### 4. Verificação da Configuração

Após configurar, você pode verificar se está funcionando:

```bash
# No Render Shell ou localmente
python manage.py check --database default
```

Se tudo estiver correto, você verá:
```
System check identified no issues (0 silenced).
```

### 5. Logs de Debug

O settings.py agora inclui logs que ajudam a identificar problemas:

```
🔄 Detectado Supabase pooler: aws-0-us-east-1.pooler.supabase.com
✅ Configurado timeout de socket para IPv4
✅ Configurações PostgreSQL aplicadas: ['connect_timeout', 'options', 'client_encoding', 'sslmode']
```

## Troubleshooting Adicional

### Erro: "password authentication failed"

**Causa**: Senha incorreta ou usuário inválido

**Solução**:
1. Verifique se a senha não contém caracteres especiais que precisam ser URL-encoded
2. Use a senha do database (não a senha da conta Supabase)
3. Caracteres especiais devem ser encoded: `@` → `%40`, `#` → `%23`, etc.

### Erro: "connection timeout"

**Causa**: Firewall ou problemas de rede

**Solução**:
1. Verifique se o Render tem acesso ao Supabase (geralmente sim)
2. Aumente o `connect_timeout` no settings.py se necessário
3. Verifique se o projeto Supabase não está pausado

### Erro: "SSL required"

**Causa**: Supabase exige SSL mas a conexão não está configurada

**Solução**:
- Já está resolvido no `settings.py` com `sslmode: 'require'`

## Referências

- [Supabase Database Settings](https://supabase.com/docs/guides/database/connecting-to-postgres)
- [Render Environment Variables](https://render.com/docs/environment-variables)
- [Django Database Configuration](https://docs.djangoproject.com/en/5.2/ref/settings/#databases)

## Changelog

- **2025-11-22**: Configuração inicial para IPv4 e Supabase pooler
