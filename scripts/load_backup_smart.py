"""
Script para carregar backup do Supabase no SQLite local.
Carrega dados em ordem correta de dependências e pula modelos problemáticos.
"""
import os
import json
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from django.core import serializers
from django.db import transaction
from django.contrib.auth.models import User
from django.core.cache import cache

# Modelos para pular (problemas de migração ou conflitos)
SKIP_MODELS = [
    'new_authors.',        # Tabela não existe
    'socialaccount.',      # Conflitos de OAuth
    'account.',            # allauth - conflitos
    'sites.',              # Já existe site default
]

# Ordem de carregamento (dependências primeiro)
MODEL_ORDER = [
    'auth.user',
    'auth.group',
    'auth.permission',
    'contenttypes.contenttype',
    'core.category',
    'core.author',
    'core.book',
    'core.section',
    'core.sectionitem',
    'accounts.userprofile',
    'accounts.bookshelf',
    'accounts.achievement',
    'accounts.badge',
    'accounts.notification',
    'recommendations.',
    'chatbot_literario.',
    'news.',
    'debates.',
    'finance.',
]

def should_skip(model_name):
    """Verifica se o modelo deve ser pulado."""
    for skip in SKIP_MODELS:
        if model_name.startswith(skip):
            return True
    return False

def get_order_key(model_name):
    """Retorna a ordem de prioridade para o modelo."""
    for i, prefix in enumerate(MODEL_ORDER):
        if model_name.startswith(prefix) or model_name == prefix:
            return i
    return 999  # Modelos não listados vão para o final

print("🔄 Carregando backup do Supabase...")

# Carregar JSON
with open('backup_supabase_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"   Total de registros no backup: {len(data)}")

# Filtrar modelos problemáticos
filtered_data = [d for d in data if not should_skip(d['model'])]
print(f"   Registros após filtrar: {len(filtered_data)}")

# Ordenar por dependências
filtered_data.sort(key=lambda x: get_order_key(x['model']))

# Limpar cache
cache.clear()
print("   Cache limpo")

# Contadores
loaded = 0
skipped = 0
errors = 0
error_models = set()

print("\n📥 Carregando dados...")

# Carregar em batches por modelo
current_model = None
batch = []

def process_batch(batch):
    """Processa um batch de objetos."""
    global loaded, skipped, errors, error_models
    if not batch:
        return
        
    try:
        # Converter para JSON e deserializar
        json_str = json.dumps(batch, ensure_ascii=False)
        
        with transaction.atomic():
            for obj in serializers.deserialize('json', json_str, ignorenonexistent=True):
                try:
                    obj.save()
                    loaded += 1
                except Exception as e:
                    skipped += 1
                    if 'UNIQUE constraint' not in str(e):
                        errors += 1
                        error_models.add(batch[0]['model'] if batch else 'unknown')
    except Exception as e:
        errors += len(batch)
        error_models.add(batch[0]['model'] if batch else 'unknown')
        print(f"   ❌ Erro em batch {batch[0]['model'] if batch else 'unknown'}: {str(e)[:60]}")

for record in filtered_data:
    model = record['model']
    
    if model != current_model:
        # Processar batch anterior
        process_batch(batch)
        batch = []
        current_model = model
        print(f"   → {model}...", end=" ", flush=True)
    
    batch.append(record)

# Processar último batch
process_batch(batch)
print()

print(f"\n📊 Resultado:")
print(f"   ✓ Carregados: {loaded}")
print(f"   ○ Pulados (duplicados): {skipped}")
print(f"   ✗ Erros: {errors}")

if error_models:
    print(f"\n   Modelos com erro: {', '.join(error_models)}")

# Estatísticas finais
print("\n📈 Banco de dados atual:")
from core.models import Book, Category, Author
from accounts.models import BookShelf
print(f"   Usuários: {User.objects.count()}")
print(f"   Livros: {Book.objects.count()}")
print(f"   Categorias: {Category.objects.count()}")
print(f"   Autores: {Author.objects.count()}")
print(f"   Prateleiras: {BookShelf.objects.count()}")

print("\n✅ Carregamento concluído!")
