# core/services/open_library_cover_service.py
"""
Serviço oficial de integração com a Open Library Covers API.

DIRETRIZES DE ARQUITETURA E GOVERNANÇA:
1. Exibição remota oficial: utiliza a infraestrutura oficial da Open Library
   (https://covers.openlibrary.org/b/isbn/{isbn}-{size}.jpg) sem realizar download
   nem armazenamento físico das imagens em disco local ou Supabase.
2. Deteção precisa (?default=false): ao verificar a existência de capas, sempre
   utiliza o parâmetro ?default=false para receber HTTP 404 caso a capa não exista,
   evitando imagens vazias de 1x1 pixel.
3. Associação estrita por edição: a busca é estritamente vinculada ao ISBN-10 ou ISBN-13
   da respectiva edição, nunca por título genérico ou substituição de edição.
4. Cache eficiente: cacheia confirmações positivas por 7 dias e negativas por 24 horas,
   evitando requisições redundantes à infraestrutura da Open Library.
5. Invariantes jurídicos: capas descobertas são registradas na proveniência técnica
   com audit_status='not_audited', provenance_provider='open_library', provenance_method='remote_display',
   license_type='' (não identificada) e legal_basis='', sem presunção de Domínio Público ou Creative Commons.
"""

import logging
import re
from typing import Optional, Dict, Any
import requests
from django.core.cache import cache

logger = logging.getLogger(__name__)

CACHE_TTL_POSITIVE = 7 * 86400  # 7 dias para capas confirmadas
CACHE_TTL_NEGATIVE = 24 * 3600  # 24 horas para 404 (capa inexistente)
CACHE_TTL_TRANSIENT = 3600      # 1 hora para erros temporários de rede/timeout

DEFAULT_TIMEOUT = 4.0           # Timeout em segundos para verificação rápida


class OpenLibraryCoverService:
    """
    Serviço para consulta, verificação e obtenção de capas remotas via Open Library Covers API.
    """

    COVERS_BASE_URL = "https://covers.openlibrary.org/b/isbn"
    BOOKS_API_BASE_URL = "https://openlibrary.org/api/books"
    VALID_SIZES = ('S', 'M', 'L')
    USER_AGENT = "CGBookStore-OpenLibraryIntegration/1.0 (contato@cgbookstore.local)"

    @classmethod
    def normalize_isbn(cls, isbn: Optional[str]) -> Optional[str]:
        """
        Normaliza e valida o formato de um código ISBN (ISBN-10 ou ISBN-13).
        Remove hifens, espaços e caracteres não alfanuméricos.
        Retorna a string higienizada ou None se inválido.
        """
        if not isbn or not isinstance(isbn, str):
            return None

        clean = re.sub(r'[^0-9Xx]', '', isbn.strip()).upper()

        # Validação de comprimento: ISBN-10 (10 chars) ou ISBN-13 (13 dígitos)
        if len(clean) == 10:
            # Primeiros 9 caracteres devem ser dígitos numéricos, 10º pode ser dígito ou 'X'
            if re.match(r'^\d{9}[\dX]$', clean):
                return clean
        elif len(clean) == 13:
            # Todos os 13 caracteres devem ser numéricos
            if clean.isdigit():
                return clean

        return None

    @classmethod
    def get_canonical_url(cls, isbn: str, size: str = 'L') -> Optional[str]:
        """
        Retorna a URL canônica oficial para exibição remota da capa.
        Tamanhos válidos: 'S' (pequeno), 'M' (médio), 'L' (grande).
        """
        clean_isbn = cls.normalize_isbn(isbn)
        if not clean_isbn:
            return None

        size_upper = size.upper() if size else 'L'
        if size_upper not in cls.VALID_SIZES:
            size_upper = 'L'

        return f"{cls.COVERS_BASE_URL}/{clean_isbn}-{size_upper}.jpg"

    @classmethod
    def get_verification_url(cls, isbn: str, size: str = 'L') -> Optional[str]:
        """
        Retorna a URL com ?default=false utilizada para verificar existência real da capa.
        Conforme documentação oficial da Open Library, default=false faz a API retornar
        404 em vez de redirecionar para a imagem em branco de 1x1 pixel.
        """
        canonical = cls.get_canonical_url(isbn, size=size)
        if not canonical:
            return None
        return f"{canonical}?default=false"

    @classmethod
    def get_cache_key(cls, isbn: str, size: str = 'L') -> str:
        """Gera a chave de cache normalizada para a consulta de capa."""
        return f"ol_cover:isbn:{isbn}:{size.upper()}"

    @classmethod
    def check_cover_exists(
        cls,
        isbn: str,
        size: str = 'L',
        timeout: float = DEFAULT_TIMEOUT,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Verifica se a capa existe na Open Library Covers API.
        Usa stream=True para ler apenas os cabeçalhos da resposta HTTP sem baixar o arquivo.

        Returns:
            Dict com:
            - 'exists': bool indicando se a capa existe (HTTP 200)
            - 'url': URL canônica oficial (ou vazia se não existe)
            - 'isbn': ISBN normalizado
            - 'size': tamanho ('S', 'M', 'L')
            - 'status_code': código HTTP recebido (200, 404, etc.)
            - 'error': descrição de erro caso tenha ocorrido
        """
        clean_isbn = cls.normalize_isbn(isbn)
        if not clean_isbn:
            return {
                'exists': False,
                'url': '',
                'isbn': '',
                'size': size,
                'status_code': None,
                'error': 'ISBN inválido ou não fornecido',
            }

        size_upper = size.upper() if size in cls.VALID_SIZES else 'L'
        cache_key = cls.get_cache_key(clean_isbn, size_upper)

        if use_cache:
            cached_data = cache.get(cache_key)
            if cached_data is not None and isinstance(cached_data, dict):
                return cached_data

        verification_url = cls.get_verification_url(clean_isbn, size_upper)
        canonical_url = cls.get_canonical_url(clean_isbn, size_upper)

        headers = {
            'User-Agent': cls.USER_AGENT,
            'Accept': 'image/jpeg, image/png, image/*, */*',
        }

        try:
            # Usar stream=True para obter apenas headers e evitar download do corpo da imagem
            response = requests.get(
                verification_url,
                timeout=timeout,
                headers=headers,
                stream=True,
                allow_redirects=True
            )
            status_code = response.status_code
            response.close()

            if status_code == 200:
                result = {
                    'exists': True,
                    'url': canonical_url,
                    'isbn': clean_isbn,
                    'size': size_upper,
                    'status_code': 200,
                    'error': None,
                }
                if use_cache:
                    cache.set(cache_key, result, timeout=CACHE_TTL_POSITIVE)
                return result

            elif status_code == 404:
                result = {
                    'exists': False,
                    'url': '',
                    'isbn': clean_isbn,
                    'size': size_upper,
                    'status_code': 404,
                    'error': 'Capa não encontrada na Open Library (HTTP 404)',
                }
                if use_cache:
                    cache.set(cache_key, result, timeout=CACHE_TTL_NEGATIVE)
                return result

            else:
                result = {
                    'exists': False,
                    'url': '',
                    'isbn': clean_isbn,
                    'size': size_upper,
                    'status_code': status_code,
                    'error': f'Open Library respondeu com status {status_code}',
                }
                if use_cache:
                    cache.set(cache_key, result, timeout=CACHE_TTL_TRANSIENT)
                return result

        except requests.exceptions.Timeout:
            logger.warning(f"[OpenLibraryCoverService] Timeout ({timeout}s) ao consultar capa para ISBN {clean_isbn}")
            result = {
                'exists': False,
                'url': '',
                'isbn': clean_isbn,
                'size': size_upper,
                'status_code': None,
                'error': 'Timeout de conexão com Open Library Covers API',
            }
            if use_cache:
                cache.set(cache_key, result, timeout=CACHE_TTL_TRANSIENT)
            return result

        except requests.exceptions.RequestException as exc:
            logger.warning(f"[OpenLibraryCoverService] Erro de rede ao consultar ISBN {clean_isbn}: {exc}")
            result = {
                'exists': False,
                'url': '',
                'isbn': clean_isbn,
                'size': size_upper,
                'status_code': None,
                'error': f'Erro de rede: {str(exc)[:150]}',
            }
            if use_cache:
                cache.set(cache_key, result, timeout=CACHE_TTL_TRANSIENT)
            return result

    @classmethod
    def fetch_book_api_metadata(cls, isbn: str, timeout: float = DEFAULT_TIMEOUT) -> Dict[str, Any]:
        """
        Consulta a Books API da Open Library para coletar identificadores bibliográficos
        e metadados da edição (Cover ID, Work/Edition OLID, URLs).
        Endpoint: https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&jscmd=data&format=json
        """
        clean_isbn = cls.normalize_isbn(isbn)
        if not clean_isbn:
            return {}

        cache_key = f"ol_book_meta:isbn:{clean_isbn}"
        cached = cache.get(cache_key)
        if cached is not None and isinstance(cached, dict):
            return cached

        api_url = f"{cls.BOOKS_API_BASE_URL}?bibkeys=ISBN:{clean_isbn}&jscmd=data&format=json"
        headers = {'User-Agent': cls.USER_AGENT}

        try:
            resp = requests.get(api_url, timeout=timeout, headers=headers)
            if resp.status_code != 200:
                return {}

            data = resp.json()
            book_key = f"ISBN:{clean_isbn}"
            if book_key not in data:
                cache.set(cache_key, {}, timeout=CACHE_TTL_NEGATIVE)
                return {}

            book_info = data[book_key]
            parsed_meta = {
                'title': book_info.get('title', ''),
                'url': book_info.get('url', ''),
                'edition_key': book_info.get('key', '').replace('/books/', ''),
                'cover_data': book_info.get('cover', {}),
                'number_of_pages': book_info.get('number_of_pages'),
                'publish_date': book_info.get('publish_date', ''),
            }

            # Extrair cover_id se presente na URL da capa
            cover_data = book_info.get('cover', {})
            cover_large = cover_data.get('large', '') or cover_data.get('medium', '')
            cover_id_match = re.search(r'/b/id/(\d+)-', cover_large)
            if cover_id_match:
                parsed_meta['cover_id'] = int(cover_id_match.group(1))
            else:
                parsed_meta['cover_id'] = None

            cache.set(cache_key, parsed_meta, timeout=CACHE_TTL_POSITIVE)
            return parsed_meta

        except Exception as exc:
            logger.debug(f"[OpenLibraryCoverService] Falha ao obter metadados da Books API para {clean_isbn}: {exc}")
            return {}

    @classmethod
    def resolve_and_register_book_cover(
        cls,
        book: Any,
        size: str = 'L',
        timeout: float = DEFAULT_TIMEOUT,
        performed_by=None
    ) -> Optional[str]:
        """
        Tenta resolver a capa remota do livro na Open Library e, caso exista,
        registra a proveniência técnica de forma idempotente e segura através do
        ImageRightsProvenanceService.

        Returns:
            URL canônica oficial da capa se disponível, ou None.
        """
        if not book or not getattr(book, 'isbn', None):
            return None

        check_res = cls.check_cover_exists(book.isbn, size=size, timeout=timeout)
        if not check_res.get('exists'):
            return None

        canonical_url = check_res['url']
        clean_isbn = check_res['isbn']

        # Coletar metadados complementares da Books API
        extra_meta = cls.fetch_book_api_metadata(clean_isbn, timeout=timeout)
        cover_id = extra_meta.get('cover_id')
        edition_key = extra_meta.get('edition_key', '')

        # Registrar proveniência técnica via ImageRightsProvenanceService
        from core.services.image_rights_provenance_service import ImageRightsProvenanceService
        ImageRightsProvenanceService.register_open_library_cover(
            book=book,
            source_url=canonical_url,
            isbn=clean_isbn,
            provider_asset_id=str(cover_id or edition_key or clean_isbn),
            cover_id=cover_id,
            edition_key=edition_key,
            safe_metadata={
                'isbn': clean_isbn,
                'source_type': 'open_library',
                'cover_id': cover_id,
                'edition_key': edition_key,
                'cover_size': size.upper(),
                'is_remote_storage': True,
                'stored_locally': False,
                'service': 'open_library_covers_api',
            },
            performed_by=performed_by,
            source='open_library_cover_service'
        )

        return canonical_url
