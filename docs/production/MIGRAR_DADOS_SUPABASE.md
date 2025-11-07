# 🔄 Migração de Dados: Supabase → Render

Guia completo para migrar dados do Supabase para o PostgreSQL do Render.

---

## 🎯 Métodos Disponíveis

### Método 1: Django dumpdata/loaddata (Recomendado)
✅ Mais simples
✅ Usa Django ORM
✅ Funciona em qualquer ambiente

### Método 2: pg_dump/pg_restore (Avançado)
✅ Mais rápido para grandes volumes
❌ Requer acesso direto ao PostgreSQL

### Método 3: Comando Customizado
✅ Migração seletiva
✅ Controle total
❌ Mais complexo

---

## 📋 Método 1: Django dumpdata/loaddata (RECOMENDADO)

### Passo 1: Configurar Ambiente Local com Supabase

Edite seu `.env` local para apontar para o **Supabase**:

```env
# Temporariamente use o Supabase
DATABASE_URL=postgresql://postgres.xxx:senha@aws-xxx.pooler.supabase.com:6543/postgres
```

### Passo 2: Exportar Dados do Supabase

```bash
# Ativar ambiente virtual
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate     # Windows

# Exportar TODOS os dados
python manage.py dumpdata \
    --natural-foreign \
    --natural-primary \
    --indent 2 \
    --exclude contenttypes \
    --exclude auth.permission \
    --exclude sessions.session \
    --exclude admin.logentry \
    > supabase_backup.json

# Ou exportar apenas apps específicos
python manage.py dumpdata core accounts > core_accounts_backup.json
```

**Arquivo gerado:** `supabase_backup.json` com todos os dados

### Passo 3: Configurar Ambiente Local para Render

Edite seu `.env` local para apontar para o **Render**:

```env
# Agora use o banco do Render
DATABASE_URL=postgresql://xxx:senha@xxx.render.com:5432/xxx
```

### Passo 4: Importar Dados para Render

```bash
# Aplicar migrações primeiro
python manage.py migrate

# Importar dados
python manage.py loaddata supabase_backup.json
```

**Pronto!** Dados migrados do Supabase para Render.

---

## 📋 Método 2: pg_dump/pg_restore (Avançado)

### Requisitos
- Acesso SSH ou ferramenta PostgreSQL
- Permissões de dump/restore

### Passo 1: Fazer Dump do Supabase

```bash
# Obter credenciais do Supabase
# Host: aws-xxx.pooler.supabase.com
# Port: 6543
# Database: postgres
# User: postgres.xxx
# Password: sua-senha

# Fazer dump
pg_dump -h aws-xxx.pooler.supabase.com \
        -p 6543 \
        -U postgres.xxx \
        -d postgres \
        --no-owner \
        --no-acl \
        -F c \
        -f supabase_dump.backup
```

### Passo 2: Restaurar no Render

```bash
# Obter credenciais do Render
# No painel: Database > Connection Info

# Restaurar dump
pg_restore -h dpg-xxx.render.com \
           -p 5432 \
           -U xxx \
           -d xxx \
           --no-owner \
           --no-acl \
           supabase_dump.backup
```

---

## 📋 Método 3: Ferramenta Web (Render Free)

Como o Render Free não tem Shell, use a ferramenta web:

### Via Admin do Django

1. **Local:** Exporte dados do Supabase
   ```bash
   python manage.py dumpdata > supabase_data.json
   ```

2. **Crie um endpoint temporário** para upload:

```python
# core/views/admin_tools.py

@staff_member_required
def import_data_view(request):
    if request.method == 'POST' and request.FILES.get('data_file'):
        data_file = request.FILES['data_file']

        # Salvar arquivo
        import json
        data = json.load(data_file)

        # Importar usando management command
        from django.core.management import call_command
        from io import StringIO

        # Escrever JSON temporário
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump(data, f)
            temp_path = f.name

        # Carregar dados
        try:
            call_command('loaddata', temp_path)
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return render(request, 'admin_tools/import_data.html')
```

---

## 🎯 Migração Seletiva

### Migrar Apenas Livros e Categorias

```bash
# Exportar apenas core
python manage.py dumpdata core.category core.author core.book > books_backup.json

# Importar
python manage.py loaddata books_backup.json
```

### Migrar Apenas Usuários

```bash
# Exportar usuários
python manage.py dumpdata auth.user > users_backup.json

# Importar
python manage.py loaddata users_backup.json
```

### Migrar Tudo Exceto Usuários

```bash
# Exportar sem auth.user
python manage.py dumpdata \
    --exclude auth.user \
    --exclude auth.permission \
    --exclude contenttypes \
    --natural-foreign \
    > data_without_users.json
```

---

## ⚠️ Problemas Comuns

### Erro: Duplicate Key

```
IntegrityError: duplicate key value violates unique constraint
```

**Solução:**
```bash
# Opção 1: Limpar banco destino antes
python manage.py flush --no-input

# Opção 2: Usar --ignorenonexistent
python manage.py loaddata --ignorenonexistent supabase_backup.json
```

### Erro: Foreign Key

```
IntegrityError: insert or update on table violates foreign key constraint
```

**Solução:**
```bash
# Usar --natural-foreign ao exportar
python manage.py dumpdata --natural-foreign --natural-primary > backup.json
```

### Erro: ContentType

```
ContentType matching query does not exist
```

**Solução:**
```bash
# Excluir contenttypes ao exportar
python manage.py dumpdata --exclude contenttypes > backup.json

# E importar após migrate
python manage.py migrate
python manage.py loaddata backup.json
```

---

## 📊 Script Completo de Migração

```bash
#!/bin/bash
# migrate_supabase_to_render.sh

echo "🚀 Iniciando migração Supabase → Render"

# 1. Configurar para Supabase
echo "📡 Conectando ao Supabase..."
export DATABASE_URL="postgresql://postgres.xxx:senha@supabase.com:6543/postgres"

# 2. Exportar dados
echo "📦 Exportando dados do Supabase..."
python manage.py dumpdata \
    --natural-foreign \
    --natural-primary \
    --indent 2 \
    --exclude contenttypes \
    --exclude auth.permission \
    --exclude sessions.session \
    --exclude admin.logentry \
    > supabase_full_backup.json

echo "✅ Backup criado: supabase_full_backup.json"

# 3. Configurar para Render
echo "📡 Conectando ao Render..."
export DATABASE_URL="postgresql://xxx:senha@render.com:5432/xxx"

# 4. Aplicar migrações
echo "🔄 Aplicando migrações..."
python manage.py migrate

# 5. Importar dados
echo "📥 Importando dados para Render..."
python manage.py loaddata supabase_full_backup.json

echo "🎉 Migração concluída!"
```

**Executar:**
```bash
chmod +x migrate_supabase_to_render.sh
./migrate_supabase_to_render.sh
```

---

## 🔒 Segurança

### Backup Antes de Migrar

```bash
# Backup do Render antes de importar
python manage.py dumpdata > render_backup_before_import.json
```

### Testar em Local Primeiro

1. Use SQLite local para testar
2. Importe backup do Supabase
3. Verifique integridade
4. Só então faça em produção

---

## ✅ Checklist de Migração

- [ ] Fazer backup do Supabase
- [ ] Fazer backup do Render (se tiver dados)
- [ ] Testar import localmente
- [ ] Verificar integridade dos dados
- [ ] Configurar DATABASE_URL para Render
- [ ] Aplicar migrações no Render
- [ ] Importar dados
- [ ] Verificar se tudo funcionou
- [ ] Testar login e funcionalidades
- [ ] Executar health check

---

## 🆘 Suporte

### Verificar Dados Após Migração

```bash
# Via Python shell
python manage.py shell

>>> from core.models import Book, Category
>>> Category.objects.count()
>>> Book.objects.count()
>>> from django.contrib.auth import get_user_model
>>> get_user_model().objects.count()
```

### Health Check

```
https://cgbookstore-v3.onrender.com/admin-tools/health/
```

---

**Última atualização:** Novembro 2025
