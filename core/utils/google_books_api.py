"""
Google Books API Integration
Módulo para integração com a API do Google Books.
Permite buscar livros por título, autor, ISBN e editora.
"""

import requests
from typing import Dict, List, Optional
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.conf import settings
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# URL base da API do Google Books
GOOGLE_BOOKS_API_URL = "https://www.googleapis.com/books/v1/volumes"


def search_books(
    query: str = None,
    title: str = None,
    author: str = None,
    isbn: str = None,
    publisher: str = None,
    max_results: int = 10,
    start_index: int = 0
) -> Dict:
    """
    Busca livros na API do Google Books.

    Args:
        query: Termo de busca geral
        title: Título do livro
        author: Nome do autor
        isbn: ISBN do livro
        publisher: Nome da editora
        max_results: Número máximo de resultados (1-40)
        start_index: Índice inicial para paginação

    Returns:
        Dict com os resultados da busca
    """
    try:
        # Construir query string
        search_terms = []

        if query:
            search_terms.append(query)
        if title:
            search_terms.append(f'intitle:{title}')
        if author:
            search_terms.append(f'inauthor:{author}')
        if isbn:
            search_terms.append(f'isbn:{isbn}')
        if publisher:
            search_terms.append(f'inpublisher:{publisher}')

        if not search_terms:
            return {'error': 'Nenhum termo de busca fornecido'}

        q = ' '.join(search_terms)

        # Parâmetros da requisição
        params = {
            'q': q,
            'maxResults': min(max_results, 40),  # Máximo permitido pela API
            'startIndex': start_index,
            'langRestrict': 'pt',  # Priorizar resultados em português
            'printType': 'books'  # Apenas livros
        }

        # Adicionar API key se configurada
        api_key = getattr(settings, 'GOOGLE_BOOKS_API_KEY', '')
        if api_key:
            params['key'] = api_key

        # Fazer requisição com retry em caso de Rate Limit (429)
        import time
        max_retries = 3
        base_delay = 1
        
        for attempt in range(max_retries):
            response = requests.get(GOOGLE_BOOKS_API_URL, params=params, timeout=10)
            
            if response.status_code == 429:
                if attempt < max_retries - 1:
                    sleep_time = base_delay * (2 ** attempt)
                    logger.warning(f"Rate limit do Google Books atingido. Tentativa {attempt + 1}/{max_retries}. Aguardando {sleep_time}s...")
                    time.sleep(sleep_time)
                    continue
                else:
                    return {'error': 'Limite de requisições da API excedido. Aguarde alguns minutos e tente novamente.'}
            
            response.raise_for_status()
            break

        data = response.json()

        # Processar resultados
        results = {
            'total_items': data.get('totalItems', 0),
            'books': []
        }

        for item in data.get('items', []):
            book_info = extract_book_info(item)
            if book_info:
                results['books'].append(book_info)

        return results

    except requests.exceptions.RequestException as e:
        logger.error(f"Erro ao buscar livros: {e}")
        return {'error': f'Erro na requisição: {str(e)}'}
    except Exception as e:
        logger.error(f"Erro inesperado: {e}")
        return {'error': f'Erro inesperado: {str(e)}'}


def get_book_by_id(google_book_id: str) -> Optional[Dict]:
    """
    Busca detalhes de um livro específico pelo ID do Google Books.

    Args:
        google_book_id: ID do livro no Google Books

    Returns:
        Dict com informações do livro ou None
    """
    try:
        url = f"{GOOGLE_BOOKS_API_URL}/{google_book_id}"

        # Adicionar API key se configurada
        params = {}
        api_key = getattr(settings, 'GOOGLE_BOOKS_API_KEY', '')
        if api_key:
            params['key'] = api_key

        import time
        max_retries = 3
        base_delay = 1
        
        for attempt in range(max_retries):
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 429:
                if attempt < max_retries - 1:
                    sleep_time = base_delay * (2 ** attempt)
                    logger.warning(f"Rate limit do Google Books atingido no ID {google_book_id}. Tentativa {attempt + 1}/{max_retries}. Aguardando {sleep_time}s...")
                    time.sleep(sleep_time)
                    continue
                else:
                    logger.error(f"Rate limit do Google Books atingido definitivamente para {google_book_id}.")
                    return None
            
            response.raise_for_status()
            break

        return extract_book_info(response.json())

    except requests.exceptions.RequestException as e:
        logger.error(f"Erro ao buscar livro {google_book_id}: {e}")
        return None


"""
Correções para google_books_api.py
Substitua as funções extract_book_info e download_cover
"""


def extract_book_info(item: Dict) -> Optional[Dict]:
    """
    Extrai informações relevantes de um item da resposta da API.
    ATUALIZADO: Busca imagens em alta resolução.
    """
    try:
        volume_info = item.get('volumeInfo', {})

        # ISBNs
        isbn_13 = None
        isbn_10 = None
        for identifier in volume_info.get('industryIdentifiers', []):
            if identifier.get('type') == 'ISBN_13':
                isbn_13 = identifier.get('identifier')
            elif identifier.get('type') == 'ISBN_10':
                isbn_10 = identifier.get('identifier')

        # IMAGENS - BUSCAR A MAIOR RESOLUÇÃO DISPONÍVEL
        image_links = volume_info.get('imageLinks', {})

        # Ordem de preferência: large > medium > small > thumbnail > smallThumbnail
        thumbnail = None
        for size in ['extraLarge', 'large', 'medium', 'small', 'thumbnail', 'smallThumbnail']:
            if size in image_links:
                thumbnail = image_links[size]
                break

        # Converter para HTTPS e otimizar URL
        if thumbnail:
            thumbnail = thumbnail.replace('http://', 'https://')
            # Remover parâmetros que limitam qualidade
            thumbnail = thumbnail.replace('&edge=curl', '')
            # Tentar obter zoom máximo (0 = sem zoom/máxima qualidade)
            if 'zoom=' in thumbnail:
                thumbnail = thumbnail.replace('zoom=1', 'zoom=0')
                thumbnail = thumbnail.replace('zoom=2', 'zoom=0')
            else:
                # Adicionar zoom=0 se não existir
                if '?' in thumbnail:
                    thumbnail += '&zoom=0'

        # Preço (pode não estar disponível)
        sale_info = item.get('saleInfo', {})
        price = None
        if sale_info.get('saleability') == 'FOR_SALE':
            list_price = sale_info.get('listPrice', {})
            price = list_price.get('amount')

        book_info = {
            'google_book_id': item.get('id'),
            'title': volume_info.get('title'),
            'subtitle': volume_info.get('subtitle'),
            'authors': volume_info.get('authors', []),
            'publisher': volume_info.get('publisher'),
            'published_date': volume_info.get('publishedDate'),
            'description': volume_info.get('description'),
            'isbn_13': isbn_13,
            'isbn_10': isbn_10,
            'page_count': volume_info.get('pageCount'),
            'categories': volume_info.get('categories', []),
            'language': volume_info.get('language'),
            'thumbnail': thumbnail,
            'preview_link': volume_info.get('previewLink'),
            'info_link': volume_info.get('infoLink'),
            'average_rating': volume_info.get('averageRating'),
            'ratings_count': volume_info.get('ratingsCount'),
            'price': price
        }

        return book_info

    except Exception as e:
        logger.error(f"Erro ao extrair informações: {e}")
        return None


def download_cover(image_url: str, book_slug: str, existing_cover: str = None) -> Optional[str]:
    """
    Baixa uma capa de livro da URL e salva no media storage.
    ATUALIZADO: Otimiza URL para máxima qualidade.
    """
    try:
        if not image_url:
            return None

        # Otimizar URL para máxima qualidade
        optimized_url = image_url

        # Remover limitadores de qualidade
        optimized_url = optimized_url.replace('&edge=curl', '')
        optimized_url = optimized_url.replace('&source=gbs_api', '')

        # Ajustar zoom para máxima qualidade
        if 'zoom=' in optimized_url:
            # zoom=0 retorna a melhor qualidade disponível
            optimized_url = optimized_url.replace('zoom=1', 'zoom=0')
            optimized_url = optimized_url.replace('zoom=2', 'zoom=0')
            optimized_url = optimized_url.replace('zoom=3', 'zoom=0')
        else:
            # Adicionar zoom=0 se não existir
            if '?' in optimized_url:
                optimized_url += '&zoom=0'

        # Adicionar parâmetro para imagem grande se for URL do Google Books
        if 'books.google.com' in optimized_url and 'img=' in optimized_url:
            # img=1 retorna maior resolução
            if 'img=0' in optimized_url:
                optimized_url = optimized_url.replace('img=0', 'img=1')

        logger.info(f"Baixando capa otimizada: {optimized_url}")

        # Baixar imagem com timeout maior para imagens grandes
        import time
        max_retries = 3
        base_delay = 1
        
        for attempt in range(max_retries):
            response = requests.get(optimized_url, timeout=15)
            
            if response.status_code == 429:
                if attempt < max_retries - 1:
                    sleep_time = base_delay * (2 ** attempt)
                    logger.warning(f"Rate limit ao baixar capa {optimized_url}. Tentativa {attempt + 1}/{max_retries}. Aguardando {sleep_time}s...")
                    time.sleep(sleep_time)
                    continue
                else:
                    logger.error(f"Rate limit definitivo ao baixar capa: {optimized_url}")
                    return None
            
            response.raise_for_status()
            break

        # Verificar se é realmente uma imagem
        content_type = response.headers.get('Content-Type', '')
        if 'image' not in content_type:
            logger.warning(f"URL não retornou imagem: {content_type}")
            return None

        # Nome do arquivo
        if existing_cover:
            filename = existing_cover
            if default_storage.exists(filename):
                default_storage.delete(filename)
        else:
            filename = f'books/covers/{book_slug}.jpg'

        # Salvar no storage
        path = default_storage.save(
            filename,
            ContentFile(response.content)
        )

        logger.info(f"Capa salva em alta resolução: {path} ({len(response.content)} bytes)")
        return path

    except Exception as e:
        logger.error(f"Erro ao baixar capa: {e}")
        return None


def update_book_cover_from_google(book, force: bool = False) -> bool:
    """
    Atualiza a capa de um livro do banco usando Google Books.

    Args:
        book: Instância do model Book
        force: Se True, substitui capa existente

    Returns:
        True se atualizou com sucesso, False caso contrário
    """
    try:
        # Verificar se já tem capa e não é forçado
        if book.cover_image and not force:
            logger.info(f"Livro {book.title} já tem capa")
            return False

        # Buscar no Google Books
        results = search_books(
            title=book.title,
            author=book.author.name if book.author else None,
            max_results=1
        )

        if not results.get('books'):
            logger.warning(f"Nenhum resultado para {book.title}")
            return False

        google_book = results['books'][0]
        thumbnail = google_book.get('thumbnail')

        if not thumbnail:
            logger.warning(f"Sem thumbnail para {book.title}")
            return False

        # Baixar e salvar capa
        cover_path = download_cover(thumbnail, book.slug)

        if cover_path:
            book.cover_image = cover_path
            book.save()
            logger.info(f"Capa atualizada: {book.title}")
            return True

        return False

    except Exception as e:
        logger.error(f"Erro ao atualizar capa de {book.title}: {e}")
        return False


def search_books_by_author(author_name: str, max_results: int = 20) -> Dict:
    """
    Busca todos os livros de um autor específico.

    Args:
        author_name: Nome do autor
        max_results: Número máximo de resultados

    Returns:
        Dict com os resultados
    """
    return search_books(author=author_name, max_results=max_results)


def search_books_by_publisher(publisher_name: str, max_results: int = 20) -> Dict:
    """
    Busca todos os livros de uma editora específica.

    Args:
        publisher_name: Nome da editora
        max_results: Número máximo de resultados

    Returns:
        Dict com os resultados
    """
    return search_books(publisher=publisher_name, max_results=max_results)


def get_book_by_isbn(isbn: str) -> Optional[Dict]:
    """
    Busca um livro específico pelo ISBN.

    Args:
        isbn: ISBN-10 ou ISBN-13

    Returns:
        Dict com informações do livro ou None
    """
    results = search_books(isbn=isbn, max_results=1)

    if results.get('books'):
        return results['books'][0]

    return None

def parse_google_books_date(date_string):
    """
    Converte data do Google Books para formato Django.
    Aceita: '2005', '2005-07', '2005-07-16'
    Retorna: date object ou '2000-01-01' como fallback
    """
    if not date_string:
        return datetime(2000, 1, 1).date()  # Fallback padrão

    try:
        # Tentar formato completo
        if len(date_string) == 10:  # YYYY-MM-DD
            return datetime.strptime(date_string, '%Y-%m-%d').date()
        # Apenas ano
        elif len(date_string) == 4:  # YYYY
            return datetime.strptime(f"{date_string}-01-01", '%Y-%m-%d').date()
        # Ano e mês
        elif len(date_string) == 7:  # YYYY-MM
            return datetime.strptime(f"{date_string}-01", '%Y-%m-%d').date()
        else:
            return datetime(2000, 1, 1).date()
    except:
        return datetime(2000, 1, 1).date()