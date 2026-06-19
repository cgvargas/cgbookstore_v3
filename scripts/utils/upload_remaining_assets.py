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
# 2. Escanear e Indexar Arquivos Locais (Ampla Varredura)
# ---------------------------------------------------------------------------
search_roots = {
    "Local Project Media": r"c:\ProjectDjango\cgbookstore_v3\media",
    "OneDrive Backup Media": r"C:\Users\claud\OneDrive\projectDjango\bookstore\cgbookstore\media",
    "OneDrive Arq Img": r"C:\Users\claud\OneDrive\Imagens\.arq_img_bookstore",
    "OneDrive .cgbookstore": r"C:\Users\claud\OneDrive\.cgbookstore",
    "Downloads Folder": r"C:\Users\claud\Downloads",
    "OneDrive Main": r"C:\Users\claud\OneDrive"
}

file_index = {} # filename -> (source_label, full_path)
for label, root in search_roots.items():
    if not os.path.exists(root):
        continue
    print(f"Indexando arquivos em '{label}'...")
    exclude_dirs = ['appdata', 'node_modules', '.venv', '.git', '$recycle.bin', 'system volume information', 'solutionpackages']
    for dirpath, dirs, filenames in os.walk(root):
        dirs[:] = [d for d in dirs if d.lower() not in exclude_dirs]
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

paths_to_process = []

# A. Notícias (news_article.featured_image)
cursor.execute("SELECT title, featured_image FROM public.news_article WHERE featured_image IS NOT NULL AND featured_image != ''")
for title, featured_image in cursor.fetchall():
    paths_to_process.append(('news_article', featured_image, {'title': title}))

# B. Vídeos (core_video.thumbnail_image)
cursor.execute("SELECT title, thumbnail_image FROM public.core_video WHERE thumbnail_image IS NOT NULL AND thumbnail_image != ''")
for title, thumbnail_image in cursor.fetchall():
    paths_to_process.append(('core_video', thumbnail_image, {'title': title}))

# C. Verificar se core_category possui imagem
cursor.execute("""
    SELECT column_name FROM information_schema.columns 
    WHERE table_schema = 'public' AND table_name = 'core_category' 
      AND (column_name LIKE '%image%' OR column_name LIKE '%foto%' OR column_name LIKE '%capa%')
      AND data_type IN ('character varying', 'text')
""")
category_img_cols = [r[0] for r in cursor.fetchall()]
if category_img_cols:
    print(f"Colunas de imagem detectadas em core_category: {category_img_cols}")
    for col in category_img_cols:
        cursor.execute(f"SELECT name, {col} FROM public.core_category WHERE {col} IS NOT NULL AND {col} != ''")
        for name, img_path in cursor.fetchall():
            paths_to_process.append(('core_category', img_path, {'name': name}))

# D. Verificar se core_literaryuniverse possui imagem
cursor.execute("""
    SELECT column_name FROM information_schema.columns 
    WHERE table_schema = 'public' AND table_name = 'core_literaryuniverse' 
      AND (column_name LIKE '%image%' OR column_name LIKE '%foto%' OR column_name LIKE '%capa%' OR column_name LIKE '%banner%')
      AND data_type IN ('character varying', 'text')
""")
universe_img_cols = [r[0] for r in cursor.fetchall()]
if universe_img_cols:
    print(f"Colunas de imagem detectadas em core_literaryuniverse: {universe_img_cols}")
    for col in universe_img_cols:
        cursor.execute(f"SELECT title, {col} FROM public.core_literaryuniverse WHERE {col} IS NOT NULL AND {col} != ''")
        for title, img_path in cursor.fetchall():
            paths_to_process.append(('core_literaryuniverse', img_path, {'title': title}))

print(f"Total de recursos de midia a processar nesta rodada: {len(paths_to_process)}\n")

# ---------------------------------------------------------------------------
# Helper: Content-Type
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
# Helper: Extrair ID de Vídeo do YouTube e baixar thumbnail
# ---------------------------------------------------------------------------
yt_id_pattern = re.compile(r'([a-zA-Z0-9_-]{11})')

def download_youtube_thumbnail(filename):
    match = yt_id_pattern.search(filename)
    if not match:
        return None
    video_id = match.group(1)
    print(f"      ID do YouTube detectado no nome do arquivo: {video_id}")
    
    urls = [
        f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg",
        f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
    ]
    for url in urls:
        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200 and len(r.content) > 1000:
                return r.content
        except Exception as e:
            print(f"      Erro ao tentar baixar thumbnail do YT ({url}): {e}")
    return None

# ---------------------------------------------------------------------------
# 5. Executar Migração
# ---------------------------------------------------------------------------
already_uploaded = 0
uploaded_local = 0
uploaded_yt = 0
not_found_count = 0
errors = 0

for idx, (category, db_path, meta) in enumerate(paths_to_process, start=1):
    normalized_path = db_path.replace('\\', '/')
    filename = normalized_path.split('/')[-1]
    filename_lower = filename.lower()
    
    r2_key = normalized_path
    
    print(f"[{idx}/{len(paths_to_process)}] Processando: {filename} ({category})")
    
    # 5a. Verificar se já existe no R2
    try:
        s3.head_object(Bucket=R2_BUCKET_NAME, Key=r2_key)
        print("   -> Ja existe no Cloudflare R2. Pulando...")
        already_uploaded += 1
        continue
    except Exception:
        pass
    
    # 5b. Verificar se está localmente
    if filename_lower in file_index:
        label, local_path = file_index[filename_lower]
        print(f"   -> Encontrado localmente em '{label}' ({local_path})")
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
            
    # 5c. Se não estiver local, verificar se é uma thumbnail do YouTube
    else:
        print("   -> Nao encontrado localmente. Tentando baixar do YouTube...")
        yt_bytes = download_youtube_thumbnail(filename)
        if yt_bytes:
            try:
                s3.upload_fileobj(
                    BytesIO(yt_bytes),
                    R2_BUCKET_NAME,
                    r2_key,
                    ExtraArgs={'ContentType': 'image/jpeg'}
                )
                print(f"   -> UPLOAD YOUTUBE SUCESSO: R2 Key = {r2_key}")
                uploaded_yt += 1
            except Exception as e:
                print(f"   -> ERRO no upload da thumbnail do YouTube: {e}")
                errors += 1
        else:
            print("   -> Nao foi possivel obter o recurso localmente ou via YouTube.")
            not_found_count += 1
            
    # Pequeno delay
    time.sleep(0.5)

print("\n" + "=" * 60)
print("RELATORIO FINAL DE MIGRACAO ADICIONAL")
print("=" * 60)
print(f"Total de recursos a processar: {len(paths_to_process)}")
print(f"Já existentes no R2 (pular):   {already_uploaded}")
print(f"Migrados do disco local:       {uploaded_local}")
print(f"Baixados do YouTube (Thumb):   {uploaded_yt}")
print(f"Não encontrados / Falhas:      {not_found_count}")
print(f"Erros técnicos:                {errors}")
print("=" * 60)

cursor.close()
conn.close()
