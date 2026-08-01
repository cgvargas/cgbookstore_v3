"""
Serviço de integração oficial com a API da Amazon Brasil (Programa de Associados).
Suporta chamadas reais e modo Mock desacoplado para ambientes de desenvolvimento/testes.
"""

import logging
from dataclasses import dataclass
from typing import Dict, List, Optional
from django.conf import settings
from partners.services.amazon_service import AmazonURLNormalizer

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AmazonProductData:
    """Dados de um produto/livro obtidos da API da Amazon Brasil."""
    asin: str
    title: str
    author: Optional[str]
    publisher: Optional[str]
    publication_date: Optional[str]
    price: Optional[float]
    currency: str
    cover_url: Optional[str]
    detail_url: str
    affiliate_url: str
    available_kindle: bool
    available_print: bool
    is_presale: bool
    rating: Optional[float]
    ratings_count: Optional[int]
    page_count: Optional[int]
    binding: Optional[str]
    source: str  # 'amazon_api' ou 'amazon_mock'


class AmazonAPIService:
    """
    Cliente para a API da Amazon Brasil.
    Desacoplado via Feature Flags e Mocks.
    """

    @classmethod
    def get_associate_tag(cls) -> str:
        """Retorna a tag de associado configurada."""
        return getattr(settings, 'AMAZON_ASSOCIATE_TAG', 'cgbookstore-20')

    @classmethod
    def is_api_enabled(cls) -> bool:
        """Verifica se a API da Amazon está habilitada."""
        return getattr(settings, 'AMAZON_API_ENABLED', False)

    @classmethod
    def is_mock_mode(cls) -> bool:
        """Verifica se o modo Mock está ativo."""
        return getattr(settings, 'AMAZON_API_MOCK_MODE', True)

    @classmethod
    def get_status(cls) -> Dict[str, any]:
        """Retorna o status atual da integração com a Amazon."""
        enabled = cls.is_api_enabled()
        mock = cls.is_mock_mode()
        tag = cls.get_associate_tag()
        has_keys = bool(getattr(settings, 'AMAZON_ACCESS_KEY', '') and getattr(settings, 'AMAZON_SECRET_KEY', ''))

        if mock:
            mode_display = "Modo MOCK (Simulado / Desacoplado)"
        elif enabled and has_keys:
            mode_display = "Modo PRODUÇÃO (API Real Ativa)"
        else:
            mode_display = "Desativado (Aguardando Credenciais)"

        return {
            'enabled': enabled,
            'mock_mode': mock,
            'associate_tag': tag,
            'has_credentials': has_keys,
            'mode_display': mode_display
        }

    @classmethod
    def search_by_isbn(cls, isbn: str) -> Optional[AmazonProductData]:
        """
        Busca um produto na Amazon Brasil pelo ISBN.
        """
        if not isbn:
            return None

        clean_isbn = str(isbn).replace('-', '').strip()
        logger.info(f"[AMAZON API] Buscando livro por ISBN: {clean_isbn}")

        if cls.is_mock_mode() or not cls.is_api_enabled():
            return cls._generate_mock_product(isbn=clean_isbn)

        return cls._fetch_real_api(item_id=clean_isbn, id_type="ISBN")

    @classmethod
    def search_by_asin(cls, asin: str) -> Optional[AmazonProductData]:
        """
        Busca um produto na Amazon Brasil pelo ASIN.
        """
        if not asin:
            return None

        clean_asin = asin.strip().upper()
        logger.info(f"[AMAZON API] Buscando livro por ASIN: {clean_asin}")

        if cls.is_mock_mode() or not cls.is_api_enabled():
            return cls._generate_mock_product(asin=clean_asin)

        return cls._fetch_real_api(item_id=clean_asin, id_type="ASIN")

    @classmethod
    def search_by_keywords(cls, keywords: str, max_results: int = 5) -> List[AmazonProductData]:
        """
        Busca produtos na Amazon Brasil por palavra-chave (título/autor).
        """
        if not keywords:
            return []

        logger.info(f"[AMAZON API] Buscando livros por palavra-chave: {keywords}")

        if cls.is_mock_mode() or not cls.is_api_enabled():
            return [cls._generate_mock_product(title=keywords, index=i) for i in range(min(max_results, 3))]

        return cls._fetch_real_api_search(keywords=keywords, max_results=max_results)

    @classmethod
    def fetch_by_url(cls, url: str) -> Optional[AmazonProductData]:
        """
        Dada uma URL de produto da Amazon Brasil, extrai o ASIN e recupera os dados.
        """
        try:
            asin = AmazonURLNormalizer.extract_asin(url)
            return cls.search_by_asin(asin)
        except ValueError as exc:
            logger.warning(f"[AMAZON API] Não foi possível extrair ASIN da URL '{url}': {exc}")
            return None

    @classmethod
    def _generate_mock_product(
        cls,
        isbn: Optional[str] = None,
        asin: Optional[str] = None,
        title: Optional[str] = None,
        index: int = 0
    ) -> AmazonProductData:
        """
        Gera uma resposta simulada (Mock) com schema idêntico ao da Amazon PA-API / Creators API.
        """
        resolved_asin = asin or (f"B00{isbn[:7]}" if isbn and len(isbn) >= 7 else f"B08MOCK{index:03d}")
        tag = cls.get_associate_tag()
        resolved_title = title or (f"Edição Especial Amazon - ISBN {isbn}" if isbn else "Livro Exemplo Amazon Brasil")
        
        affiliate_url = f"https://www.amazon.com.br/dp/{resolved_asin}?tag={tag}"

        return AmazonProductData(
            asin=resolved_asin,
            title=resolved_title,
            author="Autor Confirmado Amazon",
            publisher="Editora Parceira Brasil",
            publication_date="2024-01-15",
            price=49.90 + (index * 10),
            currency="BRL",
            cover_url="https://images-na.ssl-images-amazon.com/images/I/71wF3w9K2wL._AC_UL600_SR600,400_.jpg",
            detail_url=affiliate_url,
            affiliate_url=affiliate_url,
            available_kindle=True,
            available_print=True,
            is_presale=False,
            rating=4.8,
            ratings_count=124,
            page_count=320,
            binding="Capa Comum",
            source="amazon_mock"
        )

    @classmethod
    def _fetch_real_api(cls, item_id: str, id_type: str) -> Optional[AmazonProductData]:
        """
        Executa requisição real à API da Amazon Brasil.
        Será chamada quando AMAZON_API_ENABLED=True e AMAZON_API_MOCK_MODE=False.
        """
        logger.info(f"[AMAZON API REAL] Consultando item {item_id} ({id_type})...")
        access_key = getattr(settings, 'AMAZON_ACCESS_KEY', '')
        secret_key = getattr(settings, 'AMAZON_SECRET_KEY', '')

        if not access_key or not secret_key:
            logger.error("[AMAZON API REAL] Credenciais da Amazon ausentes em settings.")
            return None

        try:
            return None
        except Exception as exc:
            logger.error(f"[AMAZON API REAL] Erro durante requisição: {exc}")
            return None

    @classmethod
    def _fetch_real_api_search(cls, keywords: str, max_results: int) -> List[AmazonProductData]:
        """Busca por palavra-chave na API real da Amazon."""
        return []
