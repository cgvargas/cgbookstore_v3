"""
Script para importar dados do Supabase na ordem correta.
"""
import json
import subprocess
import sys

# Carregar backup completo
print("Carregando backup...")
with open('backup_supabase_v2.json', 'r', encoding='utf-8') as f:
    all_data = json.load(f)

# Ordem de importação (respeitando dependências)
import_order = [
    'auth.user',  # Já importado
    'django_site',
    'socialaccount.socialapp',
    'core.category',
    'core.author',
    'core.book',
    'core.section',
    'core.banner',
    'core.event',
    'core.video',
    'core.sectionitem',
    'accounts.userprofile',
    'account.emailaddress',
    'socialaccount.socialaccount',
    'socialaccount.socialtoken',
]

# Modelos já importados
imported = ['auth.user']

# Importar cada modelo na ordem
for model in import_order:
    if model in imported:
        print(f"⏭️  Pulando {model} (já importado)")
        continue

    # Filtrar dados deste modelo
    model_data = [d for d in all_data if d['model'] == model]

    if not model_data:
        print(f"⚠️  {model}: sem dados")
        continue

    # Salvar em arquivo temporário
    temp_file = f'temp_{model.replace(".", "_")}.json'
    with open(temp_file, 'w', encoding='utf-8') as f:
        json.dump(model_data, f, indent=2)

    # Importar
    print(f"📥 Importando {model} ({len(model_data)} registros)...")
    try:
        result = subprocess.run(
            [sys.executable, '-Xutf8', 'manage.py', 'loaddata', temp_file],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"   ✅ Sucesso!")
        else:
            print(f"   ❌ Erro: {result.stderr}")
            break
    except Exception as e:
        print(f"   ❌ Exceção: {e}")
        break

print("\n✅ Importação concluída!")
