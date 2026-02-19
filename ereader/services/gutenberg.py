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
            headers = {
                'User-Agent': 'CGBookStore/1.0 (Educational Project; python-requests)'
            }
            response = requests.get(
                f"{self.BASE_URL}/books",
                params={
                    'search': query,
                    # 'languages': 'pt,en,es', # Removido para permitir todos os idiomas
                },
                headers=headers,
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
            
            book = self._parse_book(data)
            if book:
                # Otimização de URL: Tentar encontrar versão direta (legacy) 
                # para evitar redirecionamentos e problemas com epub3
                best_url = self._find_best_epub_url(gutenberg_id, book['epub_url'])
                book['epub_url'] = best_url
            
            return book
            
        except requests.RequestException as e:
            logger.error(f"Erro ao obter livro {gutenberg_id} do Gutenberg: {e}")
            return None

    def _find_best_epub_url(self, gutenberg_id, original_url):
        """
        Tenta encontrar a melhor URL direta para o EPUB.
        Prioriza: pg{id}-images.epub (Legacy com imagens) -> pg{id}.epub (Legacy sem imagens) -> Original
        """
        try:
            # URLs diretas do cache (bypass redirect e epub3)
            candidates = [
                f"https://www.gutenberg.org/cache/epub/{gutenberg_id}/pg{gutenberg_id}-images.epub",
                f"https://www.gutenberg.org/cache/epub/{gutenberg_id}/pg{gutenberg_id}.epub"
            ]
            
            headers = {'User-Agent': 'CGBookStore/1.0 (Python)'}
            
            for url in candidates:
                # Se a original já for uma dessas, retorna ela
                if url == original_url:
                    return original_url
                    
                # Verificar se existe (HEAD request rápido)
                try:
                    r = requests.head(url, headers=headers, timeout=5)
                    if r.status_code == 200 and int(r.headers.get('Content-Length', 0)) > 1000:
                        logger.info(f"URL otimizada encontrada para {gutenberg_id}: {url}")
                        return url
                except:
                    continue
            
            return original_url
            
        except Exception as e:
            logger.warning(f"Erro ao otimizar URL para {gutenberg_id}: {e}")
            return original_url
    
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
        # A API geralmente retorna redirects ou versões epub3
        epub_url = formats.get('application/epub+zip', '')
        
        # Se não tiver, construir URL padrão do Gutenberg (fallback básico)
        if not epub_url and data.get('id'):
            gutenberg_id = data.get('id')
            epub_url = f"https://www.gutenberg.org/cache/epub/{gutenberg_id}/pg{gutenberg_id}.epub"
        
        # Detectar idioma
        languages = data.get('languages', ['en'])
        language = self._normalize_language(languages[0] if languages else 'en')
        
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
            'language': language,
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
