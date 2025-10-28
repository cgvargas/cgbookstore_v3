# 🔧 Solução para Problema de Login

## Problema Identificado

Você está sendo redirecionado infinitamente para a página de login sem conseguir fazer login.

**Causa:** Conflito entre sessões em cache (Redis) e a configuração atual.

---

## ✅ SOLUÇÃO APLICADA

Alterei temporariamente o sistema de sessões de **cache (Redis)** para **banco de dados**.

**Arquivo modificado:** `cgbookstore/settings.py:127`

```python
# ANTES (usando Redis):
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'

# AGORA (usando banco de dados):
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
```

---

## 🚀 Próximos Passos

### 1. Resetar Senha do Usuário

Execute:
```bash
python resetar_senha_rapido.py cgvargas nova_senha_aqui
```

**Exemplo:**
```bash
python resetar_senha_rapido.py cgvargas 123456
```

### 2. Reiniciar o Servidor

Pare o servidor atual (`CTRL+C`) e inicie novamente:

```bash
python manage.py runserver
```

### 3. Fazer Login

Acesse: http://127.0.0.1:8000/accounts/login/

- **Usuário:** cgvargas (ou o que você usou)
- **Senha:** A que você definiu no passo 1

### 4. Verificar se Funcionou

Após login bem-sucedido, você deve:
- ✅ Ver seu nome no canto superior direito
- ✅ Ter acesso às páginas protegidas
- ✅ Ver a seção "Para Você" na home (com recomendações)

---

## 🔍 Diagnóstico (Opcional)

Se quiser entender melhor o problema, execute:

```bash
python diagnostico_login.py
```

Isso vai mostrar:
- Usuários no banco
- Configurações de autenticação
- Status de middlewares
- Sugestões de solução

---

## 🔄 Reativar Redis (Depois que Login Funcionar)

Quando você resolver o problema de login, pode reativar o Redis para melhor performance:

### Passo 1: Verificar Redis

```bash
redis-cli ping
```

**Deve retornar:** `PONG`

Se não funcionar:
```bash
wsl redis-server
```

### Passo 2: Reativar Sessões em Cache

Em `cgbookstore/settings.py:122-127`, descomentar:

```python
# Cache de sessões (reduz carga no banco)
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# Comentar a linha abaixo:
# SESSION_ENGINE = 'django.contrib.sessions.backends.db'
```

### Passo 3: Reiniciar Servidor

```bash
python manage.py runserver
```

---

## 📋 Scripts Criados para Ajudar

### 1. `diagnostico_login.py`

Diagnostica problemas de autenticação:
```bash
python diagnostico_login.py
```

**Mostra:**
- Usuários no banco
- Configurações de autenticação
- Middlewares instalados
- Status do Redis
- Sugestões de solução

### 2. `resetar_senha_rapido.py`

Reseta senha de um usuário rapidamente:
```bash
python resetar_senha_rapido.py USUARIO SENHA
```

**Exemplo:**
```bash
python resetar_senha_rapido.py cgvargas 123456
```

---

## ⚠️ Problemas Comuns

### Problema 1: "CSRF token missing"

**Solução:** Limpe o cache do navegador ou use modo anônimo

### Problema 2: "Usuario ou senha invalidos"

**Solução:** Resetar senha:
```bash
python resetar_senha_rapido.py seu_usuario nova_senha
```

### Problema 3: Continua redirecionando

**Solução:**
1. Pare o servidor
2. Limpe sessões: `python manage.py clearsessions`
3. Reinicie o servidor
4. Tente novamente

### Problema 4: Redis não conecta

**Solução:** Use sessões em banco (já configurado!) ou inicie Redis:
```bash
wsl redis-server
```

---

## 🎯 Resumo da Solução

1. ✅ **Mudei sessões de cache para banco de dados**
2. ⏭️ **Você precisa resetar a senha:** `python resetar_senha_rapido.py cgvargas 123456`
3. ⏭️ **Reiniciar servidor:** `python manage.py runserver`
4. ⏭️ **Fazer login:** http://127.0.0.1:8000/accounts/login/

---

## 📞 Se Ainda Não Funcionar

Execute esses comandos em ordem:

```bash
# 1. Diagnóstico
python diagnostico_login.py

# 2. Resetar senha
python resetar_senha_rapido.py cgvargas 123456

# 3. Limpar sessões antigas
python manage.py clearsessions

# 4. Reiniciar servidor
python manage.py runserver

# 5. Testar login
# Acesse: http://127.0.0.1:8000/accounts/login/
```

---

## ✨ Depois de Logar

Quando conseguir fazer login, você poderá:

1. **Criar dados de teste das recomendações:**
   ```bash
   python criar_dados_teste_recomendacoes.py
   ```

2. **Ver as recomendações na home page:**
   - Seção "Para Você" no final da página
   - 4 algoritmos diferentes para escolher
   - Livros personalizados baseados no seu perfil

3. **Testar a API:**
   ```javascript
   fetch('/recommendations/api/recommendations/?algorithm=hybrid&limit=10')
   ```

---

**Mudança aplicada:** Sessões agora usam banco de dados em vez de Redis
**Próximo comando:** `python resetar_senha_rapido.py cgvargas 123456`
**Depois:** Reiniciar servidor e fazer login!
