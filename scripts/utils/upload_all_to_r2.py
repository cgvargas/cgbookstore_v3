import os
import re
import time
import requests
import psycopg
import boto3
from io import BytesIO

# ---------------------------------------------------------------------------
# 1. Carregar Variáveis de Ambiente do .env
# ---------------------------------------------------------------------------
env_vars = {}
with open('.env', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#'):
            parts = line.split('=', 1)
            if len(parts) == 2:
                key = parts[0].strip()
                val = parts[1].strip().strip('"').strip("'")
                env_vars[key] = val

# Configuração do R2
R2_ACCOUNT_ID = env_vars.get('R2_ACCOUNT_ID')
R2_ACCESS_KEY_ID = env_vars.get('R2_ACCESS_KEY_ID')
R2_SECRET_ACCESS_KEY = env_vars.get('R2_SECRET_ACCESS_KEY')
R2_BUCKET_NAME = env_vars.get('R2_BUCKET_NAME', 'cgbookstore-media')

# Configuração do Google Books API
GOOGLE_BOOKS_API_KEY = env_vars.get('GOOGLE_BOOKS_API_KEY')

print("=== CONFIGURACAO CLOUDFLARE R2 ===")
print(f"Account ID: {R2_ACCOUNT_ID}")
print(f"Access Key ID: {R2_ACCESS_KEY_ID}")
print(f"Bucket Name: {R2_BUCKET_NAME}")
print("==================================\n")

# Inicializar cliente S3 para Cloudflare R2
s3 = boto3.client(
    's3',
    endpoint_url=f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com",
    aws_access_key_id=R2_ACCESS_KEY_ID,
    aws_secret_access_key=R2_SECRET_ACCESS_KEY,
)

# ---------------------------------------------------------------------------
# 2. Escanear e Indexar Arquivos Locais
# ---------------------------------------------------------------------------
search_roots = {
    "Local Project Media": r"c:\ProjectDjango\cgbookstore_v3\media",
    "OneDrive Backup Media": r"C:\Users\claud\OneDrive\projectDjango\bookstore\cgbookstore\media",
    "OneDrive Arq Img": r"C:\Users\claud\OneDrive\Imagens\.arq_img_bookstore",
    "OneDrive .cgbookstore": r"C:\Users\claud\OneDrive\.cgbookstore"
}

file_index = {} # filename -> (source_label, full_path)
for label, root in search_roots.items():
    if not os.path.exists(root):
        print(f"Aviso: Pasta de busca '{root}' nao encontrada. Pulando...")
        continue
    print(f"Indexando arquivos em '{label}' ({root})...")
    for dirpath, _, filenames in os.walk(root):
        for fname in filenames:
            fname_lower = fname.lower()
            full_path = os.path.join(dirpath, fname)
            if fname_lower not in file_index:
                file_index[fname_lower] = (label, full_path)

print(f"\nTotal de arquivos únicos indexados localmente: {len(file_index)}\n")

# ---------------------------------------------------------------------------
# 3. Conectar ao Banco de Dados e Coletar Caminhos
# ---------------------------------------------------------------------------
try:
    conn = psycopg.connect(
        dbname="postgres",
        user="postgres.xmrnlckrazptjbnmmhjj",
        password="Oa023568910@",
        host="aws-0-us-west-2.pooler.supabase.com",
        port="5432"
    )
    cursor = conn.cursor()
    print("Conexao com o banco de dados ativo estabelecida com sucesso!")
except Exception as e:
    print(f"Erro ao conectar ao banco de dados ativo: {e}")
    exit(1)

# Listas de caminhos a processar: (banco_de_origem, caminho_campo, info_extra)
paths_to_process = []

# A. Capas de Livros
cursor.execute("SELECT title, cover_image, isbn FROM public.core_book WHERE cover_image IS NOT NULL AND cover_image != ''")
for title, cover_image, isbn in cursor.fetchall():
    paths_to_process.append(('books', cover_image, {'title': title, 'isbn': isbn}))

# B. Fotos de Autores
cursor.execute("SELECT name, photo FROM public.core_author WHERE photo IS NOT NULL AND photo != ''")
for name, photo in cursor.fetchall():
    paths_to_process.append(('authors', photo, {'name': name}))

# C. Avatares e Banners de Usuários
cursor.execute("SELECT user_id, avatar, banner FROM public.accounts_userprofile")
for uid, avatar, banner in cursor.fetchall():
    if avatar:
        paths_to_process.append(('users_avatar', avatar, {'user_id': uid}))
    if banner:
        paths_to_process.append(('users_banner', banner, {'user_id': uid}))

# D. Eventos (Banners e Thumbnails)
cursor.execute("SELECT title, banner_image, thumbnail_image FROM public.core_event")
for title, banner, thumb in cursor.fetchall():
    if banner:
        paths_to_process.append(('events_banner', banner, {'title': title}))
    if thumb:
        paths_to_process.append(('events_thumb', thumb, {'title': title}))

# E. Banners Gerais
cursor.execute("SELECT title, image FROM public.core_banner WHERE image IS NOT NULL AND image != ''")
for title, image in cursor.fetchall():
    paths_to_process.append(('banners', image, {'title': title}))

# F. Banners de Universo
cursor.execute("SELECT title, image, image_mobile FROM public.core_universebanner")
for title, image, image_mobile in cursor.fetchall():
    if image:
        paths_to_process.append(('universe_banner', image, {'title': title}))
    if image_mobile:
        paths_to_process.append(('universe_banner_mobile', image_mobile, {'title': title}))

print(f"Total de recursos de midia mapeados no banco ativo: {len(paths_to_process)}\n")

# ---------------------------------------------------------------------------
# Helper: Adivinhar Content-Type
# ---------------------------------------------------------------------------
def guess_content_type(filename):
    ext = filename.lower().split('.')[-1]
    types = {
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'png': 'image/png',
        'webp': 'image/webp',
        'gif': 'image/gif',
        'pdf': 'application/pdf',
        'svg': 'image/svg+xml'
    }
    return types.get(ext, 'application/octet-stream')

# ---------------------------------------------------------------------------
# Helper: Buscar no Google Books
# ---------------------------------------------------------------------------
def fetch_from_google_books(title, author_name=None, isbn=None):
    url = "https://www.googleapis.com/books/v1/volumes"
    search_terms = []
    if isbn:
        search_terms.append(f"isbn:{isbn}")
    else:
        search_terms.append(title)
        if author_name:
            search_terms.append(f"inauthor:{author_name}")
            
    params = {
        'q': ' '.join(search_terms),
        'maxResults': 1,
        'langRestrict': 'pt',
        'printType': 'books'
    }
    if GOOGLE_BOOKS_API_KEY:
        params['key'] = GOOGLE_BOOKS_API_KEY
        
    try:
        r = requests.get(url, params=params, timeout=10)
        if r.status_code == 200:
            data = r.json()
            items = data.get('items', [])
            if items:
                volume_info = items[0].get('volumeInfo', {})
                image_links = volume_info.get('imageLinks', {})
                for size in ['extraLarge', 'large', 'medium', 'small', 'thumbnail', 'smallThumbnail']:
                    if size in image_links:
                        link = image_links[size]
                        link = link.replace('http://', 'https://')
                        link = link.replace('&edge=curl', '')
                        if 'zoom=' in link:
                            link = re.sub(r'zoom=\d', 'zoom=0', link)
                        else:
                            link += '&zoom=0'
                        return link
    except Exception as e:
        print(f"      Erro na API do Google Books para '{title}': {e}")
    return None

# ---------------------------------------------------------------------------
# 4. Executar Migração
# ---------------------------------------------------------------------------
already_uploaded = 0
uploaded_local = 0
uploaded_google = 0
not_found_count = 0
errors = 0

for idx, (category, db_path, meta) in enumerate(paths_to_process, start=1):
    # Normalizar o caminho
    normalized_path = db_path.replace('\\', '/')
    filename = normalized_path.split('/')[-1]
    filename_lower = filename.lower()
    
    # O destino no R2 deve seguir exatamente o caminho gravado no banco de dados (normalized_path)
    r2_key = normalized_path
    
    print(f"[{idx}/{len(paths_to_process)}] Processando: {filename} ({category})")
    
    # 4a. Verificar se já existe no Cloudflare R2
    try:
        s3.head_object(Bucket=R2_BUCKET_NAME, Key=r2_key)
        print("   -> Ja existe no Cloudflare R2. Pulando...")
        already_uploaded += 1
        continue
    except Exception:
        # Se der erro (404), é porque o arquivo não existe e precisamos fazer o upload
        pass
    
    # 4b. Verificar se está localmente
    if filename_lower in file_index:
        label, local_path = file_index[filename_lower]
        print(f"   -> Encontrado localmente em '{label}'")
        try:
            with open(local_path, 'rb') as data:
                s3.upload_fileobj(
                    data,
                    R2_BUCKET_NAME,
                    r2_key,
                    ExtraArgs={'ContentType': guess_content_type(filename)}
                )
            print(f"   -> UPLOAD LOCAL SUCESSO: R2 Key = {r2_key}")
            uploaded_local += 1
        except Exception as e:
            print(f"   -> ERRO no upload local: {e}")
            errors += 1
            
    # 4c. Se for capa de livro e não achou local, buscar na API Google Books
    elif category == 'books':
        title = meta.get('title')
        isbn = meta.get('isbn')
        print(f"   -> Nao encontrado localmente. Buscando '{title}' no Google Books...")
        
        google_url = fetch_from_google_books(title, isbn=isbn)
        if google_url:
            print(f"   -> Encontrou link no Google Books: {google_url}")
            try:
                img_res = requests.get(google_url, timeout=15)
                if img_res.status_code == 200 and 'image' in img_res.headers.get('Content-Type', ''):
                    s3.upload_fileobj(
                        BytesIO(img_res.content),
                        R2_BUCKET_NAME,
                        r2_key,
                        ExtraArgs={'ContentType': guess_content_type(filename)}
                    )
                    print(f"   -> UPLOAD GOOGLE SUCESSO: R2 Key = {r2_key}")
                    uploaded_google += 1
                else:
                    print(f"   -> Falha ao baixar imagem do Google Books (Status: {img_res.status_code})")
                    not_found_count += 1
            except Exception as e:
                print(f"   -> ERRO ao processar download do Google Books: {e}")
                errors += 1
        else:
            print(f"   -> Nao encontrou capa no Google Books para '{title}'")
            not_found_count += 1
            
    # 4d. Outros tipos de recursos que não achou localmente
    else:
        print(f"   -> Nao encontrado localmente no computador.")
        not_found_count += 1
        
    # Delay de 1 segundo para chamadas da API do Google Books
    time.sleep(1.0)

print("\n" + "=" * 60)
print("RELATORIO FINAL DE MIGRACAO")
print("=" * 60)
print(f"Total de recursos no banco:  {len(paths_to_process)}")
print(f"Já existentes no R2 (pular): {already_uploaded}")
print(f"Migrados do disco local:     {uploaded_local}")
print(f"Baixados do Google Books:    {uploaded_google}")
print(f"Não encontrados / Falhas:    {not_found_count}")
print(f"Erros técnicos:              {errors}")
print("=" * 60)

cursor.close()
conn.close()
