# Scripts Utilitários

Scripts para manutenção, correção e verificação de dados do sistema.

## Categorias

### 🔧 Correção de Dados

Scripts que corrigem inconsistências no banco de dados:

- **fix_author_slugs.py** - Corrige e gera slugs únicos para autores
- **fix_duplicate_socialapps.py** - Remove aplicativos sociais duplicados
- **fix_placeholders.py** - Corrige placeholders de configuração
- **fix_reading_progress.py** - Corrige progresso de leitura de usuários
- **fix_section_items_ct.py** - Corrige content types de itens de seção

**Uso:**
```bash
python scripts/utils/fix_author_slugs.py
```

### ➕ Criação de Dados

Scripts para criar registros específicos:

- **create_premium_subscription.py** - Cria assinatura premium para teste
- **create_superuser_temp.py** - Cria superusuário temporário

**Uso:**
```bash
python scripts/utils/create_premium_subscription.py
```

### 🔄 Atualização

Scripts para atualizar registros existentes:

- **update_profiles.py** - Atualiza perfis de usuários
- **extract_bookshelf.py** - Extrai dados de estantes

**Uso:**
```bash
python scripts/utils/update_profiles.py
```

### ✅ Verificação

Scripts para verificar integridade dos dados:

- **verificar_dados.py** - Verificação geral de integridade
- **verificar_slugs.py** - Verifica unicidade de slugs

**Uso:**
```bash
python scripts/utils/verificar_dados.py
```

### 🔍 Comparação

Scripts para comparar dados entre bancos:

- **compare_databases.py** - Comparação básica entre bancos
- **detailed_comparison.py** - Comparação detalhada com estatísticas

**Uso:**
```bash
python scripts/utils/compare_databases.py
```

### 🧹 Limpeza

Scripts para limpeza de cache e dados temporários:

- **clear_home_cache.py** - Limpa cache da página inicial

**Uso:**
```bash
python scripts/utils/clear_home_cache.py
```

## Boas Práticas

1. **Backup:** Sempre faça backup antes de executar scripts de modificação
2. **Teste:** Execute em ambiente de desenvolvimento primeiro
3. **Verificação:** Use scripts de verificação após modificações
4. **Log:** Verifique os logs para identificar problemas

## Notas Importantes

⚠️ Scripts que modificam dados podem ter efeitos irreversíveis
⚠️ Teste sempre em ambiente de desenvolvimento primeiro
⚠️ Mantenha backups atualizados
