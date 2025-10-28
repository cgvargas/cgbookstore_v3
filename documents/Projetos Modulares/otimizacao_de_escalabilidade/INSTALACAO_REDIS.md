# INSTRUCOES PARA INSTALAR O REDIS (WSL)

**Status:** Instalação automatica em andamento...
**Se houver algum problema, siga estas instruções manuais:**

---

## OPCAO 1: INSTALACAO MANUAL VIA WSL (RECOMENDADO)

### Passo 1: Abrir terminal WSL
```bash
wsl
```

### Passo 2: Atualizar repositorios (opcional, mas recomendado)
```bash
sudo apt update
```

### Passo 3: Instalar Redis
```bash
sudo apt install redis-server -y
```

Se aparecer algum prompt, pressione ENTER para aceitar as opcoes padrao.

### Passo 4: Iniciar o servico Redis
```bash
sudo service redis-server start
```

### Passo 5: Verificar se esta funcionando
```bash
redis-cli ping
```

**Resposta esperada:** `PONG`

Se retornar `PONG`, o Redis esta funcionando! ✅

---

## OPCAO 2: REDIS COMO SERVICO PERMANENTE

Para que o Redis inicie automaticamente:

### No terminal WSL:
```bash
# Editar o arquivo wsl.conf
sudo nano /etc/wsl.conf
```

### Adicionar estas linhas:
```ini
[boot]
systemd=true
```

### Salvar (Ctrl+O, Enter, Ctrl+X)

### Reiniciar WSL:
```bash
# No PowerShell (Windows):
wsl --shutdown
wsl
```

### Habilitar Redis no systemd:
```bash
sudo systemctl enable redis-server
sudo systemctl start redis-server
sudo systemctl status redis-server
```

---

## OPCAO 3: INICIAR REDIS MANUALMENTE SEMPRE

Se nao quiser configurar como servico, basta rodar isto sempre que reiniciar o computador:

```bash
wsl sudo service redis-server start
```

---

## VERIFICAR STATUS DO REDIS

### Dentro do WSL:
```bash
# Verificar se o processo esta rodando
ps aux | grep redis

# Testar conexao
redis-cli ping

# Ver informacoes do servidor
redis-cli info server
```

### Do Windows (sem entrar no WSL):
```bash
wsl redis-cli ping
```

---

## SOLUCAO DE PROBLEMAS

### Problema: "Could not connect to Redis at 127.0.0.1:6379"

**Solucao 1:** Iniciar o servico
```bash
wsl sudo service redis-server start
```

**Solucao 2:** Verificar se a porta esta ocupada
```bash
wsl sudo netstat -tulpn | grep 6379
```

**Solucao 3:** Matar processo antigo e reiniciar
```bash
wsl sudo pkill redis-server
wsl sudo service redis-server start
```

### Problema: "Address already in use"

Outro processo esta usando a porta 6379.

```bash
# Ver qual processo esta usando
wsl sudo lsof -i :6379

# Matar o processo
wsl sudo pkill redis-server

# Iniciar novamente
wsl sudo service redis-server start
```

### Problema: WSL nao esta instalado

Instalar WSL no Windows:

1. Abrir PowerShell como Administrador
2. Executar:
```powershell
wsl --install
```
3. Reiniciar o computador
4. Voltar para este guia

---

## ALTERNATIVA: MEMURAI (REDIS NATIVO WINDOWS)

Se preferir nao usar WSL, pode usar o Memurai:

1. Acessar: https://www.memurai.com/get-memurai
2. Baixar a versao Developer (gratuita)
3. Instalar
4. O servico inicia automaticamente
5. Verificar: abrir PowerShell e executar `redis-cli ping`

**Vantagens:**
- Nativo do Windows
- Servico automatico
- Interface grafica

**Desvantagens:**
- Software de terceiros (nao e o Redis oficial)
- Versao Developer tem limitacoes

---

## APOS INSTALAR O REDIS

### 1. Verificar se esta funcionando:
```bash
wsl redis-cli ping
```

### 2. Rodar os testes do projeto:
```bash
python test_performance_simple.py
```

**Resultado esperado:** 6/6 testes passando (100%)

### 3. Iniciar o projeto:

**Terminal 1 - Django:**
```bash
python manage.py runserver
```

**Terminal 2 - Celery (opcional):**
```bash
celery -A cgbookstore worker -l info --pool=solo
```

### 4. Testar o cache:
```bash
python manage.py shell
```
```python
from django.core.cache import cache
cache.set('test', 'funcionou!', timeout=60)
print(cache.get('test'))  # Deve imprimir: funcionou!
```

---

## COMANDOS UTEIS DO REDIS

```bash
# Ver todas as chaves
wsl redis-cli KEYS '*'

# Limpar todo o cache
wsl redis-cli FLUSHALL

# Ver memoria usada
wsl redis-cli INFO memory

# Monitorar comandos em tempo real
wsl redis-cli MONITOR

# Ver estatisticas
wsl redis-cli INFO stats
```

---

## PROXIMOS PASSOS

Apos o Redis estiver funcionando:

1. ✅ Rodar `python test_performance_simple.py` (deve passar 6/6 testes)
2. ✅ Iniciar Django: `python manage.py runserver`
3. ✅ (Opcional) Iniciar Celery: `celery -A cgbookstore worker -l info --pool=solo`
4. ✅ Acessar: http://localhost:8000/debates/
5. ✅ Verificar performance melhorada!

---

**FIM DO GUIA**

Se tiver qualquer problema, consulte a secao "Solucao de Problemas" acima.
