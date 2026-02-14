"""
Serviço de integração com Project Gutenberg.
API: https://gutendex.com/
"""
import requests
import logging

logger = logging.getLogger(__name__)


class GutenbergService:
    """Serviço para buscar e importar livros do Project Gutenberg."""
    
    BASE_URL = "https://gutendex.com"
    
    def search(self, query, limit=20):
        """
        Busca livros no Project Gutenberg.
        
        Args:
            query: Termo de busca (título ou autor)
            limit: Número máximo de resultados
            
        Returns:
            Lista de dicionários com dados dos livros
        """
        try:
            response = requests.get(
                f"{self.BASE_URL}/books",
                params={
                    'search': query,
                    'languages': 'pt,en,es',
                },
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            books = []
            for item in data.get('results', [])[:limit]:
                book = self._parse_book(item)
                if book:
                    books.append(book)
            
            return books
            
        except requests.RequestException as e:
            logger.error(f"Erro ao buscar no Gutenberg: {e}")
            return []
    
    def get_book(self, gutenberg_id):
        """
        Obtém detalhes de um livro específico.
        
        Args:
            gutenberg_id: ID do livro no Project Gutenberg
            
        Returns:
            Dicionário com dados do livro ou None
        """
        try:
            response = requests.get(
                f"{self.BASE_URL}/books/{gutenberg_id}",
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            return self._parse_book(data)
            
        except requests.RequestException as e:
            logger.error(f"Erro ao obter livro {gutenberg_id} do Gutenberg: {e}")
            return None
    
    def _parse_book(self, data):
        """Converte dados da API para formato interno."""
        if not data:
            return None
        
        # Obter autores
        authors = data.get('authors', [])
        author_name = authors[0].get('name', 'Autor desconhecido') if authors else 'Autor desconhecido'
        
        # Obter capa
        formats = data.get('formats', {})
        cover_image = (
            formats.get('image/jpeg') or 
            formats.get('image/png') or
            ''
        )
        
        # Obter EPUB - tentar primeiro application/epub+zip
        epub_url = formats.get('application/epub+zip', '')
        
        # Se não tiver, construir URL padrão do Gutenberg
        if not epub_url and data.get('id'):
            gutenberg_id = data.get('id')
            epub_url = f"https://www.gutenberg.org/cache/epub/{gutenberg_id}/pg{gutenberg_id}.epub"
        
        # Detectar idioma
        languages = data.get('languages', ['en'])
        language = languages[0] if languages else 'en'
        
        # Assuntos/categorias
        subjects = data.get('subjects', [])
        bookshelves = data.get('bookshelves', [])
        
        return {
            'external_id': str(data.get('id', '')),
            'title': data.get('title', 'Sem título'),
            'author': author_name,
            'description': '',  # Gutenberg não fornece descrição
            'cover_image': cover_image,
            'epub_url': epub_url,
            'language': self._normalize_language(language),
            'subjects': subjects + bookshelves,
            'source': 'gutenberg',
            'download_count': data.get('download_count', 0),
        }
    
    def _normalize_language(self, lang):
        """Normaliza código de idioma."""
        lang_map = {
            'en': 'en',
            'pt': 'pt',
            'es': 'es',
            'fr': 'fr',
            'de': 'de',
            'it': 'it',
        }
        return lang_map.get(lang, 'other')
    
    def get_popular_books(self, limit=20):
        """
        Obtém livros mais populares.
        
        Returns:
            Lista de livros ordenados por downloads
        """
        try:
            response = requests.get(
                f"{self.BASE_URL}/books",
                params={
                    'languages': 'pt,en',
                    'sort': 'popular',
                },
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            books = []
            for item in data.get('results', [])[:limit]:
                book = self._parse_book(item)
                if book and book.get('epub_url'):
                    books.append(book)
            
            return books
            
        except requests.RequestException as e:
            logger.error(f"Erro ao obter livros populares: {e}")
            return []
    
    def get_portuguese_books(self, limit=50):
        """
        Obtém livros em português.
        
        Returns:
            Lista de livros em português
        """
        try:
            response = requests.get(
                f"{self.BASE_URL}/books",
                params={
                    'languages': 'pt',
                },
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            books = []
            for item in data.get('results', [])[:limit]:
                book = self._parse_book(item)
                if book and book.get('epub_url'):
                    books.append(book)
            
            return books
            
        except requests.RequestException as e:
            logger.error(f"Erro ao obter livros em português: {e}")
            return []
