"""
Comparar dados entre Render e Supabase
"""
import os
import sys
import django

# Configurar encoding UTF-8
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

print("=" * 80)
print("COMPARACAO: RENDER vs SUPABASE")
print("=" * 80)

# URLs
RENDER_URL = "postgresql://cgbookstore_user:VbtzEhwlTr8nMc6gF3yWtjIyGOezK7PL@dpg-d46ttd8gjchc73enjuo0-a.oregon-postgres.render.com/cgbookstore"
SUPABASE_URL = "postgresql://postgres:Oa023568910@@db.uomjbcuowfgcwhsejatn.supabase.co:5432/postgres"

# Models para comparar
models_to_compare = [
    ('core', 'Book'),
    ('core', 'Author'),
    ('core', 'Category'),
    ('core', 'Banner'),
    ('core', 'Section'),
    ('core', 'Video'),
    ('accounts', 'UserProfile'),
    ('accounts', 'BookShelf'),
    ('accounts', 'BookReview'),
    ('debates', 'DebateTopic'),
    ('debates', 'DebatePost'),
    ('finance', 'Subscription'),
    ('finance', 'Order'),
]

print("\n{:<30} {:>15} {:>15} {:>15}".format(
    "Model", "Render", "Supabase", "Diferenca"
))
print("-" * 80)

from django.apps import apps

total_render = 0
total_supabase = 0

for app_label, model_name in models_to_compare:
    try:
        model = apps.get_model(app_label, model_name)

        # Contar no Render
        os.environ['DATABASE_URL'] = RENDER_URL
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
        django.setup()
        from django.db import connections
        connections['default'].close()

        render_count = model.objects.count()
        total_render += render_count

        # Contar no Supabase
        os.environ['DATABASE_URL'] = SUPABASE_URL
        connections['default'].close()

        supabase_count = model.objects.count()
        total_supabase += supabase_count

        diff = render_count - supabase_count
        diff_str = f"+{diff}" if diff > 0 else str(diff)

        status = "OK" if diff == 0 else ("RENDER MAIOR" if diff > 0 else "SUPABASE MAIOR")

        print(f"{app_label}.{model_name:<20} {render_count:>15} {supabase_count:>15} {diff_str:>15} [{status}]")

    except Exception as e:
        print(f"{app_label}.{model_name:<20} {'ERRO':>15} {'ERRO':>15} {'-':>15}")

print("-" * 80)
print(f"{'TOTAL':<30} {total_render:>15} {total_supabase:>15} {total_render - total_supabase:>15}")

print("\n" + "=" * 80)
if total_render == total_supabase:
    print("BANCOS SINCRONIZADOS!")
    print("\nRecomendacao: Apenas atualizar DATABASE_URL para Supabase")
elif total_render > total_supabase:
    print("RENDER TEM MAIS DADOS!")
    print(f"\nDiferenca: {total_render - total_supabase} registros")
    print("Recomendacao: Migrar dados do Render para Supabase")
else:
    print("SUPABASE TEM MAIS DADOS!")
    print(f"\nDiferenca: {total_supabase - total_render} registros")
    print("Recomendacao: Verificar qual banco esta mais atualizado")

print("=" * 80)
