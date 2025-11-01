# 🔄 Guia de Migração de Caminhos

> **Data:** 01/11/2025
> **Motivo:** Reorganização da estrutura do projeto

## 📋 Mudanças de Caminhos

### Documentação

| Antes (❌ Obsoleto) | Depois (✅ Novo Caminho) |
|---------------------|--------------------------|
| `README_PRIORIZACAO.md` | `docs/guides/README_PRIORIZACAO.md` |
| `COMO_TESTAR_PRIORIZACAO.md` | `docs/testing/COMO_TESTAR_PRIORIZACAO.md` |
| `TROUBLESHOOTING_TESTES.md` | `docs/testing/TROUBLESHOOTING_TESTES.md` |
| `INTEGRACAO_PRODUCAO.md` | `docs/integration/INTEGRACAO_PRODUCAO.md` |
| `CHANGELOG_EXCLUSAO.md` | `docs/integration/CHANGELOG_EXCLUSAO.md` |
| `SOLUCAO_IMEDIATA.md` | `docs/integration/SOLUCAO_IMEDIATA.md` |
| `REDIS_SETUP.md` | `docs/guides/REDIS_SETUP.md` |
| `TESTE_REDIS.md` | `docs/testing/TESTE_REDIS.md` |
| `COMANDOS_TESTE.txt` | `docs/testing/COMANDOS_TESTE.txt` |

### Scripts de Teste

| Antes (❌ Obsoleto) | Depois (✅ Novo Caminho) |
|---------------------|--------------------------|
| `test_preferences_basic.py` | `scripts/testing/test_preferences_basic.py` |
| `test_preference_shell.py` | `scripts/testing/test_preference_shell.py` |
| `test_preference_simple.py` | `scripts/testing/test_preference_simple.py` |
| `test_preference_weighted_recommendations.py` | `scripts/testing/test_preference_weighted_recommendations.py` |
| `quick_test_preferences.py` | `scripts/testing/quick_test_preferences.py` |
| `test_production_integration.py` | `scripts/testing/test_production_integration.py` |
| `test_shelf_exclusion.py` | `scripts/testing/test_shelf_exclusion.py` |
| `debug_exclusion.py` | `scripts/testing/debug_exclusion.py` |
| `test_ai_recommendations.py` | `scripts/testing/test_ai_recommendations.py` |

### Scripts de Setup

| Antes (❌ Obsoleto) | Depois (✅ Novo Caminho) |
|---------------------|--------------------------|
| `start_dev.bat` | `scripts/setup/start_dev.bat` |
| `start_redis.bat` | `scripts/setup/start_redis.bat` |
| `start_redis.sh` | `scripts/setup/start_redis.sh` |
| `docker-compose.yml` | `scripts/setup/docker-compose.yml` |

### Scripts de Manutenção

| Antes (❌ Obsoleto) | Depois (✅ Novo Caminho) |
|---------------------|--------------------------|
| `clear_recommendations_cache.py` | `scripts/maintenance/clear_recommendations_cache.py` |
| `backup_data.py` | `scripts/maintenance/backup_data.py` |
| `check_missing.py` | `scripts/maintenance/check_missing.py` |
| `create_system_notifications.py` | `scripts/maintenance/create_system_notifications.py` |

---

## 🔧 Atualizar Comandos

### Antes (Comandos Antigos)

```python
# ❌ NÃO FUNCIONA MAIS
python manage.py shell
exec(open('test_preferences_basic.py', encoding='utf-8').read())
```

```bash
# ❌ NÃO FUNCIONA MAIS
python clear_recommendations_cache.py
```

### Depois (Novos Comandos)

```python
# ✅ FUNCIONA
python manage.py shell
exec(open('scripts/testing/test_preferences_basic.py', encoding='utf-8').read())
```

```python
# ✅ FUNCIONA (dentro do shell)
exec(open('scripts/maintenance/clear_recommendations_cache.py', encoding='utf-8').read())
```

---

## 📚 Exemplos de Uso

### Executar Testes

```bash
# Abrir Django shell
python manage.py shell
```

```python
# Teste rápido de priorização
exec(open('scripts/testing/quick_test_preferences.py', encoding='utf-8').read())

# Teste de integração em produção
exec(open('scripts/testing/test_production_integration.py', encoding='utf-8').read())

# Validar exclusão de livros das prateleiras
exec(open('scripts/testing/test_shelf_exclusion.py', encoding='utf-8').read())

# Debug de problemas de exclusão
exec(open('scripts/testing/debug_exclusion.py', encoding='utf-8').read())
```

### Manutenção

```bash
python manage.py shell
```

```python
# Limpar cache de recomendações
exec(open('scripts/maintenance/clear_recommendations_cache.py', encoding='utf-8').read())

# Backup de dados
exec(open('scripts/maintenance/backup_data.py', encoding='utf-8').read())
```

### Iniciar Serviços

```bash
# Windows - Redis
cd scripts/setup
start_redis.bat

# Windows - Servidor de desenvolvimento
cd scripts/setup
start_dev.bat

# Linux/Mac - Redis
cd scripts/setup
./start_redis.sh

# Docker
cd scripts/setup
docker-compose up -d
```

---

## 🔍 Verificação Rápida

Para verificar se você está usando o caminho correto:

```bash
# Verificar se arquivo existe
ls scripts/testing/test_preferences_basic.py

# Ou no Python
import os
os.path.exists('scripts/testing/test_preferences_basic.py')
# Deve retornar: True
```

---

## 📖 Navegação na Nova Estrutura

### Ver Documentação
```bash
# Listar guias
ls docs/guides/

# Listar testes
ls docs/testing/

# Listar guias de integração
ls docs/integration/
```

### Ver Scripts
```bash
# Listar scripts de teste
ls scripts/testing/

# Listar scripts de setup
ls scripts/setup/

# Listar scripts de manutenção
ls scripts/maintenance/
```

---

## 🆘 Problemas Comuns

### Erro: FileNotFoundError

**Sintoma:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'test_preferences_basic.py'
```

**Solução:**
Atualizar o caminho para `scripts/testing/test_preferences_basic.py`

---

### Erro: Comando Antigo em Script Salvo

**Sintoma:**
Você salvou um script com comandos antigos e agora não funciona.

**Solução:**
Substitua todos os caminhos antigos pelos novos usando a tabela acima.

**Exemplo:**
```python
# ANTES:
exec(open('quick_test_preferences.py', encoding='utf-8').read())

# DEPOIS:
exec(open('scripts/testing/quick_test_preferences.py', encoding='utf-8').read())
```

---

## ✅ Checklist de Migração

Para garantir que você atualizou tudo:

- [ ] Atualizar bookmarks/favoritos no editor
- [ ] Atualizar scripts salvos (.sh, .bat, .py)
- [ ] Atualizar documentação interna
- [ ] Atualizar comandos no histórico do terminal
- [ ] Revisar READMEs personalizados

---

## 📊 Benefícios da Nova Estrutura

✅ **Raiz Limpa:** Apenas 3 arquivos essenciais
✅ **Organização Lógica:** Documentação, scripts e código separados
✅ **Navegação Fácil:** READMEs em cada diretório
✅ **Escalabilidade:** Estrutura preparada para crescimento
✅ **Profissional:** Segue padrões da indústria

---

**Última atualização:** 01/11/2025
**Commit:** 22f1a6a
