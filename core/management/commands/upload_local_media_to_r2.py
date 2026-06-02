import os
import boto3
import logging
from django.core.management.base import BaseCommand
from django.conf import settings

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Uploads local media files to Cloudflare R2'

    def handle(self, *args, **kwargs):
        self.stdout.write("Iniciando upload das imagens locais para o Cloudflare R2...")
        
        if not getattr(settings, 'AWS_ACCESS_KEY_ID', None):
            self.stderr.write("ERRO: Credenciais R2 não configuradas no ambiente.")
            return

        s3 = boto3.client(
            's3',
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
        r2_bucket = settings.AWS_STORAGE_BUCKET_NAME
        media_root = settings.MEDIA_ROOT
        
        if not os.path.exists(media_root):
            self.stderr.write(f"Pasta media não encontrada em: {media_root}")
            return

        total_migrados = 0
        total_erros = 0

        # Percorrer recursivamente a pasta media
        for root, dirs, files in os.walk(media_root):
            for file_name in files:
                local_path = os.path.join(root, file_name)
                
                # Calcular o path relativo para o R2 (ex: books/covers/imagem.jpg)
                rel_path = os.path.relpath(local_path, media_root)
                r2_path = rel_path.replace('\\', '/')  # Garantir barras normais
                
                self.stdout.write(f"Fazendo upload de {r2_path}...")
                
                try:
                    with open(local_path, 'rb') as f:
                        s3.upload_fileobj(
                            f,
                            r2_bucket,
                            r2_path,
                            ExtraArgs={'ContentType': self.guess_content_type(file_name)}
                        )
                    self.stdout.write(self.style.SUCCESS(f"Sucesso: -> {r2_path}"))
                    total_migrados += 1
                except Exception as e:
                    self.stderr.write(f"Erro ao subir {file_name}: {e}")
                    total_erros += 1

        self.stdout.write(self.style.SUCCESS(f"\nUpload concluído! Sucesso: {total_migrados} | Erros: {total_erros}"))

    def guess_content_type(self, filename):
        ext = filename.lower().split('.')[-1]
        if ext in ['jpg', 'jpeg']: return 'image/jpeg'
        if ext == 'png': return 'image/png'
        if ext == 'webp': return 'image/webp'
        if ext == 'gif': return 'image/gif'
        if ext == 'pdf': return 'application/pdf'
        return 'application/octet-stream'
