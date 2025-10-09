# 📋 CONTEXTO DE IMPLEMENTAÇÃO - SUPABASE STORAGE
## CGBookStore v3 - Sincronização entre 2 PCs

**Data:** 09/10/2025  
**Projeto:** CGBookStore v3  
**Objetivo:** Centralizar imagens no Supabase Storage para sincronização automática entre 2 computadores

---

## 🎯 SITUAÇÃO ATUAL

### ✅ **O QUE FOI IMPLEMENTADO COM SUCESSO:**

1. **Backend de Storage Django-compatível**
   - Arquivo: `core/storage_backends.py`
   - Classe: `SupabaseMediaStorage`
   - Herda de `django.core.files.storage.Storage`
   - Implementa: `_save()`, `_open()`, `url()`, `exists()`, `delete()`
   - Mapeia pastas locais → buckets do Supabase

2. **Classe de Integração Supabase**
   - Arquivo: `core/utils/supabase_storage.py`
   - Classes: `SupabaseStorage`, `supabase_storage`, `supabase_storage_admin`
   - `supabase_storage`: usa ANON_KEY (uploads normais)
   - `supabase_storage_admin`: usa SERVICE_KEY (operações admin)

3. **Configuração do Django**
   - Arquivo: `cgbookstore/settings.py`
   - Variáveis do Supabase carregadas do `.env`:
     - `SUPABASE_URL`
     - `SUPABASE_ANON_KEY`
     - `SUPABASE_SERVICE_KEY`
   - `USE_SUPABASE_STORAGE = True` (controla uso do Supabase)
   - `STORAGES` configurado para usar `SupabaseMediaStorage`

4. **Buckets criados no Supabase:**
   - ✅ `book-covers` (público)
   - ✅ `author-photos` (público)
   - ✅ `user-avatars` (público)

5. **Management Commands:**
   - `setup_supabase.py`: cria buckets e testa conexão
   - `migrate_media_to_supabase.py`: migra arquivos locais → Supabase
     - Suporta: `--dry-run`, `--skip-existing`
     - 138 arquivos migrados com sucesso

---

## 🚨 **PROBLEMA ATUAL - CRÍTICO**

### **Inconsistência entre banco de dados e arquivos no Supabase:**

**Sintoma:**
- URLs retornam erro 400 (Bad Request)
- Imagens não aparecem no site

**Causa raiz:**
- **Path no DB:** `books/covers/1984_hHex7gr.jpg`
- **Arquivo no Supabase:** `1984.jpg` (sem sufixo)
- Django gera URLs para arquivos inexistentes

**Exemplo concreto:**
```python
# Banco de dados
book.cover_image = "books/covers/1984_hHex7gr.jpg"

# URL gerada
"https://...supabase.co/.../book-covers/1984_hHex7gr.jpg"  # ❌ 400 Error

# Arquivo real no Supabase
"https://...supabase.co/.../book-covers/1984.jpg"  # ✅ Funciona
```

**Estatísticas:**
- Total de livros com imagem: ~100+
- Arquivos no Supabase: 138 (book-covers)
- Problema: Nomes diferentes entre DB e Storage

---

## 📂 **ARQUIVOS MODIFICADOS/CRIADOS**

### **Novos arquivos:**
```
core/storage_backends.py              # Backend Django Storage
core/management/commands/migrate_media_to_supabase.py
core/utils/supabase_storage.py        # (modificado)
```

### **Arquivos modificados:**
```
cgbookstore/settings.py               # Configuração STORAGES
core/management/commands/setup_supabase.py  # Usa supabase_storage_admin
```

---

## 🔧 **PRÓXIMOS PASSOS (PRIORITÁRIOS)**

### **FASE 1: Diagnosticar extensão do problema**

```powershell
python manage.py shell
```

```python
from core.models import Book

# Contar livros com imagem
total_com_imagem = Book.objects.filter(cover_image__isnull=False).exclude(cover_image='').count()
print(f"Total de livros com imagem no DB: {total_com_imagem}")

# Listar alguns exemplos
livros = Book.objects.filter(cover_image__isnull=False).exclude(cover_image='')[:20]
for livro in livros:
    print(f"- {livro.title[:40]}: {livro.cover_image.name}")
```

### **FASE 2: Criar comando de sincronização**

**Objetivo:** Criar `core/management/commands/sync_media_paths.py`

**Funcionalidade:**
1. Para cada livro com imagem:
   - Extrair nome base do arquivo (ex: `1984_hHex7gr.jpg` → `1984`)
   - Buscar arquivos no Supabase que começam com esse nome
   - Se encontrar, atualizar o path no banco de dados
   - Se não encontrar, logar para investigação manual

**Pseudocódigo:**
```python
for book in Book.objects.filter(cover_image__isnull=False):
    # Path atual: books/covers/1984_hHex7gr.jpg
    filename = book.cover_image.name.split('/')[-1]  # 1984_hHex7gr.jpg
    base_name = filename.split('_')[0]  # 1984
    
    # Buscar no Supabase
    files = supabase_storage_admin.list_files('book-covers', '')
    matching = [f for f in files if f['name'].startswith(base_name)]
    
    if matching:
        # Atualizar path no DB
        new_path = f"books/covers/{matching[0]['name']}"
        book.cover_image = new_path
        book.save()
```

### **FASE 3: Re-migrar arquivos faltantes**

Alguns livros têm paths para arquivos que nunca foram migrados:
- Verificar pasta local `media/books/covers/`
- Identificar arquivos que existem localmente mas não no Supabase
- Re-executar migração com `--skip-existing`

### **FASE 4: Testar e validar**

1. Rodar servidor: `python manage.py runserver`
2. Acessar: http://127.0.0.1:8000
3. Verificar se imagens aparecem
4. Validar URLs no DevTools (F12 → Network)

---

## 📊 **ESTATÍSTICAS DA MIGRAÇÃO**

### **Migração executada:**
```
Total processado: 150 arquivos
✅ Migrados: 138
⏭️  Pulados: 112 (já existiam)
❌ Erros: 38 (erro 409 - duplicados)
```

### **Distribuição por tipo:**
- **Capas de livros:** 136 locais → 138 no Supabase
- **Fotos de autores:** 7 (todos migrados)
- **Imagens de eventos:** 6 (todos migrados)
- **Avatares de usuários:** 1 (migrado)

---

## 🔑 **VARIÁVEIS DE AMBIENTE (.env)**

```env
# Database (Supabase)
DATABASE_URL=postgresql://postgres.uomjbcuowfgcwhsejatn:***@aws-1-sa-east-1.pooler.supabase.com:6543/postgres

# Supabase API & Storage
SUPABASE_URL=https://uomjbcuowfgcwhsejatn.supabase.co
SUPABASE_ANON_KEY=eyJhbGci...
SUPABASE_SERVICE_KEY=eyJhbGci...

# Storage Configuration
USE_SUPABASE_STORAGE=True
```

---

## 🛠️ **COMANDOS ÚTEIS**

### **Criar buckets:**
```powershell
python manage.py setup_supabase
```

### **Migrar arquivos (simulação):**
```powershell
python manage.py migrate_media_to_supabase --dry-run
```

### **Migrar arquivos (real):**
```powershell
python manage.py migrate_media_to_supabase
```

### **Migrar pulando existentes:**
```powershell
python manage.py migrate_media_to_supabase --skip-existing
```

### **Verificar configuração do storage:**
```python
# No shell
from django.conf import settings
print(settings.STORAGES)
```

### **Testar URL de uma imagem:**
```python
# No shell
from core.models import Book
book = Book.objects.first()
print(book.cover_image.url)
```

---

## 🐛 **PROBLEMAS CONHECIDOS**

### **1. Erro 400 nas URLs das imagens**
- **Causa:** Inconsistência entre nomes no DB e no Supabase
- **Status:** 🔴 NÃO RESOLVIDO
- **Prioridade:** CRÍTICA
- **Solução proposta:** Comando de sincronização (Fase 2)

### **2. Método `exists()` não funciona corretamente**
- **Causa:** `list_files()` não retorna todos os arquivos
- **Status:** 🟡 WORKAROUND (usar erro 409 como indicador)
- **Impacto:** Baixo (não afeta funcionamento)

### **3. Alguns arquivos não foram migrados**
- **Causa:** Arquivos estavam no OneDrive, não em `media/`
- **Status:** 🟢 RESOLVIDO (4 arquivos copiados e migrados)
- **Arquivos:** beserker_maga.jpg, dandadan-vol-1.jpg, my_hero_academy.jpg, 61wa6eVb8kL._SY466_.jpg

---

## 📝 **NOTAS IMPORTANTES**

1. **Dois tipos de instância do Supabase Storage:**
   - `supabase_storage`: ANON_KEY (uploads normais do Django)
   - `supabase_storage_admin`: SERVICE_KEY (operações admin - criar buckets, migrations)

2. **Buckets já estão configurados como públicos** no painel do Supabase

3. **Arquivos locais NÃO foram deletados** - servem como backup

4. **Storage backend está ativo** - novos uploads via admin vão direto pro Supabase

5. **Git não sincroniza pasta `media/`** - por isso a necessidade do Supabase

---

## 🎯 **OBJETIVO FINAL**

Quando finalizado, o sistema deve:
- ✅ Fazer upload automático de imagens para o Supabase
- ✅ Gerar URLs corretas apontando para o Supabase
- ✅ Sincronizar automaticamente entre os 2 PCs
- ✅ Todas as imagens devem aparecer no site
- ✅ Não depender mais da pasta `media/` local

---

## 📞 **PARA CONTINUAR O TRABALHO**

1. **Executar diagnóstico (Fase 1)** para entender extensão do problema
2. **Criar comando de sincronização (Fase 2)** para corrigir paths
3. **Executar sincronização** em todos os livros
4. **Testar** se imagens aparecem
5. **Commit e push** quando tudo estiver funcionando

---

## 🔗 **LINKS ÚTEIS**

- **Painel Supabase:** https://supabase.com/dashboard
- **Projeto:** https://supabase.com/dashboard/project/uomjbcuowfgcwhsejatn
- **Storage:** https://supabase.com/dashboard/project/uomjbcuowfgcwhsejatn/storage/buckets
- **Documentação Django Storage:** https://docs.djangoproject.com/en/5.0/ref/files/storage/

---

**Última atualização:** 09/10/2025 - 09:30
**Status do projeto:** 🟡 Implementação 90% completa - Aguardando sincronização de paths