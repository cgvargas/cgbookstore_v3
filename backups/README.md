# Diretório de Backups

Este diretório contém arquivos de backup do banco de dados e scripts relacionados.

## Estrutura

- **/*.json** - Arquivos de backup em formato JSON
- **/temp/** - Arquivos temporários de backup/migração
- **backup_*.py** - Scripts para realizar backups

## Uso

Os scripts neste diretório são utilizados para:
- Backup de dados do banco de dados
- Migração entre diferentes bancos (SQLite, PostgreSQL, Supabase)
- Restauração de dados

## Nota Importante

⚠️ Estes arquivos NÃO devem ser versionados no Git por conterem dados sensíveis.
Verifique o `.gitignore` para garantir que estão excluídos.
