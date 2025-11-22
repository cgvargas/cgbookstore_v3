# Guia Rápido - Estrutura do Projeto

Referência rápida para localizar arquivos no projeto reorganizado.

## 🔍 Onde Encontrar...

### Scripts de Teste
```
tests/
├── test_api_response.py
├── test_recommendations.py
├── test_email_confirmation.py
├── check_database.py
└── ...
```

**Como usar:**
```bash
python tests/test_nome_do_teste.py
```

---

### Scripts de Migração
```
scripts/migration/
├── migrate_to_supabase.py
└── import_ordem.py
```

**Como usar:**
```bash
python scripts/migration/migrate_to_supabase.py
```

---

### Scripts Utilitários
```
scripts/utils/
├── fix_author_slugs.py          # Corrigir slugs
├── create_premium_subscription.py  # Criar dados
├── update_profiles.py           # Atualizar registros
├── verificar_dados.py           # Verificar integridade
├── compare_databases.py         # Comparar bancos
└── clear_home_cache.py          # Limpar cache
```

**Como usar:**
```bash
python scripts/utils/fix_author_slugs.py
```

---

### Backups e Dados
```
backups/
├── backup_core.json
├── backup_supabase.json
├── temp/
│   └── temp_*.json
└── backup_*.py
```

**Localização:** Todos os backups JSON e scripts de backup

---

### Documentação
```
docs/
├── INDEX.md                         # Índice principal
├── ESTRUTURA_REORGANIZADA.md        # Esta reorganização
├── deployment/                      # Deploy
├── guides/                          # Guias gerais
├── production/                      # Produção
└── troubleshooting/                 # Solução de problemas
```

**Começar por:** [docs/INDEX.md](docs/INDEX.md)

---

### Certificados SSL
```
config/ssl/
├── cert.crt
├── cert.key
└── README.md
```

**Para gerar novos:**
```bash
openssl req -x509 -newkey rsa:4096 -nodes \
  -out config/ssl/cert.crt \
  -keyout config/ssl/cert.key \
  -days 365 -subj "/CN=localhost"
```

---

## 📋 Comandos Úteis

### Executar Servidor Local
```bash
python manage.py runserver
```

### Executar com HTTPS
```bash
python manage.py runserver_plus \
  --cert-file config/ssl/cert.crt \
  --key-file config/ssl/cert.key
```

### Executar Testes
```bash
# Teste específico
python tests/test_api_response.py

# Verificação de banco
python tests/check_database.py
```

### Migração de Dados
```bash
python scripts/migration/migrate_to_supabase.py
```

### Corrigir Dados
```bash
python scripts/utils/fix_author_slugs.py
```

### Limpar Cache
```bash
python scripts/utils/clear_home_cache.py
```

---

## 🗂️ Estrutura Resumida

```
cgbookstore_v3/
├── manage.py                  # Gerenciador Django
├── requirements.txt           # Dependências
├── render.yaml               # Config Render
├── build.sh                  # Build script
│
├── Apps Django/              # Módulos da aplicação
├── backups/                  # Backups e dados
├── config/                   # Configurações
├── docs/                     # Documentação
├── scripts/                  # Scripts utilitários
├── tests/                    # Testes
├── static/                   # Arquivos estáticos
└── templates/                # Templates HTML
```

---

## 🚀 Fluxo de Trabalho Comum

### 1. Desenvolvimento
```bash
# Iniciar servidor
python manage.py runserver

# Em outro terminal: executar testes
python tests/test_recommendations.py
```

### 2. Correção de Dados
```bash
# Verificar problema
python tests/check_database.py

# Corrigir
python scripts/utils/fix_author_slugs.py

# Verificar novamente
python tests/check_database.py
```

### 3. Migração
```bash
# Backup primeiro
python backups/backup_django.py

# Migrar
python scripts/migration/migrate_to_supabase.py

# Verificar
python tests/check_supabase_data.py
```

### 4. Deploy
```bash
# Ver instruções
cat docs/deployment/INSTRUCOES_RENDER.md

# Build local
./build.sh
```

---

## 📚 Documentação Importante

| Documento | Localização | Conteúdo |
|-----------|-------------|----------|
| Estrutura Completa | [docs/ESTRUTURA_REORGANIZADA.md](docs/ESTRUTURA_REORGANIZADA.md) | Estrutura detalhada do projeto |
| Configuração Local | [docs/GUIA_CONFIGURACAO_LOCAL.md](docs/GUIA_CONFIGURACAO_LOCAL.md) | Como configurar ambiente local |
| Teste Local | [docs/GUIA_TESTE_LOCAL.md](docs/GUIA_TESTE_LOCAL.md) | Como testar localmente |
| Deploy Render | [docs/GUIA_ATUALIZACAO_RENDER.md](docs/GUIA_ATUALIZACAO_RENDER.md) | Deploy no Render |
| Troubleshooting | [docs/troubleshooting/](docs/troubleshooting/) | Solução de problemas |
| Scripts | [scripts/README.md](scripts/README.md) | Guia de scripts |

---

## ⚠️ Importante

### Arquivos que NÃO estão versionados (Git)
- `/backups/*.json` - Backups de dados
- `/backups/temp/` - Temporários
- `/config/ssl/*.crt` - Certificados
- `/config/ssl/*.key` - Chaves privadas
- `/temp/` - Arquivos temporários
- `.env` - Variáveis de ambiente

### Sempre Fazer Backup Antes de:
- Executar scripts de migração
- Executar scripts de correção (`fix_*.py`)
- Deploy em produção
- Mudanças no banco de dados

---

**Última atualização:** 22/11/2025
**Versão:** 1.0

Para mais detalhes, consulte [docs/ESTRUTURA_REORGANIZADA.md](docs/ESTRUTURA_REORGANIZADA.md)
