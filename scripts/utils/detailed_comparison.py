"""
Comparação detalhada entre Render e Supabase
"""
import os
import sys
import django
from django.db import connection, connections

# Configurar encoding UTF-8
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

print("=" * 80)
print("COMPARACAO DETALHADA: RENDER vs SUPABASE")
print("=" * 80)

# URLs
RENDER_URL = "postgresql://cgbookstore_user:VbtzEhwlTr8nMc6gF3yWtjIyGOezK7PL@dpg-d46ttd8gjchc73enjuo0-a.oregon-postgres.render.com/cgbookstore"
SUPABASE_URL = "postgresql://postgres:Oa023568910@@db.uomjbcuowfgcwhsejatn.supabase.co:5432/postgres"

# Lista de tabelas para comparar (via SQL direto)
tables_to_compare = [
    'core_book',
    'core_author',
    'core_category',
    'core_banner',
    'core_section',
    'core_sectionitem',
    'core_video',
    'core_event',
    'accounts_userprofile',
    'accounts_bookshelf',
    'accounts_bookreview',
    'accounts_readingprogress',
    'debates_debatetopic',
    'debates_debatepost',
    'debates_debatevote',
    'finance_subscription',
    'finance_order',
    'finance_product',
    'recommendations_recommendation',
]

def get_table_count(cursor, table_name):
    """Conta registros em uma tabela"""
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
        return cursor.fetchone()[0]
    except Exception:
        return None

def get_latest_record_date(cursor, table_name):
    """Pega a data do registro mais recente"""
    try:
        # Tentar campos comuns de data
        for date_field in ['updated_at', 'created_at', 'date_joined']:
            try:
                cursor.execute(f"SELECT MAX({date_field}) FROM {table_name};")
                result = cursor.fetchone()[0]
                if result:
                    return result
            except:
                continue
        return None
    except:
        return None

print("\n{:<35} {:>12} {:>12} {:>12} {}".format(
    "Tabela", "Render", "Supabase", "Diferenca", "Mais Recente"
))
print("-" * 90)

# Conectar ao Render
os.environ['DATABASE_URL'] = RENDER_URL
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')

# Forçar reconexão
if 'default' in connections:
    connections['default'].close()

django.setup()

render_cursor = connection.cursor()

total_render = 0
total_supabase = 0
render_newer = 0
supabase_newer = 0

results = []

for table_name in tables_to_compare:
    # Contar no Render
    render_count = get_table_count(render_cursor, table_name)
    render_date = get_latest_record_date(render_cursor, table_name)

    if render_count is not None:
        total_render += render_count

    # Conectar ao Supabase
    os.environ['DATABASE_URL'] = SUPABASE_URL
    connections['default'].close()
    supabase_cursor = connection.cursor()

    # Contar no Supabase
    supabase_count = get_table_count(supabase_cursor, table_name)
    supabase_date = get_latest_record_date(supabase_cursor, table_name)

    if supabase_count is not None:
        total_supabase += supabase_count

    # Reconectar ao Render para próxima iteração
    os.environ['DATABASE_URL'] = RENDER_URL
    connections['default'].close()
    render_cursor = connection.cursor()

    # Calcular diferença
    if render_count is not None and supabase_count is not None:
        diff = render_count - supabase_count
        diff_str = f"+{diff}" if diff > 0 else str(diff)

        # Determinar qual é mais recente
        if render_date and supabase_date:
            if render_date > supabase_date:
                newer = "Render"
                render_newer += 1
            elif supabase_date > render_date:
                newer = "Supabase"
                supabase_newer += 1
            else:
                newer = "Igual"
        elif render_date:
            newer = "Render"
            render_newer += 1
        elif supabase_date:
            newer = "Supabase"
            supabase_newer += 1
        else:
            newer = "-"

        status = "OK" if diff == 0 else ("R+" if diff > 0 else "S+")

        print(f"{table_name:<35} {render_count:>12} {supabase_count:>12} {diff_str:>12} {newer}")
        results.append({
            'table': table_name,
            'render': render_count,
            'supabase': supabase_count,
            'diff': diff,
            'newer': newer
        })
    else:
        print(f"{table_name:<35} {'ERRO':>12} {'ERRO':>12} {'-':>12} -")

print("-" * 90)
print(f"{'TOTAL':<35} {total_render:>12} {total_supabase:>12} {total_render - total_supabase:>12}")

print("\n" + "=" * 80)
print("RESUMO DA ANALISE")
print("=" * 80)

print(f"\nTotal de registros:")
print(f"  Render:   {total_render:,}")
print(f"  Supabase: {total_supabase:,}")
print(f"  Diferenca: {abs(total_render - total_supabase):,} ({'+' if total_render > total_supabase else '-'})")

print(f"\nTabelas com dados mais recentes:")
print(f"  Render:   {render_newer} tabelas")
print(f"  Supabase: {supabase_newer} tabelas")

print("\n" + "=" * 80)
print("RECOMENDACAO")
print("=" * 80)

if total_render > total_supabase and render_newer >= supabase_newer:
    print("\n*** RENDER ESTA MAIS COMPLETO E ATUALIZADO")
    print("\nAcao recomendada:")
    print("1. Fazer backup completo do Render")
    print("2. Limpar banco Supabase")
    print("3. Migrar TODOS os dados do Render para Supabase")
    print("4. Atualizar variaveis de ambiente")
    recommendation = "MIGRAR_RENDER_PARA_SUPABASE"

elif total_supabase > total_render and supabase_newer >= render_newer:
    print("\n*** SUPABASE ESTA MAIS COMPLETO E ATUALIZADO")
    print("\nAcao recomendada:")
    print("1. Atualizar .env local para usar Supabase")
    print("2. Testar sistema com Supabase")
    print("3. Atualizar Render.com para usar Supabase")
    print("4. Descontinuar uso do banco Render temporario")
    recommendation = "USAR_SUPABASE_DIRETO"

elif abs(total_render - total_supabase) < 50:
    print("\n*** BANCOS SIMILARES")
    print("\nAcao recomendada:")
    print("1. Verificar qual banco voce usou por ultimo em producao")
    print("2. Se Render: migrar para Supabase")
    print("3. Se Supabase: apenas atualizar variaveis de ambiente")
    recommendation = "VERIFICAR_MANUAL"

else:
    print("\n*** SITUACAO INCONCLUSIVA")
    print("\nNecessario analise manual:")
    print("1. Verificar ultimos acessos em cada banco")
    print("2. Comparar dados criticos (usuarios, pedidos)")
    print("3. Decidir qual banco preservar")
    recommendation = "ANALISE_MANUAL_NECESSARIA"

print("\n" + "=" * 80)
print(f"DECISAO: {recommendation}")
print("=" * 80)

# Fechar cursors
render_cursor.close()
connections['default'].close()
