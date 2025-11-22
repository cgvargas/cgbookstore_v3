# Scripts de Migração

Scripts para migração de dados entre diferentes bancos de dados.

## Scripts Disponíveis

### migrate_to_supabase.py
Migra dados completos do banco atual para Supabase.

**Uso:**
```bash
python scripts/migration/migrate_to_supabase.py
```

### import_ordem.py
Importa dados seguindo uma ordem específica para manter integridade referencial.

**Uso:**
```bash
python scripts/migration/import_ordem.py
```

## Boas Práticas

1. **Sempre faça backup antes de migrar**
2. Teste a migração em ambiente de desenvolvimento primeiro
3. Verifique a integridade dos dados após migração
4. Documente qualquer problema encontrado

## Notas

⚠️ Certifique-se de que as credenciais do banco de destino estão corretas no `.env`
