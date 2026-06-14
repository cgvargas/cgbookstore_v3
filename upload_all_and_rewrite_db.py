import os
import re
import mimetypes
import psycopg
import boto3
from supabase import create_client, Client
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

# R2 Config
R2_ACCOUNT_ID = env_vars.get('R2_ACCOUNT_ID')
R2_ACCESS_KEY_ID = env_vars.get('R2_ACCESS_KEY_ID')
R2_SECRET_ACCESS_KEY = env_vars.get('R2_SECRET_ACCESS_KEY')
R2_BUCKET_NAME = env_vars.get('R2_BUCKET_NAME', 'cgbookstore-media')

# Supabase Oregon Config
SUPABASE_URL = "https://xmrnlckrazptjbnmmhjj.supabase.co"
SUPABASE_KEY = env_vars.get('SUPABASE_SERVICE_KEY')

# ---------------------------------------------------------------------------
# 2. Inicializar Clientes
# ---------------------------------------------------------------------------
print("Conectando ao Cloudflare R2...")
s3 = boto3.client(
    's3',
    endpoint_url=f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com",
    aws_access_key_id=R2_ACCESS_KEY_ID,
    aws_secret_access_key=R2_SECRET_ACCESS_KEY,
)

print("Conectando ao Supabase Oregon...")
sb_client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
sb_storage = sb_client.storage

# Garantir que o bucket 'book-covers' existe e e publico
try:
    buckets = sb_storage.list_buckets()
    bucket_ids = [b.id for b in buckets]
    if 'book-covers' not in bucket_ids:
        sb_storage.create_bucket('book-covers', options={'public': True})
        print("  Bucket 'book-covers' criado no Supabase.")
except Exception as e:
    print(f"  Erro ao listar/criar bucket: {e}")

# ---------------------------------------------------------------------------
# 3. Escanear e Indexar Arquivos Locais (Incluindo Gerados e Baixados)
# ---------------------------------------------------------------------------
search_roots = {
    "Generated Placeholders": r"c:\ProjectDjango\cgbookstore_v3\generated_placeholders",
    "YouTube Temp Downloads": r"c:\ProjectDjango\cgbookstore_v3\temp_youtube_downloads",
    "Local Project Media": r"c:\ProjectDjango\cgbookstore_v3\media",
    "OneDrive Backup Media": r"C:\Users\claud\OneDrive\projectDjango\bookstore\cgbookstore\media",
    "OneDrive Arq Img": r"C:\Users\claud\OneDrive\Imagens\.arq_img_bookstore",
    "OneDrive .cgbookstore": r"C:\Users\claud\OneDrive\.cgbookstore",
    "OneDrive Imagens": r"C:\Users\claud\OneDrive\Imagens",
    "Downloads Imagens": r"C:\Users\claud\Downloads\Imagens",
    "Downloads Folder": r"C:\Users\claud\Downloads"
}

print("\nIndexando arquivos locais...")
file_index = {} # filename_lower -> list of full_paths
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

total_indexed = sum(len(v) for v in file_index.values())
print(f"Total de caminhos indexados: {total_indexed}\n")

# Helper para encontrar o melhor caminho local de um arquivo
def find_local_file(filename):
    fname_lower = filename.lower()
    if fname_lower in file_index:
        # Priorizar Generated e YouTube Downloads sobre OneDrive/Downloads geral
        paths = file_index[fname_lower]
        for label, path in paths:
            if label in ["Generated Placeholders", "YouTube Temp Downloads"]:
                return path
        return paths[0][1] # Fallback para o primeiro encontrado
    return None

# Helper para Content-Type
def get_content_type(filename):
    ext = os.path.splitext(filename)[1].lower()
    types = {
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.webp': 'image/webp',
        '.gif': 'image/gif'
    }
    return types.get(ext, 'application/octet-stream')

# Helper para fazer upload de arquivo
def upload_file_to_r2(local_path, r2_key):
    try:
        with open(local_path, 'rb') as data:
            s3.upload_fileobj(
                data,
                R2_BUCKET_NAME,
                r2_key,
                ExtraArgs={'ContentType': get_content_type(local_path)}
            )
        print(f"    -> [R2] Upload sucesso: {r2_key}")
        return True
    except Exception as e:
        print(f"    -> [R2] ERRO no upload para {r2_key}: {e}")
        return False

def upload_file_to_supabase(local_path, bucket, path_in_bucket):
    try:
        with open(local_path, 'rb') as f:
            file_content = f.read()
        content_type = get_content_type(local_path)
        
        sb_storage.from_(bucket).upload(
            path=path_in_bucket,
            file=file_content,
            file_options={"content-type": content_type, "upsert": "true"}
        )
        print(f"    -> [SUPABASE] Upload sucesso: {bucket}/{path_in_bucket}")
        return True
    except Exception as e:
        print(f"    -> [SUPABASE] ERRO no upload para {bucket}/{path_in_bucket}: {e}")
        return False

# ---------------------------------------------------------------------------
# 4. Processar Recursos Ausentes do R2 (Noticias, Videos, Universos)
# ---------------------------------------------------------------------------
print("=" * 80)
print("FASE A: PROCESSANDO RECURSOS AUSENTES DO R2...")
print("=" * 80)

missing_r2_keys = [
    "news/featured/gjIIkr9-8qc.jpg",
    "news/featured/gjIIkr9-8qc_qIDKroz.jpg",
    "news/featured/xUDobyOVM7Q.jpg",
    "news/featured/ChatGPT_Image_25_de_mai_de_2026_11_06_59.png",
    "news/featured/6LjNvjOyk6M.jpg",
    "news/featured/filters_quality95formatwebp.jpg",
    "news/featured/ChatGPT_Image_19_de_dez_de_2025_10_06_58.png",
    "news/featured/Chainsaw-Man__The-Movie-Reze-Arc-capa.png",
    "news/featured/filters_quality95formatwebp.webp",
    "news/featured/0rzaGbx3V5s_UGxfw3M.jpg",
    "news/featured/6LjNvjOyk6M_zY0gW90.jpg",
    "videos/thumbnails/Captura_de_tela_6-12-2025_95938_www.tiktok.com.jpeg",
    "videos/thumbnails/Captura_de_tela_15-11-2025_84012_www_KUaQIVw.instagram.com.jpeg",
    "videos/thumbnails/dbit_01_TPgqK8R.jpeg",
    "videos/thumbnails/Captura_de_tela_21-5-2026_161249_www_instagram_com.jpeg",
    "literary_universes/banners/O_Bruxo.png"
]

for key in missing_r2_keys:
    filename = key.split('/')[-1]
    local_path = find_local_file(filename)
    if local_path:
        print(f"Processando ausente: {filename}")
        print(f"  Localizado em: {local_path}")
        # Upload para R2
        upload_file_to_r2(local_path, key)
        # Upload para Supabase (bucket book-covers com o path completo da chave)
        upload_file_to_supabase(local_path, 'book-covers', key)
    else:
        print(f"AVISO: Nao foi possivel encontrar o arquivo local para {filename}")

# ---------------------------------------------------------------------------
# 5. Processar Imagens Embutidas do Supabase Antigo (uomjbcuowfgcwhsejatn)
# ---------------------------------------------------------------------------
print("\n" + "=" * 80)
print("FASE B: PROCESSANDO LINKS DO SUPABASE ANTIGO NO BANCO...")
print("=" * 80)

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
    print("Conectado ao banco de dados PostgreSQL.")
except Exception as e:
    print(f"Erro ao conectar ao banco: {e}")
    exit(1)

# List of files referenced in Supabase antigo
old_supabase_url_base = "https://uomjbcuowfgcwhsejatn.supabase.co/storage/v1/object/public/book-covers/"
new_supabase_url_base = "https://xmrnlckrazptjbnmmhjj.supabase.co/storage/v1/object/public/book-covers/"

# Query all news articles with content referencing old supabase
cursor.execute("SELECT id, title, content FROM public.news_article WHERE content LIKE '%uomjbcuowfgcwhsejatn.supabase.co%'")
articles_to_update = cursor.fetchall()
print(f"Total de noticias com links antigos a atualizar: {len(articles_to_update)}\n")

# Pattern to extract filename
supabase_pattern = re.compile(r'https://uomjbcuowfgcwhsejatn\.supabase\.co/storage/v1/object/public/book-covers/([^\s"\'\)>\\]+)')

for art_id, title, content in articles_to_update:
    print(f"Noticia ID {art_id}: '{title}'")
    filenames_to_upload = supabase_pattern.findall(content)
    
    # 1. Encontrar e fazer upload dos arquivos locais para R2 e Supabase Oregon
    for fname in filenames_to_upload:
        # Limpar query string se houver
        clean_fname = fname.split('?')[0]
        local_path = find_local_file(clean_fname)
        if local_path:
            print(f"  Referenciado: {clean_fname}")
            print(f"    Local: {local_path}")
            # Upload para R2 sob books/covers/
            upload_file_to_r2(local_path, f"books/covers/{clean_fname}")
            # Upload para Supabase Oregon sob a raiz de book-covers
            upload_file_to_supabase(local_path, "book-covers", clean_fname)
        else:
            print(f"    [ALERTA] Arquivo {clean_fname} nao encontrado localmente!")

    # 2. Atualizar o HTML na base de dados
    updated_content = content.replace(old_supabase_url_base, new_supabase_url_base)
    try:
        cursor.execute("UPDATE public.news_article SET content = %s WHERE id = %s", (updated_content, art_id))
        conn.commit()
        print(f"  [DB SUCESSO] Conteudo atualizado no banco para a noticia {art_id}!\n")
    except Exception as e:
        conn.rollback()
        print(f"  [DB ERRO] Falha ao atualizar noticia {art_id}: {e}\n")

cursor.close()
conn.close()
print("Processo concluido!")
