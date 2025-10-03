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

        # Fazer requisição
        response = requests.get(GOOGLE_BOOKS_API_URL, params=params, timeout=10)
        response.raise_for_status()

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

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        return extract_book_info(response.json())

    except requests.exceptions.RequestException as e:
        logger.error(f"Erro ao buscar livro {google_book_id}: {e}")
        return None


def extract_book_info(item: Dict) -> Optional[Dict]:
    """
    Extrai informações relevantes de um item da resposta da API.

    Args:
        item: Item da resposta da API

    Returns:
        Dict com informações processadas do livro
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

        # Imagens
        image_links = volume_info.get('imageLinks', {})
        thumbnail = image_links.get('thumbnail', '').replace('http://', 'https://')

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
            'small_thumbnail': image_links.get('smallThumbnail', '').replace('http://', 'https://'),
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

    Args:
        image_url: URL da imagem
        book_slug: Slug do livro para nomear o arquivo
        existing_cover: Caminho da capa existente para sobrescrever

    Returns:
        Caminho relativo da imagem salva ou None
    """
    try:
        if not image_url:
            return None

        # Baixar imagem
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()

        # Nome do arquivo - usar o existente ou criar novo com sufixo _google
        if existing_cover:
            filename = existing_cover
            # Deletar arquivo antigo se existir
            if default_storage.exists(filename):
                default_storage.delete(filename)
        else:
            filename = f'books/covers/{book_slug}.jpg'

        # Salvar no storage
        path = default_storage.save(
            filename,
            ContentFile(response.content)
        )

        logger.info(f"Capa baixada: {path}")
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