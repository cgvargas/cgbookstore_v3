"""
Storage Service - Supabase Storage Integration
Serviço para upload de imagens no Supabase Storage.
"""

from typing import Optional
import uuid
import logging
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import os

logger = logging.getLogger(__name__)


class StorageService:
    """
    Serviço para gerenciar upload de imagens.
    
    Usa o storage padrão do Django (Supabase ou local conforme configuração).
    
    Exemplo de uso:
        service = StorageService()
        url = service.upload_image(image_bytes, prefix='news')
    """
    
    def __init__(self):
        self.storage = default_storage
    
    def upload_image(
        self, 
        image_data: bytes, 
        filename: Optional[str] = None,
        prefix: str = 'news/ai-generated'
    ) -> Optional[str]:
        """
        Faz upload da imagem para o storage.
        
        Args:
            image_data: Bytes da imagem
            filename: Nome do arquivo (opcional, gera UUID se não fornecido)
            prefix: Prefixo do path (ex: 'news/ai-generated')
        
        Returns:
            URL pública da imagem ou None em caso de erro
        """
        try:
            # Gerar nome único se não fornecido
            if not filename:
                filename = f"{uuid.uuid4()}.jpg"
            
            # Montar path completo
            file_path = f"{prefix}/{filename}"
            
            # Criar ContentFile para upload
            content = ContentFile(image_data)
            
            # Fazer upload
            saved_path = self.storage.save(file_path, content)
            
            # Obter URL
            url = self.storage.url(saved_path)
            
            logger.info(f"Imagem salva: {saved_path}")
            
            return url
            
        except Exception as e:
            logger.error(f"Erro ao fazer upload da imagem: {str(e)}")
            return None
    
    def delete_image(self, file_path: str) -> bool:
        """
        Remove imagem do storage.
        
        Args:
            file_path: Caminho do arquivo no storage
        
        Returns:
            True se removido com sucesso, False caso contrário
        """
        try:
            if self.storage.exists(file_path):
                self.storage.delete(file_path)
                logger.info(f"Imagem removida: {file_path}")
                return True
            else:
                logger.warning(f"Imagem não encontrada: {file_path}")
                return False
        except Exception as e:
            logger.error(f"Erro ao remover imagem: {str(e)}")
            return False
    
    def image_exists(self, file_path: str) -> bool:
        """Verifica se a imagem existe no storage."""
        try:
            return self.storage.exists(file_path)
        except Exception:
            return False


class LocalImageSaver:
    """
    Alternativa para salvar imagens localmente quando não há Supabase.
    Salva em MEDIA_ROOT/news/ai-generated/
    """
    
    def __init__(self):
        self.media_root = getattr(settings, 'MEDIA_ROOT', 'media')
        self.media_url = getattr(settings, 'MEDIA_URL', '/media/')
    
    def save_image(
        self, 
        image_data: bytes, 
        filename: Optional[str] = None
    ) -> Optional[str]:
        """
        Salva imagem localmente.
        
        Returns:
            URL relativa da imagem (ex: /media/news/ai-generated/xxx.jpg)
        """
        try:
            # Gerar nome único se não fornecido
            if not filename:
                filename = f"{uuid.uuid4()}.jpg"
            
            # Criar diretório se não existir
            save_dir = os.path.join(self.media_root, 'news', 'ai-generated')
            os.makedirs(save_dir, exist_ok=True)
            
            # Salvar arquivo
            file_path = os.path.join(save_dir, filename)
            with open(file_path, 'wb') as f:
                f.write(image_data)
            
            # Retornar URL
            url = f"{self.media_url}news/ai-generated/{filename}"
            
            logger.info(f"Imagem salva localmente: {file_path}")
            
            return url
            
        except Exception as e:
            logger.error(f"Erro ao salvar imagem localmente: {str(e)}")
            return None
