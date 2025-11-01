# 🔧 Scripts Utilitários - CG Bookstore

Scripts para desenvolvimento, testes e manutenção do sistema.

## 📁 Estrutura

### [setup/](setup/) - Scripts de Configuração
Scripts para inicializar serviços e configurar o ambiente:

- **[start_dev.bat](setup/start_dev.bat)** - Inicia servidor de desenvolvimento (Windows)
- **[start_redis.bat](setup/start_redis.bat)** - Inicia Redis (Windows)
- **[start_redis.sh](setup/start_redis.sh)** - Inicia Redis (Linux/Mac)
- **[docker-compose.yml](setup/docker-compose.yml)** - Configuração Docker

**Uso:**
```bash
# Windows
cd scripts/setup
start_dev.bat

# Linux/Mac
cd scripts/setup
./start_redis.sh
```

---

### [testing/](testing/) - Scripts de Teste
Scripts para testar funcionalidades do sistema:

#### **Sistema de Priorização:**
- **[test_preferences_basic.py](testing/test_preferences_basic.py)** - Teste básico (sem emojis)
- **[test_preference_shell.py](testing/test_preference_shell.py)** - Teste no Django shell
- **[test_preference_simple.py](testing/test_preference_simple.py)** - Teste simples
- **[test_preference_weighted_recommendations.py](testing/test_preference_weighted_recommendations.py)** - Teste completo com comparação
- **[quick_test_preferences.py](testing/quick_test_preferences.py)** - Teste rápido automatizado
- **[test_production_integration.py](testing/test_production_integration.py)** - Teste de integração em produção
- **[test_shelf_exclusion.py](testing/test_shelf_exclusion.py)** - Valida exclusão de livros das prateleiras
- **[debug_exclusion.py](testing/debug_exclusion.py)** - Debug de problemas de exclusão

#### **Outros Testes:**
- **[test_ai_recommendations.py](testing/test_ai_recommendations.py)** - Testa recomendações com IA

**Uso:**
```bash
# No Django shell
python manage.py shell

# Executar teste
exec(open('scripts/testing/test_preferences_basic.py', encoding='utf-8').read())
```

---

### [maintenance/](maintenance/) - Scripts de Manutenção
Scripts para manutenção e administração do sistema:

- **[clear_recommendations_cache.py](maintenance/clear_recommendations_cache.py)** - Limpa cache de recomendações
- **[backup_data.py](maintenance/backup_data.py)** - Backup de dados
- **[check_missing.py](maintenance/check_missing.py)** - Verifica arquivos ausentes
- **[create_system_notifications.py](maintenance/create_system_notifications.py)** - Cria notificações do sistema

**Uso:**
```bash
# Limpar cache
python manage.py shell
exec(open('scripts/maintenance/clear_recommendations_cache.py', encoding='utf-8').read())
```

---

## 🚀 Guias Rápidos

### Testar Sistema de Priorização

```bash
# 1. Teste rápido
python manage.py shell
exec(open('scripts/testing/quick_test_preferences.py', encoding='utf-8').read())

# 2. Teste de integração
exec(open('scripts/testing/test_production_integration.py', encoding='utf-8').read())

# 3. Validar exclusão de livros
exec(open('scripts/testing/test_shelf_exclusion.py', encoding='utf-8').read())
```

### Resolver Problema de Cache

```bash
python manage.py shell
exec(open('scripts/maintenance/clear_recommendations_cache.py', encoding='utf-8').read())
```

### Iniciar Ambiente de Desenvolvimento

```bash
# Windows
cd scripts/setup
start start_redis.bat
start start_dev.bat

# Linux/Mac
cd scripts/setup
./start_redis.sh &
cd ../..
python manage.py runserver
```

---

## 📖 Documentação

Para mais informações, consulte:
- [../docs/README.md](../docs/README.md) - Documentação completa
- [../docs/testing/](../docs/testing/) - Guias de teste
- [../docs/integration/](../docs/integration/) - Guias de integração

---

## ⚠️ Notas Importantes

1. **Encoding:** Sempre use `encoding='utf-8'` ao executar scripts no Django shell
2. **Cache:** Limpe o cache após mudanças no código de recomendações
3. **Redis:** Certifique-se que o Redis está rodando antes de testar recomendações
4. **Shell:** Reinicie o Django shell após modificar arquivos Python

---

**Última atualização:** 01/11/2025
