"""
Serviço de integração com Open Library.
API: https://openlibrary.org/developers/api
"""
import requests
import logging

logger = logging.getLogger(__name__)


class OpenLibraryService:
    """Serviço para buscar e importar livros da Open Library."""
    
    BASE_URL = "https://openlibrary.org"
    COVERS_URL = "https://covers.openlibrary.org"
    
    def search(self, query, limit=20):
        """
        Busca livros na Open Library.
        
        Args:
            query: Termo de busca (título ou autor)
            limit: Número máximo de resultados
            
        Returns:
            Lista de dicionários com dados dos livros
        """
        try:
            response = requests.get(
                f"{self.BASE_URL}/search.json",
                params={
                    'q': query,
                    'limit': limit,
                    'has_fulltext': 'true',  # Apenas livros com texto completo
                },
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            books = []
            for item in data.get('docs', []):
                book = self._parse_search_result(item)
                if book:
                    books.append(book)
            
            return books
            
        except requests.RequestException as e:
            logger.error(f"Erro ao buscar na Open Library: {e}")
            return []
    
    def get_book(self, work_id):
        """
        Obtém detalhes de um livro específico.
        
        Args:
            work_id: ID do work na Open Library (ex: OL45804W)
            
        Returns:
            Dicionário com dados do livro ou None
        """
        try:
            # Obter dados do work
            response = requests.get(
                f"{self.BASE_URL}/works/{work_id}.json",
                timeout=10
            )
            response.raise_for_status()
            work_data = response.json()
            
            # Obter edições para encontrar EPUB
            editions_response = requests.get(
                f"{self.BASE_URL}/works/{work_id}/editions.json",
                timeout=10
            )
            editions_data = editions_response.json() if editions_response.ok else {}
            
            return self._parse_work(work_data, editions_data, work_id)
            
        except requests.RequestException as e:
            logger.error(f"Erro ao obter livro {work_id} da Open Library: {e}")
            return None
    
    def _parse_search_result(self, data):
        """Converte resultado de busca para formato interno."""
        if not data:
            return None
        
        # Verificar se tem edição disponível
        key = data.get('key', '')
        work_id = key.replace('/works/', '') if key else ''
        
        if not work_id:
            return None
        
        # Obter capa
        cover_id = data.get('cover_i')
        cover_image = f"{self.COVERS_URL}/b/id/{cover_id}-L.jpg" if cover_id else ''
        
        # Autor
        authors = data.get('author_name', [])
        author_name = authors[0] if authors else 'Autor desconhecido'
        
        # Idioma
        languages = data.get('language', [])
        language = self._normalize_language(languages[0] if languages else 'en')
        
        # Verificar se tem ebook disponível
        has_ebook = data.get('ebook_access', '') in ['borrowable', 'public']
        
        # Internet Archive ID para download
        ia_ids = data.get('ia', [])
        epub_url = ''
        if ia_ids:
            # Construir URL do Internet Archive
            epub_url = f"https://archive.org/download/{ia_ids[0]}/{ia_ids[0]}.epub"
        
        return {
            'external_id': work_id,
            'title': data.get('title', 'Sem título'),
            'author': author_name,
            'description': '',
            'cover_image': cover_image,
            'epub_url': epub_url,
            'language': language,
            'subjects': data.get('subject', [])[:10],  # Limitar assuntos
            'source': 'openlibrary',
            'publish_year': data.get('first_publish_year'),
            'has_ebook': has_ebook,
            'ia_id': ia_ids[0] if ia_ids else None,
        }
    
    def _parse_work(self, work_data, editions_data, work_id):
        """Converte dados do work para formato interno."""
        if not work_data:
            return None
        
        # Título
        title = work_data.get('title', 'Sem título')
        
        # Descrição
        description = work_data.get('description', '')
        if isinstance(description, dict):
            description = description.get('value', '')
        
        # Autores
        authors = work_data.get('authors', [])
        author_key = authors[0].get('author', {}).get('key', '') if authors else ''
        author_name = 'Autor desconhecido'
        
        if author_key:
            try:
                author_response = requests.get(
                    f"{self.BASE_URL}{author_key}.json",
                    timeout=5
                )
                if author_response.ok:
                    author_data = author_response.json()
                    author_name = author_data.get('name', 'Autor desconhecido')
            except:
                pass
        
        # Capa
        covers = work_data.get('covers', [])
        cover_image = f"{self.COVERS_URL}/b/id/{covers[0]}-L.jpg" if covers else ''
        
        # Buscar EPUB nas edições
        epub_url = ''
        editions = editions_data.get('entries', [])
        for edition in editions:
            ia = edition.get('ocaid')
            if ia:
                epub_url = f"https://archive.org/download/{ia}/{ia}.epub"
                break
        
        # Assuntos
        subjects = work_data.get('subjects', [])
        if isinstance(subjects, list) and subjects and isinstance(subjects[0], dict):
            subjects = [s.get('name', '') for s in subjects]
        
        return {
            'external_id': work_id,
            'title': title,
            'author': author_name,
            'description': description,
            'cover_image': cover_image,
            'epub_url': epub_url,
            'language': 'en',  # Open Library não retorna idioma consistente
            'subjects': subjects[:10],
            'source': 'openlibrary',
        }
    
    def _normalize_language(self, lang):
        """Normaliza código de idioma."""
        lang_map = {
            'eng': 'en',
            'por': 'pt',
            'spa': 'es',
            'fre': 'fr',
            'ger': 'de',
            'ita': 'it',
            'en': 'en',
            'pt': 'pt',
            'es': 'es',
            'fr': 'fr',
            'de': 'de',
            'it': 'it',
        }
        return lang_map.get(lang, 'other')
    
    def get_trending_books(self, limit=20):
        """
        Obtém livros em alta na Open Library.
        
        Returns:
            Lista de livros trending
        """
        try:
            response = requests.get(
                f"{self.BASE_URL}/trending/daily.json",
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            books = []
            for item in data.get('works', [])[:limit]:
                # Transformar formato trending para formato de busca
                book = {
                    'external_id': item.get('key', '').replace('/works/', ''),
                    'title': item.get('title', 'Sem título'),
                    'author': item.get('author_name', ['Autor desconhecido'])[0] if item.get('author_name') else 'Autor desconhecido',
                    'cover_image': f"{self.COVERS_URL}/b/id/{item.get('cover_i')}-L.jpg" if item.get('cover_i') else '',
                    'source': 'openlibrary',
                }
                books.append(book)
            
            return books
            
        except requests.RequestException as e:
            logger.error(f"Erro ao obter livros trending: {e}")
            return []
