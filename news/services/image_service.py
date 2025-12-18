"""
Image Service - Unsplash Integration
Serviço para buscar imagens de alta qualidade no Unsplash.
"""

import requests
from typing import Dict, Optional, List
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class UnsplashImageService:
    """
    Serviço para buscar imagens no Unsplash.
    
    Requer UNSPLASH_ACCESS_KEY configurada em settings.
    
    Exemplo de uso:
        service = UnsplashImageService()
        image_data = service.search_image(['literatura', 'livros'])
        if image_data:
            image_bytes = service.download_image(image_data)
    """
    
    BASE_URL = "https://api.unsplash.com"
    
    def __init__(self):
        self.access_key = getattr(settings, 'UNSPLASH_ACCESS_KEY', '')
        if not self.access_key:
            logger.warning("UNSPLASH_ACCESS_KEY não configurada. Busca de imagens desabilitada.")
    
    def is_available(self) -> bool:
        """Verifica se o serviço está disponível."""
        return bool(self.access_key)
    
    def search_image(
        self, 
        keywords: List[str], 
        orientation: str = 'landscape',
        fallback_keywords: List[str] = None
    ) -> Optional[Dict]:
        """
        Busca imagem relacionada às palavras-chave.
        
        Args:
            keywords: Lista de palavras-chave para busca
            orientation: 'landscape', 'portrait' ou 'squarish'
            fallback_keywords: Keywords alternativas se a primeira busca falhar
        
        Returns:
            Dict com dados da imagem ou None
        """
        if not self.is_available():
            logger.warning("Unsplash não disponível")
            return None
        
        try:
            # Construir query com até 3 keywords
            query = ' '.join(keywords[:3])
            
            image = self._search_query(query, orientation)
            
            # Se não encontrou, tentar fallback
            if not image and fallback_keywords:
                fallback_query = ' '.join(fallback_keywords[:3])
                logger.info(f"Tentando busca alternativa: {fallback_query}")
                image = self._search_query(fallback_query, orientation)
            
            # Se ainda não encontrou, tentar termos genéricos de literatura
            if not image:
                generic_query = "books reading library"
                logger.info(f"Tentando busca genérica: {generic_query}")
                image = self._search_query(generic_query, orientation)
            
            return image
            
        except Exception as e:
            logger.error(f"Erro ao buscar imagem no Unsplash: {str(e)}")
            return None
    
    def _search_query(self, query: str, orientation: str) -> Optional[Dict]:
        """Realiza busca no Unsplash."""
        try:
            response = requests.get(
                f"{self.BASE_URL}/search/photos",
                params={
                    'query': query,
                    'per_page': 5,
                    'orientation': orientation,
                },
                headers={
                    'Authorization': f'Client-ID {self.access_key}'
                },
                timeout=10
            )
            
            response.raise_for_status()
            data = response.json()
            
            if data.get('results'):
                # Pegar primeira imagem disponível
                image = data['results'][0]
                
                logger.info(f"Imagem encontrada para '{query}': {image['id']}")
                
                return {
                    'id': image['id'],
                    'url_regular': image['urls']['regular'],  # 1080px
                    'url_small': image['urls']['small'],  # 400px
                    'url_thumb': image['urls']['thumb'],  # 200px
                    'download_location': image['links']['download_location'],
                    'photographer': image['user']['name'],
                    'photographer_url': image['user']['links']['html'],
                    'photographer_username': image['user']['username'],
                    'alt_description': image.get('alt_description') or query,
                    'color': image.get('color', '#333333'),
                }
            
            logger.info(f"Nenhuma imagem encontrada para: {query}")
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na requisição Unsplash: {str(e)}")
            return None
    
    def download_image(self, image_data: Dict) -> Optional[bytes]:
        """
        Faz download da imagem.
        
        IMPORTANTE: Notifica Unsplash do download conforme requerido pela API.
        
        Returns:
            Bytes da imagem ou None
        """
        if not self.is_available():
            return None
        
        try:
            # Notificar Unsplash do download (requerido pela API)
            if 'download_location' in image_data:
                requests.get(
                    image_data['download_location'],
                    headers={'Authorization': f'Client-ID {self.access_key}'},
                    timeout=5
                )
            
            # Fazer download da imagem (usar url_regular para boa qualidade)
            image_url = image_data.get('url_regular', image_data.get('url_small', ''))
            if not image_url:
                logger.error("URL da imagem não disponível")
                return None
            
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            
            logger.info(f"Imagem baixada: {len(response.content)} bytes")
            
            return response.content
            
        except Exception as e:
            logger.error(f"Erro ao baixar imagem: {str(e)}")
            return None
    
    def get_attribution(self, image_data: Dict) -> str:
        """
        Retorna texto de atribuição para a imagem.
        Formato limpo: 📷 Nome do Fotógrafo / Unsplash
        """
        photographer = image_data.get('photographer', 'Unknown')
        return f'📷 {photographer} / Unsplash'
