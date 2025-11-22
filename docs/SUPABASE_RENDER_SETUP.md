# Configuração Supabase + Render - Guia de Resolução de Problemas

## Problema: Erros de Conexão no Render com Supabase

Este guia resolve dois erros principais de conexão entre Render e Supabase.

### Erro 1: "Network is unreachable" (IPv6)

**Sintoma:**
```
connection to server at "2600:1f1e:75b:4b00:...", port 5432 failed: Network is unreachable
```

**Causa:** O Render **não suporta IPv6**, mas o Supabase retorna endereços IPv6 no DNS. O psycopg tenta conectar via IPv6 primeiro e falha.

**Solução:** O `settings.py` agora resolve o hostname para IPv4 **antes** da conexão, forçando uso exclusivo de IPv4.

### Erro 2: "Tenant or user not found"

**Sintoma:**
```
django.db.utils.OperationalError: connection failed: FATAL: Tenant or user not found
```

**Causa:** Uso do pooler do Supabase ao invés da conexão direta.

### Causas Comuns de Falha de Conexão

1. **✅ Render não suporta IPv6** (resolvido automaticamente)
2. **Formato incorreto da DATABASE_URL**
3. **Uso do pooler incorreto**
4. **Credenciais inválidas**

## Solução Implementada

### 1. Forçamento Automático de IPv4

O arquivo `cgbookstore/settings.py` implementa uma solução robusta:

**Como funciona:**
1. ✅ Detecta automaticamente quando está usando Supabase
2. ✅ **Resolve o hostname DNS para IPv4 ANTES da conexão**
   - Usa `socket.getaddrinfo()` com filtro `AF_INET` (apenas IPv4)
   - Substitui o hostname pelo IP IPv4 resolvido
3. ✅ Adiciona `hostaddr` para garantir que psycopg use o IP diretamente
4. ✅ Configura SSL obrigatório para Supabase
5. ✅ Adiciona timeouts apropriados

**Logs esperados:**
```
🔍 Resolvendo db.uomjbcuowfgcwhsejatn.supabase.co para IPv4...
✅ Resolvido db.uomjbcuowfgcwhsejatn.supabase.co -> 44.XXX.XXX.XXX (IPv4)
✅ Forçado conexão IPv4: 44.XXX.XXX.XXX
✅ Detectado Supabase conexão DIRETA: db.uomjbcuowfgcwhsejatn.supabase.co
✅ Configurações PostgreSQL aplicadas: [...]
```

### 2. Como Configurar a DATABASE_URL no Render

⚠️ **IMPORTANTE para Render FREE**: A conexão direta do Supabase (db.*.supabase.co) **NÃO tem IPv4**, apenas IPv6. Por isso, **use o Transaction Pooler** que tem IPv4.

#### Passo 1: Obter a Connection Pooling String no Supabase

1. Acesse o [Supabase Dashboard](https://app.supabase.com)
2. Selecione seu projeto
3. Vá em **Project Settings** > **Database**
4. Role até **Connection Pooling** (não "Connection String"!)
5. Copie a connection string do modo **Transaction**

A connection string terá o formato:
```
postgresql://postgres.[PROJECT-REF]:[YOUR-PASSWORD]@aws-0-us-east-1.pooler.supabase.com:6543/postgres?pgbouncer=true
```

**Exemplo real:**
```
postgresql://postgres.uomjbcuowfgcwhsejatn:SuaSenha@aws-0-us-east-1.pooler.supabase.com:6543/postgres?pgbouncer=true
```

#### Passo 2: Descobrir o IP IPv4 do Pooler

**No seu computador (Windows PowerShell)**, execute:
```powershell
nslookup -type=A aws-0-us-east-1.pooler.supabase.com 8.8.8.8
```

Você verá algo como:
```
Addresses:  52.45.94.125
           44.208.221.186
           44.216.29.125
```

**Copie QUALQUER UM desses IPs IPv4** (formato XX.XX.XX.XX).

#### Passo 3: Configurar no Render

1. Acesse o [Render Dashboard](https://dashboard.render.com)
2. Selecione seu serviço web
3. Vá em **Environment**
4. Configure **DUAS** variáveis:

**Variável 1: DATABASE_URL**
```
postgresql://postgres.uomjbcuowfgcwhsejatn:SuaSenha@aws-0-us-east-1.pooler.supabase.com:6543/postgres?pgbouncer=true
```
- Substitua `SuaSenha` pela sua senha real do Supabase
- Use o **POOLER** (`aws-0-us-east-1.pooler.supabase.com`)
- Porta: `6543` (Transaction mode)
- Mantenha `?pgbouncer=true` no final

**Variável 2: DATABASE_IPV4** ⭐ **OBRIGATÓRIA para Render FREE**
```
44.208.221.186
```
- Use um dos IPs IPv4 que você descobriu no Passo 2
- **Sem** protocolo, **sem** porta, apenas o IP
- Exemplo: `44.208.221.186`

### 3. Conexão Direta vs Pooler

| Tipo | Host | Porta | IPv4? | Uso Recomendado |
|------|------|-------|-------|-----------------|
| **Direta** | `db.XXXXXXXXXX.supabase.co` | 5432 | ❌ **Apenas IPv6** | Render PAID (com IPv6) |
| **Pooler (Transaction)** | `aws-0-us-east-1.pooler.supabase.com` | 6543 | ✅ **Tem IPv4** | ✅ **Render FREE** (recomendado) |
| **Pooler (Session)** | `aws-0-us-east-1.pooler.supabase.co` | 5432 | ⚠️ Variável | Long-running queries |

**⚠️ Para o Render FREE, use SEMPRE o Transaction Pooler (porta 6543)!**

**Explicação:**
- **Conexão Direta**: Ideal, mas Supabase só oferece IPv6, e Render FREE não suporta IPv6
- **Transaction Pooler**: Tem IPv4, funciona perfeitamente no Render FREE
- **Session Pooler**: Pode ou não ter IPv4, menos confiável

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
