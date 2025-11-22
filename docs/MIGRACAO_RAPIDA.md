# ⚡ Migração Rápida: Supabase → Render

Guia ultrarrápido para migrar dados.

---

## 🚀 Método Rápido (5 Passos)

### 1️⃣ Exportar do Supabase (Local)

```bash
# Configure .env para Supabase
DATABASE_URL=postgresql://postgres.xxx:senha@supabase.com:6543/postgres

# Exporte dados
python manage.py dumpdata \
    --natural-foreign \
    --natural-primary \
    --exclude contenttypes \
    --exclude auth.permission \
    > backup_supabase.json
```

**Arquivo gerado:** `backup_supabase.json`

---

### 2️⃣ Mudar para Render (Local)

```bash
# Configure .env para Render
DATABASE_URL=postgresql://xxx:senha@render.com:5432/xxx
```

---

### 3️⃣ Aplicar Migrações

```bash
python manage.py migrate
```

---

### 4️⃣ Importar Dados

```bash
python manage.py loaddata backup_supabase.json
```

---

### 5️⃣ Verificar

```bash
python manage.py shell

>>> from core.models import Book, Category
>>> print(f"Categorias: {Category.objects.count()}")
>>> print(f"Livros: {Book.objects.count()}")
```

---

## ✅ Pronto!

Dados migrados do Supabase para Render! 🎉

---

## 📚 Documentação Completa

Ver: [docs/production/MIGRAR_DADOS_SUPABASE.md](docs/production/MIGRAR_DADOS_SUPABASE.md)

---

**Tempo estimado:** 5-10 minutos
