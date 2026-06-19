import os
import psycopg

# Paths to search
search_roots = {
    "Local Project Media": r"c:\ProjectDjango\cgbookstore_v3\media",
    "OneDrive Backup Media": r"C:\Users\claud\OneDrive\projectDjango\bookstore\cgbookstore\media",
    "OneDrive Arq Img": r"C:\Users\claud\OneDrive\Imagens\.arq_img_bookstore",
    "OneDrive .cgbookstore": r"C:\Users\claud\OneDrive\.cgbookstore"
}

# Scan all folders for files and index them by filename (case-insensitive)
file_index = {} # filename -> list of full paths
for label, root in search_roots.items():
    if not os.path.exists(root):
        continue
    for dirpath, _, filenames in os.walk(root):
        for fname in filenames:
            fname_lower = fname.lower()
            full_path = os.path.join(dirpath, fname)
            if fname_lower not in file_index:
                file_index[fname_lower] = []
            file_index[fname_lower].append((label, full_path))

try:
    conn = psycopg.connect(
        dbname="postgres",
        user="postgres.xmrnlckrazptjbnmmhjj",
        password="Oa023568910@",
        host="aws-0-us-west-2.pooler.supabase.com",
        port="5432"
    )
    cursor = conn.cursor()
    
    # Query news images
    cursor.execute("SELECT title, featured_image FROM public.news_article WHERE featured_image IS NOT NULL AND featured_image != ''")
    articles = cursor.fetchall()
    
    print(f"Total de noticias com imagem no banco ativo: {len(articles)}")
    print("-" * 80)
    
    found_count = 0
    not_found = []
    
    for title, img_path in articles:
        normalized_path = img_path.replace('\\', '/')
        fname = normalized_path.split('/')[-1]
        fname_lower = fname.lower()
        
        # Safe encoding print
        safe_title = title.encode('ascii', errors='replace').decode('ascii')
        
        if fname_lower in file_index:
            found_count += 1
            locs = ", ".join(f"{label} ({path})" for label, path in file_index[fname_lower])
            print(f"OK: '{safe_title}'")
            print(f"    Caminho no banco: {img_path}")
            print(f"    Encontrado em: {locs}\n")
        else:
            not_found.append((title, img_path))
            
    print("-" * 80)
    print(f"Resumo das Imagens de Noticias:")
    print(f"Encontradas localmente: {found_count}")
    print(f"Nao encontradas:        {len(not_found)}")
    
    if not_found:
        print("\nNoticias cujas imagens NAO foram encontradas:")
        for title, img_path in not_found:
            safe_title = title.encode('ascii', errors='replace').decode('ascii')
            print(f"  - '{safe_title}' | Imagem: {img_path}")
            
    cursor.close()
    conn.close()
except Exception as e:
    print(f"Erro: {e}")
