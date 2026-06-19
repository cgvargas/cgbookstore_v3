import os
import psycopg
import re

# Search roots
search_roots = {
    "Local Project Media": r"c:\ProjectDjango\cgbookstore_v3\media",
    "OneDrive Backup Media": r"C:\Users\claud\OneDrive\projectDjango\bookstore\cgbookstore\media",
    "OneDrive Arq Img": r"C:\Users\claud\OneDrive\Imagens\.arq_img_bookstore",
    "OneDrive .cgbookstore": r"C:\Users\claud\OneDrive\.cgbookstore",
    "OneDrive Imagens": r"C:\Users\claud\OneDrive\Imagens",
    "Downloads Imagens": r"C:\Users\claud\Downloads\Imagens",
    "Downloads Folder": r"C:\Users\claud\Downloads"
}

# Scan local directories and build index
print("Indexando arquivos locais...")
file_index = {}
exclude_dirs = ['appdata', 'node_modules', '.venv', '.git', '$recycle.bin', 'system volume information', 'solutionpackages']
for label, root in search_roots.items():
    if not os.path.exists(root):
        continue
    for dirpath, dirs, filenames in os.walk(root):
        dirs[:] = [d for d in dirs if d.lower() not in exclude_dirs]
        for fname in filenames:
            fname_lower = fname.lower()
            if fname_lower not in file_index:
                file_index[fname_lower] = []
            file_index[fname_lower].append((label, os.path.join(dirpath, fname)))

print(f"Total de arquivos locais indexados: {sum(len(v) for v in file_index.values())}")

# Connect to database
try:
    conn = psycopg.connect(
        dbname="postgres",
        user="postgres.xmrnlckrazptjbnmmhjj",
        password="Oa023568910@",
        host="aws-0-us-west-2.pooler.supabase.com",
        port="5432"
    )
    cursor = conn.cursor()
    print("Conectado ao banco de dados.")
except Exception as e:
    print(f"Erro ao conectar ao banco: {e}")
    exit(1)

# Hardcoded target tables for media scan
tables = ['news_article', 'core_book', 'core_author', 'core_literaryuniverse', 'core_category', 'core_event', 'core_video']

# Regex to find old supabase links
supabase_pattern = re.compile(r'https://uomjbcuowfgcwhsejatn\.supabase\.co/[^\s"\'\)>\\]+')

all_found_urls = {} # (table_name, column_name, row_id) -> list of urls

for table in tables:
    # Get primary key column name
    cursor.execute("""
        SELECT a.attname
        FROM pg_index i
        JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
        WHERE i.indrelid = %s::regclass AND i.indisprimary
    """, (f"public.{table}",))
    pk_row = cursor.fetchone()
    pk_col = pk_row[0] if pk_row else 'id'
    
    # Get text/character columns
    cursor.execute("""
        SELECT column_name FROM information_schema.columns 
        WHERE table_schema = 'public' AND table_name = %s 
          AND data_type IN ('character varying', 'text')
    """, (table,))
    text_cols = [r[0] for r in cursor.fetchall()]
    
    if not text_cols:
        continue
        
    for col in text_cols:
        try:
            cursor.execute(f"SELECT {pk_col}, {col} FROM public.{table} WHERE {col} LIKE %s", ('%uomjbcuowfgcwhsejatn.supabase.co%',))
            rows = cursor.fetchall()
            for pk_val, text_val in rows:
                if not text_val:
                    continue
                urls = supabase_pattern.findall(text_val)
                if urls:
                    all_found_urls[(table, col, pk_val)] = urls
        except Exception as e:
            # Table might not have standard columns or be a view
            pass

print("\n" + "=" * 80)
print("LINKS DO SUPABASE ANTIGO ENCONTRADOS NO BANCO:")
print("=" * 80)

unique_filenames = set()

for (table, col, pk_val), urls in all_found_urls.items():
    print(f"Tabela: {table} | Coluna: {col} | PK/ID: {pk_val}")
    for url in urls:
        print(f"  URL: {url}")
        # Extract filename from URL
        fname = url.split('/')[-1]
        unique_filenames.add(fname)
        
        # Check local index
        fname_lower = fname.lower()
        if fname_lower in file_index:
            print("    -> ENCONTRADO LOCALMENTE:")
            for label, path in file_index[fname_lower]:
                print(f"       [{label}] {path}")
        else:
            print("    -> NAO ENCONTRADO LOCALMENTE!")
    print()

print("=" * 80)
print(f"Total de arquivos unicos referenciados no Supabase antigo: {len(unique_filenames)}")
print(f"Lista de arquivos unicos:")
for fname in sorted(unique_filenames):
    found = fname.lower() in file_index
    status = "ENCONTRADO" if found else "NAO ENCONTRADO"
    print(f"  - {fname} ({status})")

cursor.close()
conn.close()
