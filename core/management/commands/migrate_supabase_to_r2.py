import os
import boto3
import logging
from io import BytesIO
from django.core.management.base import BaseCommand
from django.conf import settings
from core.utils.supabase_storage import supabase_storage_admin

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Migrates media files from Supabase Storage to Cloudflare R2'

    def handle(self, *args, **kwargs):
        self.stdout.write("Iniciando migração do Supabase para o Cloudflare R2...")
        
        if not getattr(settings, 'AWS_ACCESS_KEY_ID', None):
            self.stderr.write("ERRO: Credenciais R2 não configuradas no ambiente. Verifique o .env e settings.py.")
            return

        # Inicializar cliente S3 do Boto3 para o Cloudflare R2
        s3 = boto3.client(
            's3',
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
        r2_bucket = settings.AWS_STORAGE_BUCKET_NAME

        supabase = supabase_storage_admin
        
        # Mapeamento do bucket do Supabase para o prefixo (pasta) correspondente no R2
        # pois no R2 estamos usando um único bucket para tudo
        buckets = [
            (supabase.BOOK_COVERS_BUCKET, 'books/covers'),
            (supabase.AUTHOR_PHOTOS_BUCKET, 'authors/photos'),
            (supabase.USER_AVATARS_BUCKET, 'users')
        ]
        
        total_migrados = 0
        total_erros = 0

        for supabase_bucket, prefix_path in buckets:
            self.stdout.write(f"\nVerificando bucket Supabase: {supabase_bucket}")
            try:
                # Listar arquivos na raiz do bucket
                files = supabase.list_files(supabase_bucket, '')
                
                if not files:
                    self.stdout.write("Nenhum arquivo encontrado ou bucket vazio.")
                    continue

                for file_obj in files:
                    file_name = file_obj.get('name')
                    # ignorar placeholder .emptyFolderPlaceholder e pastas
                    if not file_name or file_name == '.emptyFolderPlaceholder' or file_obj.get('id') is None:
                        continue
                    
                    self.stdout.write(f"Processando {file_name}...")
                    try:
                        # Baixar do Supabase (em memória)
                        content = supabase.download_file(supabase_bucket, file_name)
                        if not content:
                            self.stderr.write(f"Falha ao baixar {file_name} do Supabase")
                            total_erros += 1
                            continue
                        
                        # Upload para o R2 (com o prefixo da pasta correta do Django)
                        r2_path = f"{prefix_path}/{file_name}"
                        
                        s3.upload_fileobj(
                            BytesIO(content),
                            r2_bucket,
                            r2_path,
                            ExtraArgs={'ContentType': self.guess_content_type(file_name)}
                        )
                        self.stdout.write(self.style.SUCCESS(f"Migrado com sucesso: -> {r2_path}"))
                        total_migrados += 1
                    except Exception as e:
                        self.stderr.write(f"Erro ao migrar {file_name}: {e}")
                        total_erros += 1

            except Exception as e:
                self.stderr.write(f"Erro ao acessar/listar bucket {supabase_bucket}: {e}")
        
        self.stdout.write(self.style.SUCCESS(f"\nMigração concluída! Sucesso: {total_migrados} | Erros: {total_erros}"))

    def guess_content_type(self, filename):
        ext = filename.lower().split('.')[-1]
        if ext in ['jpg', 'jpeg']: return 'image/jpeg'
        if ext == 'png': return 'image/png'
        if ext == 'webp': return 'image/webp'
        if ext == 'gif': return 'image/gif'
        if ext == 'pdf': return 'application/pdf'
        return 'application/octet-stream'
