"""
Backend de Storage customizado para Supabase
Integração com Django File Storage API
CG.BookStore v3
"""

from django.core.files.storage import Storage
from django.core.files.base import ContentFile
from django.conf import settings
from django.utils.deconstruct import deconstructible
from core.utils.supabase_storage import supabase_storage_admin
import os
import logging
from io import BytesIO
import unicodedata
import re

logger = logging.getLogger(__name__)


def normalize_filename(filename):
    """
    Normaliza nome de arquivo removendo acentos e caracteres especiais
    que podem causar problemas no Supabase Storage

    Args:
        filename: Nome original do arquivo

    Returns:
        str: Nome normalizado (apenas ASCII, sem acentos)
    """
    # Separar nome e extensão
    name, ext = os.path.splitext(filename)

    # Remover acentos usando NFD (Normalization Form Decomposition)
    name = unicodedata.normalize('NFD', name)
    name = name.encode('ascii', 'ignore').decode('ascii')

    # Substituir espaços e caracteres especiais por underscore
    name = re.sub(r'[^\w\-]', '_', name)

    # Remover underscores múltiplos
    name = re.sub(r'_+', '_', name)

    # Remover underscores no início e fim
    name = name.strip('_')

    # Garantir que não está vazio
    if not name:
        name = 'file'

    # Juntar nome normalizado com extensão
    return f"{name}{ext}"


@deconstructible
class SupabaseMediaStorage(Storage):
    """
    Storage backend customizado para usar Supabase Storage

    Compatível com Django File Storage API para upload de:
    - Capas de livros (books/covers/)
    - Fotos de autores (authors/photos/)
    - Banners de eventos (events/banners/)
    - Avatares de usuários (users/avatars/)
    """

    def __init__(self, location=None, base_url=None):
        """
        Inicializa o storage backend

        Args:
            location: Não usado, mantido para compatibilidade
            base_url: URL base do Supabase (opcional)
        """
        self.location = location or ''
        self.base_url = base_url or settings.SUPABASE_URL
        self._supabase = supabase_storage_admin

        # Mapeamento de pastas para buckets (com fallback se Supabase não estiver configurado)
        if hasattr(self._supabase, 'BOOK_COVERS_BUCKET'):
            self.bucket_mapping = {
                'books/covers/': self._supabase.BOOK_COVERS_BUCKET,
                'authors/photos/': self._supabase.AUTHOR_PHOTOS_BUCKET,
                'events/': self._supabase.BOOK_COVERS_BUCKET,  # Usando mesmo bucket
                'users/': self._supabase.USER_AVATARS_BUCKET,
                'banners/': self._supabase.BOOK_COVERS_BUCKET,  # Banners da home
                'videos/': self._supabase.BOOK_COVERS_BUCKET,   # Thumbnails de vídeos
            }
        else:
            # Fallback se Supabase não estiver configurado
            self.bucket_mapping = {
                'books/covers/': 'book-covers',
                'authors/photos/': 'author-photos',
                'events/': 'book-covers',
                'users/': 'user-avatars',
                'banners/': 'book-covers',  # Banners da home
                'videos/': 'book-covers',   # Thumbnails de vídeos
            }

    def _get_bucket_and_path(self, name):
        """
        Determina o bucket e path correto baseado no nome do arquivo

        Args:
            name: Path do arquivo (ex: 'books/covers/livro.jpg')

        Returns:
            tuple: (bucket_name, file_path)
        """
        # Normalizar path
        name = name.replace('\\', '/')

        # Encontrar bucket baseado no prefixo
        for prefix, bucket in self.bucket_mapping.items():
            if name.startswith(prefix):
                # Remover prefixo do path
                path = name[len(prefix):]
                return bucket, path

        # Default: usar bucket de book covers
        logger.debug(f"Path '{name}' não mapeado, usando bucket padrão")
        return self._supabase.BOOK_COVERS_BUCKET, name

    def _open(self, name, mode='rb'):
        """
        Abre um arquivo do Supabase Storage

        Args:
            name: Nome/path do arquivo
            mode: Modo de abertura (rb apenas)

        Returns:
            ContentFile com o conteúdo do arquivo
        """
        if mode != 'rb':
            raise ValueError("Supabase storage só suporta modo 'rb'")

        try:
            bucket, path = self._get_bucket_and_path(name)
            content = self._supabase.download_file(bucket, path)

            if content:
                return ContentFile(content, name=name)
            else:
                raise FileNotFoundError(f"Arquivo não encontrado: {name}")

        except Exception as e:
            logger.error(f"Erro ao abrir arquivo '{name}': {str(e)}")
            raise

    def _save(self, name, content):
        """
        Salva um arquivo no Supabase Storage

        Args:
            name: Nome/path do arquivo
            content: Conteúdo do arquivo (File object)

        Returns:
            str: Path do arquivo salvo
        """
        try:
            # Normalizar o nome do arquivo antes de processar
            folder = os.path.dirname(name)
            filename = os.path.basename(name)
            normalized_filename = normalize_filename(filename)

            # Reconstruir o path completo com nome normalizado
            if folder:
                name = os.path.join(folder, normalized_filename).replace('\\', '/')
            else:
                name = normalized_filename

            logger.info(f"Nome normalizado: {filename} -> {normalized_filename}")

            bucket, path = self._get_bucket_and_path(name)

            # Garantir que content é um arquivo
            if hasattr(content, 'read'):
                file_content = content
            else:
                file_content = BytesIO(content)

            # Fazer upload
            folder = os.path.dirname(path)
            filename = os.path.basename(path)

            url = self._supabase.upload_file(
                file=file_content,
                bucket=bucket,
                folder=folder,
                filename=filename
            )

            if url:
                logger.info(f"Arquivo '{name}' salvo com sucesso no Supabase")
                return name
            else:
                raise Exception("Upload retornou None")

        except Exception as e:
            logger.error(f"Erro ao salvar arquivo '{name}': {str(e)}")
            raise

    def exists(self, name):
        """
        Verifica se um arquivo existe no Supabase Storage

        Args:
            name: Nome/path do arquivo

        Returns:
            bool: True se existe, False caso contrário
        """
        try:
            bucket, path = self._get_bucket_and_path(name)
            files = self._supabase.list_files(bucket, os.path.dirname(path))

            filename = os.path.basename(path)
            return any(f.get('name') == filename for f in files)

        except Exception as e:
            logger.error(f"Erro ao verificar existência de '{name}': {str(e)}")
            return False

    def url(self, name):
        """
        Retorna a URL pública do arquivo

        Args:
            name: Nome/path do arquivo

        Returns:
            str: URL pública do arquivo
        """
        try:
            bucket, path = self._get_bucket_and_path(name)
            return self._supabase.get_public_url(bucket, path)
        except Exception as e:
            logger.error(f"Erro ao obter URL de '{name}': {str(e)}")
            return ''

    def delete(self, name):
        """
        Deleta um arquivo do Supabase Storage

        Args:
            name: Nome/path do arquivo
        """
        try:
            bucket, path = self._get_bucket_and_path(name)
            self._supabase.delete_file(bucket, path)
            logger.info(f"Arquivo '{name}' deletado do Supabase")
        except Exception as e:
            logger.error(f"Erro ao deletar arquivo '{name}': {str(e)}")

    def size(self, name):
        """
        Retorna o tamanho do arquivo

        Args:
            name: Nome/path do arquivo

        Returns:
            int: Tamanho em bytes
        """
        try:
            bucket, path = self._get_bucket_and_path(name)
            files = self._supabase.list_files(bucket, os.path.dirname(path))

            filename = os.path.basename(path)
            for f in files:
                if f.get('name') == filename:
                    return f.get('metadata', {}).get('size', 0)

            return 0
        except Exception as e:
            logger.error(f"Erro ao obter tamanho de '{name}': {str(e)}")
            return 0

    def listdir(self, path):
        """
        Lista arquivos e diretórios

        Args:
            path: Path do diretório

        Returns:
            tuple: (diretorios, arquivos)
        """
        try:
            bucket, folder = self._get_bucket_and_path(path)
            files = self._supabase.list_files(bucket, folder)

            directories = []
            file_names = []

            for item in files:
                name = item.get('name', '')
                if item.get('id'):  # É um arquivo
                    file_names.append(name)
                else:  # É um diretório
                    directories.append(name)

            return directories, file_names

        except Exception as e:
            logger.error(f"Erro ao listar diretório '{path}': {str(e)}")
            return [], []

    def get_available_name(self, name, max_length=None):
        """
        Retorna nome disponível para o arquivo
        Se já existe, adiciona sufixo

        Args:
            name: Nome desejado
            max_length: Tamanho máximo (opcional)

        Returns:
            str: Nome disponível
        """
        if not self.exists(name):
            return name

        # Se existe, usar o método padrão do Django
        return super().get_available_name(name, max_length)