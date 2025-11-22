# Estrutura do Projeto - Reorganização 2025

Este documento descreve a estrutura organizada do projeto CG Bookstore v3.

## Estrutura de Diretórios

```
cgbookstore_v3/
├── .claude/                    # Configurações do Claude Code
├── .git/                       # Controle de versão Git
├── .idea/                      # Configurações do PyCharm/IntelliJ
├── .venv/                      # Ambiente virtual Python
│
├── accounts/                   # App Django - Gerenciamento de usuários
├── cgbookstore/               # Configurações principais do Django
├── chatbot_literario/         # App Django - Chatbot literário
├── core/                      # App Django - Funcionalidades principais
├── debates/                   # App Django - Sistema de debates
├── finance/                   # App Django - Gestão financeira
├── recommendations/           # App Django - Sistema de recomendações
│
├── backups/                   # 🆕 Arquivos de backup e migração
│   ├── temp/                  # Backups temporários
│   ├── *.json                 # Arquivos de backup JSON
│   ├── backup_*.py            # Scripts de backup
│   └── README.md
│
├── config/                    # Configurações do projeto
│   ├── ssl/                   # 🆕 Certificados SSL para HTTPS local
│   │   ├── cert.crt
│   │   ├── cert.key
│   │   └── README.md
│   └── ...
│
├── deploy/                    # Scripts e configs de deploy
├── docs/                      # 📚 Documentação do projeto
│   ├── deployment/            # Guias de deploy
│   ├── guides/                # Guias gerais
│   ├── integration/           # Guias de integração
│   ├── production/            # Docs de produção
│   ├── setup/                 # Guias de configuração
│   ├── testing/               # Guias de teste
│   ├── troubleshooting/       # Solução de problemas
│   ├── INDEX.md               # Índice da documentação
│   └── *.md                   # Documentos diversos
│
├── documents/                 # Documentos do sistema
├── media/                     # Arquivos de mídia (uploads)
├── static/                    # Arquivos estáticos do projeto
├── staticfiles/               # Arquivos estáticos coletados
├── templates/                 # Templates HTML Django
│
├── scripts/                   # 🔧 Scripts utilitários
│   ├── maintenance/           # Scripts de manutenção
│   ├── migration/             # 🆕 Scripts de migração de dados
│   │   ├── migrate_to_supabase.py
│   │   ├── import_ordem.py
│   │   └── README.md
│   ├── setup/                 # Scripts de configuração
│   ├── testing/               # Scripts de teste integrados
│   ├── utils/                 # 🆕 Scripts utilitários diversos
│   │   ├── fix_*.py           # Scripts de correção
│   │   ├── create_*.py        # Scripts de criação
│   │   ├── update_*.py        # Scripts de atualização
│   │   ├── verificar_*.py     # Scripts de verificação
│   │   ├── compare_*.py       # Scripts de comparação
│   │   └── README.md
│   └── README.md
│
├── temp/                      # 🆕 Arquivos temporários (não versionado)
│
├── tests/                     # 🆕 Scripts de teste e verificação
│   ├── test_*.py              # Testes de funcionalidades
│   ├── check_*.py             # Scripts de verificação
│   ├── debug_*.py             # Scripts de debug
│   └── README.md
│
├── testes/                    # Testes Django originais
│
├── .env                       # Variáveis de ambiente (não versionado)
├── .env.example               # Exemplo de variáveis de ambiente
├── .gitignore                 # Arquivos ignorados pelo Git
├── build.sh                   # Script de build
├── manage.py                  # Gerenciador Django
├── README.md                  # Documentação principal
├── render.yaml                # Configuração do Render
└── requirements.txt           # Dependências Python
```

## Mudanças Principais

### 🆕 Novos Diretórios

1. **backups/** - Centralizou todos os arquivos de backup e scripts relacionados
   - Movido da raiz do projeto
   - Inclui subpasta `temp/` para backups temporários

2. **tests/** - Consolidou todos os scripts de teste
   - Scripts `test_*.py`
   - Scripts `check_*.py`
   - Scripts `debug_*.py`

3. **scripts/migration/** - Scripts de migração de dados
   - `migrate_to_supabase.py`
   - `import_ordem.py`

4. **scripts/utils/** - Scripts utilitários diversos
   - Scripts de correção (`fix_*.py`)
   - Scripts de criação (`create_*.py`)
   - Scripts de atualização (`update_*.py`)
   - Scripts de verificação (`verificar_*.py`)
   - Scripts de comparação (`compare_*.py`)

5. **config/ssl/** - Certificados SSL para desenvolvimento
   - `cert.crt`
   - `cert.key`

6. **temp/** - Diretório para arquivos temporários
   - Não versionado no Git

### 📝 Documentação Adicionada

Cada diretório novo possui um `README.md` explicando:
- Propósito do diretório
- Arquivos contidos
- Como usar
- Boas práticas
- Notas importantes

### 🧹 Arquivos Removidos

- `nul` - Arquivo temporário do Windows removido

### 📋 Arquivos Movidos

**Da raiz para backups/**:
- `backup_*.json`
- `backup_*.py`
- `bookshelf_only.json`
- `users_only.json`
- `temp_*.json` → `backups/temp/`

**Da raiz para tests/**:
- `test_*.py`
- `check_*.py`
- `debug_*.py`

**Da raiz para scripts/migration/**:
- `migrate_to_supabase.py`
- `import_ordem.py`

**Da raiz para scripts/utils/**:
- `fix_*.py`
- `create_*.py`
- `update_*.py`
- `verificar_*.py`
- `compare_*.py`
- `detailed_comparison.py`
- `extract_*.py`
- `setup_*.py`
- `clear_*.py`

**Da raiz para docs/**:
- `GUIA_*.md`
- `ESTRATEGIA_*.md`
- `ESTRUTURA_*.md`
- `INSTRUÇÕES_*.md`
- `MIGRACAO_*.md`
- `REORGANIZACAO_*.md`
- `TROUBLESHOOTING_*.md`

**Da raiz para config/ssl/**:
- `cert.crt`
- `cert.key`

## Princípios de Organização Aplicados

### 1. Separação de Responsabilidades
- Cada diretório tem um propósito específico
- Scripts organizados por tipo e funcionalidade

### 2. Código Limpo
- Raiz do projeto limpa e organizada
- Arquivos agrupados logicamente
- Documentação próxima ao código

### 3. DRY (Don't Repeat Yourself)
- Scripts similares agrupados
- Documentação centralizada

### 4. Facilidade de Navegação
- Estrutura intuitiva
- READMEs em cada diretório
- Nomenclatura clara

### 5. Segurança
- Arquivos sensíveis no `.gitignore`
- Certificados SSL não versionados
- Backups não versionados

## Como Usar Esta Estrutura

### Para Desenvolvedores

1. **Executar Testes:**
   ```bash
   python tests/test_nome_do_teste.py
   ```

2. **Scripts Utilitários:**
   ```bash
   python scripts/utils/fix_author_slugs.py
   ```

3. **Migração de Dados:**
   ```bash
   python scripts/migration/migrate_to_supabase.py
   ```

4. **Consultar Documentação:**
   - Veja `docs/INDEX.md` para índice completo
   - Cada diretório tem seu próprio README

### Para Deploy

1. Arquivos de configuração estão em `/deploy/`
2. Configurações do Render em `render.yaml`
3. Build script em `build.sh`

### Para Backup

1. Scripts de backup em `/backups/`
2. Arquivos de backup não são versionados
3. Use scripts em `/scripts/migration/` para restaurar

## Manutenção

### Adicionando Novos Scripts

- **Testes:** Adicione em `/tests/` com nome `test_*.py`
- **Utilitários:** Adicione em `/scripts/utils/`
- **Migração:** Adicione em `/scripts/migration/`
- **Manutenção:** Adicione em `/scripts/maintenance/`

### Atualizando Documentação

- Documentos gerais em `/docs/`
- READMEs específicos em cada diretório
- Mantenha `docs/INDEX.md` atualizado

## .gitignore Atualizado

Novas regras adicionadas:
```gitignore
# Diretórios organizacionais
/backups/*.json
/backups/temp/
/temp/
/config/ssl/*.crt
/config/ssl/*.key

# Scripts de teste e desenvolvimento
/tests/check_*.py
/tests/test_*.py

# Arquivos temporários
nul
*.tmp
```

## Benefícios da Reorganização

1. ✅ Raiz do projeto limpa e organizada
2. ✅ Fácil localização de arquivos
3. ✅ Melhor manutenibilidade
4. ✅ Documentação acessível
5. ✅ Separação clara de responsabilidades
6. ✅ Seguindo princípios de código limpo
7. ✅ Estrutura escalável

## Próximos Passos Recomendados

1. [ ] Revisar e consolidar diretório `/testes/` com `/tests/`
2. [ ] Avaliar necessidade de manter `/documents/`
3. [ ] Criar testes unitários em `/tests/` usando pytest
4. [ ] Adicionar CI/CD utilizando a estrutura organizada
5. [ ] Documentar APIs no diretório `/docs/api/`

---

**Última atualização:** 22/11/2025
**Reorganização por:** Claude Code
**Versão:** 1.0
