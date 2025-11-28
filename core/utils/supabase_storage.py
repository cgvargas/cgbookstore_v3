"""
Utilitário para integração com Supabase Storage
CG.BookStore v3
"""

from django.conf import settings
from supabase import create_client, Client
from typing import Optional, BinaryIO, Dict, Any
import uuid
import os
import logging

logger = logging.getLogger(__name__)


class SupabaseStorage:
    """Classe para gerenciar upload e download de arquivos no Supabase Storage"""

    def __init__(self, use_service_key=False):
        """
        Inicializa o cliente Supabase

        Args:
            use_service_key: Se True, usa SERVICE_KEY (para operações admin)
        """
        self.url = settings.SUPABASE_URL

        # Usar SERVICE_KEY para operações administrativas
        if use_service_key and hasattr(settings, 'SUPABASE_SERVICE_KEY'):
            self.key = settings.SUPABASE_SERVICE_KEY
        else:
            self.key = settings.SUPABASE_ANON_KEY

        if not self.url or not self.key:
            logger.warning("⚠️ SUPABASE_URL e chave não configurados - Supabase Storage desabilitado")
            self.client = None
            self.storage = None
            return

        self.client: Client = create_client(self.url, self.key)
        self.storage = self.client.storage

        # Buckets padrão
        self.BOOK_COVERS_BUCKET = "book-covers"
        self.USER_AVATARS_BUCKET = "user-avatars"
        self.AUTHOR_PHOTOS_BUCKET = "author-photos"

    def create_buckets(self):
        """Cria os buckets necessários se não existirem"""
        buckets_to_create = [
            self.BOOK_COVERS_BUCKET,
            self.USER_AVATARS_BUCKET,
            self.AUTHOR_PHOTOS_BUCKET
        ]

        try:
            existing_buckets = self.storage.list_buckets()
            existing_ids = [b.id for b in existing_buckets]
        except Exception as e:
            logger.warning(f"Erro ao listar buckets: {str(e)}")
            existing_ids = []

        for bucket_id in buckets_to_create:
            if bucket_id not in existing_ids:
                try:
                    # Criar bucket público
                    self.storage.create_bucket(
                        id=bucket_id,
                        options={'public': True}
                    )
                    logger.info(f"Bucket '{bucket_id}' criado com sucesso")
                except Exception as e:
                    logger.error(f"Erro ao criar bucket '{bucket_id}': {str(e)}")

    def upload_file(self, file: BinaryIO, bucket: str, folder: str = "",
                    filename: Optional[str] = None) -> Optional[str]:
        """
        Upload de arquivo para o Supabase Storage

        Args:
            file: Arquivo a ser enviado
            bucket: Nome do bucket
            folder: Pasta dentro do bucket (opcional)
            filename: Nome do arquivo (opcional, gera UUID se não fornecido)

        Returns:
            URL pública do arquivo ou None se falhar
        """
        try:
            # Gerar nome único se não fornecido
            if not filename:
                ext = os.path.splitext(file.name)[1] if hasattr(file, 'name') else '.jpg'
                filename = f"{uuid.uuid4()}{ext}"

            # Construir caminho completo
            if folder:
                path = f"{folder}/{filename}"
            else:
                path = filename

            # Fazer upload
            file.seek(0)  # Garantir que está no início do arquivo
            response = self.storage.from_(bucket).upload(
                path=path,
                file=file.read(),
                file_options={"content-type": self._get_content_type(filename)}
            )

            # Retornar URL pública
            return self.get_public_url(bucket, path)

        except Exception as e:
            logger.error(f"Erro no upload para Supabase: {str(e)}")
            return None

    def upload_book_cover(self, file: BinaryIO, book_id: str) -> Optional[str]:
        """Upload específico para capas de livros"""
        folder = f"books/{book_id}"
        return self.upload_file(file, self.BOOK_COVERS_BUCKET, folder)

    def upload_user_avatar(self, file: BinaryIO, user_id: str) -> Optional[str]:
        """Upload específico para avatares de usuários"""
        folder = f"users/{user_id}"
        return self.upload_file(file, self.USER_AVATARS_BUCKET, folder)

    def upload_author_photo(self, file: BinaryIO, author_id: str) -> Optional[str]:
        """Upload específico para fotos de autores"""
        folder = f"authors/{author_id}"
        return self.upload_file(file, self.AUTHOR_PHOTOS_BUCKET, folder)

    def delete_file(self, bucket: str, path: str) -> bool:
        """
        Deleta um arquivo do Supabase Storage

        Args:
            bucket: Nome do bucket
            path: Caminho do arquivo

        Returns:
            True se deletado com sucesso, False caso contrário
        """
        try:
            self.storage.from_(bucket).remove([path])
            logger.info(f"Arquivo {path} deletado do bucket {bucket}")
            return True
        except Exception as e:
            logger.error(f"Erro ao deletar arquivo: {str(e)}")
            return False

    def get_public_url(self, bucket: str, path: str) -> str:
        """
        Obtém a URL pública de um arquivo

        Args:
            bucket: Nome do bucket
            path: Caminho do arquivo

        Returns:
            URL pública do arquivo
        """
        return self.storage.from_(bucket).get_public_url(path)

    def list_files(self, bucket: str, folder: str = "", limit: int = 100) -> list:
        """
        Lista arquivos em um bucket/pasta

        Args:
            bucket: Nome do bucket
            folder: Pasta dentro do bucket (opcional)
            limit: Número máximo de arquivos

        Returns:
            Lista de arquivos
        """
        try:
            files = self.storage.from_(bucket).list(
                path=folder,
                options={"limit": limit}
            )
            return files
        except Exception as e:
            logger.error(f"Erro ao listar arquivos: {str(e)}")
            return []

    def download_file(self, bucket: str, path: str) -> Optional[bytes]:
        """
        Download de um arquivo do Supabase Storage

        Args:
            bucket: Nome do bucket
            path: Caminho do arquivo

        Returns:
            Conteúdo do arquivo em bytes ou None se falhar
        """
        try:
            response = self.storage.from_(bucket).download(path)
            return response
        except Exception as e:
            logger.error(f"Erro no download do Supabase: {str(e)}")
            return None

    @staticmethod
    def _get_content_type(filename: str) -> str:
        """Determina o content-type baseado na extensão do arquivo"""
        ext = os.path.splitext(filename)[1].lower()
        content_types = {
            '.jpg': 'images/jpeg',
            '.jpeg': 'images/jpeg',
            '.png': 'images/png',
            '.gif': 'images/gif',
            '.webp': 'images/webp',
            '.svg': 'images/svg+xml',
            '.pdf': 'application/pdf',
        }
        return content_types.get(ext, 'application/octet-stream')


# Instância global para uso em todo o projeto
supabase_storage = SupabaseStorage()

# Instância com SERVICE_KEY para operações administrativas
supabase_storage_admin = SupabaseStorage(use_service_key=True)
